#!/bin/bash
set -eo pipefail

scripts/control/clean.sh

scripts/install/checks.sh
if [[ $? -ne 0 ]]; then
  exit 1
fi

target=${1-prod}

scripts/install/backend.sh $target
scripts/install/workers.sh $target

echo
echo "Checking database version..."
augur db check-for-upgrade
