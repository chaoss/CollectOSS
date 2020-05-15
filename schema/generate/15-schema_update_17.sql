ALTER TABLE "augur_data"."repo" 
  ALTER COLUMN "forked_from" TYPE varchar USING "forked_from"::varchar;

ALTER TABLE "augur_data"."repo" 
  ADD COLUMN "repo_archived" int4,
  ADD COLUMN "repo_archived_date_collected" timestamptz(0),
  ALTER COLUMN "forked_from" TYPE varchar USING "forked_from"::varchar;

