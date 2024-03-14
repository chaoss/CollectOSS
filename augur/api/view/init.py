from pathlib import Path
from .server import Environment
from augur.application.logs import AugurLogger
import secrets, yaml

env = Environment()

# load configuration files and initialize globals
configFile = Path(env.setdefault("CONFIG_LOCATION", "config.yml"))

report_requests = {}
settings = {}

def init_settings():
    global settings
    settings["approot"] = "/"
    settings["caching"] = "static/cache/"
    settings["cache_expiry"] = 604800
    settings["serving"] = "http://augur.chaoss.io/api/unstable"
    settings["pagination_offset"] = 25
    settings["reports"] = "reports.yml"
    settings["session_key"] = secrets.token_hex()

def write_settings(current_settings):
    current_settings["caching"] = str(current_settings["caching"])

    if "valid" in current_settings:
        current_settings.pop("valid")

    with open(configFile, 'w') as file:
        yaml.dump(current_settings, file)

# default reports definition
reports = {
    "pull_request_reports":[
        {
            "url":"average_commits_per_PR",
            "description":"Average commits per pull request"
        },
        {
            "url":"average_comments_per_PR",
            "description":"Average comments per pull request"
        },
        {
            "url":"PR_counts_by_merged_status",
            "description":"Pull request counts by merged status"
        },
        {
            "url":"mean_response_times_for_PR",
            "description":"Mean response times for pull requests"
        },
        {
            "url":"mean_days_between_PR_comments",
            "description":"Mean days between pull request comments"
        },
        {
            "url":"PR_time_to_first_response",
            "description":"Pull request time until first response"
        },
        {
            "url":"average_PR_events_for_closed_PRs",
            "description":"Average pull request events for closed pull requests"
        },
        {
            "url":"Average_PR_duration",
            "description":"Average pull request duration"
        }
    ],
    "contributor_reports":[
        {
            "url":"new_contributors_bar",
            "description":"New contributors bar graph"
        },
        {
            "url":"returning_contributors_pie_chart",
            "description":"Returning contributors pie chart"
        }
    ],
    "contributor_reports_stacked":[
        {
            "url":"new_contributors_stacked_bar",
            "description":"New contributors stacked bar chart"
        },
        {
            "url":"returning_contributors_stacked_bar",
            "description":"Returning contributors stacked bar chart"
        }
    ]
}

# Initialize logging
def init_logging():
    global logger
    logger = AugurLogger("augur_view", reset_logfiles=True).get_logger()
