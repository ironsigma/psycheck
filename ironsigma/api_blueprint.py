from sanic import Blueprint
from sanic import Sanic, response
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrulestr


bp = Blueprint("api")

txn_type_codes = {
    'B': 'balance',
    'D': 'debit',
    'd': 'debit-adjustment',
    'C': 'credit',
    'c': 'credit-adjustment'
}


def formatDate(date):
    if date is None:
        return None
    return date.isoformat()


def toAssetValue(type, amount):
    if type in ('C', 'c'):
        return amount * -1
    return amount


def toCurrency(amount):
    return {
        "fixed": int(amount * 100),
        "scale": 2,
        "currency": "USD"
    }


def fetch_scheduled_transactions():
    cols = ['recur_id', 'type_code', 'payee', 'memo', 'amount', 'rrule', 'start_dt', 'icon', 'color']

    cur = Sanic.get_app().ctx.db.cursor()
    cur.execute("SELECT " + ",".join(cols) + " FROM recurring")

    for row in cur:
        yield dict(zip(cols, row))


def fetch_transactions():
    first_day_curr_month_sql = 'subdate(curdate(), (day(curdate()) - 1))'
    cols = ['reg_id', 'type_code', 'date', 'payee', 'memo', 'amount', 'icon', 'color', 'recur_date', 'recur_id']

    # get previous balance
    cur = Sanic.get_app().ctx.db.cursor()
    cur.execute(
        "SELECT " + first_day_curr_month_sql + ", ifNull(balance, 0)" +
        " FROM statement" +
        " WHERE date = " + first_day_curr_month_sql)


    # yield previous balance
    (date, balance) = cur.fetchone()
    txn = dict(zip(cols, [0, 'B', date, 'Previous Balance', None, balance, None, None, None, None]))
    txn['balance'] = balance
    yield txn


    # fetch transactions
    cur = Sanic.get_app().ctx.db.cursor()
    cur.execute(
        "SELECT " + ",".join(cols) + " FROM register" +
        " WHERE date >= " + first_day_curr_month_sql +
        " ORDER BY date ASC, amount DESC")


    # yield transactions
    for row in cur:
        txn = dict(zip(cols, row))
        balance += toAssetValue(txn['type_code'], txn['amount'])
        txn['balance'] = balance
        yield txn


@bp.get("/transactions")
async def transactions(req: Request) -> HTTPResponse:
    txns = []
    for row in fetch_transactions():
        txns.append({
            "id": row['reg_id'],
            "type": txn_type_codes[row['type_code']],
            "date": formatDate(row['date']),
            "payee": row['payee'],
            "memo": row['memo'],
            "amount": toCurrency(row['amount']),
            "balance": toCurrency(row['balance']),
            "icon": row['icon'],
            "color": row['color'],
            "scheduled": formatDate(row['recur_date']),
            "recur_id": row['recur_id'],
        })

    return response.json(txns)


@bp.get("/scheduled")
async def scheduled(req: Request) -> HTTPResponse:
    # compute begining of today and end date
    today = datetime.combine(date.today(), datetime.min.time())
    end_date = today + relativedelta(months=2)

    # genereate future transactions from scheduled transactions
    txns = []
    for row in fetch_scheduled_transactions():
        # build rule, and generate instances
        rule = rrulestr(row['rrule'], dtstart=row['start_dt'])
        instances = rule.between(today, end_date, inc=True)

        # for each instance build a record
        for instance in instances:
            txns.append({
                "id": len(txns),
                "type": txn_type_codes[row['type_code']],
                "date": formatDate(instance.date()),
                "payee": row['payee'],
                "memo": row['memo'],
                "amount": toCurrency(row['amount']),
                "icon": row['icon'],
                "color": row['color'],
                "recur_id": row['recur_id'],
                })

    # response
    return response.json({
        "start_date": formatDate(today.date()),
        "end_date": formatDate(end_date.date()),
        "transactions": sorted(txns, key = lambda tx: (tx['date'], - tx['amount']['fixed']))
    })
