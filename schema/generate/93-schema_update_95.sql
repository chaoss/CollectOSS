BEGIN; 
ALTER TABLE "augur_data"."pull_request_commits" 
  ALTER COLUMN "pr_cmt_comments_url" TYPE varchar USING "pr_cmt_comments_url"::varchar;
update "augur_operations"."augur_settings" set value = 95 
  where setting = 'augur_data_version'; 
COMMIT; 

