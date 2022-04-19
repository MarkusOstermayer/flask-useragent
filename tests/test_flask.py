import pytest


def test_user_agent_route(ua_app, client):

    @ua_app.ua_route("/", user_agent="user-agent-1")
    def index_user_agent_1():
        return "index_user_agent_1"

    @ua_app.ua_route("/", user_agent=r"user-agent-[0-9]")
    def index_user_agent_0_9():
        return "index_user_agent_0-9"

    @ua_app.fallback("/")
    def index_fallback():
        return "index_fallback"

    # this should work, since the useragent is a exact match
    rv = client.get("/", headers={"User-Agent": "user-agent-1"})
    assert rv.data == b"index_user_agent_1"

    # this should use the regex-route
    rv = client.get("/", headers={"User-Agent": "user-agent-2"})
    assert rv.data == b"index_user_agent_0-9"

    # should use the fallback, since the useragent does not match
    rv = client.get("/", headers={"User-Agent": "other-user-agent"})
    assert rv.data == b"index_fallback"


def test_invalid_route(ua_app, client):

    @ua_app.ua_route("/", user_agent="user-agent-1")
    def index_user_agent_1():
        return "index_user_agent_1"

    # this should return a 404, since the endpoint does exist
    # but the user-agent does not match and no fallback is
    # configured
    rv = client.get("/", headers={"User-Agent": "user-agent-2"})
    assert rv.status_code == 404
    assert rv.status == "404 NOT FOUND"


def test_mixed_decorator(app, ua_app, client):

    @app.route("/index")
    @ua_app.ua_route("/", user_agent="user-agent-1")
    def index_user_agent_1():
        return "index_user_agent_1"

    # this should work, since the useragent is a exact match
    rv = client.get("/", headers={"User-Agent": "user-agent-1"})
    assert rv.data == b"index_user_agent_1"

    rv = client.get("/index", headers={"User-Agent": "another-user-agent"})
    assert rv.data == b"index_user_agent_1"


def test_ua_decorator_without_argument(app, ua_app, client):

    # this should use the route just like the fallback decorator does
    @ua_app.ua_route("/")
    def index_user_agent_1():
        return "index_user_agent_1"

    rv = client.get("/")
    assert rv.data == b"index_user_agent_1"


@pytest.mark.parametrize(
    "rule,url,expected_args",
    [
        # trivial case
        ("/", "/", {}),
        # should default to using a string
        ("/<username>", "/user1", {"username": "user1"}),
        ("/<username>", "/123123", {"username": "123123"}),
        # explicit use string
        ("/<string:username>", "/user1", {"username": "user1"}),
        ("/<string:username>", "/123123", {"username": "123123"}),
        # test with numbers
        ("/<int:number>", "/404", {"number": 404}),
        # use multiple arguments
        ("/<user>/<int:age>", "/user/404", {"user": "user", "age": 404}),
        (
            "/<user>/<int:age>/test",
            "/user/404/test",
            {"user": "user", "age": 404}),
        # test float
        (
            "/<float:num1>/add/<float:num2>",
            "/1.23/add/2.34",
            {"num1": 1.23, "num2": 2.34}
        ),
        # Test paths
        (
            "/<path:path1>/other/rule",
            "/this/is/a/test/other/rule",
            {"path1": "this/is/a/test"}
        ),
        (
            "/<path:path1>/other/rule/<path:path2>",
            "/this/is/a/test/other/rule/test",
            {"path1": "this/is/a/test", "path2": "test"}
        )
    ]
)
def test_ua_decorator_with_arguments(ua_app, client, rule, url, expected_args):
    @ua_app.ua_route(rule)
    def index_user_agent_1(*args, **kwargs):
        for key in kwargs:
            assert key in expected_args
            assert kwargs[key] == expected_args[key]
        return "index_user_agent_1"

    rv = client.get(url)
    assert rv.data == b"index_user_agent_1"
    
