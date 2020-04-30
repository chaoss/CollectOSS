#SPDX-License-Identifier: MIT

def create_routes(server):

    metrics = server.augur_app.metrics

    server.add_repo_group_metric(metrics.issues_new, 'issues-new')

    server.add_repo_metric(metrics.issues_new, 'issues-new')

    server.add_repo_group_metric(metrics.issues_active, 'issues-active')

    server.add_repo_metric(metrics.issues_active, 'issues-active')

    server.add_repo_group_metric(metrics.issues_closed, 'issues-closed')

    server.add_repo_metric(metrics.issues_closed, 'issues-closed')

    server.add_repo_group_metric(metrics.issue_duration, 'issue-duration')

    server.add_repo_metric(metrics.issue_duration, 'issue-duration')

    server.add_repo_group_metric(metrics.issue_participants, 'issue-participants')

    server.add_repo_metric(metrics.issue_participants, 'issue-participants')

    server.add_repo_group_metric(metrics.issue_backlog, 'issue-backlog')

    server.add_repo_metric(metrics.issue_backlog, 'issue-backlog')

    server.add_repo_group_metric(metrics.issue_throughput, 'issue-throughput')

    server.add_repo_metric(metrics.issue_throughput, 'issue-throughput')

    server.add_repo_group_metric(metrics.issues_first_time_opened, 'issues-first-time-opened')

    server.add_repo_metric(metrics.issues_first_time_opened, 'issues-first-time-opened')

    server.add_repo_group_metric(metrics.issues_first_time_closed, 'issues-first-time-closed')

    server.add_repo_metric(metrics.issues_first_time_closed, 'issues-first-time-closed')

    server.add_repo_group_metric(metrics.open_issues_count, 'open-issues-count')

    server.add_repo_metric(metrics.open_issues_count, 'open-issues-count')

    server.add_repo_group_metric(metrics.closed_issues_count, 'closed-issues-count')

    server.add_repo_metric(metrics.closed_issues_count, 'closed-issues-count')

    server.add_repo_group_metric(metrics.issues_open_age, 'issues-open-age')

    server.add_repo_metric(metrics.issues_open_age, 'issues-open-age')

    server.add_repo_group_metric(metrics.issues_closed_resolution_duration, 'issues-closed-resolution-duration')

    server.add_repo_metric(metrics.issues_closed_resolution_duration, 'issues-closed-resolution-duration')

    server.add_repo_group_metric(metrics.issues_maintainer_response_duration, 'issues-maintainer-response-duration')

    server.add_repo_metric(metrics.issues_maintainer_response_duration, 'issues-maintainer-response-duration')

    server.add_repo_group_metric(metrics.average_issue_resolution_time, 'average-issue-resolution-time')

    server.add_repo_metric(metrics.average_issue_resolution_time, 'average-issue-resolution-time')

    server.add_repo_group_metric(metrics.issue_comments_mean, 'issue-comments-mean')

    server.add_repo_metric(metrics.issue_comments_mean, 'issue-comments-mean')

    server.add_repo_group_metric(metrics.issue_comments_mean_std, 'issue-comments-mean-std')

    server.add_repo_metric(metrics.issue_comments_mean_std, 'issue-comments-mean-std')

    server.add_repo_group_metric(metrics.abandoned_issues, 'abandoned_issues')