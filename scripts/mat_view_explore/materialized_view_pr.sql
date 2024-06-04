            create materialized view augur_data.explorer_pr_metrics as 
	SELECT
                repo.repo_id AS repo_id,
                pull_requests.pr_src_id AS pr_src_id,
                repo.repo_name AS repo_name,
                pr_src_author_association,
                repo_groups.rg_name AS repo_group,
                pull_requests.pr_src_state,
                pull_requests.pr_merged_at,
                pull_requests.pr_created_at AS pr_created_at,
                pull_requests.pr_closed_at AS pr_closed_at,
                date_part( 'year', pr_created_at :: DATE ) AS CREATED_YEAR,
                date_part( 'month', pr_created_at :: DATE ) AS CREATED_MONTH,
                date_part( 'year', pr_closed_at :: DATE ) AS CLOSED_YEAR,
                date_part( 'month', pr_closed_at :: DATE ) AS CLOSED_MONTH,
                pr_src_meta_label,
                pr_head_or_base,
                ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_close,
                ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_close, 
                ( EXTRACT ( EPOCH FROM first_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_first_response,
                ( EXTRACT ( EPOCH FROM first_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_first_response, 
                ( EXTRACT ( EPOCH FROM last_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_last_response,
                ( EXTRACT ( EPOCH FROM last_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_last_response, 
                first_response_time,
                last_response_time,
                (EXTRACT ( EPOCH FROM average_time_between_responses) ) / 3600 as average_hours_between_responses,
                assigned_count,
                review_requested_count,
                labeled_count,
                subscribed_count,
                mentioned_count,
                referenced_count,
                closed_count,
                head_ref_force_pushed_count,
                merged_count::INT,
                milestoned_count,
                unlabeled_count,
                head_ref_deleted_count,
                comment_count,
                COALESCE(lines_added, 0) as lines_added, 
                COALESCE(lines_removed, 0) as lines_removed,
                commit_count, 
                COALESCE(file_count, 0) as file_count
            FROM
                augur_data.repo,
                augur_data.repo_groups,
                augur_data.pull_requests LEFT OUTER JOIN ( 
                    SELECT pull_requests.pull_request_id,
                    count(*) FILTER (WHERE action = 'assigned') AS assigned_count,
                    count(*) FILTER (WHERE action = 'review_requested') AS review_requested_count,
                    count(*) FILTER (WHERE action = 'labeled') AS labeled_count,
                    count(*) FILTER (WHERE action = 'unlabeled') AS unlabeled_count,
                    count(*) FILTER (WHERE action = 'subscribed') AS subscribed_count,
                    count(*) FILTER (WHERE action = 'mentioned') AS mentioned_count,
                    count(*) FILTER (WHERE action = 'referenced') AS referenced_count,
                    count(*) FILTER (WHERE action = 'closed') AS closed_count,
                    count(*) FILTER (WHERE action = 'head_ref_force_pushed') AS head_ref_force_pushed_count,
                    count(*) FILTER (WHERE action = 'head_ref_deleted') AS head_ref_deleted_count,
                    count(*) FILTER (WHERE action = 'milestoned') AS milestoned_count,
                    COALESCE(count(*) FILTER (WHERE action = 'merged'), 0) AS merged_count,
                    COALESCE(MIN(message.msg_timestamp), pull_requests.pr_merged_at, pull_requests.pr_closed_at) AS first_response_time,
                    COALESCE(COUNT(DISTINCT message.msg_timestamp), 0) AS comment_count,
                    COALESCE(MAX(message.msg_timestamp), pull_requests.pr_closed_at) AS last_response_time,
                    COALESCE((MAX(message.msg_timestamp) - MIN(message.msg_timestamp)) / COUNT(DISTINCT message.msg_timestamp), pull_requests.pr_created_at - pull_requests.pr_closed_at) AS average_time_between_responses
                    FROM  augur_data.pull_requests 
                                            LEFT OUTER JOIN augur_data.pull_request_events on augur_data.pull_requests.pull_request_id = augur_data.pull_request_events.pull_request_id 
                                            JOIN augur_data.repo on repo.repo_id = pull_requests.repo_id 
                                            LEFT OUTER JOIN augur_data.pull_request_message_ref on pull_requests.pull_request_id = pull_request_message_ref.pull_request_id
                                            LEFT OUTER JOIN augur_data.message on pull_request_message_ref.msg_id = augur_data.message.msg_id
                    --WHERE repo.repo_id = {repo_id} 
                    GROUP BY pull_requests.pull_request_id
                ) response_times
                ON pull_requests.pull_request_id = response_times.pull_request_id
                LEFT JOIN (
                    SELECT pull_request_commits.pull_request_id, count(DISTINCT pr_cmt_sha) AS commit_count                                
                                            FROM augur_data.pull_request_commits, augur_data.pull_requests, augur_data.pull_request_meta
                    WHERE pull_requests.pull_request_id = pull_request_commits.pull_request_id
                    AND pull_requests.pull_request_id = pull_request_meta.pull_request_id
                    --AND pull_requests.repo_id  = {repo_id} 
                    AND pr_cmt_sha <> pull_requests.pr_merge_commit_sha
                    AND pr_cmt_sha <> pull_request_meta.pr_sha
                    GROUP BY pull_request_commits.pull_request_id
                ) all_commit_counts
                ON pull_requests.pull_request_id = all_commit_counts.pull_request_id
                LEFT JOIN (
                    SELECT MAX(pr_repo_meta_id), pull_request_meta.pull_request_id, pr_head_or_base, pr_src_meta_label
                    FROM augur_data.pull_requests, augur_data.pull_request_meta
                    WHERE pull_requests.pull_request_id = pull_request_meta.pull_request_id
                    --AND pull_requests.repo_id  = {repo_id} 
                    AND pr_head_or_base = 'base'
                    GROUP BY pull_request_meta.pull_request_id, pr_head_or_base, pr_src_meta_label
                ) base_labels
                ON base_labels.pull_request_id = all_commit_counts.pull_request_id
                LEFT JOIN (
                    SELECT sum(cmt_added) AS lines_added, sum(cmt_removed) AS lines_removed, pull_request_commits.pull_request_id, count(DISTINCT cmt_filename) AS file_count
                    FROM augur_data.pull_request_commits, augur_data.commits, augur_data.pull_requests, augur_data.pull_request_meta
                    WHERE cmt_commit_hash = pr_cmt_sha
                    AND pull_requests.pull_request_id = pull_request_commits.pull_request_id
                    AND pull_requests.pull_request_id = pull_request_meta.pull_request_id
                    --AND pull_requests.repo_id  = {repo_id} 
                    AND commits.repo_id = pull_requests.repo_id
                    AND commits.cmt_commit_hash <> pull_requests.pr_merge_commit_sha
                    AND commits.cmt_commit_hash <> pull_request_meta.pr_sha
                    GROUP BY pull_request_commits.pull_request_id
                ) master_merged_counts 
                ON base_labels.pull_request_id = master_merged_counts.pull_request_id                    
            WHERE 
                repo.repo_group_id = repo_groups.repo_group_id 
                AND repo.repo_id = pull_requests.repo_id 
                --AND repo.repo_id  = {repo_id} 
            ORDER BY
                merged_count DESC
