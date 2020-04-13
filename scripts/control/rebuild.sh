#!/bin/bash
set -euo pipefail

scripts/install/checks.sh

if [[ $? -ne 0 ]]; then
  exit 1
fi

scripts/control/clean.sh

target=${1-prod}

#rebuild everything
scripts/install/backend.sh $target
scripts/install/workers.sh $target
scripts/install/api_docs.sh
scripts/install/frontend.sh