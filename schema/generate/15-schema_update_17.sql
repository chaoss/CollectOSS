-- #SPDX-License-Identifier: MIT
ALTER TABLE "augur_data"."repo" 
  ALTER COLUMN "forked_from" TYPE varchar USING "forked_from"::varchar;

ALTER TABLE "augur_data"."repo" 
  ADD COLUMN IF NOT EXISTS "repo_archived" int4,
  ADD COLUMN IF NOT EXISTS "repo_archived_date_collected" timestamptz(0),
  ALTER COLUMN "forked_from" TYPE varchar USING "forked_from"::varchar;

update "augur_operations"."augur_settings" set value = 17 where setting = 'augur_data_version'; 
