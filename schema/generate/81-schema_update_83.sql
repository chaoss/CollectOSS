BEGIN; 

CREATE OR REPLACE FUNCTION create_constraint_if_not_exists (t_name text, c_name text, constraint_sql text)
  RETURNS void
AS
$BODY$
  BEGIN
    -- Look for our constraint
    IF NOT EXISTS (SELECT constraint_name
                   FROM information_schema.constraint_column_usage
                   WHERE constraint_name = c_name) THEN
        EXECUTE 'ALTER TABLE ' || t_name || ' ADD CONSTRAINT ' || c_name || ' ' || constraint_sql;
    END IF;
  END;
$BODY$
LANGUAGE plpgsql VOLATILE;

update "augur_operations"."augur_settings" set value = 83 where setting = 'augur_data_version'; 


COMMIT; 

BEGIN; 

DELETE FROM augur_data.pull_request_files a
USING pull_request_files b
WHERE a.pr_file_id < b.pr_file_id
AND a.pull_request_id = b.pull_request_id
AND a.repo_id = b.repo_id 
AND a.pr_file_path = b.pr_file_path;

SELECT create_constraint_if_not_exists('augur_data.pull_request_files', 'prfiles_unique', 'UNIQUE ("pull_request_id", "repo_id", "pr_file_path");');

SELECT create_constraint_if_not_exists('augur_data.pull_request_commits', 'pr_commit_nk', 'UNIQUE ("pull_request_id", "repo_id", "pr_cmt_sha")');

update "augur_operations"."augur_settings" set value = 83 where setting = 'augur_data_version'; 


COMMIT; 