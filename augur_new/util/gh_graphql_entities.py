from augur_new.worker_base import *
"""
    Should be designed on a per entity basis that has attributes that call 
    defined graphql queries.

    e.g. create a GHContributor graphql class that represents a contributor in github
    then various attributes call queries on the fly.

    Or like a 
"""


class GitHubRepo():
    def __init__(self):
        pass