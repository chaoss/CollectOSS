--draft

BEGIN; 
ALTER TABLE "augur_data"."issue_events" 
  DROP CONSTRAINT "fk_issue_events_issues_1",
  ADD CONSTRAINT "fk_issue_events_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "augur_data"."issue_message_ref" 
  DROP CONSTRAINT "fk_issue_message_ref_issues_1",
  ADD CONSTRAINT "fk_issue_message_ref_issues_1" FOREIGN KEY ("issue_id") REFERENCES "augur_data"."issues" ("issue_id") ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

  delete from issues CASCADE where issue_id in (
  select distinct max(issue_id) as issue_id from issues, (
  select repo_id,  gh_issue_id, count(*) as counter from issues
   group by repo_id,  gh_issue_id order by counter desc
   ) a where a.counter >1 and a.gh_issue_id = issues.gh_issue_id group by a.gh_issue_id );
 
ALTER TABLE "augur_data"."issues" 
  ADD CONSTRAINT "unique-issue" UNIQUE ("repo_id", "gh_issue_id");


---

ALTER TABLE "augur_data"."pull_request_message_ref" 
  DROP CONSTRAINT "fk_pull_request_message_ref_pull_requests_1",
  ADD CONSTRAINT "fk_pull_request_message_ref_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE CASCADE DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "augur_data"."pull_request_assignees" 
  DROP CONSTRAINT "fk_pull_request_assignees_pull_requests_1",
  ADD CONSTRAINT "fk_pull_request_assignees_pull_requests_1" FOREIGN KEY ("pull_request_id") REFERENCES "augur_data"."pull_requests" ("pull_request_id") ON DELETE CASCADE ON UPDATE NO ACTION;

  delete from pull_requests CASCADE where pull_request_id in (
  select distinct max(pull_request_id) as pull_request_id from pull_requests, (
  select repo_id,  pr_src_id, count(*) as counter from pull_requests
   group by repo_id,  pr_src_id order by counter desc
   ) a where a.counter >1 and a.pr_src_id = pull_requests.pr_src_id group by a.pr_src_id );
  
ALTER TABLE "augur_data"."pull_requests" 
  ADD CONSTRAINT "unique-pr" UNIQUE ("repo_id", "pr_src_id");

update "augur_operations"."augur_settings" set value = 96
  where setting = 'augur_data_version'; 
COMMIT; 

