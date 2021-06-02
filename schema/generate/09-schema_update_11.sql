-- #SPDX-License-Identifier: MIT
CREATE SEQUENCE "augur_data"."pull_request_commits_pr_cmt_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

CREATE TABLE "augur_data"."pull_request_commits" (
  "pr_cmt_id" int8 NOT NULL DEFAULT nextval('"augur_data".pull_request_commits_pr_cmt_id_seq'::regclass),
  "pull_request_id" int8,
  "pr_cmt_sha" varchar COLLATE "pg_catalog"."default",
  "pr_cmt_node_id" varchar COLLATE "pg_catalog"."default",
  "pr_cmt_message" varchar COLLATE "pg_catalog"."default",
  "pr_cmt_comments_url" varbit,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "pull_request_commits_pkey" PRIMARY KEY ("pr_cmt_id")
)
;

ALTER TABLE "augur_data"."pull_request_commits" OWNER TO "augur";

COMMENT ON COLUMN "augur_data"."pull_request_commits"."pr_cmt_sha" IS 'This is the commit SHA for a pull request commit. If the PR is not to the master branch of the main repository (or, in rare cases, from it), then you will NOT find a corresponding commit SHA in the commit table. (see table comment for further explanation). ';

COMMENT ON TABLE "augur_data"."pull_request_commits" IS 'Pull request commits are an enumeration of each commit associated with a pull request. 
Not all pull requests are from a branch or fork into master. 
The commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).
Therefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. 
In cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. ';

ALTER TABLE "augur_data"."pull_request_commits" ADD CONSTRAINT "fk_pull_request_commits_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

SELECT setval('"augur_data"."pull_request_commits_pr_cmt_id_seq"', 3000000, true);

ALTER SEQUENCE "augur_data"."pull_request_commits_pr_cmt_id_seq"
OWNED BY "augur_data"."pull_request_commits"."pr_cmt_id";

ALTER SEQUENCE "augur_data"."pull_request_commits_pr_cmt_id_seq" OWNER TO "augur";

CREATE INDEX "repos_id,statusops" ON "augur_data"."repos_fetch_log" USING btree (
  "repos_id" "pg_catalog"."int4_ops" ASC NULLS LAST,
  "status" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);


update "augur_operations"."augur_settings" set value = 11 where setting = 'augur_data_version'; 
