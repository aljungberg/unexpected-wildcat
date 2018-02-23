#!/bin/bash
set -xeuo pipefail
IFS=$'\n\t'

. "$(dirname "${BASH_SOURCE[0]}")"/common.sh

docker rm -f "$APP" "$APP"-tests || true
