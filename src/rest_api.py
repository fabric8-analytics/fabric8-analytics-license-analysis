"""Definition of all REST API endpoints of the license analysis module."""

import flask
from flask import Flask, request
from flask_cors import CORS
import sys
import logging
from src.stack_license import StackLicenseAnalyzer
from fabric8a_auth.auth import login_required
from fabric8a_auth.errors import AuthError
from flask.json import jsonify
from raven.contrib.flask import Sentry
import os


# logging.basicConfig(filename='/tmp/error.log', level=logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app = Flask(__name__)
app.config.from_object('config')
CORS(app)
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
sentry = Sentry(app, dsn=SENTRY_DSN, logging=True, level=logging.ERROR)
app.logger.info('App initialized, ready to roll...')


@app.before_first_request
def load_model():
    """Initialize the stack license analyzer before the first request."""
    app.stack_license_analyzer = StackLicenseAnalyzer()


@app.route('/')
def heart_beat():
    """Handle the REST API endpoint /."""
    return flask.jsonify({"status": "ok"})


@app.route('/api/v1/stack_license', methods=['POST'])
def stack_license():
    """Handle the REST API endpoint /api/v1/stack_license."""
    input_json = request.get_json(force=True)
    # app.logger.debug("Stack analysis input: {}".format(input_json))

    response = app.stack_license_analyzer.compute_stack_license(payload=input_json)
    # app.logger.debug("Stack analysis output: {}".format(response))

    return flask.jsonify(response)


@app.route('/api/v1/license-recommender', methods=['POST'])
@login_required
def stack_license_api():
    """Handle the REST API endpoint /api/v1/license-recommender."""
    input_json = request.get_json(force=True)
    # app.logger.debug("Stack analysis input: {}".format(input_json))

    response = app.stack_license_analyzer.license_recommender(input=input_json)
    # app.logger.debug("Stack analysis output: {}".format(response))
    return response


@app.errorhandler(AuthError)
def api_401_handler(err):
    """Handle AuthError exceptions."""
    return jsonify(error=err.error), err.status_code


def log_it(func):
    """Func decorator for logging."""
    def inner1(*args, **kwargs):
        app.logger.info("Executed {}".format(func.__name__))
        return func(*args, **kwargs)
    return inner1


if __name__ == "__main__":
    app.run()
