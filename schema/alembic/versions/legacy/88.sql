BEGIN; 

ALTER TABLE "augur_data"."pull_request_message_ref" 
  ADD COLUMN IF NOT EXISTS "pr_issue_url" varchar;

update "augur_operations"."augur_settings" set value = 88 where setting = 'augur_data_version'; 


COMMIT; 