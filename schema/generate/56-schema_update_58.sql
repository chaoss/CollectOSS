BEGIN; 

ALTER TABLE "augur_data"."contributors" 
  ADD CONSTRAINT "GH-UNIQUE-A" UNIQUE ("cntrb_login") DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "GH-UNIQUE-B" UNIQUE ("gh_user_id") DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "GH-UNIQUE-C" UNIQUE ("gh_login") DEFERRABLE INITIALLY DEFERRED;


ALTER TABLE IF EXISTS "augur_data"."message" 
  ADD COLUMN "platform_msg_id" int8,
  ADD COLUMN "platform_node_id" varchar;

ALTER TABLE IF EXISTS "augur_data"."pull_request_review_message_ref" 
  ADD COLUMN "repo_id" int8;

ALTER TABLE IF EXISTS "augur_data"."issue_message_ref" 
  ADD COLUMN "repo_id" int8;

ALTER TABLE IF EXISTS "augur_data"."pull_request_message_ref"
  ADD COLUMN "repo_id" int8; 

ALTER TABLE "augur_data"."issue_message_ref" 
  DROP CONSTRAINT  "fk_issue_message_ref_issues_1";

ALTER TABLE "augur_data"."issue_message_ref" 
  DROP CONSTRAINT  "fk_issue_message_ref_message_1"; 

ALTER TABLE "augur_data"."issue_message_ref" 
  ADD CONSTRAINT "fk_issue_message_ref_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT "fk_issue_message_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE RESTRICT ON UPDATE CASCADE;



update "augur_operations"."augur_settings" set value = 58 where setting = 'augur_data_version';


COMMIT; 

