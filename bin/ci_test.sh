#!/bin/bash
set -xeuo pipefail
IFS=$'\n\t'

. "$(dirname "${BASH_SOURCE[0]}")"/common.sh

echo "Running main tests..."

TEAMCITY_VERSION=${TEAMCITY_VERSION:-0}

DEV_MOUNT=""
PHABRICATOR_API_URL="https://truecode.trueship.com/api/"

if [[ "${DEV:-0}" == "1" ]]; then
    DEV_MOUNT="-v$SOURCEDIR:/app:rw"
fi

docker run \
    --rm \
    --name="$APP"-tests \
    $DEV_MOUNT \
    -e "PHABRICATOR_API_URL=PHABRICATOR_API_URL" \
    -e "PHABRICATOR_API_TOKEN=api-123" \
    -e "TEAMCITY_VERSION=$TEAMCITY_VERSION" \
    "gcr.io/rc-apps-images/$APP-tests:$GITHASH" \
    sh -c "nosetests"
