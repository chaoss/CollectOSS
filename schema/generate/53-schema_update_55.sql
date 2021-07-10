BEGIN;


ALTER TABLE "augur_operations"."worker_history" ALTER COLUMN "oauth_id" DROP NOT NULL;

ALTER TABLE "augur_data"."pull_requests" DROP CONSTRAINT if exists "fk_pull_requests_pull_request_meta_2";

ALTER TABLE "augur_data"."pull_requests" DROP CONSTRAINT if exists "fk_pull_requests_pull_request_meta_1";

CREATE INDEX CONCURRENTLY IF NOT EXISTS "cntrb_canonica-idx11" ON "augur_data"."contributors" USING btree (
  "cntrb_canonical" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

update "augur_operations"."augur_settings" set value = 55 where setting = 'augur_data_version';

COMMIT; 

