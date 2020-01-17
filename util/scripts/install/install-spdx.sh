#!/bin/bash
cd workers/spdx_worker/
if [ ! -d "augur-spdx/" ]
then
  echo "Augur-SPDX has not been cloned"
  echo "Cloning it now..."
  git clone https://github.com/chaoss/augur-spdx.git augur-spdx
else
  echo "Augur-SPDX exists"
fi
cd augur-spdx
pip3 install .
./scripts/install-nomos.sh
cd ..
pwd
rm -r augur-spdx
