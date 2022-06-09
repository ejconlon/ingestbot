#!/bin/bash

# Entrypoint for the packaged application:
#
#     unzip __PACKAGE_NAME__.zip
#     __PACKAGE_NAME__/entrypoint.sh --log-level debug

set -eux

PACKAGE_NAME="__PACKAGE_NAME__"
RUN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

pushd ${RUN_DIR}
  export PYTHONPATH="${RUN_DIR}:${PYTHONPATH:-}"

  if [ -d bin ]; then
    export PATH="${RUN_DIR}/bin:${PATH}"
  fi

  if [ -d ${PACKAGE}/bin ]; then
    export PATH="${RUN_DIR}/${PACKAGE_NAME}/bin:${PATH}"
  fi

  python3 -m ${PACKAGE_NAME}.main $@
popd
