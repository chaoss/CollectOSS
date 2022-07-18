BEGIN;
ALTER TABLE "augur_data"."issue_events" ADD COLUMN IF NOT EXISTS "platform_id" int8;
update "augur_operations"."augur_settings" set value = 92 where setting = 'augur_data_version';
COMMIT;