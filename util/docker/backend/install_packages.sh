#!/bin/bash
set -euo pipefail

# Tell apt-get we're never going to be able to give manual
# feedback:
export DEBIAN_FRONTEND=noninteractive
uname -a
apt-get update
apt-get -y upgrade
#Net tools is for testing purposes
apt-get -y install --no-install-recommends procps

#Debian requires python3.8 to be built from source so these are needed
apt-get -y install --no-install-recommends build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev
curl -O https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tar.xz
tar -xf Python-3.8.2.tar.xz
cd Python-3.8.2
./configure --enable-optimizations
make -j 4
#This overwrites any other python binaries it finds so keep that in mind.
make install
cd ..
#Delete build files
rm *.tar.xz
rm -r Python-3.8.2

#facade
apt-get -y install --no-install-recommends git

# https://github.com/giampaolo/psutil/issues/1714
apt-get -y install --no-install-recommends gcc
uname -a
apt-get -y install --no-install-recommends python3-pip
#maybe this will fix it? 
#apt-get -y install --no-install-recommends python3.7 python3-pip
# python3.8-dev

apt-get clean
rm -rf /var/lib/apt/lists/*
