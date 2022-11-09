#!/bin/bash
set -eo pipefail

scripts/control/clean.sh

scripts/install/checks.sh
if [[ $? -ne 0 ]]; then
  exit 1
fi


scripts/install/backend.sh
scripts/install/workers.sh

echo
echo "Checking database version..."
augur db check-for-upgrade
