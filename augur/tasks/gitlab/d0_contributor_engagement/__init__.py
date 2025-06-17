from augur.tasks.gitlab.d0_contributor_engagement.d0_worker import D0ContributorEngagementWorker

__all__ = ['D0ContributorEngagementWorker']

def worker():
    return D0ContributorEngagementWorker 