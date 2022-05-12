import ctypes
import json
import os
from functools import wraps
from http import HTTPStatus

from flask import current_app, Response, session, request


def gateway_token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        gateway_token = request.headers.get('X-Gateway-Token', None)
        if gateway_token is None:
            return Response(status=HTTPStatus.UNAUTHORIZED)
        if current_app.config['USER_IDENTITY_SESSION_KEY'] not in session:
            return Response(status=HTTPStatus.UNAUTHORIZED)
        payload = json.dumps(session[current_app.config['USER_IDENTITY_SESSION_KEY']])
        if gateway_token != ctypes.c_uint64(hash(payload)).value.to_bytes(8, "big").hex():
            return Response(status=HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)
    return wrapper


def get(route: str, **kwargs):
    def wrapper(function):
        function.is_action = True
        function.route = route
        function.method = 'GET'
        function.endpoint = None

        if 'endpoint' in kwargs.keys():
            function.endpoint = kwargs['endpoint']
        return function

    return wrapper


def post(route: str, **kwargs):
    def wrapper(function):
        function.is_action = True
        function.route = route
        function.method = 'POST'
        function.endpoint = None

        if 'endpoint' in kwargs.keys():
            function.endpoint = kwargs['endpoint']

        return function

    return wrapper


def put(route: str, **kwargs):
    def wrapper(function):
        function.is_action = True
        function.route = route
        function.method = 'PUT'
        function.endpoint = None

        if 'endpoint' in kwargs.keys():
            function.endpoint = kwargs['endpoint']

        return function

    return wrapper


def patch(route: str, **kwargs):
    def wrapper(function):
        function.is_action = True
        function.route = route
        function.method = 'PATCH'
        function.endpoint = None

        if 'endpoint' in kwargs.keys():
            function.endpoint = kwargs['endpoint']

        return function

    return wrapper


def delete(route: str, **kwargs):
    def wrapper(function):
        function.is_action = True
        function.route = route
        function.method = 'DELETE'
        function.endpoint = None

        if 'endpoint' in kwargs.keys():
            function.endpoint = kwargs['endpoint']

        return function

    return wrapper
