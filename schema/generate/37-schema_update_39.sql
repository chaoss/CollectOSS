ALTER TABLE "augur_data"."pull_request_commits" DROP CONSTRAINT "fk_pull_request_commits_pull_requests_1";

ALTER TABLE "augur_data"."pull_request_events" DROP CONSTRAINT "fk_pull_request_events_pull_requests_1";

ALTER TABLE "augur_data"."pull_request_files" DROP CONSTRAINT "fk_pull_request_commits_pull_requests_1";

ALTER TABLE "augur_data"."pull_request_labels" DROP CONSTRAINT "fk_pull_request_labels_pull_requests_1";

ALTER TABLE "augur_data"."pull_request_message_ref" DROP CONSTRAINT "fk_pull_request_message_ref_pull_requests_1";

ALTER TABLE "augur_data"."pull_request_message_ref" DROP CONSTRAINT "fk_pull_request_message_ref_message_1";

ALTER TABLE "augur_data"."pull_request_meta" DROP CONSTRAINT "fk_pull_request_meta_pull_requests_1";

ALTER TABLE "augur_data"."pull_request_repo" DROP CONSTRAINT "fk_pull_request_repo_pull_request_meta_1";

ALTER TABLE "augur_data"."pull_request_review_message_ref" DROP CONSTRAINT "fk_pull_request_review_message_ref_pull_request_reviews_1";

ALTER TABLE "augur_data"."pull_request_reviewers" DROP CONSTRAINT "fk_pull_request_reviewers_pull_requests_1";

ALTER TABLE "augur_data"."pull_request_reviews" DROP CONSTRAINT "fk_pull_request_reviews_pull_requests_1";

ALTER TABLE "augur_data"."pull_request_reviews" ALTER COLUMN "pr_review_author_association" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."pull_request_reviews" ALTER COLUMN "pr_review_state" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."pull_request_reviews" ALTER COLUMN "pr_review_body" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."pull_request_reviews" ALTER COLUMN "pr_review_node_id" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."pull_request_reviews" ALTER COLUMN "pr_review_html_url" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."pull_request_reviews" ALTER COLUMN "pr_review_pull_request_url" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."pull_request_reviews" ALTER COLUMN "pr_review_commit_id" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."pull_request_reviews" ALTER COLUMN "tool_source" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."pull_request_reviews" ALTER COLUMN "tool_version" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."pull_request_reviews" ALTER COLUMN "data_source" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."pull_request_teams" DROP CONSTRAINT "fk_pull_request_teams_pull_requests_1";

ALTER TABLE "augur_data"."pull_requests" DROP CONSTRAINT "fk_pull_requests_pull_request_meta_2";

ALTER TABLE "augur_data"."pull_requests" DROP CONSTRAINT "fk_pull_requests_pull_request_meta_1";

ALTER TABLE "augur_data"."pull_request_commits" ADD CONSTRAINT "fk_pull_request_commits_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_events" ADD CONSTRAINT "fk_pull_request_events_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_files" ADD CONSTRAINT "fk_pull_request_commits_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_labels" ADD CONSTRAINT "fk_pull_request_labels_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_message_ref" ADD CONSTRAINT "fk_pull_request_message_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_message_ref" ADD CONSTRAINT "fk_pull_request_message_ref_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_meta" ADD CONSTRAINT "fk_pull_request_meta_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_repo" ADD CONSTRAINT "fk_pull_request_repo_pull_request_meta_1" FOREIGN KEY ("pr_repo_meta_id") REFERENCES "augur_data"."pull_request_meta" ("pr_repo_meta_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_review_message_ref" ADD CONSTRAINT "fk_pull_request_review_message_ref_pull_request_reviews_1" FOREIGN KEY ("pr_review_id") REFERENCES "augur_data"."pull_request_reviews" ("pr_review_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_reviewers" ADD CONSTRAINT "fk_pull_request_reviewers_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_reviews" ADD CONSTRAINT "fk_pull_request_reviews_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_request_teams" ADD CONSTRAINT "fk_pull_request_teams_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_requests" ADD CONSTRAINT "fk_pull_requests_pull_request_meta_1" FOREIGN KEY ("pr_meta_head_id") REFERENCES "augur_data"."pull_request_meta" ("pr_repo_meta_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."pull_requests" ADD CONSTRAINT "fk_pull_requests_pull_request_meta_2" FOREIGN KEY ("pr_meta_base_id") REFERENCES "augur_data"."pull_request_meta" ("pr_repo_meta_id") ON DELETE CASCADE ON UPDATE CASCADE;



update "augur_operations"."augur_settings" set value = 39 where setting = 'augur_data_version'; 
