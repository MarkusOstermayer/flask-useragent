import pytest

import flask_useragent
from flask_useragent import EndpointContainer
from flask_useragent import UserAgentEndpoints
from flask_useragent import UserAgentEndpointException


@pytest.fixture
def dummy_func():
    def func():
        pass

    return func


@pytest.fixture
def dummy_func_2():
    def func():
        pass

    return func


def test_fallback_function_with_none(dummy_func, dummy_func_2):
    ua_endpoint = UserAgentEndpoints(None, dummy_func)
    assert ua_endpoint.get_fallback() == dummy_func

    ua_endpoint_2 = UserAgentEndpoints("user-agent-1", dummy_func)
    ua_endpoint_2.add_user_agent_endpoint(None, dummy_func_2)

    assert ua_endpoint_2.get_fallback() == dummy_func_2
    assert ua_endpoint_2.get_function("user-agent-1") == dummy_func


def test_fallback_function_with_star(dummy_func):
    ua_endpoint = UserAgentEndpoints("*", dummy_func)

    assert ua_endpoint.get_fallback() == dummy_func


def test_fallback_function_overwrite(dummy_func, dummy_func_2):
    ua_endpoint = UserAgentEndpoints(None, dummy_func)

    ua_endpoint.add_fallback(dummy_func_2)

    assert ua_endpoint.get_fallback() == dummy_func_2


def test_fallback_with_legit_function(dummy_func, dummy_func_2):
    ua_endpoint = UserAgentEndpoints("user-agent-1", dummy_func)
    ua_endpoint.add_fallback(dummy_func_2)

    assert ua_endpoint.get_function("user-agent-1") == dummy_func
    # should return the fallback function because of a false useragent
    assert ua_endpoint.get_function("wrong_useragent") == dummy_func_2
    # gets the fallback function
    assert ua_endpoint.get_fallback() == dummy_func_2


def test_regex(dummy_func, dummy_func_2):
    def dummy_func_3():
        pass

    ua_endpoint = UserAgentEndpoints("user-agent-2", dummy_func_2)
    ua_endpoint.add_user_agent_endpoint("user-agent-[0-9]$", dummy_func)
    ua_endpoint.add_fallback(dummy_func_3)

    # this should return the first function added
    assert ua_endpoint.get_function("user-agent-1") == dummy_func
    # this should return the second one because of an exact match
    assert ua_endpoint.get_function("user-agent-2") == dummy_func_2

    # this should return dummy_func, because the regex matches
    assert ua_endpoint.get_function("user-agent-3") == dummy_func

    # because the regex does not match anymore, the fallback should be returned
    assert ua_endpoint.get_function("user-agent-33") == dummy_func_3


def test_add_same_ua_multiple_times(dummy_func, dummy_func_2):
    ua_endpoint = UserAgentEndpoints("user-agent-1", dummy_func)
    with pytest.raises(UserAgentEndpointException):
        ua_endpoint.add_user_agent_endpoint("user-agent-1", dummy_func_2)


def test_get_invalid_user_agent():
    ua_endpoint = UserAgentEndpoints("user-agent-1", dummy_func)
    ua_endpoint = UserAgentEndpoints("user-agent-1", dummy_func)
    # should return None, since no fallback is configured
    assert ua_endpoint.get_function("invalid-user-agent") is None


def test_function_adding(dummy_func, dummy_func_2):
    endpoint_container = EndpointContainer()

    endpoint_container.add_function("/", "user-agent-1", dummy_func)
    endpoint_container.add_function("/", "user-agent-2", dummy_func_2)
    assert endpoint_container.get_function("/", "user-agent-1") == dummy_func
    assert endpoint_container.get_function("/", "user-agent-2") == dummy_func_2


def test_fallback_adding(dummy_func, dummy_func_2):
    endpoint_container = EndpointContainer()

    # check if the fallback gets set correctly if no other function exists
    endpoint_container.add_fallback("/", dummy_func)
    assert endpoint_container.get_fallback("/") == dummy_func

    # test if an invalid rule returns None
    assert endpoint_container.get_fallback("/invalid-rule") is None

    endpoint_container_2 = EndpointContainer()
    endpoint_container_2.add_function("/", "user-agent-1", dummy_func)
    endpoint_container_2.add_fallback("/", dummy_func_2)

    assert endpoint_container_2.get_fallback("/") != dummy_func
    assert endpoint_container_2.get_fallback("/") == dummy_func_2


@pytest.mark.parametrize(
    "rule,expected_regex",
    [
        ("/", "/"),
        ("/<variable>", "/([a-zA-Z0-9]+)"),
        ("/<string:variable>", "/([a-zA-Z0-9]+)"),
        ("/<int:variable>", "/([0-9]+)"),
        ("/<float:variable>", "/([0-9]+.[0-9]+)"),
        (
            "/<uuid:variable>",
            "/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
        ),
        ("/<path:variable>", "/([a-zA-Z0-9/]+)")
    ]
)
def test_rule_to_regex(rule, expected_regex):
    assert flask_useragent.helper.rule_to_regex(rule) == expected_regex
