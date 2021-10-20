BEGIN; 

ALTER TABLE "augur_data"."commits" 
  ALTER CONSTRAINT "fk_commits_contributors_3" DEFERRABLE INITIALLY DEFERRED,
  ALTER CONSTRAINT "fk_commits_contributors_4" DEFERRABLE INITIALLY DEFERRED;

update "augur_operations"."augur_settings" set value = 82 where setting = 'augur_data_version'; 


COMMIT; 