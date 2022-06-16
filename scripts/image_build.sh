#!/bin/bash

# Builds a docker image tagged `ibot-build` that contains everything needed to build and deploy.
# Use: ./scripts/image_build.sh

set -eux

pushd support/docker
  docker build -t ibot-build .
popd
