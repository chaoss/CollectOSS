ALTER TABLE "augur_data"."releases" ALTER COLUMN "release_id" TYPE char(64) COLLATE "pg_catalog"."default" USING "release_id"::char(64);

ALTER TABLE "augur_data"."releases" ALTER COLUMN "release_description" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."releases" ADD COLUMN "tag_only" bool;

update "augur_operations"."augur_settings" set value = 26 where setting = 'augur_data_version'; 
