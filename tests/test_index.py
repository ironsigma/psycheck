import pytest

from sanic_testing import TestManager
from tests.mocks import MockDatabaseFactory
from ironsigma import app_factory


@pytest.fixture
def app():
    config = {}
    app = app_factory.create(config, MockDatabaseFactory)
    TestManager(app)
    return app


def test_api(app):
    req, res = app.test_client.get("/")

    assert res.status == 200
    assert b'<div id="app"></div>' in res.body
