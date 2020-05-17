#SPDX-License-Identifier: MIT

def create_routes(server):

    metrics = server.augur_app.metrics

    server.add_standard_metric(metrics.reviews, 'reviews')

    server.add_standard_metric(metrics.reviews_accepted, 'reviews-accepted')

    server.add_standard_metric(metrics.reviews_declined, 'reviews-declined')

    server.add_standard_metric(metrics.review_duration, 'review-duration')

    server.add_standard_metric(metrics.pull_requests_merge_contributor_new, 'pull-requests-merge-contributor-new')

    server.add_standard_metric(metrics.pull_request_acceptance_rate, 'pull-request-acceptance-rate')

    server.add_standard_metric(metrics.pull_requests_closed_no_merge, 'pull-requests-closed-no-merge')

    server.add_standard_metric(metrics.pull_request_merged_status_counts, 'pull-request-merged-status-counts')

    server.add_standard_metric(metrics.pull_request_average_time_to_close, 'pull-request-average-time-to-close')

    server.add_standard_metric(metrics.pull_request_average_time_between_responses, 'pull-request-average-time-between-responses')

    server.add_standard_metric(metrics.pull_request_average_commit_counts, 'pull-request-average-commit-counts')

    server.add_standard_metric(metrics.pull_request_average_event_counts, 'pull-request-average-event-counts')

    server.add_standard_metric(metrics.pull_request_average_time_to_responses_and_close, 'pull-request-average-time-to-responses-and-close')
