CREATE INDEX CONCURRENTLY "contributor_delete_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_id",
  "cntrb_email"
);

CREATE INDEX CONCURRENTLY "contributor_worker_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_login",
  "cntrb_email", 
  "cntrb_id"
);

CREATE INDEX CONCURRENTLY "contributor_worker_fullname_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_full_name"
);

CREATE INDEX CONCURRENTLY "contributor_worker_email_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_email"
);

-- 
