#!/bin/bash

set -eux

# Update apt and install system deps
apt-get update
apt-get install -y awscli curl unzip zip

# Upgrade python build tools
python3 -m pip install --upgrade pip setuptools wheel pip-tools

# Install node and cdk
curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
apt-get update
apt-get install -y nodejs
npm install -g aws-cdk

# Clean apt caches
apt-get clean
