BEGIN; 
ALTER TABLE "augur_data"."pull_request_review_message_ref" 
  DROP CONSTRAINT "fk_pull_request_review_message_ref_message_1",
  DROP CONSTRAINT "fk_pull_request_review_message_ref_pull_request_reviews_1",
  ADD CONSTRAINT "fk_pull_request_review_message_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "fk_pull_request_review_message_ref_pull_request_reviews_1" FOREIGN KEY ("pr_review_id") REFERENCES "augur_data"."pull_request_reviews" ("pr_review_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "fk_review_repo" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "augur_data"."pull_request_message_ref" 
  DROP CONSTRAINT "fk_pull_request_message_ref_message_1",
  DROP CONSTRAINT "fk_pull_request_message_ref_pull_requests_1",
  ADD CONSTRAINT "fk_pull_request_message_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "fk_pull_request_message_ref_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "fk_pr_repo" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE "augur_data"."issue_message_ref" 
  ALTER CONSTRAINT "fk_issue_message_ref_issues_1" DEFERRABLE INITIALLY DEFERRED,
  ALTER CONSTRAINT "fk_issue_message_ref_message_1" DEFERRABLE INITIALLY DEFERRED,
  ALTER CONSTRAINT "fk_repo_id_fk1" DEFERRABLE INITIALLY DEFERRED;

update "augur_operations"."augur_settings" set value = 85 where setting = 'augur_data_version'; 


COMMIT; 