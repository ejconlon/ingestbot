#!/bin/bash

# Entrypoint for the packaged application. Example:
#
#     unzip __COMPONENT_NAME__.zip -d __COMPONENT_NAME__
#     __COMPONENT_NAME__/entrypoint.sh --log-level debug

set -eux

COMPONENT_NAME="__COMPONENT_NAME__"
RUN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

cd ${RUN_DIR}

export PYTHONPATH="${RUN_DIR}:${PYTHONPATH:-}"

if [ -d bin ]; then
  export PATH="${RUN_DIR}/bin:${PATH}"
fi

if [ -d ${COMPONENT_NAME}/bin ]; then
  export PATH="${RUN_DIR}/${COMPONENT_NAME}/bin:${PATH}"
fi

exec python3 -m ${COMPONENT_NAME}.main $@
