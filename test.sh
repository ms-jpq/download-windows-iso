#!/usr/bin/env bash

set -u
set -o pipefail


cd "$(dirname "$0")" || exit 1


./download.py
CODE=$?

PLACE_HOLDER='https://raw.githubusercontent.com/ms-jpq/docker-time-machine/tim-apple/preview/dog.JPG'


if [[ ! -f ./debug.png ]]
then
  wget --output-document debug.png -- "$PLACE_HOLDER"
fi


exit $CODE

