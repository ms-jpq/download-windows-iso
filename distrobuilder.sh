#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s nullglob globstar

DIRNAME="$(dirname -- "$0")"

cd "$DIRNAME" || exit 1


SRC="$*"
NAME="$(basename -- "$SRC")"
DST="$DIRNAME/tmp/${NAME%.*}.lxd.iso"

exec distrobuilder repack-windows --drivers ./virtio-win*.iso -- "$SRC" "$DST"
