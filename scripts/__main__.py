#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from asyncio import run
from sys import stdout

from .logging import log
from .play import down


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-l", "--language", default="English",
                        help="Language name, canonical or localized (default: English)")
    parser.add_argument("--timeout", default=100, type=int,
                        help="Timeout in seconds for page waits (default: 100)")
    parser.add_argument("-w", "--windows-version", choices=["10", "11"], default="11",
                        help="Windows version to download (10 or 11, default: 11)")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    uri = run(down(lang=args.language, timeout=args.timeout * 1000,
                     windows_version=args.windows_version))
    log.info("%s", uri)
    stdout.write(uri)


if __name__ == "__main__":
    main()
