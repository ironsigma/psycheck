from sanic import Sanic


class MockCursor:
    def __init__(self):
        self.item_list = []

    def execute(self, query, values=None):
        print("SQL:", query, values)

        app = Sanic.get_app()
        if hasattr(app.ctx, 'sql_cur_results'):
            self.item_list = app.ctx.sql_cur_results

    def fetchone(self):
        if not self.item_list:
            print("row:", None)
            return None

        row = self.item_list.pop(0)
        print("row:", row)
        return row

    def __iter__(self):
        for item in self.item_list:
            print("row:", item)
            yield item

        self.item_list = []


class MockDatabase:
    @staticmethod
    def cursor():
        return MockCursor()

    @staticmethod
    def close():
        pass


class MockDatabaseFactory:
    @staticmethod
    def create():
        return MockDatabase
