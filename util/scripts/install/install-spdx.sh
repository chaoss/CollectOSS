#!/bin/bash
cd spdx-scanner/
if [ ! -d "augur-spdx/" ]
then
  echo "Augur-SPDX has not been cloned"
  echo "Cloning it now..."
  git clone https://github.com/chaoss/augur-spdx.git augur-spdx
else
  echo "Augur-SPDX exists"
fi
cd augur-spdx
sudo apt-get install git python3-pip postgresql
sudo apt-get install libpq-dev
sudo apt-get install libglib2.0-dev libjsoncpp-dev libjson-c-dev
pip3 install .
./scripts/install-nomos.sh
