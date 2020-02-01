#!/bin/bash

password=${POSTGRES_PASSWORD:-augur}
db_user=${POSTGRES_USER:-augur}
db_name=${POSTGRES_DB:-augur}

psql -h localhost -p 5432 -a -w -c "CREATE DATABASE $db_name;"
psql -h localhost -p 5432 -a -w -c "CREATE USER $db_user WITH ENCRYPTED PASSWORD '$password';"
psql -h localhost -p 5432 -a -w -c "ALTER DATABASE $db_name OWNER TO $db_user;"
psql -h localhost -p 5432 -a -w -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;"

psql -h localhost -d augur -U augur -p 5432 -a -w -f 1-schema.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 2-augur_data.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 3-augur_operations.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 4-spdx.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 5-seed-data.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 6-schema_update_8.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 7-schema_update_9.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -c "UPDATE augur_data.settings SET VALUE = 'repos/' WHERE setting='repo_directory';"
