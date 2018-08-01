"""Definition of all REST API endpoints of the license analysis module."""

from imp import reload

import flask
from flask import Flask, request
from flask_cors import CORS
from functools import lru_cache
import sys
import logging
from src.stack_license import StackLicenseAnalyzer
from src.auth import login_required, decode_token

try:
    from importlib import reload
except ImportError:
    from imp import reload


# Python2.x: Make default encoding as UTF-8
if sys.version_info.major == 2:
    reload(sys)
    sys.setdefaultencoding('UTF8')


# logging.basicConfig(filename='/tmp/error.log', level=logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app = Flask(__name__)
app.config.from_object('config')
CORS(app)


@app.before_first_request
@lru_cache(maxsize=32)
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

    return flask.jsonify(response)


if __name__ == "__main__":
    app.run()
