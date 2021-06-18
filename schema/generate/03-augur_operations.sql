-- #SPDX-License-Identifier: MIT
-- ----------------------------
-- Sequence structure for gh_worker_history_history_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "augur_operations"."gh_worker_history_history_id_seq";
CREATE SEQUENCE "augur_operations"."gh_worker_history_history_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "augur_operations"."gh_worker_history_history_id_seq" OWNER TO "augur";

-- ----------------------------
-- Table structure for all
-- ----------------------------
DROP TABLE IF EXISTS "augur_operations"."all";
CREATE TABLE "augur_operations"."all" (
  "Name" varchar COLLATE "pg_catalog"."default",
  "Bytes" varchar COLLATE "pg_catalog"."default",
  "Lines" varchar COLLATE "pg_catalog"."default",
  "Code" varchar COLLATE "pg_catalog"."default",
  "Comment" varchar COLLATE "pg_catalog"."default",
  "Blank" varchar COLLATE "pg_catalog"."default",
  "Complexity" varchar COLLATE "pg_catalog"."default",
  "Count" varchar COLLATE "pg_catalog"."default",
  "WeightedComplexity" varchar COLLATE "pg_catalog"."default",
  "Files" varchar COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "augur_operations"."all" OWNER TO "augur";

-- ----------------------------
-- Table structure for cncf_users
-- ----------------------------
DROP TABLE IF EXISTS "augur_operations"."cncf_users";
CREATE TABLE "augur_operations"."cncf_users" (
  "login" varchar COLLATE "pg_catalog"."default",
  "email" varchar COLLATE "pg_catalog"."default",
  "affiliation" varchar COLLATE "pg_catalog"."default",
  "source" varchar COLLATE "pg_catalog"."default",
  "name" varchar COLLATE "pg_catalog"."default",
  "commits" int8,
  "location" varchar COLLATE "pg_catalog"."default",
  "country_id" varchar COLLATE "pg_catalog"."default",
  "sex" varchar COLLATE "pg_catalog"."default",
  "sex_prob" int8,
  "tz" varchar COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "augur_operations"."cncf_users" OWNER TO "augur";

-- ----------------------------
-- Table structure for science
-- ----------------------------
DROP TABLE IF EXISTS "augur_operations"."science";
CREATE TABLE "augur_operations"."science" (
  "name" varchar COLLATE "pg_catalog"."default",
  "description" varchar COLLATE "pg_catalog"."default",
  "details" varchar COLLATE "pg_catalog"."default",
  "maintainer" varchar COLLATE "pg_catalog"."default",
  "keywords" varchar COLLATE "pg_catalog"."default",
  "github" varchar COLLATE "pg_catalog"."default",
  "status" varchar COLLATE "pg_catalog"."default",
  "onboarding" varchar COLLATE "pg_catalog"."default",
  "on_cran" varchar COLLATE "pg_catalog"."default",
  "on_bioc" varchar COLLATE "pg_catalog"."default",
  "url" varchar COLLATE "pg_catalog"."default",
  "ropensci_category" varchar COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "augur_operations"."science" OWNER TO "augur";

-- ----------------------------
-- Table structure for worker_history
-- ----------------------------
DROP TABLE IF EXISTS "augur_operations"."worker_history";
CREATE TABLE "augur_operations"."worker_history" (
  "history_id" int8 NOT NULL DEFAULT nextval('"augur_operations".gh_worker_history_history_id_seq'::regclass),
  "repo_id" int8,
  "worker" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "job_model" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "oauth_id" int4 NOT NULL,
  "timestamp" timestamp(0) NOT NULL,
  "status" varchar(7) COLLATE "pg_catalog"."default" NOT NULL,
  "total_results" int4
)
;
ALTER TABLE "augur_operations"."worker_history" OWNER TO "augur";

-- ----------------------------
-- Table structure for worker_job
-- ----------------------------
DROP TABLE IF EXISTS "augur_operations"."worker_job";
CREATE TABLE "augur_operations"."worker_job" (
  "job_model" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "state" int4 NOT NULL DEFAULT 0,
  "zombie_head" int4,
  "since_id_str" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT '0'::character varying,
  "description" varchar(255) COLLATE "pg_catalog"."default" DEFAULT 'None'::character varying,
  "last_count" int4,
  "last_run" timestamp(0) DEFAULT NULL::timestamp without time zone,
  "analysis_state" int4 DEFAULT 0,
  "oauth_id" int4 NOT NULL
)
;
ALTER TABLE "augur_operations"."worker_job" OWNER TO "augur";

-- ----------------------------
-- Table structure for worker_oauth
-- ----------------------------
DROP TABLE IF EXISTS "augur_operations"."worker_oauth";
CREATE TABLE "augur_operations"."worker_oauth" (
  "oauth_id" int4 NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "consumer_key" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "consumer_secret" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "access_token" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "access_token_secret" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "repo_directory" varchar COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "augur_operations"."worker_oauth" OWNER TO "augur";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "augur_operations"."gh_worker_history_history_id_seq"
OWNED BY "augur_operations"."worker_history"."history_id";
SELECT setval('"augur_operations"."gh_worker_history_history_id_seq"', 39841, true);

-- ----------------------------
-- Primary Key structure for table worker_history
-- ----------------------------
ALTER TABLE "augur_operations"."worker_history" ADD CONSTRAINT "history_pkey" PRIMARY KEY ("history_id");

-- ----------------------------
-- Primary Key structure for table worker_job
-- ----------------------------
ALTER TABLE "augur_operations"."worker_job" ADD CONSTRAINT "job_pkey" PRIMARY KEY ("job_model");
