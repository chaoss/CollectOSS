BEGIN; 

ALTER TABLE "augur_data"."pull_requests" 
  ALTER COLUMN "pr_meta_head_id" TYPE varchar USING "pr_meta_head_id"::varchar,
  ALTER COLUMN "pr_meta_base_id" TYPE varchar USING "pr_meta_base_id"::varchar;

update "augur_operations"."augur_settings" set value = 86 where setting = 'augur_data_version'; 


COMMIT; 