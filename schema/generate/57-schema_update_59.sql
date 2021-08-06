BEGIN; 

ALTER TABLE "augur_data"."contributors" 
  DROP CONSTRAINT "GH-UNIQUE-A";

update "augur_operations"."augur_settings" set value = 59 where setting = 'augur_data_version';


COMMIT; 

