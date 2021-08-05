import pytest
import json

from sanic_testing import TestManager
from ironsigma import app_factory

from tests.mocks import DatabaseFactory


@pytest.fixture
def app():
    config = {}
    app = app_factory.create(config, DatabaseFactory)
    TestManager(app)
    return app


def test_api(app):
    req, res = app.test_client.get("/api")

    assert res.status == 200

    json_res = json.loads(res.body)
    assert json_res['status'] == 'OK'
