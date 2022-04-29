# Machine Learning Queries

```sql
-- clustering

SELECT
    repo.repo_name,
    repo.repo_git,
    repo.repo_id,
    A.cluster_content,
    MAX ( msg_cluster_id ) AS msg_cluster_id, 
    d.message_count 
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
    left outer join (select repo_id, count(*) as message_count from message 
where repo_id is not null group by repo_id) d on repo.repo_id = d.repo_id 
GROUP BY
    repo.repo_name,
    repo.repo_git,
    A.cluster_content,
    repo.repo_id,
    d.message_count;
	
-- discourse_insights
SELECT
    discourse_act,
    COUNT ( * ) AS discourse_type_count,
    repo.repo_id,
    repo_name 
FROM
    discourse_insights,
    repo,
    issue_message_ref 
WHERE
    repo.repo_id = issue_message_ref.repo_id 
    AND discourse_insights.msg_id = issue_message_ref.msg_id 
GROUP BY
    discourse_act,
    repo.repo_id 
ORDER BY
    repo_name;
		
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