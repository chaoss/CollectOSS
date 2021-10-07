BEGIN; 

ALTER TABLE "augur_data"."pull_request_labels" 
  DROP CONSTRAINT "unique-pr-src-label-id",
  ADD CONSTRAINT "unique-pr-src-label-id" UNIQUE ("pr_src_id", "pull_request_id");

ALTER TABLE "augur_data"."issue_labels" 
  ADD CONSTRAINT "unique_issue_label" UNIQUE ("label_src_id", "issue_id");


ALTER TABLE "augur_data"."issue_events" 
  ADD CONSTRAINT "unique_event_id_key" UNIQUE ("issue_id", "issue_event_src_id");

COMMENT ON CONSTRAINT "unique_event_id_key" ON "augur_data"."issue_events" IS 'Natural key for issue events. ';

ALTER TABLE "augur_data"."pull_request_reviewers" 
  ADD COLUMN "pr_source_id" int8;

ALTER TABLE "augur_data"."pull_request_reviewers" 
  ADD CONSTRAINT "unique_pr_src_reviewer_key" UNIQUE ("pr_source_id", "pr_reviewer_src_id") DEFERRABLE INITIALLY DEFERRED;

COMMENT ON COLUMN "augur_data"."pull_request_reviewers"."pr_reviewer_src_id" IS 'The platform ID for the pull/merge request reviewer. Used as part of the natural key, along with pr_source_id in this table. ';

COMMENT ON COLUMN "augur_data"."pull_request_reviewers"."pr_source_id" IS 'The platform ID for the pull/merge request. Used as part of the natural key, along with pr_reviewer_src_id in this table. ';



update "augur_operations"."augur_settings" set value = 78 where setting = 'augur_data_version'; 


COMMIT; 