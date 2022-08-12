#!/usr/bin/env bash
#SPDX-License-Identifier: MIT
set -e

source /opt/venv/bin/activate


if [[ "$AUGUR_DB_SCHEMA_BUILD" == "1" ]]; then
    augur db create-schema
fi

target='docker'
export AUGUR_FACADE_REPO_DIRECTORY=/augur/facade/

./scripts/install/config.sh $target

if [[ -f /repo_groups.csv ]]; then
    augur db add-repo-groups /repo_groups.csv
fi

if [[ -f /repos.csv ]]; then
   augur db add-repos /repos.csv
fi

exec augur backend start