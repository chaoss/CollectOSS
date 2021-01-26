CREATE INDEX pull_requests_idx_repo_id_data_datex ON pull_requests (repo_id,data_collection_date);
CREATE INDEX repo_idx_repo_id_repo_namex ON repo (repo_id,repo_name);
CREATE INDEX repo_info_idx_repo_id_data_datex ON repo_info (repo_id,data_collection_date);
CREATE INDEX repo_info_idx_repo_id_data_date_1x ON repo_info (repo_id,data_collection_date);

update "augur_operations"."augur_settings" set value = 41 where setting = 'augur_data_version'; 
