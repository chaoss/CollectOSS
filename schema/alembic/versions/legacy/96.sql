BEGIN; 
CREATE OR REPLACE PROCEDURE "augur_data"."refresh_aggregates"()
 AS $BODY$
    begin
        perform pg_advisory_lock(124);
        execute 'REFRESH MATERIALIZED VIEW "augur_data"."issue_reporter_created_at"';
        perform pg_advisory_unlock(124);
    end;
$BODY$
  LANGUAGE plpgsql;

ALTER PROCEDURE "augur_data"."refresh_aggregates"() OWNER TO "augur";

DROP INDEX IF EXISTS "augur_data"."author_affiliation";

CREATE INDEX "author_affiliation" ON "augur_data"."commits" USING btree (
  "cmt_author_affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

DROP INDEX "augur_data"."committer_affiliation";

CREATE INDEX "committer_affiliation" ON "augur_data"."commits" USING btree (
  "cmt_committer_affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

DROP INDEX IF EXISTS "augur_data"."cmt-author-date-idx2";

DROP INDEX IF EXISTS "augur_data"."cmt_author_contrib_worker";

DROP INDEX IF EXISTS "augur_data"."cmt_commiter_contrib_worker";

DROP INDEX IF EXISTS "augur_data"."commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam";

DROP INDEX IF EXISTS "augur_data"."commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam2";

DROP INDEX IF EXISTS "augur_data"."committer_email,committer_affiliation,committer_date";

update "augur_operations"."augur_settings" set value = 96
  where setting = 'augur_data_version'; 
COMMIT; 

