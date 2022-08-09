BEGIN; 
DROP MATERIALIZED VIEW IF EXISTS "augur_data"."explorer_commits_and_committers_daily_count";
CREATE MATERIALIZED VIEW "augur_data"."explorer_commits_and_committers_daily_count"
AS
SELECT repo.repo_id,
            repo.repo_name,
            commits.cmt_committer_date,
            COUNT(commits.cmt_id) AS num_of_commits,
            COUNT(DISTINCT commits.cmt_committer_raw_email) AS num_of_unique_committers
            from 
            augur_data.commits 
            left join augur_data.repo on repo.repo_id = commits.repo_id 
            group by 
            repo.repo_id,
            repo.repo_name,
            commits.cmt_committer_date
            order by repo.repo_id, commits.cmt_committer_date
            ;

COMMENT ON MATERIALIZED VIEW "augur_data"."explorer_commits_and_committers_daily_count" IS 'This view indicates the total number of commits by day, and the total number of unique committers by day. ';
GRANT SELECT ON "augur_data"."explorer_commits_and_committers_daily_count" to PUBLIC; 

-- THESE ARE REPEATED BECAUSE THEY WERE INITIALY OMMITTED FROM VERSION 106
GRANT SELECT ON
    "augur_data"."explorer_libyear_all" TO PUBLIC;

GRANT SELECT ON
    "augur_data"."explorer_libyear_detail" TO PUBLIC;

---------

update "augur_operations"."augur_settings" set value = 107
  where setting = 'augur_data_version'; 

COMMIT; 
