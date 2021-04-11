
BEGIN;

alter table pull_requests drop constraint if exists fk_pr_contribs; 
 ALTER TABLE "augur_data"."pull_requests" ADD CONSTRAINT  "fk_pr_contribs" FOREIGN KEY ("pr_augur_contributor_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE RESTRICT ON UPDATE CASCADE NOT VALID;

update "augur_operations"."augur_settings" set value = 49 where setting = 'augur_data_version';


COMMIT; 

