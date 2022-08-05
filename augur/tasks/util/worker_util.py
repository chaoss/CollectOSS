#SPDX-License-Identifier: MIT
import os, json, requests, logging
from flask import Flask, Response, jsonify, request
#import gunicorn.app.base
import numpy as np
from celery import group
from augur.application.logs import AugurLogger
from augur.tasks.util.task_session import TaskSession

def create_grouped_task_load(*args,processes=6,dataList=[],task=None):
    
    if not dataList or not task:
        raise AssertionError
    
    numpyData = np.array(list(dataList))
    listsSplitForProcesses = np.array_split(numpyData, processes)

    task_list = [task.s(data.tolist(), *args) for data in listsSplitForProcesses]

    jobs = group(task_list)

    return jobs



# def create_server(app, worker=None):
#     """ Consists of AUGWOP endpoints for the broker to communicate to this worker
#     Can post a new task to be added to the workers queue
#     Can retrieve current status of the worker
#     Can retrieve the workers config object
#     """

#     server.app.route("/AUGWOP/task", methods=['POST', 'GET'])
#     def augwop_task():
#         """ AUGWOP endpoint that gets hit to add a task to the workers queue or is used to get the heartbeat/status of worker
#         """
#         if request.method == 'POST': #will post a task to be added to the queue
#             app.worker.logger.info("Sending to work on task: {}".format(str(request.json)))
#             app.worker.task = request.json
#             return Response(response=request.json,
#                         status=200,
#                         mimetype="application/json")
#         if request.method == 'GET': #will retrieve the current tasks/status of the worker
#             return jsonify({
#                 "status": "ALIVE",
#                 "results_counter": app.worker.results_counter,
#                 "task": app.worker.task,
#             })
#         return Response(response=request.json,
#                         status=200,
#                         mimetype="application/json")

#     server.app.route("/AUGWOP/heartbeat", methods=['GET'])
#     def heartbeat():
#         if request.method == 'GET':
#             return jsonify({
#                 "status": "alive"
#             })

#     server.app.route("/AUGWOP/config")
#     def augwop_config():
#         """ Retrieve worker's config
#         """
#         return app.worker.config

# class WorkerGunicornApplication(gunicorn.app.base.BaseApplication):

#     def __init__(self, app):
#         self.options = {
#             'bind': '%s:%s' % (app.worker.config["host"], app.worker.config["port"]),
#             'workers': 1,
#             'errorlog': app.worker.config['server_logfile'],
#             'accesslog': app.worker.config['server_logfile'],
#             'loglevel': app.worker.config['log_level'],
#             'capture_output': app.worker.config['capture_output']
#         }

#         self.application = app
#         super().__init__()

#     def load_config(self):
#         config = {key: value for key, value in self.options.items()
#                   if key in self.cfg.settings and value is not None}
#         for key, value in config.items():
#             self.cfg.set(key.lower(), value)

#     def load(self):
#         return self.application
