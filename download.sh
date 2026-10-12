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

case "$URI" in
    https://software.download.prss.microsoft.com/*) ;;
    *)
        echo "error: the container did not return a valid ISO URL (got: '$URI')" >&2
        exit 1
        ;;
esac

mkdir --parent -- "$DIRNAME/tmp"
cd './tmp' || exit 1

echo "Downloading $(basename -- "${URI%%\?*}") ..."
wget --content-disposition --continue --tries=3 --timeout=60 \
    --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" \
    -- "$URI"
