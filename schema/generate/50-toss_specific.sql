/*
 Navicat PostgreSQL Data Transfer

 Source Server         : facetrust
 Source Server Type    : PostgreSQL
 Source Server Version : 120004
 Source Host           : facetrust.io:5433
 Source Catalog        : toss
 Source Schema         : toss_specific

 Target Server Type    : PostgreSQL
 Target Server Version : 120004
 File Encoding         : 65001

 Date: 27/11/2020 18:27:23
*/

ALTER TABLE augur_data.repo_info
ALTER COLUMN keywords DROP DEFAULT,
ALTER COLUMN keywords TYPE VARCHAR [] USING keywords :: CHARACTER VARYING [],
ALTER COLUMN keywords SET DEFAULT '{}';

-- ----------------------------
-- Sequence structure for contributor_language_experience_contributor_language_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "toss_specific"."contributor_language_experience_contributor_language_id_seq";
CREATE SEQUENCE "toss_specific"."contributor_language_experience_contributor_language_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "toss_specific"."contributor_language_experience_contributor_language_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for contributor_library_experience_contributor_library_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "toss_specific"."contributor_library_experience_contributor_library_id_seq";
CREATE SEQUENCE "toss_specific"."contributor_library_experience_contributor_library_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "toss_specific"."contributor_library_experience_contributor_library_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for file_extension_language_map_file_extension_language_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "toss_specific"."file_extension_language_map_file_extension_language_id_seq";
CREATE SEQUENCE "toss_specific"."file_extension_language_map_file_extension_language_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "toss_specific"."file_extension_language_map_file_extension_language_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_language_info_repo_language_info_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "toss_specific"."repo_language_info_repo_language_info_id_seq";
CREATE SEQUENCE "toss_specific"."repo_language_info_repo_language_info_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "toss_specific"."repo_language_info_repo_language_info_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for repo_library_info_repo_library_info_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "toss_specific"."repo_library_info_repo_library_info_id_seq";
CREATE SEQUENCE "toss_specific"."repo_library_info_repo_library_info_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "toss_specific"."repo_library_info_repo_library_info_id_seq" OWNER TO "augur";

-- ----------------------------
-- Sequence structure for users_user_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "toss_specific"."users_user_id_seq";
CREATE SEQUENCE "toss_specific"."users_user_id_seq"
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
ALTER SEQUENCE "toss_specific"."users_user_id_seq" OWNER TO "augur";

-- ----------------------------
-- Table structure for contributor_language_experience
-- ----------------------------
DROP TABLE IF EXISTS "toss_specific"."contributor_language_experience";
CREATE TABLE "toss_specific"."contributor_language_experience" (
  "contributor_language_id" int8 NOT NULL DEFAULT nextval('"toss_specific".contributor_language_experience_contributor_language_id_seq'::regclass),
  "augur_cntrb_id" int8,
  "language" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "earliest_commit_time" timestamp(6) NOT NULL,
  "commit_count" int8,
  "file_count" int8,
  "loc_additions" int8,
  "loc_deletions" int8,
  "data_collection_time" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "latest_commit_time" timestamp(6) NOT NULL
)
;
ALTER TABLE "toss_specific"."contributor_language_experience" OWNER TO "augur";

-- ----------------------------
-- Table structure for contributor_library_experience
-- ----------------------------
DROP TABLE IF EXISTS "toss_specific"."contributor_library_experience";
CREATE TABLE "toss_specific"."contributor_library_experience" (
  "contributor_library_id" int8 NOT NULL DEFAULT nextval('"toss_specific".contributor_library_experience_contributor_library_id_seq'::regclass),
  "augur_cntrb_id" int8,
  "library" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "earliest_commit_time" timestamp(6) NOT NULL,
  "commit_count" int8,
  "file_count" int8,
  "loc_additions" int8,
  "loc_deletions" int8,
  "data_collection_time" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "latest_commit_time" timestamp(6) NOT NULL
)
;
ALTER TABLE "toss_specific"."contributor_library_experience" OWNER TO "augur";

