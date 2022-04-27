# Data collection completeness queries. 

```sql
SELECT
    * 
FROM
    (
        ( SELECT repo_id, issues_enabled, COUNT ( * ) AS meta_count 
        FROM repo_info 
        WHERE issues_count != 0 
        GROUP BY repo_id, issues_enabled 
        ORDER BY repo_id ) zz
        LEFT OUTER JOIN (
        SELECT A.repo_id,
            A.repo_name,
            b.issues_count,
            d.repo_id AS issue_repo_id,
            e.last_collected,
                        f.most_recently_collected_issue, 
            COUNT ( * ) AS issue_count,
            (
            b.issues_count - COUNT ( * )) AS issues_missing,
            ABS (
            CAST (( COUNT ( * )) +1 AS DOUBLE PRECISION )  / CAST ( b.issues_count + 1 AS DOUBLE PRECISION )) AS ratio_abs,
            (
            CAST (( COUNT ( * )) +1 AS DOUBLE PRECISION )  / CAST ( b.issues_count + 1 AS DOUBLE PRECISION )) AS ratio_issues 
        FROM
            augur_data.repo A,
            augur_data.issues d,
            augur_data.repo_info b,
            ( SELECT repo_id, MAX ( data_collection_date ) AS last_collected FROM augur_data.repo_info GROUP BY repo_id ORDER BY repo_id ) e, 
            ( SELECT repo_id, MAX ( data_collection_date ) AS most_recently_collected_issue FROM issues GROUP BY repo_id ORDER BY repo_id ) f 
        WHERE
            A.repo_id = b.repo_id 
                        AND lower(A.repo_git) like '%github.com%'
            AND A.repo_id = d.repo_id 
            AND b.repo_id = d.repo_id 
            AND e.repo_id = A.repo_id 
            AND b.data_collection_date = e.last_collected 
            -- AND d.issue_id IS NULL 
            AND f.repo_id = A.repo_id
                        and d.pull_request is NULL 
                        and b.issues_count is not NULL 
        GROUP BY
            A.repo_id,
            d.repo_id,
            b.issues_count,
            e.last_collected,
            f.most_recently_collected_issue 
        ORDER BY ratio_abs
        ) yy ON zz.repo_id = yy.repo_id 
    ) D 
        where d.issues_enabled = 'true';
-- order by most_recently_collected_issue desc 

SELECT
    * 
FROM
    (
    SELECT
        repo_info.repo_id,
        repo.repo_name,
        MAX ( pull_request_count ) AS max_pr_count,	
        COUNT ( * ) AS meta_count 
    FROM
        repo_info,
        repo -- WHERE issues_enabled = 'true' 
    WHERE
        pull_request_count >= 1
        AND repo.repo_id = repo_info.repo_id 
    GROUP BY
        repo_info.repo_id,
        repo.repo_name 
    ORDER BY
        repo_info.repo_id,
        repo.repo_name 
    ) yy
    LEFT OUTER JOIN (
    SELECT A
        .repo_id,
        A.repo_name,	
                a.repo_git, 
        b.pull_request_count,
        d.repo_id AS pull_request_repo_id,
        e.last_collected,
        f.last_pr_collected,
        COUNT ( * ) AS pull_requests_collected,
        ( b.pull_request_count - COUNT ( * ) ) AS pull_requests_missing,
        ABS ( CAST ( ( COUNT ( * ) ) + 1 AS DOUBLE PRECISION ) / CAST ( b.pull_request_count + 1 AS DOUBLE PRECISION ) ) AS ratio_abs,
        ( CAST ( ( COUNT ( * ) ) + 1 AS DOUBLE PRECISION ) / CAST ( b.pull_request_count + 1 AS DOUBLE PRECISION ) ) AS ratio_issues 
    FROM
        augur_data.repo A,
        augur_data.pull_requests d,
        augur_data.repo_info b,
        ( SELECT repo_id, MAX ( data_collection_date ) AS last_collected FROM augur_data.repo_info GROUP BY repo_id ORDER BY repo_id ) e,
        ( SELECT repo_id, MAX ( data_collection_date ) AS last_pr_collected FROM augur_data.pull_requests GROUP BY repo_id ORDER BY repo_id ) f 
    WHERE
        A.repo_id = b.repo_id 
        AND LOWER ( A.repo_git ) LIKE'%github.com%' 
        AND A.repo_id = d.repo_id 
        AND b.repo_id = d.repo_id 
        AND e.repo_id = A.repo_id 
        AND b.data_collection_date = e.last_collected 
        AND f.repo_id = A.repo_id -- AND d.pull_request_id IS NULL
    GROUP BY
        A.repo_id,
        d.repo_id,
        b.pull_request_count,
        e.last_collected,
        f.last_pr_collected 
    ORDER BY
        A.repo_id DESC 
    ) zz ON yy.repo_id = zz.repo_id 
ORDER BY
		ratio_abs; 
		--last_pr_collected desc;
		--pull_requests_missing desc; 
		

SELECT
    * 
FROM
    (
    SELECT
        repo_info.repo_id,
        repo.repo_name,
        MAX ( pull_request_count ) AS max_pr_count,	
        COUNT ( * ) AS meta_count 
    FROM
        repo_info,
        repo -- WHERE issues_enabled = 'true' 
    WHERE
        pull_request_count >= 1
        AND repo.repo_id = repo_info.repo_id 
    GROUP BY
        repo_info.repo_id,
        repo.repo_name 
    ORDER BY
        repo_info.repo_id,
        repo.repo_name 
    ) yy
    LEFT OUTER JOIN (
    SELECT A
        .repo_id,
        A.repo_name,	
                a.repo_git, 
        b.pull_request_count,
        d.repo_id AS pull_request_repo_id,
        e.last_collected,
        f.last_pr_collected,
        COUNT ( * ) AS pull_requests_collected,
        ( b.pull_request_count - COUNT ( * ) ) AS pull_requests_missing,
        ABS ( CAST ( ( COUNT ( * ) ) + 1 AS DOUBLE PRECISION ) / CAST ( b.pull_request_count + 1 AS DOUBLE PRECISION ) ) AS ratio_abs,
        ( CAST ( ( COUNT ( * ) ) + 1 AS DOUBLE PRECISION ) / CAST ( b.pull_request_count + 1 AS DOUBLE PRECISION ) ) AS ratio_issues 
    FROM
        augur_data.repo A,
        augur_data.pull_requests d,
        augur_data.repo_info b,
        ( SELECT repo_id, MAX ( data_collection_date ) AS last_collected FROM augur_data.repo_info GROUP BY repo_id ORDER BY repo_id ) e,
        ( SELECT repo_id, MAX ( data_collection_date ) AS last_pr_collected FROM augur_data.pull_requests GROUP BY repo_id ORDER BY repo_id ) f 
    WHERE
        A.repo_id = b.repo_id 
        AND LOWER ( A.repo_git ) LIKE'%github.com%' 
        AND A.repo_id = d.repo_id 
        AND b.repo_id = d.repo_id 
        AND e.repo_id = A.repo_id 
        AND b.data_collection_date = e.last_collected 
        AND f.repo_id = A.repo_id -- AND d.pull_request_id IS NULL
    GROUP BY
        A.repo_id,
        d.repo_id,
        b.pull_request_count,
        e.last_collected,
        f.last_pr_collected 
    ORDER BY
        A.repo_id DESC 
    ) zz ON yy.repo_id = zz.repo_id 
ORDER BY
		ratio_abs; 
--		last_pr_collected desc;
		--pull_requests_missing desc; 		

        
select 'pull requets collected' as data_point, count(*) as count from pull_requests
union 
select data_point, sum(COUNT) 
from 
(
SELECT
    data_point, 
    SUM ( COUNT ) AS COUNT 
FROM
    (
    SELECT distinct on (repo_id) repo_id, 'pull request metadata count' as data_point, max(latest_collection_date) as maxdate,
        SUM ( pull_request_count ) AS COUNT 
    FROM
        ( SELECT distinct on (repo_id) repo_id, MAX( data_collection_date) as latest_collection_date, pull_request_count FROM augur_data.repo_info GROUP BY repo_id, pull_request_count ORDER BY repo_id ) A 
    GROUP BY
        data_point, repo_id
		order by repo_id
    ) b group by data_point, repo_id, count, maxdate ) d group by data_point ;
		
	
-- Some repositories will have no pull requests. If there are no pull requests, and no issues, the repositories cannot be clustered or evaluated by the machine learning workers, which look at the message text following each issue and each PR. 		
select repo_id, pull_request_count, max(data_collection_date) from repo_info where pull_request_count=0
group by repo_id, pull_request_count
order by repo_id, pull_request_count asc; 

select count(*) from message; 

select tool_source, count(*) as counter from message
group by tool_source; 
```