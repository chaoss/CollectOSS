#!/bin/bash
set -euo pipefail

# Tell apt-get we're never going to be able to give manual
# feedback:
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get -y upgrade
apt-get -y install --no-install-recommends procps
apt-get -y install --no-install-recommends git
apt-get clean
rm -rf /var/lib/apt/lists/*
