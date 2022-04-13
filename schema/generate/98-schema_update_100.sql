BEGIN; 
-- ----------------------------
-- Table structure for chaoss_user
-- ----------------------------
DROP TABLE IF EXISTS "augur_data"."chaoss_user";
CREATE TABLE "augur_data"."chaoss_user" (
  "chaoss_id" serial8 NOT NULL,
  "chaoss_login_name" varchar COLLATE "pg_catalog"."default",
  "chaoss_login_hashword" varchar COLLATE "pg_catalog"."default",
  "chaoss_email" varchar COLLATE "pg_catalog"."default",
  "chaoss_text_phone" varchar COLLATE "pg_catalog"."default",
  "chaoss_first_name" varchar COLLATE "pg_catalog"."default",
  "chaoss_last_name" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamptz(6) DEFAULT now()
)
;
ALTER TABLE "augur_data"."chaoss_user" OWNER TO "augur";

-- ----------------------------
-- Uniques structure for table chaoss_user
-- ----------------------------
ALTER TABLE "augur_data"."chaoss_user" ADD CONSTRAINT "chaoss_unique_email_key" UNIQUE ("chaoss_email");

-- ----------------------------
-- Primary Key structure for table chaoss_user
-- ----------------------------
ALTER TABLE "augur_data"."chaoss_user" ADD CONSTRAINT "chaoss_user_pkey" PRIMARY KEY ("chaoss_id");

update "augur_operations"."augur_settings" set value = 100 where setting = 'augur_data_version'; 

COMMIT; 