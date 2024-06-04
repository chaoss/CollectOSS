
-- View indexes:
CREATE UNIQUE INDEX explorer_contributor_recent_actions_unique_idx ON augur_data.explorer_contributor_recent_actions USING btree (cntrb_id, created_at, repo_id, action, repo_name, login, rank);
CREATE INDEX explorer_contributor_recent_actions_cntrb_id_idx ON augur_data.explorer_contributor_recent_actions USING btree (cntrb_id);
CREATE INDEX explorer_contributor_recent_actions_repo_id_idx ON augur_data.explorer_contributor_recent_actions USING btree (repo_id DESC);
