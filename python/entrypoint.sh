#!/bin/bash

# Entrypoint for the packaged application:
#
#     unzip ingestbot.zip
#     ingestbot/entrypoint.sh --log-level debug

set -eux

PACKAGE="ingestbot"
RUN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

pushd ${RUN_DIR}
  export PYTHONPATH="${RUN_DIR}:${PYTHONPATH:-}"

  if [ -d bin ]; then
    export PATH="${RUN_DIR}/bin:${PATH}"
  fi

  if [ -d ${PACKAGE}/bin ]; then
    export PATH="${RUN_DIR}/${PACKAGE}/bin:${PATH}"
  fi

  python3 -m ${PACKAGE}.main $@
popd
