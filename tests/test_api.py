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


def test_transactions(app):
    first_of_the_month = datetime.datetime.now().replace(day=1).date()

    app.ctx.sql_cur_results = {
        'FROM statement': [
            [first_of_the_month, 3500],
        ],
        'FROM register': [
            [2, 'D', first_of_the_month, 'ACME Co.', 'Salary', 1500, None, None, None, None],
            [1, 'C', first_of_the_month, 'Bank One', 'Morgage', 2300.12, 'home', 'red', None, None],
        ]
    }

    _, res = app.test_client.get("/api/transactions")

    json_res = json.loads(res.body)

    assert res.status == 200

    tx = json_res[0]
    assert tx['type'] == 'balance'
    assert tx['amount'] == { 'fixed': 350000, 'scale': 2, 'currency': 'USD' }
    assert tx['balance'] == { 'fixed': 350000, 'scale': 2, 'currency': 'USD' }

    tx = json_res[1]
    assert tx['type'] == 'debit'
    assert tx['payee'] == 'ACME Co.'
    assert tx['amount'] == { 'fixed': 150000, 'scale': 2, 'currency': 'USD' }
    assert tx['balance'] == { 'fixed': 500000, 'scale': 2, 'currency': 'USD' }

    tx = json_res[2]
    assert tx['type'] == 'credit'
    assert tx['payee'] == 'Bank One'
    assert tx['amount'] == { 'fixed': 230012, 'scale': 2, 'currency': 'USD' }
    assert tx['balance'] == { 'fixed': 269988, 'scale': 2, 'currency': 'USD' }


def test_scheduled(app):
    today = datetime.datetime.now().date()

    app.ctx.sql_cur_results = {
        'FROM register': [
            [2, today]
        ],
        'FROM recurring': [
            [1, 'C', 'Mr. Smith', 'Rent', 1200, 'RRULE:FREQ=MONTHLY', today, 'home', 'red'],
            [2, 'C', 'eCafee', None, 550, 'RRULE:FREQ=MONTHLY', today, None, None],
        ]
    }

    _, res = app.test_client.get("/api/scheduled")

    assert res.status == 200

    json_res = json.loads(res.body)
    assert json_res['start_date'] == datetime.date.today().isoformat()

    assert len(json_res['transactions']) == 5

    tx = json_res['transactions'][0]
    assert tx['type'] == 'credit'
    assert tx['date'] == json_res['start_date']
    assert tx['payee'] == 'Mr. Smith'
    assert tx['memo'] == 'Rent'
    assert tx['amount'] == { 'fixed': 120000, 'scale': 2, 'currency': 'USD'}
    assert tx['icon'] == 'home'
    assert tx['color'] == 'red'
    assert tx['recur_id'] == 1
