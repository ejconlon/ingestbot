#!/bin/bash

set -eux

pushd support/docker
  docker build -t ibot-build .
popd
