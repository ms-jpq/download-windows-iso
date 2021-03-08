#!/usr/bin/env python3

from pathlib import Path
from subprocess import check_call, run
from sys import executable

_TOP_LV = Path(__file__).resolve().parent
_SCRIPT = _TOP_LV / "download.py"
_MIN_SIZE = 1000 ** 3

_PLACE_HOLDER = "https://raw.githubusercontent.com/ms-jpq/docker-time-machine/tim-apple/preview/dog.JPG"
_DEBUG = _TOP_LV / "debug.png"


def main() -> None:
    proc = run((executable, _SCRIPT))
    has_err = proc.returncode
    for path in _TOP_LV.glob("*.iso"):
        stat = path.stat()
        print(path, stat.st_size, _MIN_SIZE)
        if stat.st_size > _MIN_SIZE:
            break
    else:
        has_err = True

    if not _DEBUG.exists():
        check_call(("wget", "--output-document", str(_DEBUG), "--", _PLACE_HOLDER))

    exit(has_err)


main()
