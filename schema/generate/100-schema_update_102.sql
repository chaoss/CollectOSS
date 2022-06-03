BEGIN; 
DROP MATERIALIZED VIEW IF   EXISTS "augur_data"."explorer_contributor_actions";
CREATE MATERIALIZED VIEW "augur_data"."explorer_contributor_actions" AS 
SELECT
cntrb_id,
created_at,
repo_id,
LOGIN,
ACTION,
RANK 
FROM
    (
    SELECT
        * 
    FROM
        (
        SELECT ID AS
            cntrb_id,
            A.created_at AS created_at,
            date_part( 'month', A.created_at :: DATE ) AS MONTH,
            date_part( 'year', A.created_at :: DATE ) AS YEAR,
            A.repo_id,
            repo_name,
            full_name,
            LOGIN,
            ACTION,
            RANK ( ) OVER ( PARTITION BY ID, A.repo_id ORDER BY A.created_at ASC ) 
        FROM
            (
                (
                SELECT
                    canonical_id AS ID,
                    created_at AS created_at,
                    repo_id,
                    'issue_opened' AS ACTION,
                    contributors.cntrb_full_name AS full_name,
                    contributors.cntrb_login AS LOGIN 
                FROM
                    augur_data.issues
                    LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = issues.reporter_id
                    LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                WHERE
                    pull_request IS NULL 
                GROUP BY
                    canonical_id,
                    repo_id,
                    issues.created_at,
                    contributors.cntrb_full_name,
                    contributors.cntrb_login 
                ) UNION ALL
                (
                SELECT
                    canonical_id AS ID,
                    TO_TIMESTAMP( cmt_author_date, 'YYYY-MM-DD' ) AS created_at,
                    repo_id,
                    'commit' AS ACTION,
                    contributors.cntrb_full_name AS full_name,
                    contributors.cntrb_login AS LOGIN 
                FROM
                    augur_data.commits
                    LEFT OUTER JOIN augur_data.contributors ON cntrb_email = cmt_author_email
                    LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                GROUP BY
                    repo_id,
                    canonical_email,
                    canonical_id,
                    commits.cmt_author_date,
                    contributors.cntrb_full_name,
                    contributors.cntrb_login 
                ) UNION ALL
                (
                SELECT
                    message.cntrb_id AS ID,
                    created_at AS created_at,
                    commits.repo_id,
                    'commit_comment' AS ACTION,
                    contributors.cntrb_full_name AS full_name,
                    contributors.cntrb_login AS LOGIN 
                FROM
                    augur_data.commit_comment_ref,
                    augur_data.commits,
                    augur_data.message
                    LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = message.cntrb_id
                    LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                WHERE
                    commits.cmt_id = commit_comment_ref.cmt_id /**AND commits.repo_id in (30347, 33226)**/
                    
                    AND commit_comment_ref.msg_id = message.msg_id 
                GROUP BY
                    ID,
                    commits.repo_id,
                    commit_comment_ref.created_at,
                    contributors.cntrb_full_name,
                    contributors.cntrb_login 
                ) UNION ALL
                (
                SELECT
                    issue_events.cntrb_id AS ID,
                    issue_events.created_at AS created_at,
                    issues.repo_id,
                    'issue_closed' AS ACTION,
                    contributors.cntrb_full_name AS full_name,
                    contributors.cntrb_login AS LOGIN 
                FROM
                    augur_data.issues,
                    augur_data.issue_events
                    LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = issue_events.cntrb_id
                    LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                WHERE
                    issues.issue_id = issue_events.issue_id 
                    AND issues.pull_request IS NULL 
                    AND issue_events.cntrb_id IS NOT NULL 
                    AND ACTION = 'closed' 
                GROUP BY
                    issue_events.cntrb_id,
                    issues.repo_id,
                    issue_events.created_at,
                    contributors.cntrb_full_name,
                    contributors.cntrb_login 
                ) UNION ALL
                (
                SELECT
                    pr_augur_contributor_id AS ID,
                    pr_created_at AS created_at,
                    pull_requests.repo_id,
                    'open_pull_request' AS ACTION,
                    contributors.cntrb_full_name AS full_name,
                    contributors.cntrb_login AS LOGIN 
                FROM
                    augur_data.pull_requests
                    LEFT OUTER JOIN augur_data.contributors ON pull_requests.pr_augur_contributor_id = contributors.cntrb_id
                    LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                GROUP BY
                    pull_requests.pr_augur_contributor_id,
                    pull_requests.repo_id,
                    pull_requests.pr_created_at,
                    contributors.cntrb_full_name,
                    contributors.cntrb_login 
                ) UNION ALL
                (
                SELECT
                    message.cntrb_id AS ID,
                    msg_timestamp AS created_at,
                    pull_requests.repo_id AS repo_id,
                    'pull_request_comment' AS ACTION,
                    contributors.cntrb_full_name AS full_name,
                    contributors.cntrb_login AS LOGIN 
                FROM
                    augur_data.pull_requests,
                    augur_data.pull_request_message_ref,
                    augur_data.message
                    LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = message.cntrb_id
                    LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                WHERE
                    pull_request_message_ref.pull_request_id = pull_requests.pull_request_id 
                    AND pull_request_message_ref.msg_id = message.msg_id 
                GROUP BY
                    message.cntrb_id,
                    pull_requests.repo_id,
                    message.msg_timestamp,
                    contributors.cntrb_full_name,
                    contributors.cntrb_login 
                ) UNION ALL
                (
                SELECT
                    issues.reporter_id AS ID,
                    msg_timestamp AS created_at,
                    issues.repo_id AS repo_id,
                    'issue_comment' AS ACTION,
                    contributors.cntrb_full_name AS full_name,
                    contributors.cntrb_login AS LOGIN 
                FROM
                    augur_data.issues,
                    augur_data.issue_message_ref,
                    augur_data.message
                    LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = message.cntrb_id
                    LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                WHERE
                    issue_message_ref.msg_id = message.msg_id 
                    AND issues.issue_id = issue_message_ref.issue_id 
                    AND issues.pull_request_id = NULL 
                GROUP BY
                    issues.reporter_id,
                    issues.repo_id,
                    message.msg_timestamp,
                    contributors.cntrb_full_name,
                    contributors.cntrb_login 
                ) 
            ) A,
            augur_data.repo 
        WHERE
        ID IS NOT NULL 
            AND A.repo_id = augur_data.repo.repo_id 
        GROUP BY
            A.ID,
            A.repo_id,
            A.ACTION,
            A.created_at,
            repo.repo_name,
            A.full_name,
            A.LOGIN,
            A.ACTION 
        ORDER BY
            cntrb_id 
        ) b 
    ) x;
ALTER MATERIALIZED VIEW "augur_data"."explorer_contributor_actions" OWNER TO "augur";
REFRESH MATERIALIZED VIEW "augur_data"."explorer_contributor_actions";
GRANT SELECT ON
    "augur_data"."explorer_contributor_actions" TO PUBLIC;

--- 
drop materialized view IF EXISTS "augur_data"."explorer_all_new_contributors";

DROP MATERIALIZED VIEW if exists "augur_data"."explorer_entry_list";

CREATE MATERIALIZED VIEW "augur_data"."explorer_entry_list"
AS
SELECT DISTINCT r.repo_git,
    rg.rg_name
   FROM (repo r
     JOIN repo_groups rg ON ((rg.repo_group_id = r.repo_group_id)))
  ORDER BY rg.rg_name; 

ALTER MATERIALIZED VIEW "augur_data"."explorer_entry_list" OWNER TO "augur";

REFRESH MATERIALIZED VIEW "augur_data"."explorer_entry_list";

GRANT SELECT ON "augur_data"."explorer_entry_list" to PUBLIC; 


--
update "augur_operations"."augur_settings" set value = 102
  where setting = 'augur_data_version'; 

COMMIT; 