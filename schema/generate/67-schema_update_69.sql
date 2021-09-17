BEGIN; 

CREATE TABLE "augur_data"."unresolved_commit_emails" (
  "email_unresolved_id" serial8,
  "email" varchar COLLATE "pg_catalog"."default" NOT NULL,
  "tool_source" varchar(255) COLLATE "pg_catalog"."default",
  "tool_version" varchar(255) COLLATE "pg_catalog"."default",
  "data_source" varchar(255) COLLATE "pg_catalog"."default",
  "data_collection_date" timestamp(0) DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("email_unresolved_id"),
  UNIQUE ("email")
)
;

ALTER TABLE "augur_data"."contributors_aliases" ADD CONSTRAINT "only-email-once" UNIQUE ("alias_email") DEFERRABLE INITIALLY DEFERRED;



update "augur_operations"."augur_settings" set value = 69 where setting = 'augur_data_version'; 

COMMIT; 
