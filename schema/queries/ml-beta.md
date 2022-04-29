
```sql
SELECT
	repo.repo_name,
	repo.repo_git,
	repo.repo_id,
	A.cluster_content,
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
GROUP BY
	repo.repo_name,
	repo.repo_git,
	A.cluster_content,
	repo.repo_id;

```