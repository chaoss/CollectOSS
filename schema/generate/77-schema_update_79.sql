BEGIN; 

ALTER TABLE "augur_data"."message" 
  DROP CONSTRAINT "REPOGROUPLISTER",
  DROP CONSTRAINT "platformer";

update "augur_operations"."augur_settings" set value = 79 where setting = 'augur_data_version'; 


COMMIT; 