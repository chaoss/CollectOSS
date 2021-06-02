--  # Pull request commit updates
ALTER TABLE "augur_data"."pull_request_commits" ADD COLUMN "pr_cmt_author_cntrb_id" int8;
ALTER TABLE "augur_data"."pull_request_commits" ADD COLUMN "pr_cmt_timestamp" timestamp(0);
ALTER TABLE "augur_data"."pull_request_commits" ADD COLUMN "pr_cmt_author_email" varchar COLLATE "pg_catalog"."default";

update "augur_operations"."augur_settings" set value = 33 where setting = 'augur_data_version'; 
