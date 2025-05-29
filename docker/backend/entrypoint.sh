#!/bin/bash
#SPDX-License-Identifier: MIT
set -e

if [[ "$AUGUR_DB" == *"localhost"* ]]; then
    echo "localhost db connection"
    export AUGUR_DB="${AUGUR_DB/localhost/host.docker.internal}"
elif [[ "$AUGUR_DB" == *"127.0.0.1"* ]]; then
    echo "localhost db connection"
    export AUGUR_DB="${AUGUR_DB/127.0.0.1/host.docker.internal}"
fi

export AUGUR_FACADE_REPO_DIRECTORY=${AUGUR_FACADE_REPO_DIRECTORY:-/augur/facade/}
export AUGUR_DOCKER_DEPLOY="1"

#Deal with special case where 'localhost' is the machine that started the container
if [[ "$REDIS_CONN_STRING" == *"localhost"* ]] || [[ "$REDIS_CONN_STRING" == *"127.0.0.1"* ]]; then
    echo "localhost redis connection"
    export redis_conn_string="redis://host.docker.internal:6379"
else
    export redis_conn_string=$REDIS_CONN_STRING
fi

exec "$@"
