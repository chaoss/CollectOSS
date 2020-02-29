#!/bin/bash
set -euo pipefail

if [[ ! -d logs ]]; then
    mkdir logs
fi

echo
echo "**********************************"
echo "Starting augur..."
echo "**********************************"
echo

nohup augur run > logs/augur.log 2>&1 &
