# Machine Learning Queries

```sql
-- clustering
SELECT
	repo_cluster_messages.repo_id,
	repo.repo_name,
	repo_cluster_messages.cluster_content,
	MAX ( repo_cluster_messages.data_collection_date ) 
FROM
	repo_cluster_messages,
	repo 
WHERE
	repo_cluster_messages.repo_id = repo.repo_id 
GROUP BY
	repo_cluster_messages.repo_id,
	repo.repo_name,
	repo_cluster_messages.cluster_content
	
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