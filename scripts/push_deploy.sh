#!/bin/bash

# Trigger a deploy by pushing to the deploy branch
# Note that this tags the current origin master, so pull and compare before deploying.
# Use: ./scripts/push_deploy.sh [dev]

set -eux

ENVIRONMENT="$1"
shift

if [[ "${ENVIRONMENT}" != "dev" ]]; then
  echo "Supported environments: dev"
  exit 1
fi

DEPLOY_BRANCH="deploy-${ENVIRONMENT}"

git branch -f ${DEPLOY_BRANCH} origin/master
git push -f origin ${DEPLOY_BRANCH}
