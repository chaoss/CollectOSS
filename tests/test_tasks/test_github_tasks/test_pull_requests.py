import pytest
import httpx
import logging

from augur.tasks.github.pull_requests.core import *
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Config 


logger = logging.getLogger(__name__)

@pytest.fixture
def github_api_key_headers():

    with DatabaseSession(logger) as session:

        api_key = session.query(Config).filter(Config.section_name == "Keys", Config.setting_name == "github_api_key").one().value

        headers = {"Authorization": f'token {api_key}'}

        yield headers

@pytest.mark.parametrize("pr_number", [1, 2, 26])
def test_extract_data_from_pr(github_api_key_headers, pr_number):
    
    url = f"https://api.github.com/repos/operate-first/blueprint/pulls/{str(pr_number)}" 

    with httpx.Client() as client:

        data = client.request(method="GET", url=url, headers=github_api_key_headers, timeout=180).json()

        metadata_keys = ["head", "base"]

        meatadata_len = 0
        contributors_len = 0

        try:
            data["user"]
            contributors_len +=1
        except KeyError:
            pass

        for key in metadata_keys:

            try:
                metadata = data[key]
                meatadata_len += 1
            except KeyError:
                continue

            # if login exists on metadata then add count to contributors
            try:
                data[key]["user"]["login"]
                contributors_len += 1
            except KeyError:
                pass

        # count one contributor for every reviewer and assignee
        for value in data["requested_reviewers"] + data["assignees"]:

            try:
                value["login"]
                contributors_len += 1
            except KeyError:
                continue


        labels_len = len(data["labels"])
        requested_reviewers_len = len(data["requested_reviewers"])
        assignees_len = len(data["assignees"])        

        # print(f"Pr number: {pr_number}")
        # print(f"Metadata: {meatadata_len}")
        # print(f"Labels: {labels_len}")
        # print(f"Reviewers: {requested_reviewers_len}")
        # print(f"Assignees: {assignees_len}")
        # print(f"Contributors: {contributors_len}")

        repo_id = -1
        tool_source = "Pr Task"
        tool_version = "2.0"
        data_source = "Github API"

        pr, labels, assignees, reviewers, metadata, contributors = extract_data_from_pr(data, repo_id, tool_source, tool_version, data_source)

        assert pr is not None
        assert labels is not None
        assert assignees is not None
        assert reviewers is not None
        assert metadata is not None
        assert contributors is not None

        assert type(pr) == dict
        assert len(labels) == labels_len
        assert len(assignees) == assignees_len
        assert len(reviewers) == requested_reviewers_len
        assert len(metadata) == meatadata_len
        assert len(contributors) == contributors_len
        

def test_extract_data_from_pr_list(github_api_key_headers):

    base_url = f"https://api.github.com/repos/operate-first/blueprint/pulls/" 

    contributor_count = 0
    metadata_count = 0
    reviewer_count = 0
    assignee_count = 0
    label_count = 0

    raw_pr_data = []

    numbers = [1, 2, 3, 4, 5, 6, 7, 26]
    for pr_number in numbers:

        url = base_url + str(pr_number)

        print(url)

        with httpx.Client() as client:

            data = client.request(method="GET", url=url, headers=github_api_key_headers, timeout=180).json()

            raw_pr_data.append(data)

            metadata_keys = ["head", "base"]

            try:
                data["user"]
                contributor_count +=1
            except KeyError:
                pass

            for key in metadata_keys:

                # if "head" or "base" exist add one ot metadata_len
                if data[key]:

                    metadata_count += 1
                
                    # if login exists on metadata then add count to contributors
                    try:
                        data[key]["user"]["login"]
                        contributor_count += 1
                    except KeyError:
                        pass

            # count one contributor for every reviewer and assignee
            for value in data["requested_reviewers"] + data["assignees"]:

                try:
                    value["login"]
                    contributor_count += 1
                except KeyError:
                    continue

            label_count += len(data["labels"])
            reviewer_count += len(data["requested_reviewers"])
            assignee_count += len(data["assignees"])

    repo_id = -1
    tool_source = "Pr Task"
    tool_version = "2.0"
    data_source = "Github API"

    pr_dicts, pr_mapping_data, pr_numbers, contributors = extract_data_from_pr_list(raw_pr_data, repo_id, tool_source, tool_version, data_source)

    assert pr_dicts is not None
    assert pr_mapping_data is not None
    assert pr_numbers is not None
    assert contributors is not None 

    assert len(pr_dicts) == len(numbers)
    assert len(pr_mapping_data) == len(numbers)
    assert len(pr_numbers) == len(numbers)
    assert contributor_count == len(contributors)

    

    urls = [base_url + str(pr_number) for pr_number in numbers]

    returned_metadata_count = 0
    returned_reviewer_count = 0
    returned_assignee_count = 0
    returned_label_count = 0 

    for pr_number in numbers:

        url = base_url + str(pr_number)

        other_pr_data = pr_mapping_data[url]


        returned_metadata_count += len(other_pr_data["metadata"])
        returned_reviewer_count += len(other_pr_data["reviewers"])
        returned_assignee_count += len(other_pr_data["assignees"])
        returned_label_count += len(other_pr_data["labels"])      

    assert metadata_count == returned_metadata_count
    assert reviewer_count == returned_reviewer_count
    assert assignee_count == returned_assignee_count
    assert label_count == returned_label_count
        


def test_insert_pr_contributors():
    pass


def insert_prs():

   pass

def test_map_other_pr_data_to_pr():

    pass

def test_insert_other_pr_data():

    pass

