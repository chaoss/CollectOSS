BEGIN; 

ALTER TABLE "augur_data"."contributors" 
  DROP CONSTRAINT "GH-UNIQUE-B";

ALTER TABLE "augur_data"."commits" 
  DROP CONSTRAINT "fk_commits_contributors_1",
  DROP CONSTRAINT "fk_commits_contributors_2",
  DROP CONSTRAINT "fk_commits_repo_1",
  ADD COLUMN "cmt_author_platform_username" varchar,
  ADD CONSTRAINT "fk_commits_contributors_3" FOREIGN KEY ("cmt_author_platform_username") REFERENCES "augur_data"."contributors" ("cntrb_login") ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT "fk_commits_contributors_4" FOREIGN KEY ("cmt_author_platform_username") REFERENCES "augur_data"."contributors" ("cntrb_login") ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT "fk_commits_repo_2" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE;

  
update "augur_operations"."augur_settings" set value = 76 where setting = 'augur_data_version'; 


COMMIT; 