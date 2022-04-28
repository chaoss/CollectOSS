#ML BETA

```sql
-- clustering
SELECT
	repo_cluster_messages.repo_id,
	repo.repo_name,
	repo_cluster_messages.cluster_content,
  a.data_collection_date
FROM
(
select max(msg_cluster_id), repo_id, max(data_collection_date) as data_collection_date from 
repo_cluster_messages
group by repo_id) a, 
 

SELECT
	repo_cluster_messages.repo_id,
	repo.repo_name,
	repo_cluster_messages.cluster_content,
	MAX ( repo_cluster_messages.data_collection_date ) 
FROM
	repo_cluster_messages,
    message,
	repo 
WHERE
	repo_cluster_messages.repo_id = repo.repo_id 
	and message.repo_id = repo_cluster_messages.repo_id 
GROUP BY
	repo_cluster_messages.repo_id,
	repo.repo_name,
	repo_cluster_messages.cluster_content


```