-- ----------------------------
-- Table structure for file_extension_language_map
-- ----------------------------
DROP TABLE IF EXISTS "toss_specific"."file_extension_language_map";
CREATE TABLE "toss_specific"."file_extension_language_map" (
  "file_extension_language_id" int8 NOT NULL DEFAULT nextval('"toss_specific".file_extension_language_map_file_extension_language_id_seq'::regclass),
  "file_extension" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "language" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "data_collection_time" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
ALTER TABLE "toss_specific"."file_extension_language_map" OWNER TO "augur";

-- ----------------------------
-- Table structure for repo_language_info
-- ----------------------------
DROP TABLE IF EXISTS "toss_specific"."repo_language_info";
CREATE TABLE "toss_specific"."repo_language_info" (
  "repo_language_info_id" int8 NOT NULL DEFAULT nextval('"toss_specific".repo_language_info_repo_language_info_id_seq'::regclass),
  "repo_id" int8 NOT NULL,
  "language" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "percentage" float8,
  "commit_count" int8,
  "file_count" int8,
  "earliest_commit_time" timestamp(6),
  "latest_commit_time" timestamp(6),
  "data_collection_time" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "loc_additions" int8,
  "loc_deletions" int8
)
;
ALTER TABLE "toss_specific"."repo_language_info" OWNER TO "augur";

-- ----------------------------
-- Table structure for repo_library_info
-- ----------------------------
DROP TABLE IF EXISTS "toss_specific"."repo_library_info";
CREATE TABLE "toss_specific"."repo_library_info" (
  "repo_library_info_id" int8 NOT NULL DEFAULT nextval('"toss_specific".repo_library_info_repo_library_info_id_seq'::regclass),
  "repo_id" int8 NOT NULL,
  "library" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "percentage" float8,
  "commit_count" int8,
  "file_count" int8,
  "earliest_commit_time" timestamp(6),
  "latest_commit_time" timestamp(6),
  "data_collection_time" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
ALTER TABLE "toss_specific"."repo_library_info" OWNER TO "augur";

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS "toss_specific"."users";
CREATE TABLE "toss_specific"."users" (
  "user_id" int8 NOT NULL DEFAULT nextval('"toss_specific".users_user_id_seq'::regclass),
  "dev_or_repo_account_type" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "augur_cntrb_id" int8,
  "augur_repo_id" int8,
  "user_email" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "user_password" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "data_collection_time" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "taken_quiz" bool DEFAULT false
)
;
ALTER TABLE "toss_specific"."users" OWNER TO "augur";

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "toss_specific"."contributor_language_experience_contributor_language_id_seq"
OWNED BY "toss_specific"."contributor_language_experience"."contributor_language_id";
SELECT setval('"toss_specific"."contributor_language_experience_contributor_language_id_seq"', 2, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "toss_specific"."contributor_library_experience_contributor_library_id_seq"
OWNED BY "toss_specific"."contributor_library_experience"."contributor_library_id";
SELECT setval('"toss_specific"."contributor_library_experience_contributor_library_id_seq"', 2, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "toss_specific"."file_extension_language_map_file_extension_language_id_seq"
OWNED BY "toss_specific"."file_extension_language_map"."file_extension_language_id";
SELECT setval('"toss_specific"."file_extension_language_map_file_extension_language_id_seq"', 1957, true);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "toss_specific"."repo_language_info_repo_language_info_id_seq"
OWNED BY "toss_specific"."repo_language_info"."repo_language_info_id";
SELECT setval('"toss_specific"."repo_language_info_repo_language_info_id_seq"', 2, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "toss_specific"."repo_library_info_repo_library_info_id_seq"
OWNED BY "toss_specific"."repo_library_info"."repo_library_info_id";
SELECT setval('"toss_specific"."repo_library_info_repo_library_info_id_seq"', 2, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "toss_specific"."users_user_id_seq"
OWNED BY "toss_specific"."users"."user_id";
SELECT setval('"toss_specific"."users_user_id_seq"', 24, true);

-- ----------------------------
-- Primary Key structure for table contributor_language_experience
-- ----------------------------
ALTER TABLE "toss_specific"."contributor_language_experience" ADD CONSTRAINT "contributor_language_id" PRIMARY KEY ("contributor_language_id");

-- ----------------------------
-- Primary Key structure for table contributor_library_experience
-- ----------------------------
ALTER TABLE "toss_specific"."contributor_library_experience" ADD CONSTRAINT "contributor_library_id" PRIMARY KEY ("contributor_library_id");

-- ----------------------------
-- Primary Key structure for table file_extension_language_map
-- ----------------------------
ALTER TABLE "toss_specific"."file_extension_language_map" ADD CONSTRAINT "file_extension_language_id" PRIMARY KEY ("file_extension_language_id");

-- ----------------------------
-- Primary Key structure for table repo_language_info
-- ----------------------------
ALTER TABLE "toss_specific"."repo_language_info" ADD CONSTRAINT "repo_language_info_id" PRIMARY KEY ("repo_language_info_id");

-- ----------------------------
-- Primary Key structure for table repo_library_info
-- ----------------------------
ALTER TABLE "toss_specific"."repo_library_info" ADD CONSTRAINT "repo_library_info_id" PRIMARY KEY ("repo_library_info_id");

-- ----------------------------
-- Primary Key structure for table users
-- ----------------------------
ALTER TABLE "toss_specific"."users" ADD CONSTRAINT "user_id" PRIMARY KEY ("user_id");

-- ----------------------------
-- Foreign Keys structure for table contributor_language_experience
-- ----------------------------
ALTER TABLE "toss_specific"."contributor_language_experience" ADD CONSTRAINT "fk_contributor_experience_contributors_1_copy_1" FOREIGN KEY ("augur_cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table contributor_library_experience
-- ----------------------------
ALTER TABLE "toss_specific"."contributor_library_experience" ADD CONSTRAINT "fk_contributor_experience_contributors_1" FOREIGN KEY ("augur_cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table repo_language_info
-- ----------------------------
ALTER TABLE "toss_specific"."repo_language_info" ADD CONSTRAINT "fk_repo_language_map_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table repo_library_info
-- ----------------------------
ALTER TABLE "toss_specific"."repo_library_info" ADD CONSTRAINT "fk_repo_library_map_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table users
-- ----------------------------
ALTER TABLE "toss_specific"."users" ADD CONSTRAINT "fk_users_contributors_1" FOREIGN KEY ("augur_cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "toss_specific"."users" ADD CONSTRAINT "fk_users_repo_1" FOREIGN KEY ("augur_repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE NO ACTION ON UPDATE NO ACTION;
