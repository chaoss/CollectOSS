-- commits

CREATE INDEX CONCURRENTLY IF NOT EXISTS "author_email,author_affiliation,author_date" ON "augur_data"."commits" USING btree (
  "cmt_author_email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops",
  "cmt_author_affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops",
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops"
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS "committer_cntrb_id" ON "augur_data"."commits" USING btree (
  "cmt_ght_committer_id"
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS "author_cntrb_id" ON "augur_data"."commits" USING btree (
  "cmt_ght_author_id"
);


-- pull_request_repo
CREATE INDEX CONCURRENTLY IF NOT EXISTS "pr-cntrb-idx-repo" ON "augur_data"."pull_request_repo" USING btree (
  "pr_cntrb_id"
);

-- messages

CREATE INDEX CONCURRENTLY IF NOT EXISTS "msg-cntrb-id-idx" ON "augur_data"."message" USING btree (
  "cntrb_id"
);

-- pull request meta
CREATE INDEX CONCURRENTLY IF NOT EXISTS "pr_meta-cntrbid-idx" ON "augur_data"."pull_request_meta" USING btree (
  "cntrb_id"
);


-- pull request assignees
CREATE INDEX CONCURRENTLY IF NOT EXISTS "pr_meta_cntrb-idx" ON "augur_data"."pull_request_assignees" USING btree (
  "contrib_id"
);


-- pull request reviewers
CREATE INDEX CONCURRENTLY IF NOT EXISTS "pr-reviewers-cntrb-idx1" ON "augur_data"."pull_request_reviewers" USING btree (
  "cntrb_id"
);


-- issue assignees
CREATE INDEX CONCURRENTLY IF NOT EXISTS  "issue-cntrb-assign-idx-1" ON "augur_data"."issue_assignees" USING btree (
  "cntrb_id"
);


-- issues
CREATE INDEX CONCURRENTLY IF NOT EXISTS "issue-cntrb-dix2" ON "augur_data"."issues" USING btree (
  "cntrb_id"
);



-- issue events
CREATE INDEX CONCURRENTLY IF NOT EXISTS "issue-cntrb-idx2" ON "augur_data"."issue_events" USING btree (
  "issue_event_src_id"
);


-- contributor aliases
CREATE INDEX CONCURRENTLY IF NOT EXISTS "issue-alias-cntrb-idx1" ON "augur_data"."contributors_aliases" USING btree (
  "cntrb_id"
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS "issue-alias-cntrb-idx2" ON "augur_data"."contributors_aliases" USING btree (
  "cntrb_a_id"
);


-- contributor history
CREATE INDEX CONCURRENTLY IF NOT EXISTS "contrb-history-dix1" ON "augur_data"."contributors_history" USING btree (
  "cntrb_id"
);

  
CREATE INDEX CONCURRENTLY
IF
  NOT EXISTS commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam ON "augur_data"."commits" ( repo_id, cmt_author_email, cmt_author_date, cmt_author_name );

CREATE INDEX CONCURRENTLY
IF
  NOT EXISTS commits_idx_cmt_email_cmt_date_cmt_name ON "augur_data"."commits" ( cmt_author_email, cmt_author_date, cmt_author_name );

CREATE INDEX CONCURRENTLY
IF
  NOT EXISTS commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam2 ON "augur_data"."commits" ( repo_id, cmt_committer_email, cmt_committer_date, cmt_committer_name );

CREATE INDEX CONCURRENTLY
IF
  NOT EXISTS commits_idx_cmt_email_cmt_date_cmt_name2 ON "augur_data"."commits" ( cmt_committer_email, cmt_committer_date, cmt_committer_name );

CREATE INDEX CONCURRENTLY
IF
  NOT EXISTS commits_idx_repo_id_cmt_ema_cmt_nam_cmt_dat2 ON "augur_data"."commits" ( repo_id, cmt_author_email, cmt_author_name, cmt_author_date );

CREATE INDEX CONCURRENTLY
IF
  NOT EXISTS commits_idx_cmt_name_cmt_date2 ON "augur_data"."commits" ( cmt_author_name, cmt_author_date );

CREATE INDEX CONCURRENTLY
IF
  NOT EXISTS commits_idx_repo_id_cmt_ema_cmt_nam_cmt_dat3 ON "augur_data"."commits" ( repo_id, cmt_committer_email, cmt_committer_name, cmt_author_date );

CREATE INDEX CONCURRENTLY
IF
  NOT EXISTS commits_idx_cmt_name_cmt_date_cmt_date3 ON "augur_data"."commits" ( cmt_committer_name, cmt_author_date, cmt_committer_date );

CREATE INDEX CONCURRENTLY
IF
  NOT EXISTS contributors_idx_cntrb_email3 ON "augur_data"."contributors" ( cntrb_email );


-- Field Name Consistency

ALTER TABLE "augur_data"."contributors" 
  ALTER COLUMN "cntrb_email" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."commits" 
  ALTER COLUMN "cmt_author_email" TYPE varchar COLLATE "pg_catalog"."default",
  ALTER COLUMN "cmt_committer_email" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."contributors" 
  ALTER COLUMN "cntrb_canonical" TYPE varchar COLLATE "pg_catalog"."default";

ALTER TABLE "augur_data"."contributors_aliases" 
  ALTER COLUMN "canonical_email" TYPE varchar COLLATE "pg_catalog"."default";

--- Hash index change

DROP INDEX "augur_data"."author_affiliation";

CREATE INDEX CONCURRENTLY IF NOT EXISTS  "author_affiliation" ON "augur_data"."commits" USING hash (
  "cmt_author_affiliation" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops"
); 

CREATE INDEX CONCURRENTLY IF NOT EXISTS "cmt-author-date-idx2" ON "augur_data"."commits" USING btree (
  "cmt_author_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS "cmt-committer-date-idx3" ON "augur_data"."commits" USING btree (
  "cmt_committer_date" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS "cmt_author-name-idx5" ON "augur_data"."commits" USING btree (
  "cmt_committer_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS "cmt_cmmter-name-idx4" ON "augur_data"."commits" USING btree (
  "cmt_author_name" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

update "augur_operations"."augur_settings" set value = 29 where setting = 'augur_data_version'; 
