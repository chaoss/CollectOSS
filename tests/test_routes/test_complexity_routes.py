#SPDX-License-Identifier: MIT
import requests
import pytest

def test_complexity_languages(metrics):
    response = requests.get('http://localhost:5000/api/unstable/complexity/languages')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_complexity_files(metrics):
    response = requests.get('http://localhost:5000/api/unstable/complexity/project_files')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_complexity_lines(metrics):
    response = requests.get('http://localhost:5000/api/unstable/complexity/project_lines')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_complexity_comments(metrics):
    response = requests.get('http://localhost:5000/api/unstable/complexity/project_comment_lines')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_complexity_blanks(metrics):
    response = requests.get('http://localhost:5000/api/unstable/complexity/project_blank_lines')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_complexity_files_complexity(metrics):
    response = requests.get('http://localhost:5000/api/unstable/complexity/project_file_complexity')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
