import mariadb
from sanic.log import logger


class DatabaseFactory:
    def __init__(self, config):
        self.config = config

    def create(self):
        db = mariadb.connect(
            host=self.config['DB_HOST'], port=self.config['DB_PORT'],
            user=self.config['DB_USER'], password=self.config['DB_PASS'],
            database=self.config['DB_NAME'])

        logger.info(f'DB connection created mysql://{self.config["DB_USER"]}' +
                    f'@{self.config["DB_HOST"]}:{self.config["DB_PORT"]}' +
                    f'/{self.config["DB_NAME"]}')

        return db
