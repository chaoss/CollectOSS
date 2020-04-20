CREATE TABLE "augur_data"."pull_request_files" (
  "pull_reques" int8,
  "tool_source" varchar(254) COLLATE "pg_catalog"."default",
  "tool_versio" varchar(254) COLLATE "pg_catalog"."default",
  "data_source" varchar(254) COLLATE "pg_catalog"."default",
  "data_collec" date,
  "pr_file_id" int8 NOT NULL,
  "pr_file_add" int8,
  "pr_file_del" int8,
  "pr_file_pat" varchar(254) COLLATE "pg_catalog"."default",
  CONSTRAINT "pull_request_files_pkey" PRIMARY KEY ("pr_file_id")
)
;

ALTER TABLE "augur_data"."pull_request_files" ADD CONSTRAINT "PR_ID-Files" FOREIGN KEY ("pull_reques") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE;

ALTER TABLE "augur_data"."pull_request_files" OWNER TO "augur";

