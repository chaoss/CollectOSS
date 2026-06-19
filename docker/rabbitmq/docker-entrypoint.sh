#!/bin/sh
set -eu

python3 /update_config.py
exec /usr/local/bin/docker-entrypoint.sh "$@"
