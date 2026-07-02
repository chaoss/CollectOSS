#SPDX-License-Identifier: MIT

from flask import Response
from flask import request
import datetime
import base64
import sqlalchemy as s
import pandas as pd
from collectoss.api.util import metric_metadata
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import os
import requests
import slack

from collectoss.application.environment import SystemEnv

from ..server import app


API_VERSION = 'api/unstable'


@app.route('/auggie/get_user', methods=['POST'])
def get_auggie_user():
    # arg = [request.json]
    # response = server.transform(metrics.get_auggie_user, args=arg)
    # return Response(response=response, status=200, mimetype="application/json")
    ## From Method
    profile_name = 'collectoss'
    if SystemEnv.get('COLLECTOSS_IS_PROD'):
        profile_name = 'default'
    client = boto3.Session(region_name='us-east-1', profile_name=profile_name).client('dynamodb')
    response = client.get_item(
        TableName="auggie-users",
                Key={
                    "email": {"S":'{}:{}'.format(body["email"],body["teamID"])}
                }
    )
    user = response['Item']

    filteredUser = {
        "interestedRepos":user["interestedRepos"],
        "interestedGroups":user["interestedGroups"],
        "host":user["host"]
    }
    
    return filteredUser

@app.route('/auggie/update_tracking', methods=['POST'])
def update_auggie_user_tracking():
    # arg = [request.json]
    # response = server.transform(metrics.update_tracking, args=arg)
    # return Response(response=response, status=200, mimetype="application/json")
    ## From Method
    profile_name = 'collectoss'
    if SystemEnv.get('COLLECTOSS_IS_PROD'):
        profile_name = 'default'
    client = boto3.Session(region_name='us-east-1', profile_name=profile_name).client('dynamodb')
    response = client.update_item(
        TableName="auggie-users",
        Key={
            "email": {"S": '{}:{}'.format(body["email"], body["teamID"])}
        },
        UpdateExpression="SET interestedGroups = :valGroup, interestedRepos = :valRepo, maxMessages = :valMax, host = :valHost, interestedInsightTypes = :valInterestedInsights",
        ExpressionAttributeValues={
            ":valGroup": {
                "L": body["groups"]
            },
            ":valRepo": {
                "L": body["repos"]
            },
            ":valMax": {
                "N": body["maxMessages"]
            },
            ":valHost": {
                "S": body["host"]
            },
            ":valInterestedInsights": {
                "L": body["insightTypes"]
            }
        },
        ReturnValues="ALL_NEW"
    )

    updated_values = response['Attributes']

    filtered_values = {
        "interestedRepos": updated_values["interestedRepos"],
        "interestedGroups": updated_values["interestedGroups"],
        "host": updated_values["host"]
    }

    return filtered_values

@app.route('/auggie/slack_login', methods=['POST'])
def slack_login():
    # arg = [request.json]
    # response = server.transform(metrics.slack_login, args=arg)
    # return Response(response=response, status=200, mimetype="application/json")
    # From Method
    print("slack_login")

    r = requests.get(
        url=f'https://slack.com/api/oauth.v2.access?code={body["code"]}&client_id={SystemEnv.get("AUGGIE_CLIENT_ID")}&client_secret={SystemEnv.get("AUGGIE_CLIENT_SECRET")}&redirect_uri=http%3A%2F%2Flocalhost%3A8080')
    data = r.json()

    if (data["ok"]):
        print(data)
        token = data["authed_user"]["access_token"]
        team_id = data["team"]["id"]
        webclient = slack.WebClient(token=token)

        user_response = webclient.users_identity()
        print(user_response)
        email = user_response["user"]["email"]

        profile_name = 'collectoss'
        if SystemEnv.get('COLLECTOSS_IS_PROD'):
            profile_name = 'default'
        print("Making Boto3 Session")
        client = boto3.Session(region_name='us-east-1',
                            profile_name=profile_name).client('dynamodb')
        response = client.get_item(
            TableName="auggie-users",
            Key={
                "email": {"S": '{}:{}'.format(email, team_id)}
            }
        )

        if ('Item' in response):
            user = response['Item']
            print(user)

            filteredUser = {
                "interestedRepos": user["interestedRepos"],
                "interestedGroups": user["interestedGroups"],
                "host": user["host"],
                "maxMessages": user["maxMessages"],
                "interestedInsights": user["interestedInsightTypes"]
            }

            user_body = json.dumps({
                'team_id': team_id,
                'email': email,
                'user': filteredUser
            })

            print(user_body)

            return user_body
        else:
            client.put_item(
                TableName="auggie-users",
                Item={
                    'botToken': {'S': 'null'},
                    'currentMessages': {'N': "0"},
                    'maxMessages': {'N': "0"},
                    'email': {'S': '{}:{}'.format(email, team_id)},
                    'host': {'S': 'null'},
                    'interestedGroups': {'L': []},
                    'interestedRepos': {'L': []},
                    'interestedInsightTypes': {'L': []},
                    'teamID': {'S': team_id},
                    'thread': {'S': 'null'},
                    'userID': {'S': user_response['user']['id']}
                }
            )

            # users_response = webclient.users_list()
            # for user in users_response["members"]:
            #     if "api_app_id" in user["profile"] and user["profile"]["api_app_id"] == "ASQKB8JT0":
            #         im_response = webclient.conversations_open(
            #             users=user["id"]
            #         )
            #         print("Hopefully IM is opened")
            #         channel = im_response["channel"]["id"]

            #         message_response = webclient.chat_postMessage(
            #             channel=channel,
            #             text="what repos?",
            #             as_user="true")
            #         print(message_response)

            #         ts = message_response["ts"]
            #         webclient.chat_delete(
            #             channel=channel,
            #             ts=ts
            #         )

            response = client.get_item(
                TableName="auggie-users",
                Key={
                    "email": {"S": '{}:{}'.format(email, team_id)}
                }
            )

            user = response['Item']
            print(user)

            filteredUser = {
                "interestedRepos": user["interestedRepos"],
                "interestedGroups": user["interestedGroups"],
                "host": user["host"],
                "maxMessages": user["maxMessages"],
                "interestedInsights": user["interestedInsightTypes"]
            }

            user_body = json.dumps({
                'team_id': team_id,
                'email': email,
                'user': filteredUser
            })

            print(user_body)

            return user_body
    else:
        return data