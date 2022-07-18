#SPDX-License-Identifier: MIT
import requests
import pytest

def test_contributors_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/10/contributors')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["total"] > 0


def test_contributors_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/10/repos/25430/contributors')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["total"] > 0

def test_contributors_new_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/10/contributors-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["new_contributors"] > 0


def test_contributors_new_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/10/repos/25430/contributors-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["new_contributors"] > 0

