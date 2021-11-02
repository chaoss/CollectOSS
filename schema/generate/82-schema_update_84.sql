BEGIN; 
ALTER TABLE "augur_data"."repo" 
  ALTER COLUMN "tool_source" SET DEFAULT CLI and API,
  ALTER COLUMN "tool_version" SET DEFAULT See release notes,
  ALTER COLUMN "data_source" SET DEFAULT Data Load,
  ALTER COLUMN "data_collection_date" SET DEFAULT CURRENT_TIMESTAMP;
update "augur_operations"."augur_settings" set value = 84 where setting = 'augur_data_version'; 


COMMIT; 