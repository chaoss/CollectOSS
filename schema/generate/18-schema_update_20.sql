-- #SPDX-License-Identifier: MIT
DROP INDEX if exists "augur_data"."cntrb_id";

CREATE INDEX "cnt-fullname" ON "augur_data"."contributors" USING hash (
  "cntrb_full_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops"
);

CREATE INDEX "cntrb-theemail" ON "augur_data"."contributors" USING hash (
  "cntrb_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops"
);

CREATE INDEX "cmt_author_contrib_worker" ON "augur_data"."commits" USING brin (
  "cmt_author_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops",
  "cmt_author_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops",
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops"
);

CREATE INDEX "cmt_commiter_contrib_worker" ON "augur_data"."commits" USING brin (
  "cmt_committer_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops",
  "cmt_committer_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops",
  "cmt_committer_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_minmax_ops"
);

CREATE INDEX "cntrb_login_platform_index" ON "augur_data"."contributors" USING btree (
  "cntrb_login" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

ALTER TABLE "augur_data"."repo_info" ALTER COLUMN "data_collection_date" SET DEFAULT CURRENT_TIMESTAMP;

update "augur_operations"."augur_settings" set value = 20 where setting = 'augur_data_version'; 


-- BRIN Index Summary Calls
-- SELECT brin_summarize_new_values('cmt_commiter_contrib_worker'::regclass);
-- SELECT brin_summarize_new_values('cmt_author_contrib_worker'::regclass);
