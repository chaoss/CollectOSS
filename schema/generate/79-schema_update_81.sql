BEGIN; 

ALTER TABLE "augur_operations"."augur_settings" 
  ALTER COLUMN "last_modified" SET DEFAULT CURRENT_TIMESTAMP,
  ADD CONSTRAINT "setting-unique" UNIQUE ("setting");

update "augur_operations"."augur_settings" set value = 81 where setting = 'augur_data_version'; 


COMMIT; 