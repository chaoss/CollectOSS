COMMENT ON TABLE "augur_data"."contributor_repo" IS 'Developed in Partnership with Andrew Brain';

ALTER TABLE "augur_data"."contributor_repo" ADD COLUMN IF NOT EXISTS "repo_id" int8 NOT NULL;

ALTER TABLE "augur_data"."contributor_repo" ADD COLUMN IF NOT EXISTS "repo_name" varchar COLLATE "pg_catalog"."default" NOT NULL;

ALTER TABLE "augur_data"."contributor_repo" ADD COLUMN IF NOT EXISTS "event_id" int8 NOT NULL;

ALTER TABLE "augur_data"."contributor_repo" ADD COLUMN IF NOT EXISTS "created_at" timestamp(0) NOT NULL;

ALTER TABLE "augur_data"."contributors_aliases" DROP CONSTRAINT IF EXISTS "fk_contributors_aliases_contributors_1";

ALTER TABLE "augur_data"."message" DROP CONSTRAINT IF EXISTS "fk_message_repo_groups_list_serve_1";

ALTER TABLE "augur_data"."message" DROP CONSTRAINT IF EXISTS "fk_message_platform_1";

ALTER TABLE "augur_data"."message" DROP CONSTRAINT IF EXISTS "fk_message_contributors_1";

ALTER TABLE "augur_data"."pull_request_reviewers" DROP CONSTRAINT IF EXISTS "fk_pull_request_reviewers_contributors_1";

ALTER TABLE "augur_data"."pull_request_reviews" DROP CONSTRAINT IF EXISTS "fk_pull_request_reviews_contributors_1";

ALTER TABLE "augur_data"."pull_requests" DROP CONSTRAINT IF EXISTS "fk_pull_requests_repo_1";

ALTER TABLE "augur_data"."contributors_aliases" DROP CONSTRAINT IF EXISTS "fk_alias_id"; 

ALTER TABLE "augur_data"."pull_request_commits" DROP CONSTRAINT IF EXISTS "fk_pr_commit_cntrb_id";

ALTER TABLE "augur_data"."contributors_aliases" ADD CONSTRAINT "fk_alias_id" FOREIGN KEY ("cntrb_a_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE CASCADE ON UPDATE CASCADE NOT VALID;

ALTER TABLE "augur_data"."contributors_aliases" ADD CONSTRAINT "fk_contributors_aliases_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE CASCADE ON UPDATE CASCADE NOT VALID;

ALTER TABLE "augur_data"."message" ADD CONSTRAINT  "fk_message_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE CASCADE ON UPDATE CASCADE NOT VALID;

ALTER TABLE "augur_data"."message" ADD CONSTRAINT  "fk_message_platform_1" FOREIGN KEY ("pltfrm_id") REFERENCES "augur_data"."platform" ("pltfrm_id") ON DELETE CASCADE ON UPDATE CASCADE NOT VALID;

ALTER TABLE "augur_data"."message" ADD CONSTRAINT "fk_message_repo_groups_list_serve_1" FOREIGN KEY ("rgls_id") REFERENCES "augur_data"."repo_groups_list_serve" ("rgls_id") ON DELETE CASCADE ON UPDATE CASCADE NOT VALID;

ALTER TABLE "augur_data"."pull_request_commits" ADD CONSTRAINT  "fk_pr_commit_cntrb_id" FOREIGN KEY ("pr_cmt_author_cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE CASCADE ON UPDATE CASCADE NOT VALID;

ALTER TABLE "augur_data"."pull_request_reviewers" ADD CONSTRAINT  "fk_pull_request_reviewers_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE CASCADE ON UPDATE CASCADE NOT VALID;

ALTER TABLE "augur_data"."pull_request_reviews" ADD CONSTRAINT  "fk_pull_request_reviews_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE CASCADE ON UPDATE CASCADE NOT VALID;

ALTER TABLE "augur_data"."pull_requests" ADD CONSTRAINT  "fk_pr_contribs" FOREIGN KEY ("pr_augur_contributor_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE CASCADE ON UPDATE CASCADE NOT VALID;

ALTER TABLE "augur_data"."pull_requests" ADD CONSTRAINT  "fk_pull_requests_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE CASCADE ON UPDATE CASCADE NOT VALID;

update "augur_operations"."augur_settings" set value = 40 where setting = 'augur_data_version'; 
