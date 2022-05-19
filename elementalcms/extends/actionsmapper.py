import functools
import inspect
from flask import Flask


class ActionsMapper:

    __app: Flask

    def __init__(self, api: Flask):
        self.__app = api

    def register_actions(self, controllers) -> []:
        registered_views = []
        for controller in controllers:
            predicate = inspect.ismethod
            all_members = inspect.getmembers(controller, predicate=predicate)
            for fn_name, value in all_members:
                if 'is_action' in dir(value):
                    controller_name = type(controller).__name__
                    view = getattr(controller, fn_name)

                    def make_func(fn):
                        @functools.wraps(fn)
                        def inner(*args, **kwargs):
                            return fn(*args, **kwargs)

                        return inner

                    view = make_func(view)

                    endpoint = self.__build_endpoint(view, controller_name, fn_name)
                    self.__app.add_url_rule(view.route,
                                            endpoint,
                                            view,
                                            methods=[view.method])
                    registered_views.append(view)
        return registered_views

    @staticmethod
    def __build_endpoint(view, controller_name, fn_name):
        if view.endpoint is not None:
            return view.endpoint
        return f'{controller_name}.{fn_name}'
