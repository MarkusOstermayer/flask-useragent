import os

import pytest
import flask
import flask_useragent


# From: https://github.com/pallets/flask/blob/main/tests/conftest.py#L52
@pytest.fixture
def app():
    app = flask.Flask(
        "flask_test",
        root_path=os.path.dirname(__file__)
    )

    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture
def ua_app(app):
    ua_app = flask_useragent.FlaskUserAgent(app)

    yield ua_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
