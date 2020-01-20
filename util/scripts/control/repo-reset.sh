#!/bin/bash
export AUGUR_SCHEMA_HOME=$AUGUR_HOME/augur/persistence_schema 
cd AUGUR_SCHEMA_HOME
psql -h localhost -d redhat -U augur -p 5433 -a -w -f $AUGUR_HOME/augur/persistence_schema/repo-reset.sql


