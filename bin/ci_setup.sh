#!/bin/bash
set -xeuo pipefail
IFS=$'\n\t'

. "$(dirname "${BASH_SOURCE[0]}")"/common.sh

# show version in build log
docker --version

# remove stale containers if needed
"$SCRIPTDIR"/ci_clean.sh

docker build -f "Dockerfile" -t "gcr.io/rc-apps-images/$APP:$GITHASH" .
docker tag "gcr.io/rc-apps-images/$APP:$GITHASH" "gcr.io/rc-apps-images/$APP:latest"
docker build -f "Dockerfile-tests" -t "gcr.io/rc-apps-images/$APP-tests:$GITHASH" .
