-- Update Repo Foreign Key
ALTER TABLE "augur_data"."repo" DROP CONSTRAINT "fk_repo_repo_groups_1";

ALTER TABLE "augur_data"."repo" ADD CONSTRAINT "fk_repo_repo_groups_1" FOREIGN KEY ("repo_group_id") REFERENCES "augur_data"."repo_groups" ("repo_group_id") ON DELETE NO ACTION ON UPDATE NO ACTION NOT VALID;

COMMENT ON CONSTRAINT "fk_repo_repo_groups_1" ON "augur_data"."repo" IS 'Repo_groups cardinality set to one and only one because, although in theory there could be more than one repo group for a repo, this might create dependencies in hosted situation that we do not want to live with. ';

ALTER TABLE "augur_data"."message" 
  ALTER COLUMN "data_collection_date" SET DEFAULT CURRENT_TIMESTAMP;

update "augur_operations"."augur_settings" set value = 42 where setting = 'augur_data_version'; 
