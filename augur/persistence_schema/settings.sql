/*
 Navicat Premium Data Transfer

 Source Server         : New Augur Mudcats
 Source Server Type    : PostgreSQL
 Source Server Version : 110004
 Source Host           : mudcats.augurlabs.io:5433
 Source Catalog        : augur_twitter_test
 Source Schema         : augur_data

 Target Server Type    : PostgreSQL
 Target Server Version : 110004
 File Encoding         : 65001

 Date: 15/07/2019 07:18:11
*/


-- ----------------------------
-- Table structure for settings
-- ----------------------------
DROP TABLE IF EXISTS "augur_data"."settings";
CREATE TABLE "augur_data"."settings" (
  "id" int4 NOT NULL,
  "setting" varchar(32) COLLATE "pg_catalog"."default" NOT NULL,
  "value" varchar(128) COLLATE "pg_catalog"."default" NOT NULL,
  "last_modified" timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP
)
;
ALTER TABLE "augur_data"."settings" OWNER TO "augur";

-- ----------------------------
-- Records of settings
-- ----------------------------
BEGIN;
INSERT INTO "augur_data"."settings" VALUES (5, 'report_date', 'committer', '2019-05-07 12:47:26');
INSERT INTO "augur_data"."settings" VALUES (6, 'report_attribution', 'author', '2019-05-07 12:47:26');
INSERT INTO "augur_data"."settings" VALUES (10, 'google_analytics', 'disabled', '2019-05-07 12:47:26');
INSERT INTO "augur_data"."settings" VALUES (11, 'update_frequency', '24', '2019-05-07 12:47:26');
INSERT INTO "augur_data"."settings" VALUES (12, 'database_version', '7', '2019-05-07 12:47:26');
INSERT INTO "augur_data"."settings" VALUES (13, 'results_visibility', 'show', '2019-05-07 12:47:26');
INSERT INTO "augur_data"."settings" VALUES (1, 'start_date', '2001-01-01', '1900-01-22 20:34:51');
INSERT INTO "augur_data"."settings" VALUES (4, 'log_level', 'Debug', '2019-05-07 12:47:26');
INSERT INTO "augur_data"."settings" VALUES (2, 'repo_directory', '/mnt/md0/repos/twitter-new-test/', '2019-05-07 12:47:26');
INSERT INTO "augur_data"."settings" VALUES (8, 'affiliations_processed', '2019-07-09 20:53:01.072787+00', '1900-01-22 20:36:27');
INSERT INTO "augur_data"."settings" VALUES (9, 'aliases_processed', '2019-07-09 20:53:01.074865+00', '1900-01-22 20:36:27');
INSERT INTO "augur_data"."settings" VALUES (7, 'working_author', 'done', '1900-01-22 20:23:43');
INSERT INTO "augur_data"."settings" VALUES (3, 'utility_status', 'Idle', '1900-01-22 20:38:07');
COMMIT;

-- ----------------------------
-- Primary Key structure for table settings
-- ----------------------------
ALTER TABLE "augur_data"."settings" ADD CONSTRAINT "settings_pkey" PRIMARY KEY ("id");
