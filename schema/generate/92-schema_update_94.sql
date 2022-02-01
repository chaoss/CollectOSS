BEGIN; 

CREATE MATERIALIZED VIEW "augur_data"."issue_reporter_created_at"
AS
SELECT
  i.reporter_id,
  i.created_at,
  i.repo_id 
FROM
  augur_data.issues i 
ORDER BY
  i.created_at;

ALTER MATERIALIZED VIEW "augur_data"."issue_reporter_created_at" OWNER TO "augur";

CREATE INDEX ON "augur_data"."issue_reporter_created_at" (repo_id);

create or replace procedure refresh_aggregates()
language plpgsql
as $$
    begin
        perform pg_advisory_lock(124);
        execute 'REFRESH MATERIALIZED VIEW "augur_data"."issue_reporter_created_at"';
        perform pg_advisory_unlock(124);
    end;
$$;

call refresh_aggregates();

update "augur_operations"."augur_settings" set value = 94 
  where setting = 'augur_data_version'; 


COMMIT; 

