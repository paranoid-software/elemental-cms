import secrets
from functools import wraps
from http import HTTPStatus

from flask import Blueprint, session, request, Response

identity = Blueprint('identity', __name__)


@identity.app_context_processor
def gateway_token_processor():
    if 'gatewayToken' not in session:
        session['gatewayToken'] = secrets.token_hex(nbytes=16)
    return dict(gateway_token=session.get('gatewayToken'))


def gateway_token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        session_gateway_token = session.get('gatewayToken', None)
        if session_gateway_token is None:
            return Response(status=HTTPStatus.UNAUTHORIZED)
        gateway_token = request.headers.get('X-Gateway-Token', None)
        if gateway_token is None:
            return Response(status=HTTPStatus.UNAUTHORIZED)
        if gateway_token != session_gateway_token:
            return Response(status=HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)
    return wrapper


@identity.route('/identity/', methods=['POST'])
@gateway_token_required
def set_user_identity():
    if not request.data:
        return Response(status=HTTPStatus.BAD_REQUEST)
    session['userIdentity'] = request.json
    return {}, HTTPStatus.CREATED


@identity.route('/identity/', methods=['DELETE'])
@gateway_token_required
def remove_user_identity():
    if 'userIdentity' in session:
        session.pop('userIdentity')
    return {}, HTTPStatus.OK
