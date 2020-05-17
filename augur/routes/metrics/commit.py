def create_routes(server):
    
    metrics = server.augur_app.metrics

    server.add_standard_metric(metrics.annual_commit_count_ranked_by_new_repo_in_repo_group,'annual-commit-count-ranked-by-new-repo-in-repo-group')

    server.add_standard_metric(metrics.annual_commit_count_ranked_by_repo_in_repo_group,'annual-commit-count-ranked-by-repo-in-repo-group')

