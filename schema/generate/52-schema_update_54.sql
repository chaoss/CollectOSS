BEGIN;
DROP TABLE IF EXISTS "augur_data"."repo_deps_scorecard";
CREATE TABLE "augur_data"."repo_deps_scorecard" (
  "repo_deps_scorecard_id" serial8 NOT NULL,
  "repo_id" int8, 
  "name" varchar COLLATE "pg_catalog"."default",
  "status" varchar COLLATE "pg_catalog"."default",
  "score" varchar COLLATE "pg_catalog"."default",
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
ALTER TABLE "augur_data"."repo_deps_scorecard" ADD CONSTRAINT "repo_deps_scorecard_pkey1" PRIMARY KEY ("repo_deps_scorecard_id");

-- ----------------------------
-- Foreign Keys structure for table repo_deps_scorecard
-- ----------------------------
ALTER TABLE "augur_data"."repo_deps_scorecard" ADD CONSTRAINT "repo_id" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;


update "augur_operations"."augur_settings" set value = 54 
  where setting = 'augur_data_version'; 

COMMIT;