-- Pull request worker schema changes for PR Reviews

CREATE SEQUENCE "augur_data"."pull_request_review_message_ref_pr_review_msg_ref_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

CREATE SEQUENCE "augur_data"."pull_request_reviews_pr_review_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

ALTER TABLE "augur_data"."pull_request_assignees" ADD COLUMN "pr_assignee_src_id" int8;

CREATE TABLE "augur_data"."pull_request_review_message_ref" (
  "pr_review_msg_ref_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_review_message_ref_pr_review_msg_ref_id_seq'::regclass),
  "pr_review_id" int8 NOT NULL,
  "msg_id" int8 NOT NULL,
  "pr_review_msg_url" varchar COLLATE "pg_catalog"."default",
  "pr_review_src_id" int8,
  "pr_review_msg_src_id" int8,
  "pr_review_msg_node_id" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_diff_hunk" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_path" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_position" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_original_position" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_commit_id" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_original_commit_id" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_updated_at" timestamp(6),
  "pr_review_msg_html_url" varchar COLLATE "pg_catalog"."default",
  "pr_url" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_author_association" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_start_line" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_original_start_line" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_start_side" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_line" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_original_line" varchar COLLATE "pg_catalog"."default",
  "pr_review_msg_side" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pr_review_msg_ref_id" PRIMARY KEY ("pr_review_msg_ref_id")
)
;

ALTER TABLE "augur_data"."pull_request_review_message_ref" OWNER TO "augur";

ALTER TABLE "augur_data"."pull_request_reviewers" ADD COLUMN "pr_reviewer_src_id" int8;

CREATE TABLE "augur_data"."pull_request_reviews" (
  "pr_review_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_reviews_pr_review_id_seq'::regclass),
  "pull_request_id" int8 NOT NULL,
  "cntrb_id" int8 NOT NULL,
  "pr_review_author_association" varchar(255) COLLATE "pg_catalog"."default",
  "pr_review_state" varchar(255) COLLATE "pg_catalog"."default",
  "pr_review_body" varchar(255) COLLATE "pg_catalog"."default",
  "pr_review_submitted_at" timestamp(6),
  "pr_review_src_id" int8,
  "pr_review_node_id" varchar(255) COLLATE "pg_catalog"."default",
  "pr_review_html_url" varchar(255) COLLATE "pg_catalog"."default",
  "pr_review_pull_request_url" varchar(255) COLLATE "pg_catalog"."default",
  "pr_review_commit_id" varchar(255) COLLATE "pg_catalog"."default",
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_review_id" PRIMARY KEY ("pr_review_id")
)
;

ALTER TABLE "augur_data"."pull_request_reviews" OWNER TO "augur";

ALTER TABLE "augur_data"."pull_request_review_message_ref" ADD CONSTRAINT "fk_pull_request_review_message_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "augur_data"."pull_request_review_message_ref" ADD CONSTRAINT "fk_pull_request_review_message_ref_pull_request_reviews_1" FOREIGN KEY ("pr_review_id") REFERENCES "augur_data"."pull_request_reviews" ("pr_review_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "augur_data"."pull_request_reviews" ADD CONSTRAINT "fk_pull_request_reviews_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE "augur_data"."pull_request_reviews" ADD CONSTRAINT "fk_pull_request_reviews_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

SELECT setval('"augur_data"."pull_request_review_message_ref_pr_review_msg_ref_id_seq"', 1, false);

ALTER SEQUENCE "augur_data"."pull_request_review_message_ref_pr_review_msg_ref_id_seq"
OWNED BY "augur_data"."pull_request_review_message_ref"."pr_review_msg_ref_id";

ALTER SEQUENCE "augur_data"."pull_request_review_message_ref_pr_review_msg_ref_id_seq" OWNER TO "augur";

SELECT setval('"augur_data"."pull_request_reviews_pr_review_id_seq"', 1, false);

ALTER SEQUENCE "augur_data"."pull_request_reviews_pr_review_id_seq"
OWNED BY "augur_data"."pull_request_reviews"."pr_review_id";

ALTER SEQUENCE "augur_data"."pull_request_reviews_pr_review_id_seq" OWNER TO "augur";



update "augur_operations"."augur_settings" set value = 36 where setting = 'augur_data_version'; 
