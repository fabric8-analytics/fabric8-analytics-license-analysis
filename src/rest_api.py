"""Definition of all REST API endpoints of the license analysis module."""

from imp import reload

import flask
from flask import Flask, request
from flask_cors import CORS
import sys
import logging
from src.stack_license import StackLicenseAnalyzer
import json
import os


# Python2.x: Make default encoding as UTF-8
if sys.version_info.major == 2:
    reload(sys)
    sys.setdefaultencoding('UTF8')


# logging.basicConfig(filename='/tmp/error.log', level=logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app = Flask(__name__)
app.config.from_object('config')
CORS(app)
licenselist = json.load(open(os.path.abspath('src/license_synonyms.json')))


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
    input_json = json.loads(request.values.get('packages'))
    app.logger.debug("Stack analysis input: {}".format(input_json))
    if request.files:
        license = request.files['LICENSE']
        if license is not None:
            for line in license.readlines():
                for lic in licenselist:
                    if line.decode("utf-8").strip() == lic:
                        matchedLicense = lic
                        break
        input_json["matchedlicense"] = matchedLicense
    app.logger.debug("Stack analysis input: {}".format(input_json))
    response = app.stack_license_analyzer.compute_stack_license(payload=input_json)
    # app.logger.debug("Stack analysis output: {}".format(response))
    return flask.jsonify(response)


if __name__ == "__main__":
    app.run()
