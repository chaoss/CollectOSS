BEGIN; 

ALTER TABLE "augur_data"."pull_request_events" 
  DROP CONSTRAINT IF EXISTS "unique-pr-event-id",
  ADD CONSTRAINT "unique-pr-event-id" UNIQUE ("platform_id", "node_id");
--
update "augur_operations"."augur_settings" set value = 104
  where setting = 'augur_data_version'; 

COMMIT; 