# Gets the count of types of contributions by user, only returning users who have interacted with a project in some way

SET @owner = "rails";
SET @repo  = "rails";

USE 'msr14'; # Test database
# USE 'ghtorrent'; # Production database

SET @proj = (SELECT projects.id FROM projects INNER JOIN users ON projects.owner_id = users.id WHERE projects.name = @repo AND users.login = @owner);

SELECT * FROM

	(
   SELECT users.id        as "user_id", 
	        users.login     as "login",
	        com.count       as "commits",
	        pulls.count     as "pull_requests",
	        iss.count       as "issues",
	        comcoms.count   as "commit_comments",
	        pullscoms.count as "pull_request_comments",
	        isscoms.count   as "issue_comments"
	        
   FROM users

   LEFT JOIN (SELECT committer_id AS id, COUNT(*) AS count FROM commits WHERE commits.project_id = @proj GROUP BY commits.committer_id) AS com
   ON com.id = users.id

   LEFT JOIN (SELECT pull_request_history.actor_id AS id, COUNT(*) AS count FROM pull_request_history JOIN pull_requests ON pull_requests.id = pull_request_history.pull_request_id WHERE pull_requests.base_repo_id = @proj AND pull_request_history.action = 'merged' GROUP BY pull_request_history.actor_id) AS pulls
   ON pulls.id = users.id

   LEFT JOIN (SELECT reporter_id AS id, COUNT(*) AS count FROM issues WHERE issues.repo_id = @proj GROUP BY issues.reporter_id) AS iss
   ON iss.id = users.id

   LEFT JOIN (SELECT commit_comments.user_id AS id, COUNT(*) AS count FROM commit_comments JOIN commits ON commit_comments.commit_id = commits.id WHERE commits.project_id = @proj GROUP BY commit_comments.user_id) AS comcoms
   ON comcoms.id = users.id

   LEFT JOIN (SELECT pull_request_comments.user_id AS id, COUNT(*) AS count FROM pull_request_comments JOIN pull_requests ON pull_request_comments.pull_request_id = pull_requests.id WHERE pull_requests.base_repo_id = @proj GROUP BY pull_request_comments.user_id) AS pullscoms
   ON pullscoms.id = users.id

   LEFT JOIN (SELECT issue_comments.user_id AS id, COUNT(*) AS count FROM issue_comments JOIN issues ON issue_comments.issue_id = issues.id WHERE issues.repo_id = @proj GROUP BY issue_comments.user_id) AS isscoms
   ON isscoms.id = users.id

   GROUP BY users.id
   ORDER BY com.count
   ) user_activity

WHERE commits IS NOT NULL
OR    pull_requests IS NOT NULL
OR    issues IS NOT NULL
OR    commit_comments IS NOT NULL
OR    pull_request_comments IS NOT NULL
OR    issue_comments IS NOT NULL;
