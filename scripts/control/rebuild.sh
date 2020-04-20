#!/bin/bash
set -eo pipefail

scripts/install/checks.sh

if [[ $? -ne 0 ]]; then
  exit 1
fi

echo "Cleaning up..."
scripts/control/clean.sh
echo

target=${1-prod}

echo
echo "Rebuilding backend and workers..."
scripts/install/backend.sh $target
scripts/install/workers.sh $target
echo

if [[ $target == *"dev"* ]]; then

    scripts/install/api_docs.sh
    scripts/install/frontend.sh
fi

echo
echo "Checking database version..."
augur db check-for-upgrade