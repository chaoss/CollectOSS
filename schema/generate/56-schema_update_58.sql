BEGIN; 



ALTER TABLE "augur_data"."message" 
  ADD COLUMN "platform_msg_id" int8,
  ADD COLUMN "platform_node_id" varchar;

ALTER TABLE "augur_data"."pull_request_review_message_ref" 
  ADD COLUMN "repo_id" int8;

ALTER TABLE "augur_data"."issue_message_ref" 
  ADD COLUMN "repo_id" int8;

update "augur_operations"."augur_settings" set value = 56 where setting = 'augur_data_version';


COMMIT; 

