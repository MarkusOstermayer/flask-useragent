from typing import Any
from typing import Callable
from typing import TypeVar

import flask

from .helper import EndpointContainer

F = TypeVar("F", bound=Callable[..., Any])


class FlaskUserAgent():
    def __init__(self, app: flask.app.Flask):
        self.app = app
        self.endpoint_rules: EndpointContainer = EndpointContainer()

    # from: https://github.com/pallets/flask/blob/main/src/flask/scaffold.py
    def ua_route(self, rule: str, **options: Any) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            if "user_agent" not in options:
                # This will use the route as if it was a fallback route
                user_agent = None
            else:
                user_agent = options["user_agent"]
                options.pop("user_agent", None)

            endpoint = options.pop("endpoint", None)

            self.endpoint_rules.add_function(rule, user_agent, func)

            self.app.add_url_rule(rule, endpoint, self.routehelper, **options)

            return func

        return decorator

    def fallback(self, rule: str, **options) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            endpoint = options.pop("endpoint", None)

            self.endpoint_rules.add_fallback(rule, func)
            self.app.add_url_rule(rule, endpoint, self.routehelper, **options)
            return func

        return decorator

    def routehelper(self):
        request_uri = flask.request.path
        user_agent = flask.request.headers.get("User-Agent")

        func = self.endpoint_rules.get_function(request_uri, user_agent)

        if not func:
            flask.abort(404)

        return func()
