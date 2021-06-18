-- #SPDX-License-Identifier: MIT
ALTER TABLE "augur_data"."repo" ALTER COLUMN "repo_git" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."repo" ALTER COLUMN "repo_name" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."repo_groups" ALTER COLUMN "rg_name" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."repo_groups" ALTER COLUMN "rg_description" TYPE varchar COLLATE "pg_catalog"."default";

COMMENT ON COLUMN "augur_data"."pull_requests"."pr_src_id" IS 'The pr_src_id is unique across all of github.';

COMMENT ON COLUMN "augur_data"."pull_requests"."pr_src_number" IS 'The pr_src_number is unique within a repository.';

update "augur_operations"."augur_settings" set value = 10 where setting = 'augur_data_version'; 
