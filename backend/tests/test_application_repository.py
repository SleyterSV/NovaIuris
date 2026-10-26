import unittest
from types import SimpleNamespace

from app.services.application_repository import ApplicationRepository


class FakeQuery:
    def __init__(self, client, table):
        self.client, self.table_name = client, table
        self.filters, self.operation, self.payload = [], 'select', None
    def select(self, fields): self.fields = fields; return self
    def eq(self, key, value): self.filters.append(('eq', key, value)); return self
    def in_(self, key, values): self.filters.append(('in', key, values)); return self
    def limit(self, value): self.limit_value = value; return self
    def order(self, *args, **kwargs): return self
    def insert(self, payload): self.operation, self.payload = 'insert', payload; return self
    def update(self, payload): self.operation, self.payload = 'update', payload; return self
    def upsert(self, payload, **kwargs): self.operation, self.payload = 'upsert', payload; return self
    def execute(self):
        self.client.queries.append((self.table_name, self.filters, self.operation, self.payload))
        rows = list(self.client.rows.get(self.table_name, []))
        for op, key, value in self.filters:
            rows = [row for row in rows if (row.get(key) == value if op == 'eq' else row.get(key) in value)]
        if hasattr(self, 'limit_value'): rows = rows[:self.limit_value]
        if self.operation == 'insert':
            self.client.rows.setdefault(self.table_name, []).append(self.payload)
            rows = [self.payload]
        return SimpleNamespace(data=rows)


class FakeClient:
    def __init__(self):
        self.queries = []
        self.rows = {
            'workspace_members': [
                {'user_id':'user-a','workspace_id':'workspace-a'},
                {'user_id':'user-b','workspace_id':'workspace-b'}],
            'cases': [
                {'id':'case-a','workspace_id':'workspace-a'},
                {'id':'case-b','workspace_id':'workspace-b'}],
            'analysis_runs': [
                {'id':'run-a','workspace_id':'workspace-a','status':'completed'},
                {'id':'run-b','workspace_id':'workspace-b','status':'completed'}]
        }
    def table(self, name): return FakeQuery(self, name)


class ApplicationRepositoryScopeTests(unittest.TestCase):
    def setUp(self): self.client = FakeClient(); self.repo = ApplicationRepository('https://example.test','server-only',self.client)

    def test_user_a_cannot_list_or_open_user_b_case(self):
        self.assertEqual(self.repo.list_cases('user-a'), [{'id':'case-a','workspace_id':'workspace-a'}])
        self.assertIsNone(self.repo.get_case('user-a','case-b'))
        case_query = [q for q in self.client.queries if q[0] == 'cases'][-1]
        self.assertIn(('in','workspace_id',['workspace-a']), case_query[1])

    def test_user_a_cannot_read_user_b_historical_result(self):
        self.assertIsNone(self.repo.historical_result('user-a','run-b'))
        run_query = [q for q in self.client.queries if q[0] == 'analysis_runs'][-1]
        self.assertIn(('in','workspace_id',['workspace-a']), run_query[1])


if __name__ == '__main__':
    unittest.main()
