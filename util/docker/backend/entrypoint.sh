#!/usr/bin/env bash
#SPDX-License-Identifier: MIT
set -e

if [[ "$AUGUR_DB_SCHEMA_BUILD" == "1" ]]; then
    augur db create-schema
fi

augur config init \
    --db_name "${AUGUR_DB_NAME:-augur}" \
    --db_host "${AUGUR_DB_HOST:-database}" \
    --db_port "${AUGUR_DB_PORT:-5432}" \
    --db_user "${AUGUR_DB_DB_USER:-augur}" \
    --db_password "$AUGUR_DB_PASSWORD" \
    --github_api_key "$AUGUR_GITHUB_API_KEY"

if [[ -f /repo_groups.csv ]]; then
    augur db add-repo-groups /repo_groups.csv
fi

if [[ -f /repos.csv ]]; then
   augur db add-repos /repos.csv
fi

exec augur backend start
