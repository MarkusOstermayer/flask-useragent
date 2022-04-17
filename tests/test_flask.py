def test_user_agent_route(app, client):

    @app.ua_route("/", user_agent="user-agent-1")
    def index_user_agent_1():
        return "index_user_agent_1"

    @app.ua_route("/", user_agent=r"user-agent-[0-9]")
    def index_user_agent_0_9():
        return "index_user_agent_0-9"

    @app.fallback("/")
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


def test_invalid_route(app, client):

    @app.ua_route("/", user_agent="user-agent-1")
    def index_user_agent_1():
        return "index_user_agent_1"

    # this should return a 404, since the endpoint does exist
    # but the user-agent does not match and no fallback is
    # configured
    rv = client.get("/", headers={"User-Agent": "user-agent-2"})
    assert rv.status_code == 404
    assert rv.status == "404 NOT FOUND"


def test_mixed_decorator(app, client):

    @app.route("/index")
    @app.ua_route("/", user_agent="user-agent-1")
    def index_user_agent_1():
        return "index_user_agent_1"

    # this should work, since the useragent is a exact match
    rv = client.get("/", headers={"User-Agent": "user-agent-1"})
    assert rv.data == b"index_user_agent_1"

    rv = client.get("/index", headers={"User-Agent": "another-user-agent"})
    assert rv.data == b"index_user_agent_1"


def test_ua_decorator_without_argument(app, client):

    # this should use the route just like the fallback decorator does
    @app.ua_route("/")
    def index_user_agent_1():
        return "index_user_agent_1"

    rv = client.get("/")
    assert rv.data == b"index_user_agent_1"
