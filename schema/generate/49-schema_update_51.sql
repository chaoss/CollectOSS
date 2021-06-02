BEGIN;

ALTER TABLE IF EXISTS "augur_data"."repo_dependencies" 
  ALTER COLUMN "repo_id" DROP NOT NULL,
  ADD PRIMARY KEY ("repo_dependencies_id");

update "augur_operations"."augur_settings" set value = 51 
  where setting = 'augur_data_version'; 

COMMIT;
