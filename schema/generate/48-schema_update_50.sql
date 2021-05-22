/*
 Navicat Premium Data Transfer

 Source Server         : data.guillotine.io
 Source Server Type    : PostgreSQL
 Source Server Version : 120006
 Source Host           : data.guillotine.io:5432
 Source Catalog        : augur_osshealth
 Source Schema         : augur_data

 Target Server Type    : PostgreSQL
 Target Server Version : 120006
 File Encoding         : 65001

 Date: 29/04/2021 13:14:58
 
 This is base off of a SQL file suggested by Dr. Goggins
*/


-- ----------------------------
-- Table structure for contributors
-- ----------------------------
BEGIN;

DROP TABLE IF EXISTS "augur_data"."dependencies";

DROP TABLE IF EXISTS "augur_data"."repo_dependencies";

CREATE TABLE "augur_data"."repo_dependencies" (
  "repo_id" int8 NOT NULL,
  "dep_name" varchar(255),
  "dep_count" int,
  "dep_language" varchar(255),
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE "augur_data"."repo_dependencies" OWNER TO "augur";
COMMENT ON COLUMN "augur_data"."repo_dependencies"."repo_id" IS 'Forign key for repo id. ';
COMMENT ON COLUMN "augur_data"."repo_dependencies"."dep_name" IS 'Name of the dependancy found in project. ';
COMMENT ON COLUMN "augur_data"."repo_dependencies"."dep_count" IS 'Number of times the dependancy was found. ';
COMMENT ON COLUMN "augur_data"."repo_dependencies"."dep_language" IS 'Language of the dependancy. ';
COMMENT ON TABLE "augur_data"."repo_dependencies" IS 'Contains the dependencies for a repo.';

-- ----------------------------
-- Indexes structure for table contributors
-- leaving this blank for getting moving
-- ----------------------------


-- adding the constraint isn't working
-- ----------------------------
-- add foreign keys to tie into everything else
-- ----------------------------
ALTER TABLE "augur_data"."repo_dependencies" ADD CONSTRAINT "repo_id" FOREIGN KEY (repo_id) REFERENCES augur_data.repo(repo_id);

update "augur_operations"."augur_settings" set value = 50 where setting = 'augur_data_version'; 

COMMIT;
