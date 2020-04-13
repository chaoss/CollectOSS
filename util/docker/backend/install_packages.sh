#!/bin/bash
set -euo pipefail

# Tell apt-get we're never going to be able to give manual
# feedback:
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get -y upgrade
apt-get -y install --no-install-recommends procps

#facade
apt-get -y install --no-install-recommends git

# https://github.com/giampaolo/psutil/issues/1714
apt-get -y install --no-install-recommends gcc
apt-get -y install --no-install-recommends python3-dev

apt-get clean
rm -rf /var/lib/apt/lists/*
