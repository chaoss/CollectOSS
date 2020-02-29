#!/bin/bash
set -euo pipefail

scripts/install/checks.sh

if [[ $? -ne 0 ]]; then
  exit 1
fi

#remove build files
rm -rf build/ dist/ docs/build/ workers/**/build/** workers/**/dist** node_modules frontend/node_modules

#rebuild everything
scripts/install/backend.sh
scripts/install/workers.sh
scripts/install/api_docs.sh
scripts/install/frontend.sh