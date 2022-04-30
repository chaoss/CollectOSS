# Machine Learning Queries

```sql
-- clustering
/**
This query shows the most recent cluster id for repos in a cluster. The field is `cluster_content`.
Also shown are the total number of messages per repo.
Also shown are the total number of issue events per repo
Also shown are the total number of pull request events per repo. 

The field `msg_cluster_id` is not meaningful. Its necessary to ensure only the most recent cluster
for each repository is shown. 

The use of out joins will ensure that all repositories have a record. There are a significant 
number of cases in open source software where there are too few messages against a repository 
for them to be part of a cluster in a collection of repositories. 

**/

SELECT
    repo.repo_name,
    repo.repo_git,
    repo.repo_id,
    A.cluster_content,
    d.message_count,
    e.issue_event_count,
    f.pull_request_event_count,
    MAX ( msg_cluster_id ) AS msg_cluster_id 
FROM
    repo
    LEFT OUTER JOIN (
    SELECT
        repo.repo_id,
        repo_cluster_messages.cluster_content,
        repo_cluster_messages.msg_cluster_id,
        repo.repo_name 
    FROM
        ( SELECT MAX ( msg_cluster_id ) AS msg_cluster_id, repo_id, MAX ( data_collection_date ) AS data_collection_date FROM repo_cluster_messages GROUP BY repo_id )
        C LEFT OUTER JOIN repo ON repo.repo_id = C.repo_id
        LEFT OUTER JOIN repo_cluster_messages ON C.msg_cluster_id = repo_cluster_messages.msg_cluster_id 
    ) A ON repo.repo_id = A.repo_id 
    AND A.msg_cluster_id = msg_cluster_id
    LEFT OUTER JOIN ( SELECT repo_id, COUNT ( * ) AS message_count FROM message WHERE repo_id IS NOT NULL GROUP BY repo_id ) d ON repo.repo_id = d.repo_id
    LEFT OUTER JOIN ( SELECT repo_id, COUNT ( * ) AS issue_event_count FROM issue_events GROUP BY repo_id ) e ON repo.repo_id = e.repo_id
    LEFT OUTER JOIN ( SELECT repo_id, COUNT ( * ) AS pull_request_event_count FROM pull_request_events GROUP BY repo_id ) f ON repo.repo_id = f.repo_id 
GROUP BY
    repo.repo_name,
    repo.repo_git,
    A.cluster_content,
    repo.repo_id,
    d.message_count,
    e.issue_event_count,
    f.pull_request_event_count;
```

```sql
		
-- message_analysis
SELECT
    --message_analysis.msg_id,
    AVG ( sentiment_score ) as average_sentiment,
    count(*),
    repo.repo_id,
    repo_name 
FROM
    message_analysis,
    repo,
    issue_message_ref 
WHERE
    repo.repo_id = issue_message_ref.repo_id 
    AND message_analysis.msg_id = issue_message_ref.msg_id 
GROUP BY
    --message_analysis.msg_id,
    repo.repo_id,
    repo_name
order by average_sentiment; 
```