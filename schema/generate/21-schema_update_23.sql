-- #SPDX-License-Identifier: MIT
CREATE INDEX CONCURRENTLY if not exists "contributor_delete_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_id",
  "cntrb_email"
);

CREATE INDEX CONCURRENTLY if not exists "contributor_worker_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_login",
  "cntrb_email", 
  "cntrb_id"
);

CREATE INDEX CONCURRENTLY if not exists "contributor_worker_fullname_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_full_name"
);

CREATE INDEX CONCURRENTLY if not exists "contributor_worker_email_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_email"
);

update "augur_operations"."augur_settings" set value = 23 where setting = 'augur_data_version'; 


-- 

