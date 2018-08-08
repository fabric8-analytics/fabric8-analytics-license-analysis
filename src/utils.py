"""Utility function to fetch public key."""
from requests import get, exceptions
import flask


def fetch_public_key(app):
    """Get public key and caches it on the app object for future use."""
    if not getattr(app, 'public_key', ''):
        keycloak_url = app.config.get(
                'BAYESIAN_FETCH_PUBLIC_KEY', '')
        if keycloak_url:
            pub_key_url = keycloak_url.strip('/') + '/auth/realms/fabric8/'
            try:
                result = get(pub_key_url, timeout=10)
                app.logger.info('Fetching public key from %s, status %d, result: %s',
                                pub_key_url, result.status_code, result.text)
            except exceptions.Timeout:
                app.logger.error(
                    'Timeout fetching public key from %s', pub_key_url)
                return ''
            if result.status_code != 200:
                return ''
            pkey = result.json().get('public_key', '')
            app.public_key = \
                '-----BEGIN PUBLIC KEY-----\n{pkey}\n-----END PUBLIC KEY-----'.format(
                    pkey=pkey)
        else:
            app.public_key = app.config.get('BAYESIAN_PUBLIC_KEY')

    return app.public_key


def http_error(err_msg):
    """Return http error message."""
    return flask.jsonify(dict(error=err_msg))
