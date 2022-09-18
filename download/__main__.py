#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from asyncio import run
from sys import stdout

from .logging import log
from .play import down


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--language", default="English International")
    parser.add_argument("--timeout", default=100, type=int)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    uri = run(down(lang=args.language, timeout=args.timeout * 1000))
    log.info("%s", uri)
    stdout.write(uri)


if __name__ == "__main__":
    main()
