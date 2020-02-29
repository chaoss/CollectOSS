#!/bin/bash
set -euo pipefail

./scripts/control/augur.sh
echo "Waiting for the server to start... (this will take a moment)"
./scripts/control/collect.sh
echo "Workers have been started. Happy collecting!"