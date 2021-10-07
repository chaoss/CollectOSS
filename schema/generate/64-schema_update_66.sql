BEGIN; 

ALTER TABLE "augur_data"."issues" ALTER COLUMN "issue_title" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."issues" ALTER COLUMN "issue_body" TYPE varchar COLLATE "pg_catalog"."default" USING "issue_body"::varchar;

ALTER TABLE "augur_data"."message" ALTER COLUMN "msg_text" TYPE varchar COLLATE "pg_catalog"."default" USING "msg_text"::varchar;

ALTER TABLE "augur_data"."message" ALTER COLUMN "msg_header" TYPE varchar COLLATE "pg_catalog"."default";

update "augur_operations"."augur_settings" set value = 66 where setting = 'augur_data_version';


COMMIT; 

