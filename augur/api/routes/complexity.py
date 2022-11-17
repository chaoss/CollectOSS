#SPDX-License-Identifier: MIT
from flask import Response
import datetime
import base64
import sqlalchemy as s
import pandas as pd
from augur.api.util import metric_metadata
import json
import os
import requests

AUGUR_API_VERSION = 'api/unstable'

def create_routes(server):

    @server.app.route('/{}/complexity/project_languages'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_languages():
        return Response(response="[{'repo_name': 'augur', languages: { 'python': 100 }}]",
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_files'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_files():
        return Response(response="[{'repo_name': 'augur', files: 100}]",
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_lines'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_lines():
        return Response(response="[{'repo_name': 'augur', 'lines': 100000}]",
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_comments_lines'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_comment_lines():
        return Response(response="[{'repo_name': 'augur', 'comment_lines': 10000}]",
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_blank_lines'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_blank_lines():
        return Response(response="[{'repo_name': 'augur', 'blank_lines': 10000}]",
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_file_complexity'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_file_complexity():
        return Response(response="[{'repo_name': 'augur', 'file_complexity': 100}]",
                    status=200,
                    mimetype="application/json")
    
