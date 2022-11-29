BEGIN; 
ALTER TABLE "augur_data"."dm_repo_annual" 
  ALTER COLUMN "email" TYPE varchar COLLATE "pg_catalog"."default",
  ALTER COLUMN "affiliation" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."dm_repo_group_monthly" 
  ALTER COLUMN "email" TYPE varchar COLLATE "pg_catalog"."default",
  ALTER COLUMN "affiliation" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."dm_repo_group_weekly" 
  ALTER COLUMN "email" TYPE varchar COLLATE "pg_catalog"."default",
  ALTER COLUMN "affiliation" TYPE varchar COLLATE "pg_catalog"."default";


ALTER TABLE "augur_data"."dm_repo_monthly" 
  ALTER COLUMN "email" TYPE varchar COLLATE "pg_catalog"."default",
  ALTER COLUMN "affiliation" TYPE varchar COLLATE "pg_catalog"."default";



--
update "augur_operations"."augur_settings" set value = 99
  where setting = 'augur_data_version'; 
 
