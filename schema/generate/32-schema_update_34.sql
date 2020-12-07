--  # Pull request commit updates

ALTER TABLE "augur_data"."pull_requests" DROP CONSTRAINT "fk_pull_requests_repo_1";

ALTER TABLE "augur_data"."pull_requests" ALTER COLUMN "repo_id" SET DEFAULT 0;

update "augur_operations"."augur_settings" set value = 34 where setting = 'augur_data_version'; 
