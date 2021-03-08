#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from json import loads
from pathlib import Path
from shutil import which
from subprocess import check_call, check_output
from sys import stderr
from uuid import uuid4

_FILE = Path(__file__)
_DOCKER_ENV = Path("/", ".dockerenv")

_TIMEOUT = 10.0
_SITE = "https://www.microsoft.com/en-ca/software-download/windows10ISO"
_LANGUAGE = "English"

_FIRST_SELECT_ID = "product-edition"
_FIRST_BUTTON_ID = "submit-product-edition"

_SECOND_SELECT_ID = "product-languages"
_SECOND_BUTTON_ID = "submit-sku"

_DOWNLOAD_BUTTON_CLASS = "product-download-type"


def _download_link(remote: str) -> str:
    from selenium.webdriver import Remote
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.support.expected_conditions import element_to_be_clickable
    from selenium.webdriver.support.ui import WebDriverWait

    endpoint = f"http://{remote}:4444/wd/hub"
    firefox = Remote(endpoint, DesiredCapabilities.FIREFOX)
    try:
        firefox.get(_SITE)

        WebDriverWait(firefox, timeout=_TIMEOUT).until(
            element_to_be_clickable((By.ID, _FIRST_SELECT_ID))
        )
        product = firefox.find_element_by_id(_FIRST_SELECT_ID)
        for option in product.find_elements_by_tag_name("option"):
            value = option.get_attribute("value") or ""
            if value.isdigit():
                option.click()
                break
        else:
            assert False

        WebDriverWait(firefox, timeout=_TIMEOUT).until(
            element_to_be_clickable((By.ID, _FIRST_BUTTON_ID))
        )
        button = firefox.find_element_by_id(_FIRST_BUTTON_ID)
        button.click()

        WebDriverWait(firefox, timeout=_TIMEOUT).until(
            element_to_be_clickable((By.ID, _SECOND_SELECT_ID))
        )
        languages = firefox.find_element_by_id(_SECOND_SELECT_ID)

        for option in languages.find_elements_by_tag_name("option"):
            value = option.get_attribute("value") or "{}"
            json = loads(value)
            if json.get("language") == _LANGUAGE:
                option.click()
                break
        else:
            assert False

        button = firefox.find_element_by_id(_SECOND_BUTTON_ID)
        button.click()

        WebDriverWait(firefox, timeout=_TIMEOUT).until(
            element_to_be_clickable((By.CLASS_NAME, _DOWNLOAD_BUTTON_CLASS))
        )
        button = firefox.find_element_by_link_text("64-bit Download")
        href = button.get_attribute("href")
        return href
    finally:
        firefox.quit()


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    if _DOCKER_ENV.exists():
        parser.add_argument("remote")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if _DOCKER_ENV.exists():
        remote = args.remote
        check_call(("pip3", "install", "selenium"))
        link = _download_link(remote)

        print(link, file=stderr)
        print(link, end="")
    else:
        net_name = str(uuid4().hex)
        name = str(uuid4().hex)
        try:
            check_call(("docker", "network", "create", net_name))
            check_call(
                (
                    "docker",
                    "run",
                    "--detach",
                    "--name",
                    name,
                    "--shm-size",
                    "500M",
                    "selenium/standalone-firefox",
                )
            )
            link = check_output(
                (
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{_FILE}:/main",
                    "--entrypoint",
                    "/main",
                    "python",
                    name,
                )
            )
        except:
            pass
        else:
            if which("wget"):
                pass
            print(link)
        finally:
            try:
                check_call(("docker", "rm", "--force", name))
            finally:
                check_call(("docker", "network", "rm", net_name))



main()
