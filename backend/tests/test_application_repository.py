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
    def delete(self): self.operation = 'delete'; return self
    def execute(self):
        self.client.queries.append((self.table_name, self.filters, self.operation, self.payload))
        rows = list(self.client.rows.get(self.table_name, []))
        for op, key, value in self.filters:
            rows = [row for row in rows if (row.get(key) == value if op == 'eq' else row.get(key) in value)]
        if hasattr(self, 'limit_value'): rows = rows[:self.limit_value]
        if self.operation == 'insert':
            self.client.rows.setdefault(self.table_name, []).append(self.payload)
            rows = [self.payload]
        elif self.operation == 'update':
            for row in rows:
                row.update(self.payload)
        elif self.operation == 'delete':
            self.client.rows[self.table_name] = [row for row in self.client.rows.get(self.table_name, []) if row not in rows]
            rows = []
        return SimpleNamespace(data=rows)


class FakeStorageBucket:
    def __init__(self, client, bucket): self.client, self.bucket = client, bucket
    def upload(self, path, content, options):
        self.client.objects[(self.bucket, path)] = content.read()
        self.client.uploads.append((self.bucket, path, options))
    def download(self, path): return self.client.objects[(self.bucket, path)]
    def remove(self, paths):
        for path in paths: self.client.objects.pop((self.bucket, path), None)


class FakeClient:
    def __init__(self):
        self.queries = []
        self.objects, self.uploads = {}, []
        self.rows = {
            'workspace_members': [
                {'user_id':'user-a','workspace_id':'workspace-a'},
                {'user_id':'user-b','workspace_id':'workspace-b'}],
            'cases': [
                {'id':'case-a','workspace_id':'workspace-a'},
                {'id':'case-b','workspace_id':'workspace-b'}],
            'analysis_runs': [
                {'id':'run-a','workspace_id':'workspace-a','case_id':'case-a','status':'completed'},
                {'id':'run-b','workspace_id':'workspace-b','case_id':'case-b','status':'completed'}],
            'case_artifacts': [
                {'run_id':'run-a','workspace_id':'workspace-a','artifact_type':'case_result',
                 'schema_version':'novacase.v1','content':{'server_owned':'A'}},
                {'run_id':'run-b','workspace_id':'workspace-b','artifact_type':'case_result',
                 'schema_version':'novacase.v1','content':{'server_owned':'B'}}]
        }
    def table(self, name): return FakeQuery(self, name)
    class _Storage:
        def __init__(self, client): self.client = client
        def from_(self, bucket): return FakeStorageBucket(self.client, bucket)
    @property
    def storage(self): return self._Storage(self)


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

    def test_historical_result_returns_only_server_owned_scoped_artifacts(self):
        result = self.repo.historical_result('user-a', 'run-a')
        self.assertEqual(result['artifacts'][0]['content'], {'server_owned':'A'})
        self.assertIsNone(self.repo.historical_result('user-b', 'run-a'))

    def test_private_document_uses_server_scoped_path_and_isolated_download(self):
        from io import BytesIO
        from uuid import uuid4
        document_id = str(uuid4())
        metadata = self.repo.store_case_document('user-a', 'case-a', document_id,
            '../contrato.txt', 'text/plain', 5, 'a' * 64, BytesIO(b'hello'))
        self.assertEqual(metadata['storage_path'],
            f"workspaces/workspace-a/cases/case-a/{document_id}/contrato.txt")
        self.assertFalse(self.client.uploads[0][2]['upsert'] == 'true')
        downloaded = self.repo.download_case_document('user-a', 'case-a', document_id)
        self.assertEqual(downloaded[1], b'hello')
        self.assertIsNone(self.repo.get_case_document('user-b', 'case-a', document_id))
        self.assertIsNone(self.repo.download_case_document('user-b', 'case-a', document_id))
        self.assertTrue(self.repo.delete_case_document('user-a', 'case-a', document_id))
        self.assertFalse(self.client.objects)

    def test_private_document_rejects_invalid_type_and_size_before_storage(self):
        from io import BytesIO
        from uuid import uuid4
        with self.assertRaisesRegex(ValueError, 'INVALID_DOCUMENT_TYPE'):
            self.repo.store_case_document('user-a', 'case-a', str(uuid4()), 'evidence.txt',
                'application/pdf', 5, 'a' * 64, BytesIO(b'hello'))
        with self.assertRaisesRegex(ValueError, 'INVALID_DOCUMENT_SIZE'):
            self.repo.store_case_document('user-a', 'case-a', str(uuid4()), 'evidence.txt',
                'text/plain', 0, 'a' * 64, BytesIO(b''))
        self.assertFalse(self.client.objects)


if __name__ == '__main__':
    unittest.main()
