BEGIN; 

INSERT INTO "augur_operations"."worker_history" ("history_id", "repo_id", "worker", "job_model", "oauth_id", "timestamp", "status", "total_results") VALUES (1, 1, 'seed.worker.record', 'seed', NULL, '2021-07-27 09:50:56', 'Success', 0);

update "augur_operations"."augur_settings" set value = 61 where setting = 'augur_data_version';


COMMIT; 

