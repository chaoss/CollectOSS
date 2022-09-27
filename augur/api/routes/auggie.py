#SPDX-License-Identifier: MIT

from flask import Response
from flask import request
import datetime
import base64
import sqlalchemy as s
import pandas as pd
from augur.api.util import metric_metadata
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import os
import requests
import slack


AUGUR_API_VERSION = 'api/unstable'


# def annotate(metadata=None, **kwargs):
#     """
#     Decorates a function as being a metric
#     """
#     if metadata is None:
#         metadata = {}
#     def decorate(func):
#         if not hasattr(func, 'metadata'):
#             func.metadata = {}
#             metric_metadata.append(func.metadata)

#         func.metadata.update(metadata)
#         if kwargs.get('endpoint_type', None):
#             endpoint_type = kwargs.pop('endpoint_type')
#             if endpoint_type == 'repo':
#                 func.metadata['repo_endpoint'] = kwargs.get('endpoint')
#             else:
#                 func.metadata['group_endpoint'] = kwargs.get('endpoint')

#         func.metadata.update(dict(kwargs))

#         func.metadata['metric_name'] = request.sub('_', ' ', func.__name__).title()
#         func.metadata['source'] = request.sub(r'(.*\.)', '', func.__module__)
#         func.metadata['ID'] = "{}-{}".format(func.metadata['source'].lower(), func.metadata['tag'])

#         return func
#     return decorate

# def add_metrics(metrics, module_name):
#     # find all unbound endpoint functions objects (ones that have metadata) defined the given module_name 
#     # and bind them to the metrics class
#     # Derek are you proud of me
#     for name, obj in inspect.getmembers(sys.modules[module_name]):
#         if inspect.isfunction(obj) is True:
#             if hasattr(obj, 'metadata') is True:
#                 setattr(metrics, name, types.MethodType(obj, metrics))


# #@annotate(tag='slack_login')
# def slack_login(metric, body):
#     print("slack_login")

#     r = requests.get(
#         url=f'https://slack.com/api/oauth.v2.access?code={body["code"]}&client_id={os.environ["AUGGIE_CLIENT_ID"]}&client_secret={os.environ["AUGGIE_CLIENT_SECRET"]}&redirect_uri=http%3A%2F%2Flocalhost%3A8080')
#     data = r.json()

#     if (data["ok"]):
#         print(data)
#         token = data["authed_user"]["access_token"]
#         team_id = data["team"]["id"]
#         webclient = slack.WebClient(token=token)

#         user_response = webclient.users_identity()
#         print(user_response)
#         email = user_response["user"]["email"]

#         profile_name = 'augur'
#         if os.environ.get('AUGUR_IS_PROD'):
#             profile_name = 'default'
#         print("Making Boto3 Session")
#         client = boto3.Session(region_name='us-east-1',
#                             profile_name=profile_name).client('dynamodb')
#         response = client.get_item(
#             TableName="auggie-users",
#             Key={
#                 "email": {"S": '{}:{}'.format(email, team_id)}
#             }
#         )

#         if ('Item' in response):
#             user = response['Item']
#             print(user)

#             filteredUser = {
#                 "interestedRepos": user["interestedRepos"],
#                 "interestedGroups": user["interestedGroups"],
#                 "host": user["host"],
#                 "maxMessages": user["maxMessages"],
#                 "interestedInsights": user["interestedInsightTypes"]
#             }

#             user_body = json.dumps({
#                 'team_id': team_id,
#                 'email': email,
#                 'user': filteredUser
#             })

#             print(user_body)

#             return user_body
#         else:
#             client.put_item(
#                 TableName="auggie-users",
#                 Item={
#                     'botToken': {'S': 'null'},
#                     'currentMessages': {'N': "0"},
#                     'maxMessages': {'N': "0"},
#                     'email': {'S': '{}:{}'.format(email, team_id)},
#                     'host': {'S': 'null'},
#                     'interestedGroups': {'L': []},
#                     'interestedRepos': {'L': []},
#                     'interestedInsightTypes': {'L': []},
#                     'teamID': {'S': team_id},
#                     'thread': {'S': 'null'},
#                     'userID': {'S': user_response['user']['id']}
#                 }
#             )

#             # users_response = webclient.users_list()
#             # for user in users_response["members"]:
#             #     if "api_app_id" in user["profile"] and user["profile"]["api_app_id"] == "ASQKB8JT0":
#             #         im_response = webclient.conversations_open(
#             #             users=user["id"]
#             #         )
#             #         print("Hopefully IM is opened")
#             #         channel = im_response["channel"]["id"]

#             #         message_response = webclient.chat_postMessage(
#             #             channel=channel,
#             #             text="what repos?",
#             #             as_user="true")
#             #         print(message_response)

