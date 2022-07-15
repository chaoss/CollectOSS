BEGIN; 
CREATE SEQUENCE "augur_operations"."chaoss_user_repos_user_repo_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

CREATE TABLE "augur_operations"."chaoss_user" (
  "chaoss_id" int8 NOT NULL DEFAULT nextval('augur_data.chaoss_user_chaoss_id_seq'::regclass),
  "chaoss_login_name" varchar COLLATE "pg_catalog"."default",
  "chaoss_login_hashword" varchar COLLATE "pg_catalog"."default",
  "chaoss_email" varchar COLLATE "pg_catalog"."default",
  "chaoss_text_phone" varchar COLLATE "pg_catalog"."default",
  "chaoss_first_name" varchar COLLATE "pg_catalog"."default",
  "chaoss_last_name" varchar COLLATE "pg_catalog"."default",
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamptz(6) DEFAULT now(),
  CONSTRAINT "chaoss_user_pkey" PRIMARY KEY ("chaoss_id"),
  CONSTRAINT "chaoss_unique_email_key" UNIQUE ("chaoss_email")
)
;

ALTER TABLE "augur_operations"."chaoss_user" OWNER TO "augur";

CREATE TABLE "augur_operations"."chaoss_user_repos" (
  "user_repo_id" int8 NOT NULL DEFAULT nextval('"augur_operations".chaoss_user_repos_user_repo_id_seq'::regclass),
  "chaoss_user_id" int8,
  "augur_rg_id" int8,
  "augur_repo_id" int8,
  "tool_source" varchar COLLATE "pg_catalog"."default",
  "tool_version" varchar COLLATE "pg_catalog"."default",
  "data_source" varchar COLLATE "pg_catalog"."default",
  "data_collection_date" timestamptz(6),
  CONSTRAINT "chaoss_user_repos_pkey" PRIMARY KEY ("user_repo_id")
)
;

ALTER TABLE "augur_operations"."chaoss_user_repos" OWNER TO "augur";

COMMENT ON COLUMN "augur_operations"."chaoss_user_repos"."chaoss_user_id" IS 'maps to chaoss_id in chaoss_user table in augur_operations. ';

COMMENT ON COLUMN "augur_operations"."chaoss_user_repos"."augur_rg_id" IS 'Maps to repo_group_id in repo_groups table in augur_data. ';

COMMENT ON COLUMN "augur_operations"."chaoss_user_repos"."augur_repo_id" IS 'Maps to repo_id in repos table in augur_data';

SELECT setval('"augur_operations"."chaoss_user_repos_user_repo_id_seq"', 1, false);

ALTER SEQUENCE "augur_operations"."chaoss_user_repos_user_repo_id_seq"
OWNED BY "augur_operations"."chaoss_user_repos"."user_repo_id";

ALTER SEQUENCE "augur_operations"."chaoss_user_repos_user_repo_id_seq" OWNER TO "augur";

update "augur_operations"."augur_settings" set value = 105
  where setting = 'augur_data_version'; 

COMMIT; 