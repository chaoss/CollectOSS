-- #SPDX-License-Identifier: MIT
CREATE SEQUENCE "augur_data"."pull_request_files_pr_file_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 25150
CACHE 1;

CREATE TABLE "augur_data"."pull_request_files" (
  "pull_request_id" int8,
  "pr_file_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_files_pr_file_id_seq'::regclass),
  "pr_file_additions" int8,
  "pr_file_deletions" int8,
  "pr_file_path" varchar COLLATE "pg_catalog"."default",
	"tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_files_pkey" PRIMARY KEY ("pr_file_id")
)
;

ALTER TABLE "augur_data"."pull_request_files" OWNER TO "augur";

COMMENT ON TABLE "augur_data"."pull_request_files" IS 'Pull request commits are an enumeration of each commit associated with a pull request. 
Not all pull requests are from a branch or fork into master. 
The commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).
Therefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. 
In cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. ';

ALTER TABLE "augur_data"."pull_request_files" ADD CONSTRAINT "fk_pull_request_commits_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

SELECT setval('"augur_data"."pull_request_files_pr_file_id_seq"', 25150, true);

ALTER SEQUENCE "augur_data"."pull_request_files_pr_file_id_seq" OWNER TO "augur";

update "augur_operations"."augur_settings" set value = 16 where setting = 'augur_data_version'; 
