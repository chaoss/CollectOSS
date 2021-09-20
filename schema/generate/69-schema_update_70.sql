BEGIN;

ALTER TABLE "augur_data"."message" ADD COLUMN "repo_id" int8;


ALTER TABLE "augur_data"."message" 
  ADD CONSTRAINT "fk_message_repoid" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;


update "augur_operations"."augur_settings" set value = 71 where setting = 'augur_data_version'; 


COMMIT; 