#             #         ts = message_response["ts"]
#             #         webclient.chat_delete(
#             #             channel=channel,
#             #             ts=ts
#             #         )

#             response = client.get_item(
#                 TableName="auggie-users",
#                 Key={
#                     "email": {"S": '{}:{}'.format(email, team_id)}
#                 }
#             )

#             user = response['Item']
#             print(user)

#             filteredUser = {
#                 "interestedRepos": user["interestedRepos"],
#                 "interestedGroups": user["interestedGroups"],
#                 "host": user["host"],
#                 "maxMessages": user["maxMessages"],
#                 "interestedInsights": user["interestedInsightTypes"]
#             }

#             user_body = json.dumps({
#                 'team_id': team_id,
#                 'email': email,
#                 'user': filteredUser
#             })

#             print(user_body)

#             return user_body
#     else:
#         return data

# #@annotate(tag='update-auggie-user-tracking')
# def update_tracking(metric, body):
#     profile_name = 'augur'
#     if os.environ.get('AUGUR_IS_PROD'):
#         profile_name = 'default'
#     client = boto3.Session(region_name='us-east-1', profile_name=profile_name).client('dynamodb')
#     response = client.update_item(
#         TableName="auggie-users",
#         Key={
#             "email": {"S": '{}:{}'.format(body["email"], body["teamID"])}
#         },
#         UpdateExpression="SET interestedGroups = :valGroup, interestedRepos = :valRepo, maxMessages = :valMax, host = :valHost, interestedInsightTypes = :valInterestedInsights",
#         ExpressionAttributeValues={
#             ":valGroup": {
#                 "L": body["groups"]
#             },
#             ":valRepo": {
#                 "L": body["repos"]
#             },
#             ":valMax": {
#                 "N": body["maxMessages"]
#             },
#             ":valHost": {
#                 "S": body["host"]
#             },
#             ":valInterestedInsights": {
#                 "L": body["insightTypes"]
#             }
#         },
#         ReturnValues="ALL_NEW"
#     )

#     updated_values = response['Attributes']

#     filtered_values = {
#         "interestedRepos": updated_values["interestedRepos"],
#         "interestedGroups": updated_values["interestedGroups"],
#         "host": updated_values["host"]
#     }

#     return filtered_values


# #@annotate(tag='get-auggie-user')
# def get_auggie_user(metric, body):
#     profile_name = 'augur'
#     if os.environ.get('AUGUR_IS_PROD'):
#         profile_name = 'default'
#     client = boto3.Session(region_name='us-east-1', profile_name=profile_name).client('dynamodb')
#     response = client.get_item(
#         TableName="auggie-users",
#              Key={
#                  "email": {"S":'{}:{}'.format(body["email"],body["teamID"])}
#              }
#     )
#     user = response['Item']

#     filteredUser = {
#         "interestedRepos":user["interestedRepos"],
#         "interestedGroups":user["interestedGroups"],
#         "host":user["host"]
#     }
   
#     return filteredUser

def create_routes(server):


    @server.app.route('/auggie/get_user', methods=['POST'])
    def get_auggie_user():
        # arg = [request.json]
        # response = server.transform(metrics.get_auggie_user, args=arg)
        # return Response(response=response, status=200, mimetype="application/json")
        ## From Method
        profile_name = 'augur'
        if os.environ.get('AUGUR_IS_PROD'):
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

    @server.app.route('/auggie/update_tracking', methods=['POST'])
    def update_auggie_user_tracking():
        # arg = [request.json]
        # response = server.transform(metrics.update_tracking, args=arg)
        # return Response(response=response, status=200, mimetype="application/json")
        ## From Method
        profile_name = 'augur'
        if os.environ.get('AUGUR_IS_PROD'):
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

    @server.app.route('/auggie/slack_login', methods=['POST'])
    def slack_login():
        # arg = [request.json]
        # response = server.transform(metrics.slack_login, args=arg)
        # return Response(response=response, status=200, mimetype="application/json")
        # From Method
        print("slack_login")

        r = requests.get(
            url=f'https://slack.com/api/oauth.v2.access?code={body["code"]}&client_id={os.environ["AUGGIE_CLIENT_ID"]}&client_secret={os.environ["AUGGIE_CLIENT_SECRET"]}&redirect_uri=http%3A%2F%2Flocalhost%3A8080')
        data = r.json()

        if (data["ok"]):
            print(data)
            token = data["authed_user"]["access_token"]
            team_id = data["team"]["id"]
            webclient = slack.WebClient(token=token)

            user_response = webclient.users_identity()
            print(user_response)
            email = user_response["user"]["email"]

            profile_name = 'augur'
            if os.environ.get('AUGUR_IS_PROD'):
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