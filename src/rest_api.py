from imp import reload

import flask
from flask import Flask, request
from flask_cors import CORS
import sys
import logging
from stack_license import StackLicenseAnalyzer


# Python2.x: Make default encoding as UTF-8
if sys.version_info.major == 2:
    reload(sys)
    sys.setdefaultencoding('UTF8')


# logging.basicConfig(filename='/tmp/error.log', level=logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app = Flask(__name__)
app.config.from_object('config')
CORS(app)

global stack_license_analyzer


@app.before_first_request
def load_model():
    app.stack_license_analyzer = StackLicenseAnalyzer()


@app.route('/')
def heart_beat():
    return flask.jsonify({"status": "ok"})


@app.route('/api/v1/stack_license', methods=['POST'])
def stack_license():
    input_json = request.get_json(force=True)
    # app.logger.debug("Stack analysis input: {}".format(input_json))

    response = app.stack_license_analyzer.compute_stack_license(payload=input_json)
    # app.logger.debug("Stack analysis output: {}".format(response))

    return flask.jsonify(response)


if __name__ == "__main__":
    app.run()
