import pathlib

from sanic import Sanic, Blueprint
from sanic.log import logger
from ironsigma import api_blueprint


def create(config, db_factory):
    app = Sanic("Checkbook")
    app.ctx.db_factory = db_factory

    # Config
    app.config.update(config)

    # Blueprints
    app.blueprint(Blueprint.group(api_blueprint.bp, url_prefix="/api"))

    # DB Setup
    @app.before_server_start
    async def db_connect(app, loop):
        app.ctx.db = app.ctx.db_factory.create()

    # DB Close
    @app.after_server_stop
    async def db_close(app, loop):
        app.ctx.db.close()
        logger.info('DB connection closed')

    # Static paths
    pkg_path = pathlib.Path(__file__).parent
    static_path = pkg_path.joinpath("static")
    app.static("/static", static_path, name='static')
    app.static("/favicon.ico", static_path.joinpath("favicon.ico"))

    return app
