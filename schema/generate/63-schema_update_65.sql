BEGIN; 

ALTER TABLE "augur_data"."pull_request_message_ref" ADD CONSTRAINT "pr-comment-nk" UNIQUE ("pr_message_ref_src_comment_id", "tool_source");

ALTER TABLE "augur_data"."pull_request_review_message_ref" ADD CONSTRAINT "pr-review-nk" UNIQUE ("pr_review_msg_src_id", "tool_source");

DROP TABLE IF EXISTS "augur_data"."_dev1_repo_deps_scorecard";

update "augur_operations"."augur_settings" set value = 65 where setting = 'augur_data_version';


COMMIT; 

