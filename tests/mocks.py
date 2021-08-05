class MockCursor:
    def __init__(self):
        self.item_list = []

    def execute(self, query):
        print("SQL:", query)

    def __iter__(self):
        for item in self.item_list:
            yield item


class MockDatabase:
    def cursor():
        print("new Cursor")
        return MockCursor()

    def close():
        print("Closing DB")


class DatabaseFactory:
    def create():
        return MockDatabase
