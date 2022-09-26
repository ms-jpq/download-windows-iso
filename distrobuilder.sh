#!/usr/bin/env bash

set -eu
set -o pipefail
shopt -s failglob globstar

DIRNAME="$(dirname -- "$0")"

cd "$DIRNAME" || exit 1


SRC="$*"
NAME="$(basename -- "$SRC")"
DST="$DIRNAME/tmp/${NAME%.*}.lxd.iso"

exec distrobuilder repack-windows --drivers ./tmp/virtio-win*.iso -- "$SRC" "$DST"
