"""Utility function to fetch public key."""
import flask


def http_error(err_msg):
    """Return http error message."""
    return flask.jsonify(dict(error=err_msg))
