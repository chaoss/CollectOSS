#!/bin/bash

host=$1
database=$2
db_user=$3
port=$4

psql -h $host -d $database -U $db_user -p $port -a -w -c "\copy augur_data.repo_groups from  'schema/test_data/repo_groups.txt'" 
psql -h $host -d $database -U $db_user -p $port -a -w -c "\copy augur_data.repo from  'schema/test_data/repo.txt'" 

