BEGIN; 
ALTER TABLE "augur_data"."pull_request_commits" 
  ALTER COLUMN "pr_cmt_comments_url" TYPE varchar USING "pr_cmt_comments_url"::varchar;
COMMIT; 

