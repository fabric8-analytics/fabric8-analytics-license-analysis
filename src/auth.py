"""Authorization token handling."""

from flask import current_app, request, g
from flask_security import UserMixin
import jwt
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm
from os import getenv
from src.exceptions import HTTPError
from src.utils import fetch_public_key

jwt.register_algorithm('RS256', RSAAlgorithm(RSAAlgorithm.SHA256))


def decode_token():
    token = request.headers.get('Authorization')
    if token is None:
        return {}

    if token.startswith('Bearer '):
        _, token = token.split(' ', 1)

    pub_key = fetch_public_key(current_app)
    audiences = current_app.config.get('BAYESIAN_JWT_AUDIENCE').split(',')
    for aud in audiences:
        try:
            decoded_token = jwt.decode(token, pub_key, audience=aud)
        except jwt.InvalidTokenError:
            current_app.logger.error(
                'Auth Token could not be decoded for audience {}'.format(aud))
            decoded_token = None

        if decoded_token is not None:
            break

    if decoded_token is None:
        raise jwt.InvalidTokenError('Auth token audience cannot be verified.')

    return decoded_token


def login_required(view):
    def wrapper(*args, **kwargs):
        # Disable authentication for local setup
        if getenv('DISABLE_AUTHENTICATION') in ('1', 'True', 'true'):
            return view(*args, **kwargs)

        lgr = current_app.logger
        user = None

        try:
            decoded = decode_token()
            if not decoded:
                lgr.exception(
                    'Provide an Authorization token with the API request')
                raise HTTPError(401, 'Authentication failed - token missing')

            lgr.info('Successfuly authenticated user {e} using JWT'.
                     format(e=decoded.get('email')))
        except jwt.ExpiredSignatureError as exc:
            lgr.exception('Expired JWT token')
            decoded = {'email': 'unauthenticated@jwt.failed'}
            raise HTTPError(401, 'Authentication failed - token has expired') from exc
        except Exception as exc:
            lgr.exception('Failed decoding JWT token')
            decoded = {'email': 'unauthenticated@jwt.failed'}
            raise HTTPError(401, 'Authentication failed - could not decode JWT token') from exc
        else:
            user = APIUser(decoded.get('email', 'nobody@nowhere.nodomain'))

        if user:
            g.current_user = user
        else:
            g.current_user = APIUser('unauthenticated@no.auth.token')
            raise HTTPError(401, 'Authentication required')
        return view(*args, **kwargs)
    return wrapper


class APIUser(UserMixin):
    """Structure representing user accessing the API."""

    def __init__(self, email):
        """Construct the instance of APIUsed class and initialize the 'email' attribute."""
        self.email = email
