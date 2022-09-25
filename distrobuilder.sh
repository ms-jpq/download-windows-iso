#!/usr/bin/env bash

set -eu

SRC="$1"
DST="$2"

exec distrobuilder repack-windows -- "$SRC" "$DST"
