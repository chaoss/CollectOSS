#!/usr/bin/env bash
#SPDX-License-Identifier: MIT
set -e

source /opt/venv/bin/activate


if [[ "$AUGUR_DB" == *"localhost"* ]]; then
    echo "localhost db connection"
    export AUGUR_DB="${AUGUR_DB/localhost/host.docker.internal}"
elif [[ "$AUGUR_DB" == *"127.0.0.1"* ]]; then
    echo "localhost db connection"
    export AUGUR_DB="${AUGUR_DB/127.0.0.1/host.docker.internal}"
fi



if [[ "$AUGUR_DB_SCHEMA_BUILD" == "1" ]]; then
    echo "why"
    augur db create-schema
fi

target="docker"
echo $target
export AUGUR_FACADE_REPO_DIRECTORY=/augur/facade/
export AUGUR_DOCKER_DEPLOY="1"

#Deal with special case where 'localhost' is the machine that started the container
if [[ "$REDIS_CONN_STRING" == *"localhost"* ]] || [[ "$REDIS_CONN_STRING" == *"127.0.0.1"* ]]; then
    echo "localhost redis connection"
    export redis_conn_string="redis://host.docker.internal:6379"
else
    export redis_conn_string=$REDIS_CONN_STRING
fi

./scripts/install/config.sh $target

if [[ -f /repo_groups.csv ]]; then
    augur db add-repo-groups /repo_groups.csv
fi

if [[ -f /repos.csv ]]; then
   augur db add-repos /repos.csv
fi

exec augur backend start