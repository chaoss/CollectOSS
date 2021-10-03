BEGIN;

ALTER TABLE "augur_data"."commits" 
  DROP CONSTRAINT "fk_commits_contributors_1",
  DROP CONSTRAINT "fk_commits_contributors_2",
  DROP CONSTRAINT "fk_commits_repo_1",
  ADD CONSTRAINT "fk_commits_contributors_1" FOREIGN KEY ("cmt_ght_author_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "fk_commits_contributors_2" FOREIGN KEY ("cmt_ght_committer_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED,
  ADD CONSTRAINT "fk_commits_repo_1" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

COMMENT ON CONSTRAINT "fk_commits_contributors_1" ON "augur_data"."commits" IS 'This foreign key is initially deferred, and deferrable, in order to support the insertion of commits prior to the insertion of contributors, which Augur performs as a second step. On delete is “restrict” because we don’t want contributor deletes to cause commit deletes. On update it is cascade because we want changes to be cascaded to the commits table from the contributors table. ';

COMMENT ON CONSTRAINT "fk_commits_contributors_2" ON "augur_data"."commits" IS 'This foreign key is initially deferred, and deferrable, in order to support the insertion of commits prior to the insertion of contributors, which Augur performs as a second step. On delete is “restrict” because we don’t want contributor deletes to cause commit deletes. On update it is cascade because we want changes to be cascaded to the commits table from the contributors table. ';

COMMENT ON CONSTRAINT "fk_commits_repo_1" ON "augur_data"."commits" IS 'This foreign key is initially deferred, and deferrable, in order to prevent any changes in repo_ids from affecting commits. On delete is “cascade” because we do want repo deletes to cause commit deletes. On update it is cascade because we want changes to be cascaded to the commits table from the repo table. ';


update "augur_operations"."augur_settings" set value = 75 where setting = 'augur_data_version'; 


COMMIT; 