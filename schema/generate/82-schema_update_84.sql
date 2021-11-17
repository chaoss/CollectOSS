BEGIN; 
ALTER TABLE "augur_data"."repo" 
  ALTER COLUMN "data_collection_date" SET DEFAULT CURRENT_TIMESTAMP;
update "augur_operations"."augur_settings" set value = 84 where setting = 'augur_data_version'; 


COMMIT; 