BEGIN;

ALTER TABLE "augur_data"."contributors" 
  DROP CONSTRAINT "GH-UNIQUE-B",
  ADD CONSTRAINT "GH-UNIQUE-B" UNIQUE ("gh_user_id", "gh_login") DEFERRABLE INITIALLY DEFERRED;

COMMENT ON TABLE "augur_data"."contributors" IS 'For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login. 
Github now allows a user to change their login name, but their user id remains the same in this case. So, the natural key is the combination of id and login, but there should never be repeated logins. ';


update "augur_operations"."augur_settings" set value = 74 where setting = 'augur_data_version'; 


COMMIT; 