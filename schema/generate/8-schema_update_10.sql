ALTER TABLE "augur_data"."repo" ALTER COLUMN "repo_git" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."repo" ALTER COLUMN "repo_name" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."repo_groups" ALTER COLUMN "rg_name" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."repo_groups" ALTER COLUMN "rg_description" TYPE varchar COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "augur_data"."pull_requests"."pr_src_id" IS 'The pr_src_id is unique across all of github.';

COMMENT ON COLUMN "augur_data"."pull_requests"."pr_src_number" IS 'The pr_src_number is unique within a repository.';

INSERT INTO "augur_operations"."augur_settings"("id", "setting", "value", "last_modified") VALUES (1, 'augur_data_version', '10', '2019-11-18 08:41:51');

update "augur_operations"."augur_settings" set value = 10 where setting = 'augur_data_version'; 
