#!/usr/bin/env python3

from pathlib import Path
from shutil import make_archive
from subprocess import run
from sys import executable

_TOP_LV = Path(__file__).resolve().parent
_SCRIPT = _TOP_LV / "download.py"
_DEBUG = _TOP_LV / "debug"
_MIN_SIZE = 1000 ** 3


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

    make_archive("debug", "zip", root_dir=_DEBUG)
    exit(has_err)


main()
