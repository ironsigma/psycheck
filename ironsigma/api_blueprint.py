from sanic import Blueprint
from sanic import Sanic, response
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse


bp = Blueprint("api")


@bp.get("/")
async def index(req: Request) -> HTTPResponse:
    logger.info("index called")

    cur = Sanic.get_app().ctx.db.cursor()
    cur.execute("SELECT * FROM recurring")

    res = {"status": "OK", "rows": []}
    for row in cur:
        res["rows"].append(row)

    return response.json(res)
