#!/bin/bash

psql -h localhost -d augur -U augur -p 5432 -a -w -f 1-schema.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 2-augur_data.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 3-augur_operations.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 4-spdx.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 5-seed-data.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 6-schema_update_8.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -f 7-schema_update_9.sql
psql -h localhost -d augur -U augur -p 5432 -a -w -c "UPDATE augur_data.settings SET VALUE = 'repos/' WHERE setting='repo_directory';"



