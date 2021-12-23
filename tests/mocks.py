from sanic import Sanic


class MockCursor:
    def __init__(self):
        self.item_list = []

    def execute(self, query, values=None):
        print("SQL:", query, values)

        app = Sanic.get_app()
        if hasattr(app.ctx, 'sql_cur_results'):
            for sql, results in app.ctx.sql_cur_results.items():
                if sql in query:
                    self.item_list = results
                    break

    def fetchone(self):
        if not self.item_list:
            print("fetchone() ->", None)
            return None

        row = self.item_list.pop(0)
        print("fetchone() ->", row)
        return row

    def __iter__(self):
        for item in self.item_list:
            print("iter ->:", item)
            yield item


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
