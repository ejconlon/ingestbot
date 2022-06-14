#!/bin/bash

# Entrypoint for the packaged application. Example:
#
#     unzip ibot_cdk.zip -d ibot_cdk
#     IBOT_ENV=... AWS_REGION=... ibot_cdk/entrypoint.sh [options for cdk]

set -eux

RUN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

cd ${RUN_DIR}

export PYTHONPATH="${RUN_DIR}:${PYTHONPATH:-}"

exec cdk $@
