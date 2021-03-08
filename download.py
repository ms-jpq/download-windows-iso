#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from http.client import HTTPResponse
from io import BufferedIOBase
from json import loads
from pathlib import Path, PurePosixPath
from random import random
from subprocess import CalledProcessError, check_call, check_output
from sys import stderr
from time import sleep
from typing import Iterator, Union, cast
from urllib.parse import urlsplit
from urllib.request import Request, build_opener
from uuid import uuid4

_FILE = Path(__file__).resolve()
_DOCKER_ENV = Path("/", ".dockerenv")
_DUMP = Path("/", "dump.png")
_DEBUG = "debug.png"

_MB = 1000 ** 2

_SITE = "https://www.microsoft.com/en-ca/software-download/windows10ISO"

_FIRST_SELECT_ID = "product-edition"
_FIRST_BUTTON_ID = "submit-product-edition"

_SECOND_SELECT_ID = "product-languages"
_SECOND_BUTTON_ID = "submit-sku"

_DOWNLOAD_BUTTON_CLASS = "product-download-type"


def _urlopen(req: Union[Request, str]) -> HTTPResponse:
    opener = build_opener()
    resp = opener.open(req)
    return cast(HTTPResponse, resp)


def _rand_slep() -> None:
    sleep(random() * 2)


def _download_link(remote: str, lang: str, timeout: float) -> str:
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver import Remote
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.support.expected_conditions import element_to_be_clickable
    from selenium.webdriver.support.ui import WebDriverWait

    endpoint = f"http://{remote}:4444/wd/hub"
    firefox = Remote(endpoint, DesiredCapabilities.FIREFOX)
    try:
        firefox.get(_SITE)

        WebDriverWait(firefox, timeout=timeout).until(
            element_to_be_clickable((By.ID, _FIRST_SELECT_ID))
        )
        _rand_slep()

        product = firefox.find_element_by_id(_FIRST_SELECT_ID)
        for option in product.find_elements_by_tag_name("option"):
            value = option.get_attribute("value") or ""
            if value.isdigit():
                option.click()
                break
        else:
            assert False

        WebDriverWait(firefox, timeout=timeout).until(
            element_to_be_clickable((By.ID, _FIRST_BUTTON_ID))
        )
        _rand_slep()

        button = firefox.find_element_by_id(_FIRST_BUTTON_ID)
        button.click()

        WebDriverWait(firefox, timeout=timeout).until(
            element_to_be_clickable((By.ID, _SECOND_SELECT_ID))
        )
        _rand_slep()

        languages = firefox.find_element_by_id(_SECOND_SELECT_ID)
        for option in languages.find_elements_by_tag_name("option"):
            value = option.get_attribute("value") or "{}"
            json = loads(value)
            if json.get("language") == lang:
                option.click()
                break
        else:
            assert False

        button = firefox.find_element_by_id(_SECOND_BUTTON_ID)
        button.click()

        WebDriverWait(firefox, timeout=timeout).until(
            element_to_be_clickable((By.CLASS_NAME, _DOWNLOAD_BUTTON_CLASS))
        )
        _rand_slep()

        button = firefox.find_element_by_link_text("64-bit Download")
        href = button.get_attribute("href")
        assert isinstance(href, str)
        return href
    except TimeoutException:
        firefox.get_screenshot_as_file(str(_DUMP))
        raise
    finally:
        firefox.quit()


def _run_from_docker(lang: str, timeout: float) -> str:
    net_name = str(uuid4().hex)
    name1, name2 = str(uuid4().hex), str(uuid4().hex)
    try:
        check_call(("docker", "network", "create", net_name))
        check_call(
            (
                "docker",
                "run",
                "--detach",
                "--name",
                name1,
                "--network",
                net_name,
                "--shm-size",
                "500M",
                "selenium/standalone-firefox:latest",
            )
        )

        try:
            link = check_output(
                (
                    "docker",
                    "run",
                    "--name",
                    name2,
                    "--network",
                    net_name,
                    "-v",
                    f"{_FILE}:/script.py",
                    "python:latest",
                    "/script.py",
                    name1,
                    "--language",
                    lang,
                    "--timeout",
                    str(timeout),
                ),
                text=True,
            )
        except CalledProcessError:
            check_call(("docker", "cp", f"{name2}:{_DUMP}", _DEBUG))
            raise

        return link
    finally:
        try:
            check_call(("docker", "rm", "--force", name1))
        finally:
            try:
                check_call(("docker", "rm", "--force", name2))
            finally:
                check_call(("docker", "network", "rm", net_name))


def _read_io(io: BufferedIOBase, buf: int) -> Iterator[bytes]:
    chunk = io.read1(buf)
    while chunk:
        yield chunk
        chunk = io.read1(buf)


def _download(link: str) -> None:

    parsed = urlsplit(link)
    name = PurePosixPath(parsed.path).name
    dest = Path() / name
    with _urlopen(link) as resp, dest.open("wb") as fd:
        print(resp.headers, file=stderr)
        for key, val in resp.headers.items():
            if key.lower() == "content-length":
                tot = int(val)
                break
        else:
            raise RuntimeError()

        assert tot > _MB * 1000
        print(dest, file=stderr)

        current = 0
        for chunk in _read_io(resp, _MB):
            fd.write(chunk)
            current += len(chunk)
            if current % (_MB * 10) == 0:
                print(
                    f"{current // _MB}MB / {tot // _MB}MB - {format(current / tot, '.2%')}"
                )


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--language", default="English")
    if _DOCKER_ENV.exists():
        parser.add_argument("remote")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    lang = args.language
    timeout = args.timeout

    if _DOCKER_ENV.exists():
        remote = args.remote
        check_output(("pip3", "install", "selenium"))
        link = _download_link(remote, lang=lang, timeout=timeout)
        print(link, end="")
    else:
        link = _run_from_docker(lang=lang, timeout=timeout)
        print(link, file=stderr)
        _download(link=link)


main()
