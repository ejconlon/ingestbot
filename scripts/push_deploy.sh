#!/bin/bash

# Trigger a deploy by pushing to the deploy branch
# Note that this tags the current origin master, so pull and compare before deploying.
# Use: ./scripts/push_deploy.sh [gh|aws] [dev]

set -eux

PLATFORM="$1"
ENVIRONMENT="$2"
shift
shift

if [[ "${PLATFORM}" != "gh" && "${PLATFORM}" != "aws" ]]; then
  echo "Supported platforms: {gh, aws}"
  exit 1
fi

if [[ "${ENVIRONMENT}" != "dev" ]]; then
  echo "Supported environments: {dev}"
  exit 1
fi

DEPLOY_BRANCH="deploy-${PLATFORM}-${ENVIRONMENT}"

git branch -f ${DEPLOY_BRANCH} origin/master
git push -f origin ${DEPLOY_BRANCH}
