BEGIN; 

ALTER TABLE "augur_data"."issue_events" 
  ADD COLUMN IF NOT EXISTS "platform_id" int8,
  ADD CONSTRAINT "fk_issue_event_platform_ide" FOREIGN KEY ("platform_id") REFERENCES "augur_data"."platform" ("pltfrm_id") ON DELETE RESTRICT ON UPDATE CASCADE;



update "augur_operations"."augur_settings" set value = 92 
  where setting = 'augur_data_version'; 


COMMIT; 