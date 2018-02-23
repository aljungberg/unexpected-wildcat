#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# Deploy only on TeamCity
[[ -n ${TEAMCITY_VERSION+x} ]] || exit 0

. "$(dirname "${BASH_SOURCE[0]}")"/common.sh

DEPLOYABLES=(
    production
    staging
)

PUSHING=0
for branch in ${DEPLOYABLES[@]}; do
    [[ "$branch" == "$GITBRANCH" ]] && PUSHING=1
done

[[ $PUSHING -eq 0  ]] && exit 0

if [[ "$GITBRANCH" == "production" ]]; then
    echo 'Detected production environment.'
    GOOGLE_SERVICE_ACCOUNT="$GOOGLE_SERVICE_ACCOUNT_KEY_PROD"
else
    echo 'Detected staging environment.'
    GOOGLE_SERVICE_ACCOUNT="$GOOGLE_SERVICE_ACCOUNT_KEY_STAGE"
fi

# Login to docker
set +x
GCR_SA=$(echo $GOOGLE_SERVICE_ACCOUNT | base64 -d)
set -x

set +x
docker login -u _json_key -p "$GCR_SA" gcr.io
set -x

# Push images to repo
docker push "gcr.io/rc-apps-images/$APP:$GITHASH"

# Fetch deploy image
docker pull "gcr.io/rc-apps-images/deployer"

# Deploy on Kubernetes
docker run \
    -e "GOOGLE_SERVICE_ACCOUNT=$GOOGLE_SERVICE_ACCOUNT" \
    -e "GITHASH=$GITHASH" \
    -e "GITBRANCH=$GITBRANCH" \
    -e "APP=$APP" \
    gcr.io/rc-apps-images/deployer
