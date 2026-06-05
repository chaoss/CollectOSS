#!/bin/bash
#SPDX-License-Identifier: MIT
set -e

if [[ -f /repo_groups.csv ]]; then
    collectoss db add-repo-groups /repo_groups.csv
fi

if [[ -f /repos.csv ]]; then
   collectoss db add-repos /repos.csv
fi
exec collectoss backend start --pidfile /tmp/main.pid
