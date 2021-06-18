-- #SPDX-License-Identifier: MIT
ALTER TABLE "augur_operations"."worker_oauth" ADD COLUMN "platform" varchar COLLATE "pg_catalog"."default" DEFAULT 'github'::character varying;

update "augur_operations"."worker_oauth" set platform = 'github' where platform is NULL; 

update "augur_operations"."augur_settings" set value = 19 where setting = 'augur_data_version'; 
