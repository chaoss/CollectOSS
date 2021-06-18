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



update "augur_operations"."augur_settings" set value = 38 where setting = 'augur_data_version'; 
