#!/usr/bin/env bash

set -Eeu
set -o pipefail
shopt -s globstar nullglob

DIRNAME="$(dirname -- "$0")"

cd -- "$DIRNAME" || exit 1


SRC="$*"
NAME="$(basename -- "$SRC")"
DST="$DIRNAME/tmp/${NAME%.*}.lxd.iso"

# apt install --yes -- libwin-hivex-perl
exec distrobuilder repack-windows --drivers ./tmp/virtio-win*.iso -- "$SRC" "$DST"
