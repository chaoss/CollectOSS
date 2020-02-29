#!/bin/bash
set -euo pipefail

./util/scripts/control/augur.sh
echo "Waiting for the server to start... (this will take a moment)"
./util/scripts/control/collect.sh
echo "Workers have been started. Happy collecting!"