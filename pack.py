#!/usr/bin/env python3

from pathlib import Path
from subprocess import CalledProcessError, check_call
from sys import executable

_TOP_LV = Path(__file__).resolve().parent
_SCRIPT = _TOP_LV / "download.py"


def main() -> None:
    check_call(("apt-get", "install", "--yes", "--", "wimtools", "libguestfs-tools"))
    try:
        check_call(("snap", "install", "--classic", "--edge", "--", "distrobuilder"))
    except CalledProcessError:
        check_call(("snap", "refresh", "--classic", "--edge", "--", "distrobuilder"))
    check_call((executable, _SCRIPT, "--tries", "666"))
    for path in _TOP_LV.glob("*.iso"):
        dest = path.parent / path.with_name(f"packed-{path.name}")
        check_call(("distrobuilder", "repack-windows", str(path), str(dest)))


main()
