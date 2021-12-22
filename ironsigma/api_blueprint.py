from sanic import Blueprint
from sanic import Sanic, response
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrulestr


bp = Blueprint("api")


def toCurrency(amount):
    return {
        "fixed": int(amount * 100),
        "scale": 2,
        "currency": "USD"
    }


@bp.get("/transactions")
async def transactions(req: Request) -> HTTPResponse:

    # compute begining of today and end date
    today = datetime.combine(date.today(), datetime.min.time())
    end_date = today + relativedelta(months=2)

    # fetch records
    cur = Sanic.get_app().ctx.db.cursor()
    cur.execute("SELECT recur_id, type_code, payee, memo, amount, rrule, start_dt, icon, color " +
                "FROM recurring")

    # genereate transactions from recurrence rules
    txns = []
    for (recur_id, type_code, payee, memo, amount, rrule, start_dt, icon, color) in cur:

        # build rule, and generate instances
        rule = rrulestr(rrule, dtstart=start_dt)
        instances = rule.between(today, end_date, inc=True)

        # for each instance build a record
        for dt in instances:
            txns.append({
                "id": len(txns),
                "type": 'credit' if type_code == 'C' else 'debit',
                "date": dt.date().isoformat(),
                "payee": payee,
                "memo": memo,
                "amount": toCurrency(amount),
                "icon": icon,
                "color": color,
                "recur_id": recur_id,
                })

    # response
    return response.json({
        "start_date": today.date().isoformat(),
        "end_date": end_date.date().isoformat(),
        "transactions": sorted(txns, key = lambda tx: (tx['date'], - tx['amount']['fixed']))
    })
