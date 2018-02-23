#!/bin/bash
set -xeuo pipefail
IFS=$'\n\t'

SCRIPTDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SOURCEDIR=$(git rev-parse --show-toplevel)
GITBRANCH=$(git rev-parse --abbrev-ref HEAD)
GITHASH=$(git rev-parse --short HEAD)
APP="unexpected-wildcat"
