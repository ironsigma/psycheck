from sanic import Blueprint
from sanic import Sanic, response
from sanic.request import Request
from sanic.response import HTTPResponse
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrulestr
from typing import cast, Any, Final


bp = Blueprint("api")

FIRST_DAY_CURR_MONTH_SQL : Final = 'subdate(curdate(), (day(curdate()) - 1))'

TXN_TYPE_CODES : Final = {
    'B': 'balance',
    'D': 'debit',
    'd': 'debit-adjustment',
    'C': 'credit',
    'c': 'credit-adjustment'
}


def formatDate(dt: date) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()


def toAssetValue(type_code: str, amount: float) -> float:
    if type_code in ('C', 'c'):
        return amount * -1
    return amount


def toCurrency(amount: float) -> dict[str, Any]:
    return {
        "fixed": int(amount * 100),
        "scale": 2,
        "currency": "USD"
    }

def toMapKey(txn_id: int, txn_date: date) -> str:
    return f'{txn_id}:{txn_date.isoformat()}'


def fetch_scheduled_instances_map() -> dict:
    cur = Sanic.get_app().ctx.db.cursor()
    cur.execute("SELECT recur_id, recur_date" +
        " FROM register" +
        " WHERE date >= " + FIRST_DAY_CURR_MONTH_SQL)

    inst_map = {}
    for row in cur:
        inst_map[toMapKey(row[0], row[1])] = True

    return inst_map


def fetch_scheduled_transactions():
    COLS = ['recur_id', 'type_code', 'payee', 'memo', 'amount', 'rrule', 'start_dt', 'icon', 'color']

    cur = Sanic.get_app().ctx.db.cursor()
    cur.execute("SELECT " + ",".join(COLS) + " FROM recurring")

    for row in cur:
        yield dict(zip(COLS, row))


def fetch_transactions():
    COLS = ['reg_id', 'type_code', 'date', 'payee', 'memo',
            'amount', 'icon', 'color', 'recur_date', 'recur_id']

    # get previous balance
    cur = Sanic.get_app().ctx.db.cursor()
    cur.execute(
        "SELECT " + FIRST_DAY_CURR_MONTH_SQL + ", ifNull(balance, 0)" +
        " FROM statement" +
        " WHERE date = " + FIRST_DAY_CURR_MONTH_SQL)


    # yield previous balance
    (date, balance) = cur.fetchone()
    txn = dict(zip(COLS, [0, 'B', date, 'Previous Balance', None, balance, None, None, None, None]))
    txn['balance'] = balance
    yield txn


    # fetch transactions
    cur = Sanic.get_app().ctx.db.cursor()
    cur.execute(
        "SELECT " + ",".join(COLS) + " FROM register" +
        " WHERE date >= " + FIRST_DAY_CURR_MONTH_SQL +
        " ORDER BY date ASC, amount DESC")


    # yield transactions
    for row in cur:
        txn = dict(zip(COLS, row))
        balance += toAssetValue(txn['type_code'], txn['amount'])
        txn['balance'] = balance
        yield txn


@bp.get("/transactions")
async def transactions(_: Request) -> HTTPResponse:
    txns = []
    for row in fetch_transactions():
        txns.append({
            "id": row['reg_id'],
            "type": TXN_TYPE_CODES[str(row['type_code'])],
            "date": formatDate(cast(date, row['date'])),
            "payee": row['payee'],
            "memo": row['memo'],
            "amount": toCurrency(cast(float, row['amount'])),
            "balance": toCurrency(cast(float, row['balance'])),
            "icon": row['icon'],
            "color": row['color'],
            "scheduled": formatDate(cast(date, row['recur_date'])),
            "recur_id": row['recur_id'],
        })

    return response.json(txns)


@bp.get("/scheduled")
async def scheduled(_: Request) -> HTTPResponse:
    # compute begining of today and end date
    today = datetime.combine(date.today(), datetime.min.time())
    end_date = today + relativedelta(months=2)

    txns = []
    reg_map = fetch_scheduled_instances_map()

    # genereate future transactions from scheduled transactions
    for row in fetch_scheduled_transactions():
        # build rule, and generate instances
        rule = rrulestr(row['rrule'], dtstart=row['start_dt'])
        instances = rule.between(today, end_date, inc=True)

        # for each instance build a record
        for instance in instances:
            if toMapKey(row['recur_id'], instance.date()) in reg_map:
                continue

            txns.append({
                "id": len(txns),
                "type": TXN_TYPE_CODES[row['type_code']],
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
