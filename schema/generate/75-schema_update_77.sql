BEGIN; 

ALTER TABLE "augur_data"."commit_comment_ref" 
  DROP CONSTRAINT "fk_commit_comment_ref_commits_1",
  DROP CONSTRAINT "fk_commit_comment_ref_message_1",
  DROP CONSTRAINT "commitcomment",
  ADD COLUMN "repo_id" int8,
  ADD CONSTRAINT "fk_commit_comment_ref_commits_1" FOREIGN KEY ("cmt_id") REFERENCES "augur_data"."commits" ("cmt_id") ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT "fk_commit_comment_ref_message_1" FOREIGN KEY ("msg_id") REFERENCES "augur_data"."message" ("msg_id") ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT "commitcomment" UNIQUE ("cmt_comment_src_id");
  

COMMENT ON TABLE "augur_data"."contributor_affiliations" IS 'This table exists outside of relations with other tables. The purpose is to provide a dynamic, owner maintained (and augur augmented) list of affiliations. This table is processed in affiliation information in the DM_ tables generated when Augur is finished counting commits using the Facade Worker. ';

COMMENT ON TABLE "augur_data"."discourse_insights" IS 'This table is populated by the “Discourse_Analysis_Worker”. It examines sequential discourse, using computational linguistic methods, to draw statistical inferences regarding the discourse in a particular comment thread. ';

DROP TABLE
IF
  EXISTS contributors_history;

COMMENT ON TABLE "augur_data"."contributors_aliases" IS 'Every open source user may have more than one email used to make contributions over time. Augur selects the first email it encounters for a user as its “canonical_email”. 

The canonical_email is also added to the contributors_aliases table, with the canonical_email and alias_email being identical.  Using this strategy, an email search will only need to join the alias table for basic email information, and can then more easily map the canonical email from each alias row to the same, more detailed information in the contributors table for a user. ';

-- issue events repo id and foreign key updates

ALTER TABLE "augur_data"."issue_events" 
  DROP CONSTRAINT "fk_issue_events_contributors_1",
  DROP CONSTRAINT "fk_issue_events_issues_1",
  ADD COLUMN "repo_id" int8,
  ADD CONSTRAINT "fk_issue_events_contributors_1" FOREIGN KEY ("cntrb_id") REFERENCES "augur_data"."contributors" ("cntrb_id") ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT "fk_issue_events_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE RESTRICT ON UPDATE CASCADE,
  ADD CONSTRAINT "fk_issue_events_repo" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- issue labels repo id and foreign key

ALTER TABLE "augur_data"."issue_labels" 
  ADD COLUMN "repo_id" int8,
  ADD CONSTRAINT "fk_issue_labels_repo_id" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- issue assignee repo id and foreign key

ALTER TABLE "augur_data"."issue_assignees" 
  ADD COLUMN "repo_id" int8,
  ADD CONSTRAINT "fk_issue_assignee_repo_id" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE;


-- pr assignee repo id and foreign key

ALTER TABLE "augur_data"."pull_request_assignees" 
  ADD COLUMN "repo_id" int8,
  ADD CONSTRAINT "fk_pull_request_assignees_repo_id" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;


-- pr commits repo id and foreign key

ALTER TABLE "augur_data"."pull_request_commits" 
  ADD COLUMN "repo_id" int8,
  ADD CONSTRAINT "fk_pull_request_commits_repo_id" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- pr files repo id and foreign key

ALTER TABLE "augur_data"."pull_request_files" 
  ADD COLUMN "repo_id" int8,
  ADD CONSTRAINT "fk_pull_request_files_repo_id" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

-- pr labels repo id and foreign key

ALTER TABLE "augur_data"."pull_request_labels" 
  ADD COLUMN "repo_id" int8,
  ADD CONSTRAINT "fk_pull_request_labels_repo" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- pr meta repo id and foreign key

ALTER TABLE "augur_data"."pull_request_meta" 
  ADD COLUMN "repo_id" int8,
  ADD CONSTRAINT "fk_pull_request_repo_meta_repo_id" FOREIGN KEY ("repo_id") REFERENCES "augur_data"."repo" ("repo_id") ON DELETE RESTRICT ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

     


update "augur_operations"."augur_settings" set value = 77 where setting = 'augur_data_version'; 


COMMIT; 