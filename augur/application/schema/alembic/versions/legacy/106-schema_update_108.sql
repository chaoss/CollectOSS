BEGIN; 
DROP MATERIALIZED VIEW IF EXISTS "augur_data"."api_get_all_repos_commits"; 
DROP MATERIALIZED VIEW IF EXISTS "augur_data"."api_get_all_repos_issues"; 


CREATE MATERIALIZED VIEW "augur_data"."api_get_all_repos_commits"
AS
SELECT commits.repo_id,
    count(DISTINCT commits.cmt_commit_hash) AS commits_all_time
   FROM augur_data.commits
  GROUP BY commits.repo_id;

ALTER MATERIALIZED VIEW "augur_data"."api_get_all_repos_commits" OWNER TO "augur";


CREATE MATERIALIZED VIEW "augur_data"."api_get_all_repos_issues"
AS
SELECT issues.repo_id,
    count(*) AS issues_all_time
   FROM augur_data.issues
  WHERE (issues.pull_request IS NULL)
  GROUP BY issues.repo_id;

ALTER MATERIALIZED VIEW "augur_data"."api_get_all_repos_issues" OWNER TO "augur";

GRANT SELECT ON "augur_data"."api_get_all_repos_commits" to PUBLIC; 
GRANT SELECT ON "augur_data"."api_get_all_repos_issues" to PUBLIC; 

update "augur_operations"."augur_settings" set value = 108
  where setting = 'augur_data_version'; 

COMMIT; 
