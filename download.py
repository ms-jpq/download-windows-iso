#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from http.client import HTTPResponse
from io import BufferedIOBase
from json import loads
from multiprocessing import cpu_count
from os import linesep
from pathlib import Path, PurePosixPath
from random import uniform
from shutil import get_terminal_size
from subprocess import CalledProcessError, check_call, check_output
from sys import stderr
from time import sleep
from typing import Iterator, Union, cast
from urllib.parse import urlsplit
from urllib.request import Request, build_opener
from uuid import uuid4

_FILE = Path(__file__).resolve()
_DOCKER_ENV = Path("/", ".dockerenv")
_DUMP = Path("/", "dump")
_DEBUG = _FILE.parent / "debug"

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
    print("...", end="", flush=True, file=stderr)
    sleep(uniform(0.5, 1))


@contextmanager
def _use_network() -> Iterator[str]:
    name = str(uuid4().hex)
    try:
        check_call(("docker", "network", "create", name))
        yield name
    finally:
        check_call(("docker", "network", "rm", name))


@contextmanager
def _use_remote(net_name: str) -> Iterator[str]:
    name = str(uuid4().hex)
    try:
        check_call(
            (
                "docker",
                "run",
                "--detach",
                "--name",
                name,
                "--network",
                net_name,
                "--shm-size",
                "500M",
                "selenium/standalone-firefox:latest",
            )
        )
        yield name
    finally:
        check_call(("docker", "rm", "--force", name))


def _run_in_docker(net_name: str, remote_name: str, lang: str, timeout: float) -> str:
    name = str(uuid4().hex)
    try:
        link = check_output(
            (
                "docker",
                "run",
                "--name",
                name,
                "--network",
                net_name,
                "-v",
                f"{_FILE}:/script.py",
                "python:latest",
                "python3",
                "/script.py",
                remote_name,
                "--language",
                lang,
                "--timeout",
                str(timeout),
            ),
            text=True,
        )
        return link
    finally:
        check_call(("docker", "rm", "--force", name))


def _download_link(remote: str, lang: str, timeout: float) -> str:
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver import Remote
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    # from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.expected_conditions import element_to_be_clickable
    from selenium.webdriver.support.ui import WebDriverWait

    # def dump(driver: WebDriver, name: str) -> None:
    # screen_dump = str(_DUMP / f"{name}-screenshot.png")
    # driver.get_screenshot_as_file(screen_dump)
    # (_DUMP / f"{name}-index.html").write_text(driver.page_source)

    try:
        endpoint = f"http://{remote}:4444/wd/hub"
        firefox = Remote(endpoint, DesiredCapabilities.FIREFOX)
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

        WebDriverWait(firefox, timeout=timeout).until(
            element_to_be_clickable((By.ID, _SECOND_BUTTON_ID))
        )
        _rand_slep()

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
        exit(1)


def _run_from_docker(lang: str, timeout: float, tries: int) -> str:
    with ThreadPoolExecutor() as pool, _use_network() as net_name:

        def single() -> str:
            with _use_remote(net_name) as remote_name:
                return _run_in_docker(
                    net_name, remote_name=remote_name, timeout=timeout, lang=lang
                )

        def multiple() -> Iterator[Future]:
            for _ in range(cpu_count()):
                yield pool.submit(single)

        for _ in range(tries):
            link = ""
            for fut in as_completed(tuple(multiple())):
                try:
                    ret = cast(str, fut.result())
                    if ret:
                        link = ret
                except CalledProcessError:
                    pass

            if link:
                return link
        else:
            raise RuntimeError()


def _read_io(io: BufferedIOBase, buf: int) -> Iterator[bytes]:
    chunk = io.read(buf)
    while chunk:
        yield chunk
        chunk = io.read(buf)


def _download(link: str) -> None:
    cols, _ = get_terminal_size()
    parsed = urlsplit(link)
    name = PurePosixPath(parsed.path).name
    dest = (Path() / name).resolve()
    tmp = dest.with_suffix(f"{dest.suffix}.part")

    with _urlopen(link) as resp, tmp.open("wb") as fd:
        print(resp.headers, file=stderr)
        for key, val in resp.headers.items():
            if key.lower() == "content-length":
                tot = int(val)
                break
        else:
            raise RuntimeError()

        assert tot > (_MB * 1000)

        print("=" * cols, name, "=" * cols, sep=linesep, file=stderr)

        current = 0
        for chunk in _read_io(resp, _MB):
            fd.write(chunk)
            current += len(chunk)
            if current % (_MB * 10) == 0:
                percent = format(current / tot, ".2%")
                line = f"{current // _MB}MB / {tot // _MB}MB - {percent}"
                print(line, file=stderr)

        print("=" * cols, file=stderr)

    tmp.rename(dest)


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--tries", type=int, default=66)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--language", default="English")
    if _DOCKER_ENV.exists():
        parser.add_argument("remote")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    lang = args.language
    timeout = args.timeout

    if _DOCKER_ENV.exists():
        _DUMP.mkdir(parents=True, exist_ok=True)
        remote = args.remote
        print("...", end="", flush=True, file=stderr)
        check_output(("pip3", "install", "selenium"))
        print("...", end="", flush=True, file=stderr)
        link = _download_link(remote, lang=lang, timeout=timeout)
        print(link, end="")
    else:
        print("...", file=stderr)
        link = _run_from_docker(lang=lang, timeout=timeout, tries=args.tries)
        print(link, file=stderr)
        _download(link=link)


main()
