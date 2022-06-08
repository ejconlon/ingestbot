"""
An AWS Lambda handler that processes API Gateway requests with the singleton
Flask app. Do not import this in other code unless you want that app constructed!

Your handler module/function should be `ingestbot.handler.handler`
"""

from ingestbot.main import build_app_from_args

import awsgi


APP = build_app_from_args()


def handler(event, context):
    return awsgi.response(APP, event, context)
