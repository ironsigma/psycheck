import pytest

from sanic_testing import TestManager
from tests.mocks import DatabaseFactory
from ironsigma import app_factory


@pytest.fixture
def app():
    config = {}
    app = app_factory.create(config, DatabaseFactory)
    TestManager(app)
    return app


def test_api(app):
    req, res = app.test_client.get("/")

    assert res.status == 200
    assert b'<h1>Checkbook</h1>' in res.body
