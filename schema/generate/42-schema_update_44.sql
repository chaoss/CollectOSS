ALTER TABLE "augur_data"."pull_request_analysis" ALTER COLUMN "merge_probability" TYPE numeric(256,250) USING "merge_probability"::numeric(256,250);

ALTER TABLE "augur_data"."pull_requests" ALTER COLUMN "repo_id" SET DEFAULT 0;

COMMENT ON CONSTRAINT "fk_repo_repo_groups_1" ON "augur_data"."repo" IS 'Repo_groups cardinality set to one and only one because, although in theory there could be more than one repo group for a repo, this might create dependencies in hosted situation that we do not want to live with. ';

CREATE INDEX IF NOT EXISTS "probability_idx" ON "augur_data"."pull_request_analysis" USING btree (
  "merge_probability" "pg_catalog"."numeric_ops" DESC NULLS LAST
);


update "augur_operations"."augur_settings" set value = 44 where setting = 'augur_data_version'; 
