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
