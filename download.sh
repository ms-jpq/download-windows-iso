#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar nullglob


DIRNAME="$(dirname -- "$(realpath -- "$0")")"
cd -- "$DIRNAME" || exit 1

IMAGE="$(basename -- "$DIRNAME")-bindows"
LOG="$(mktemp)"

docker compose build
docker run -- "$IMAGE" "$@" | tee -- "$LOG"

URI="$(tail --lines 1 -- "$LOG")"

mkdir --parent -- "$DIRNAME/tmp"
cd './tmp' || exit 1
wget --content-disposition -- "$URI"
