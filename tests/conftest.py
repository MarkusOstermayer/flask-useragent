import os

import pytest

import flask_useragent


# From: https://github.com/pallets/flask/blob/main/tests/conftest.py#L52
@pytest.fixture
def app():
    app = flask_useragent.Flask(
        "flask_test",
        root_path=os.path.dirname(__file__)
    )

    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
