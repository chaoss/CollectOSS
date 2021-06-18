BEGIN;
DROP TABLE IF EXISTS "augur_data"."repo_deps_scorecard";
CREATE TABLE "augur_data"."repo_deps_scorecard" (
  "repo_deps_scorecard_id" serial8 NOT NULL,
  "repo_id" int8, 
  "ossf_active_status" varchar COLLATE "pg_catalog"."default",
  "ossf_branch_protection_status" varchar COLLATE "pg_catalog"."default",
  "ossf_ci_tests_status" varchar COLLATE "pg_catalog"."default",
  "ossf_cii_badge_status" varchar COLLATE "pg_catalog"."default",
  "ossf_code_review_status" varchar COLLATE "pg_catalog"."default",
  "ossf_contributors_status" varchar COLLATE "pg_catalog"."default",
  "ossf_frozen_deps_status" varchar COLLATE "pg_catalog"."default",
  "ossf_fuzzing_status" varchar COLLATE "pg_catalog"."default",
  "ossf_packaging_status" varchar COLLATE "pg_catalog"."default",
  "ossf_pull_request_status" varchar COLLATE "pg_catalog"."default",
  "ossf_sast_status" varchar COLLATE "pg_catalog"."default",
  "ossf_security_policy_status" varchar COLLATE "pg_catalog"."default",
  "ossf_signed_releases_status" varchar COLLATE "pg_catalog"."default",
  "ossf_signed_tags_status" varchar COLLATE "pg_catalog"."default",
  "ossf_active_score" varchar COLLATE "pg_catalog"."default",
  "ossf_branch_protection_score" varchar COLLATE "pg_catalog"."default",
  "ossf_ci_tests_score" varchar COLLATE "pg_catalog"."default",
  "ossf_cii_badge_score" varchar COLLATE "pg_catalog"."default",
  "ossf_code_review_score" varchar COLLATE "pg_catalog"."default",
  "ossf_contributors_score" varchar COLLATE "pg_catalog"."default",
  "ossf_frozen_deps_score" varchar COLLATE "pg_catalog"."default",
  "ossf_fuzzing_score" varchar COLLATE "pg_catalog"."default",
  "ossf_packaging_score" varchar COLLATE "pg_catalog"."default",
  "ossf_pull_request_score" varchar COLLATE "pg_catalog"."default",
  "ossf_sast_score" varchar COLLATE "pg_catalog"."default",
  "ossf_security_policy_score" varchar COLLATE "pg_catalog"."default",
  "ossf_signed_releases_score" varchar COLLATE "pg_catalog"."default",
  "ossf_signed_tags_score" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
)
;
ALTER TABLE "augur_data"."repo_deps_scorecard" OWNER TO "augur";

-- ----------------------------
-- Primary Key structure for table repo_deps_scorecard
-- ----------------------------
ALTER TABLE "augur_data"."repo_deps_scorecard" ADD CONSTRAINT "repo_deps_scorecard_pkey" PRIMARY KEY ("repo_deps_scorecard_id");

-- ----------------------------
-- Foreign Keys structure for table repo_deps_scorecard
-- ----------------------------
ALTER TABLE "augur_data"."repo_deps_scorecard" ADD CONSTRAINT "repo_id" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;


update "augur_operations"."augur_settings" set value = 52 
  where setting = 'augur_data_version'; 

COMMIT;
