

--draft

BEGIN; 
-- code added following PR review
/*
The foreign key from the pull_request_reviews table to the pull_requests table still has on delete restrict on it, which I believe needs to be on delete cascade

The foreign key from the issue_labels table to the issues table still has on delete restrict on it, which I believe needs to be on delete cascade
*/


ALTER TABLE "augur_data"."issue_labels" 
  DROP CONSTRAINT IF EXISTS "fk_issue_labels_issues_1",
  ADD CONSTRAINT "fk_issue_labels_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE CASCADE ON UPDATE CASCADE;

---

ALTER TABLE "augur_data"."issue_events" 
  DROP CONSTRAINT "fk_issue_events_issues_1",
  ADD CONSTRAINT "fk_issue_events_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."issue_message_ref" 
  DROP CONSTRAINT "fk_issue_message_ref_issues_1",
  ADD CONSTRAINT "fk_issue_message_ref_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

  delete from "augur_data"."issues" CASCADE where issue_id in (
  select distinct max(issue_id) as issue_id from "augur_data"."issues", (
  select repo_id,  gh_issue_id, count(*) as counter from "augur_data"."issues"
   group by repo_id,  gh_issue_id order by counter desc
   ) a where a.counter >1 and a.gh_issue_id = issues.gh_issue_id group by a.gh_issue_id );
 
ALTER TABLE "augur_data"."issues" 
  DROP CONSTRAINT IF EXISTS "unique-issue",
  ADD CONSTRAINT "unique-issue" UNIQUE ("repo_id", "gh_issue_id");

ALTER TABLE "augur_data"."pull_request_reviews" 
  DROP CONSTRAINT "fk_pull_request_reviews_pull_requests_1",
  ADD CONSTRAINT "fk_pull_request_reviews_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;
---

ALTER TABLE "augur_data"."pull_request_message_ref" 
  DROP CONSTRAINT "fk_pull_request_message_ref_pull_requests_1",
  ADD CONSTRAINT "fk_pull_request_message_ref_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "augur_data"."pull_request_assignees" 
  DROP CONSTRAINT "fk_pull_request_assignees_pull_requests_1",
  ADD CONSTRAINT "fk_pull_request_assignees_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE;

  delete from "augur_data"."pull_requests" CASCADE where pull_request_id in (
  select distinct max(pull_request_id) as pull_request_id from "augur_data"."pull_requests", (
  select repo_id,  pr_src_id, count(*) as counter from "augur_data"."pull_requests"
   group by repo_id,  pr_src_id order by counter desc
   ) a where a.counter >1 and a.pr_src_id = pull_requests.pr_src_id group by a.pr_src_id );
  
ALTER TABLE "augur_data"."pull_requests" 
  DROP CONSTRAINT IF EXISTS "unique-prx",
  ADD CONSTRAINT "unique-prx" UNIQUE ("repo_id", "pr_src_id");

  delete from "augur_data"."repo_labor" CASCADE where repo_labor_id in (
  select distinct max(repo_labor.repo_labor_id) as repo_labor_id from "augur_data"."repo_labor", (
  select repo_id, repo_labor_id, rl_analysis_date, file_path, file_name, count(*) as counter from "augur_data"."repo_labor"
   group by repo_id, repo_labor_id, rl_analysis_date, file_path, file_name order by counter desc
   ) a where a.counter >1 and a.repo_labor_id = "augur_data"."repo_labor".repo_labor_id group by a.repo_labor_id);
   
ALTER TABLE "augur_data"."repo_labor" 
  DROP CONSTRAINT IF EXISTS "rl-unique",
  ADD CONSTRAINT "rl-unique" UNIQUE ("repo_id", "rl_analysis_date", "file_path", "file_name") DEFERRABLE INITIALLY DEFERRED;



--
update "augur_operations"."augur_settings" set value = 97
  where setting = 'augur_data_version'; 
COMMIT; 
