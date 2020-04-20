
-- ----------------------------
-- Table structure for pull_request_files
-- ----------------------------
DROP TABLE IF EXISTS "augur_data"."pull_request_files";
CREATE TABLE "augur_data"."pull_request_files" (
  "pull_request_id" int8,
  "tool_source" varchar(254) COLLATE "pg_catalog"."default",
  "tool_version" varchar(254) COLLATE "pg_catalog"."default",
  "data_source" varchar(254) COLLATE "pg_catalog"."default",
  "data_collection_date" date,
  "pr_file_id" int8 NOT NULL,
  "pr_file_additions" int8,
  "pr_file_deletions" int8,
  "pr_file_path" varchar(254) COLLATE "pg_catalog"."default"
)
;
ALTER TABLE "augur_data"."pull_request_files" OWNER TO "augur";

-- ----------------------------
-- Primary Key structure for table pull_request_files
-- ----------------------------
ALTER TABLE "augur_data"."pull_request_files" ADD CONSTRAINT "pull_request_files_pkey" PRIMARY KEY ("pr_file_id");

-- ----------------------------
-- Foreign Keys structure for table pull_request_files
-- ----------------------------
ALTER TABLE "augur_data"."pull_request_files" ADD CONSTRAINT "PR_ID-Files" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE;


update "augur_operations"."augur_settings" set value = 16 where setting = 'augur_data_version'; 
