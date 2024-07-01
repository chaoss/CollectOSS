#!/bin/bash
#SPDX-License-Identifier: MIT
set -e

source /opt/venv/bin/activate

export AUGUR_FACADE_REPO_DIRECTORY=/augur/facade/
export AUGUR_DOCKER_DEPLOY="1"

echo "Running with $AUGUR_FLAGS"

# Run the graphical startup wizard at port 5000
# -u option specifies unbuffered output
python -u ./scripts/install/wizard.py 5000
