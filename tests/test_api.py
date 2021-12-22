import pytest
import datetime
import json

from sanic_testing import TestManager
from ironsigma import app_factory

from tests.mocks import MockDatabaseFactory, MockCursor


@pytest.fixture
def app():
    config = {}
    app = app_factory.create(config, MockDatabaseFactory)
    TestManager(app)
    return app


def test_api(app):
    now = datetime.datetime.now()

    app.ctx.sql_cur_results = [[1, 'home', 'red', 'Mr. Smith', 'Rent', -1200,
        'RRULE:FREQ=MONTHLY', now]]

    req, res = app.test_client.get("/api/transactions")

    assert res.status == 200

    json_res = json.loads(res.body)
    assert json_res['start_date'] == datetime.date.today().isoformat()

    tx = json_res['transactions'][0]
    assert tx['recur_id'] == 1
    assert tx['icon'] == 'home'
    assert tx['color'] == 'red'
    assert tx['payee'] == 'Mr. Smith'
    assert tx['memo'] == 'Rent'
    assert tx['amount'] == { 'fixed': -120000, 'scale': 2, 'currency': 'USD'}
    assert tx['date'] == json_res['start_date']
