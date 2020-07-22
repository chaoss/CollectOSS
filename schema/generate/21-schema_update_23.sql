CREATE INDEX CONCURRENTLY "contributor_delete_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_id",
  "cntrb_email"
);

CREATE INDEX CONCURRENTLY "contributor_worker_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_login",
  "cntrb_email", 
  "cntrb_id"
);

CREATE INDEX CONCURRENTLY "contributor_worker_fullname_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_full_name"
);

CREATE INDEX CONCURRENTLY "contributor_worker_email_finder" ON "augur_data"."contributors" USING brin (
  "cntrb_email"
);

-- 


CREATE INDEX CONCURRENTLY "contributor_worker_issue_events_finder" ON "augur_data"."issue_events" USING brin (
  "cntrb_id"
);


CREATE INDEX CONCURRENTLY "contributor_worker_pull_request_events_finder" ON "augur_data"."pull_request_events" USING brin (
  "cntrb_id"
);




    issue_events_result = self.db.execute(self.issue_events_table.update().where(
            self.issue_events_table.c.cntrb_id.in_(dupe_ids)).values(update_col))
        self.logger.info("Updated cntrb_id column for tuples in the issue_events table with value: {} replaced with new cntrb id: {}".format(new_id, self.cntrb_id_inc))

        pr_events_result = self.db.execute(self.pull_request_events_table.update().where(
            self.pull_request_events_table.c.cntrb_id.in_(dupe_ids)).values(update_col))
        self.logger.info("Updated cntrb_id column for tuples in the pull_request_events table with value: {} replaced with new cntrb id: {}".format(new_id, self.cntrb_id_inc))

        issues_cntrb_result = self.db.execute(self.issues_table.update().where(
            self.issues_table.c.cntrb_id.in_(dupe_ids)).values(update_col))
        self.logger.info("Updated cntrb_id column for tuples in the issues table with value: {} replaced with new cntrb id: {}".format(new_id, self.cntrb_id_inc))

        issues_reporter_result = self.db.execute(self.issues_table.update().where(
            self.issues_table.c.reporter_id.in_(dupe_ids)).values(reporter_col))
        self.logger.info("Updated reporter_id column in the issues table with value: {} replaced with new cntrb id: {}".format(new_id, self.cntrb_id_inc))

        issue_assignee_result = self.db.execute(self.issue_assignees_table.update().where(
            self.issue_assignees_table.c.cntrb_id.in_(dupe_ids)).values(update_col))
        self.logger.info("Updated cntrb_id column for tuple in the issue_assignees table with value: {} replaced with new cntrb id: {}".format(new_id, self.cntrb_id_inc))

        pr_assignee_result = self.db.execute(self.pull_request_assignees_table.update().where(
            self.pull_request_assignees_table.c.contrib_id.in_(dupe_ids)).values(pr_assignee_col))
        self.logger.info("Updated contrib_id column for tuple in the pull_request_assignees table with value: {} replaced with new cntrb id: {}".format(new_id, self.cntrb_id_inc))

        message_result = self.db.execute(self.message_table.update().where(
            self.message_table.c.cntrb_id.in_(dupe_ids)).values(update_col))
        self.logger.info("Updated cntrb_id column for tuple in the message table with value: {} replaced with new cntrb id: {}".format(new_id, self.cntrb_id_inc))

        pr_reviewers_result = self.db.execute(self.pull_request_reviewers_table.update().where(
            self.pull_request_reviewers_table.c.cntrb_id.in_(dupe_ids)).values(update_col))
        self.logger.info("Updated cntrb_id column for tuple in the pull_request_reviewers table with value: {} replaced with new cntrb id: {}".format(new_id, self.cntrb_id_inc))

        pr_meta_result = self.db.execute(self.pull_request_meta_table.update().where(
            self.pull_request_meta_table.c.cntrb_id.in_(dupe_ids)).values(update_col))
        self.logger.info("Updated cntrb_id column for tuple in the pull_request_meta table with value: {} replaced with new cntrb id: {}".format(new_id, self.cntrb_id_inc))

        pr_repo_result = self.db.execute(self.pull_request_repo_table.update().where(
            self.pull_request_repo_table.c.pr_cntrb_id.in_(dupe_ids)).values(pr_repo_col))
        self.logger.info("Updated cntrb_id column for tuple in the pull_request_repo table with value: {} replaced with new cntrb id: {}".format(new_id, self.cntrb_id_inc))
