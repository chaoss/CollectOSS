#!/bin/bash
set -euo pipefail

util/scripts/install/checks.sh

if [[ $? -ne 0 ]]; then
  exit 1
fi

#remove build files
rm -rf build/ dist/ docs/build/ workers/**/build/** workers/**/dist** node_modules frontend/node_modules

#rebuild everything
util/scripts/install/backend.sh
util/scripts/install/workers.sh
util/scripts/install/api_docs.sh
util/scripts/install/frontend.sh