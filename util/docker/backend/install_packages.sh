#!/bin/bash
set -euo pipefail

apt-get update
apt-get -y upgrade
apt-get -y install --no-install-recommends procps
apt-get clean
rm -rf /var/lib/apt/lists/*
