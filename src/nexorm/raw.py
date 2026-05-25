from nexorm.database import default_db


class RawQuery:
    def __init__(self, model, sql, params=None, db=None):
        self.model = model
        self.sql = sql
        self.params = params or []
        self.db = db or default_db

    def all(self):
        return [self.model.from_row(row, db=self.db) for row in self.db.fetchall(self.sql, self.params)]

    def first(self):
        row = self.db.fetchone(self.sql, self.params)
        return self.model.from_row(row, db=self.db) if row else None
