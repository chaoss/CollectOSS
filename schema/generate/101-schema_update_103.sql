BEGIN; 

ALTER TABLE "augur_data"."pull_requests" 
  ADD CONSTRAINT "unqiue-prurl" UNIQUE ("pr_url");

ALTER TABLE "augur_data"."pull_request_reviewers" 
  DROP CONSTRAINT "unique_pr_src_reviewer_key",
  ADD CONSTRAINT "unique_pr_src_reviewer_key" UNIQUE ("pull_request_id", "pr_reviewer_src_id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "augur_data"."pull_request_meta" 
  ADD CONSTRAINT "meta-unique" UNIQUE ("pull_request_id", "pr_head_or_base", "pr_sha");

ALTER TABLE "augur_data"."pull_request_assignees" 
  ADD CONSTRAINT "assigniees-unique" UNIQUE ("pull_request_id", "pr_assignee_src_id");

--
update "augur_operations"."augur_settings" set value = 103
  where setting = 'augur_data_version'; 
COMMIT; 