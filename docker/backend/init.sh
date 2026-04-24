#!/bin/bash
#SPDX-License-Identifier: MIT
set -e

if [[ "$AUGUR_DB_SCHEMA_BUILD" == "1" ]]; then
    collectoss db create-schema
fi


if [ ! -v AUGUR_NO_CONFIG ]; then
	./scripts/docker/config.sh docker
fi

if [[ -f /repo_groups.csv ]]; then
    collectoss db add-repo-groups /repo_groups.csv
fi

if [[ -f /repos.csv ]]; then
   collectoss db add-repos /repos.csv
fi

echo "PATH: $PATH"
echo "Python executable: $(which python)"
python --version

exec collectoss backend start --pidfile /tmp/main.pid
