#!/bin/bash
set -euo pipefail

scripts/install/checks.sh

if [[ $? -ne 0 ]]; then
  exit 1
fi

scripts/install/clean.sh

#rebuild everything
scripts/install/backend.sh
scripts/install/workers.sh
scripts/install/api_docs.sh
scripts/install/frontend.sh