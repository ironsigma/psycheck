import pathlib

from sanic import Blueprint
from sanic import response
from sanic.request import Request
from sanic.response import HTTPResponse


bp = Blueprint("index")


@bp.get("/")
async def index(req: Request) -> HTTPResponse:
    template = pathlib.Path(__file__).parent.joinpath("views/index.html")
    return await response.file(template)
