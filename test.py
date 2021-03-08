#!/usr/bin/env python3

from pathlib import Path
from subprocess import check_call, check_output
from typing import Iterator

_TOP_LV = Path(__file__).parent
_SCRIPT = _TOP_LV / "download.py"
_MIN_SIZE = 1000 ** 3


def _git_added() -> Iterator[Path]:
    raw = check_output(("git", "status", "--ignored", "--short", "-z"), text=True)
    for line in raw.split("\0"):
        lhs, _, rhs = line.partition(" ")
        if lhs == "??":
            yield Path(rhs)


def main() -> None:
    check_call(("python3", _SCRIPT))
    for path in _git_added():
        stat = path.stat()
        if stat.st_size > _MIN_SIZE:
            break
    else:
        exit(1)


main()
