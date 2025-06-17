-- D0 Contributor Engagement table for GitLab
-- This table stores contributor engagement metrics for GitLab projects
-- Note: The same table is used for both GitHub and GitLab data, differentiated by the 'platform' field

-- The table should already exist from the GitHub implementation, but if not:
-- CREATE TABLE IF NOT EXISTS augur_data.d0_contributor_engagement (
--     id SERIAL PRIMARY KEY, 
--     updated_at TIMESTAMP, 
--     username_github TEXT, 
--     username_gitlab TEXT, 
--     full_name TEXT, 
--     country TEXT, 
--     social_links JSONB, 
--     company TEXT, 
--     contributions_last_year INT, 
--     has_starred BOOLEAN, 
--     has_forked BOOLEAN, 
--     is_watching BOOLEAN,  -- For GitLab, this represents project membership
--     collected_at TIMESTAMP, 
--     platform TEXT,  -- 'github' or 'gitlab'
--     repo_id BIGINT REFERENCES augur_data.repo(repo_id), 
--     UNIQUE(username_gitlab, repo_id)
-- );

-- Index for GitLab queries
CREATE INDEX IF NOT EXISTS idx_d0_contributor_engagement_gitlab_username ON augur_data.d0_contributor_engagement(username_gitlab);
CREATE INDEX IF NOT EXISTS idx_d0_contributor_engagement_platform ON augur_data.d0_contributor_engagement(platform);
CREATE INDEX IF NOT EXISTS idx_d0_contributor_engagement_gitlab_repo ON augur_data.d0_contributor_engagement(username_gitlab, repo_id) WHERE platform = 'gitlab'; 