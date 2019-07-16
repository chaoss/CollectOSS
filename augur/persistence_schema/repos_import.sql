/*
 Navicat Premium Data Transfer

 Source Server         : New Augur Mudcats
 Source Server Type    : PostgreSQL
 Source Server Version : 110004
 Source Host           : mudcats.augurlabs.io:5433
 Source Catalog        : augur_rh
 Source Schema         : augur_operations

 Target Server Type    : PostgreSQL
 Target Server Version : 110004
 File Encoding         : 65001

 Date: 15/07/2019 06:40:18
*/


-- ----------------------------
-- Table structure for repos_import
-- ----------------------------
DROP TABLE IF EXISTS "augur_operations"."repos_import";
CREATE TABLE "augur_operations"."repos_import" (
  "repos_id" int8,
  "projects_id" int8,
  "repo_url" varchar COLLATE "pg_catalog"."default",
  "path" varchar COLLATE "pg_catalog"."default",
  "facade_name" varchar COLLATE "pg_catalog"."default",
  "added" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  "status" varchar(255) COLLATE "pg_catalog"."default",
  "name" varchar COLLATE "pg_catalog"."default",
  "description" varchar COLLATE "pg_catalog"."default",
  "project_url" varchar COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "augur_operations"."repos_import" OWNER TO "augur";
