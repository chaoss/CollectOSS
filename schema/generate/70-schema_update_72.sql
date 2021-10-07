BEGIN;

ALTER TABLE "augur_data"."pull_request_events" 
  ADD COLUMN "platform_id" int8 DEFAULT 25150,
  ADD COLUMN "pr_platform_event_id" int8,
  ADD COLUMN "repo_id" int8,
  ADD CONSTRAINT "fkpr_platform" FOREIGN KEY ("platform_id") REFERENCES "augur_data"."platform" ("pltfrm_id") ON DELETE RESTRICT ON UPDATE RESTRICT DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "fkprevent_repo_id" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE RESTRICT DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "unique-pr-event-id" UNIQUE ("pr_platform_event_id", "platform_id");

ALTER TABLE "augur_data"."pull_request_labels" 
  ADD CONSTRAINT "unique-pr-src-label-id" UNIQUE ("pr_src_id");


update "augur_operations"."augur_settings" set value = 72 where setting = 'augur_data_version'; 


COMMIT; 