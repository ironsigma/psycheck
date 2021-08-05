from sanic import Sanic

from ironsigma import env, app_factory
from ironsigma.db_factory import DatabaseFactory


def create() -> Sanic:
    config = env.load(".env", "SANIC_")
    db_factory = DatabaseFactory(config)
    return app_factory.create(config, db_factory)
