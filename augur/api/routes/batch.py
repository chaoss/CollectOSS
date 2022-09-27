#SPDX-License-Identifier: MIT
"""
Creates routes for the manager
"""

import logging
import time
import requests
import sqlalchemy as s
from sqlalchemy import exc
from flask import request, Response
from augur.api.util import metric_metadata
import json

AUGUR_API_VERSION = 'api/unstable'

logger = logging.getLogger(__name__)

def create_routes(server):

        @server.app.route('/{}/batch'.format(AUGUR_API_VERSION), methods=['GET', 'POST'])
        def batch():
            """
            Execute multiple requests, submitted as a batch.
            :statuscode 207: Multi status
            """

            if request.method == 'GET':
                """this will return sensible defaults in the future"""
                return app.make_response('{"status": "501", "response": "Defaults for batch requests not implemented. Please POST a JSON array of requests to this endpoint for now."}')

            try:
                requests = json.loads(request.data.decode('utf-8'))
            except ValueError as e:
                request.abort(400)

            responses = []

            for index, req in enumerate(requests):


                method = req['method']
                path = req['path']
                body = req.get('body', None)

                try:

                    logger.debug('batch-internal-loop: %s %s' % (method, path))

                    with app.server.app.context():
                        with app.test_request_context(path,
                                                      method=method,
                                                      data=body):
                            try:
                                # Can modify flask.g here without affecting
                                # flask.g of the root request for the batch

                                # Pre process Request
                                rv = app.preprocess_request()

                                if rv is None:
                                    # Main Dispatch
                                    rv = app.dispatch_request()

                            except Exception as e:
                                rv = app.handle_user_exception(e)

                            response = app.make_response(rv)

                            # Post process Request
                            response = app.process_response(response)

                    # Response is a Flask response object.
                    # _read_response(response) reads response.response
                    # and returns a string. If your endpoints return JSON object,
                    # this string would be the response as a JSON string.
                    responses.append({
                        "path": path,
                        "status": response.status_code,
                        "response": str(response.get_data(), 'utf8'),
                    })

                except Exception as e:

                    responses.append({
                        "path": path,
                        "status": 500,
                        "response": str(e)
                    })


            return Response(response=json.dumps(responses),
                            status=207,
                            mimetype="application/json")


        """
        @api {post} /batch Batch Request Metadata
        @apiName BatchMetadata
        @apiGroup Batch
        @apiDescription Returns metadata of batch requests
        POST JSON of API requests metadata
        """
        @server.app.route('/{}/batch/metadata'.format(AUGUR_API_VERSION), methods=['GET', 'POST'])
        def batch_metadata():
            """
            Returns endpoint metadata in batch format
            """

            if request.method == 'GET':
                """this will return sensible defaults in the future"""
                return app.make_response(json.dumps(metric_metadata))

            try:
                requests = json.loads(request.data.decode('utf-8'))
            except ValueError as e:
                request.abort(400)

            responses = []

            for index, req in enumerate(requests):
                method = req['method']
                path = req['path']
                body = req.get('body', None)

                try:
                    logger.info('batch endpoint: ' + path)
                    with app.server.app.context():
                        with app.test_request_context(path,
                                                      method=method,
                                                      data=body):
                            try:
                                rv = app.preprocess_request()
                                if rv is None:
                                    rv = app.dispatch_request()
                            except Exception as e:
                                rv = app.handle_user_exception(e)
                            response = app.make_response(rv)
                            response = app.process_response(response)

                    responses.append({
                        "path": path,
                        "status": response.status_code,
                        "response": str(response.get_data(), 'utf8'),
                    })

                except Exception as e:
                    responses.append({
                        "path": path,
                        "status": 500,
                        "response": str(e)
                    })

            return Response(response=json.dumps(responses),
                            status=207,
                            mimetype="application/json")

