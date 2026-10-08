"""The V2 entrypoint reads only its dedicated process variable."""
import os
import io
import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from app.legal_ingestion import publication_entrypoint
from app.legal_ingestion.publication import PublicationAdapter, PublicationResult
from tests.test_legal_publication import fixture


class PublicationEntrypointTests(unittest.TestCase):
    DSN = "postgresql://postgres.emelxkoztshmzukydqzj@host.invalid/postgres"

    def test_missing_dsn_fails_before_connection(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "MYKE_LEGAL_DATABASE_URL"):
                publication_entrypoint.configured_publication_adapter()

    def test_passes_full_dsn_to_factory_without_connecting(self):
        example_dsn = "postgresql://pilot@host.invalid:5432/postgres?sslmode=require"
        factory = lambda: None
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": example_dsn}, clear=True), \
             patch.object(publication_entrypoint, "postgres_connection_factory",
                          return_value=factory) as make_factory:
            adapter = publication_entrypoint.configured_publication_adapter(batch_size=4)
        make_factory.assert_called_once_with(example_dsn)
        self.assertIs(adapter.connection_factory, factory)
        self.assertEqual(adapter.batch_size, 4)

    def test_allowlist_rejects_arbitrary_document(self):
        with self.assertRaises(SystemExit) as stopped, redirect_stderr(io.StringIO()):
            publication_entrypoint.main(["publish", "another-document"])
        self.assertEqual(stopped.exception.code, 2)

    def test_inspect_never_uses_database_or_embedding_provider(self):
        doc = fixture(1)
        doc.metadata["number"] = "123"
        with patch.object(publication_entrypoint, "_stage", return_value=doc), \
             patch.object(publication_entrypoint, "configured_publication_adapter",
                          side_effect=AssertionError("database opened")), \
             redirect_stdout(io.StringIO()) as output:
            self.assertEqual(publication_entrypoint.main(["inspect", "decree"]), 0)
        self.assertIn("DOCUMENT=decree", output.getvalue())

    def test_preflight_requires_dedicated_database_variable(self):
        with patch.dict(os.environ, {"SUPABASE_URL": "legacy.invalid", "OPENAI_API_KEY": "fake"}, clear=True), \
             redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(publication_entrypoint.main(["preflight"]), 1)
        self.assertIn("DATABASE_NOT_CONFIGURED", errors.getvalue())
        self.assertNotIn("legacy.invalid", errors.getvalue())

    def test_publish_requires_database_and_embedding_credential(self):
        with patch.dict(os.environ, {}, clear=True), redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(publication_entrypoint.main(["publish", "decree"]), 1)
        self.assertIn("DATABASE_NOT_CONFIGURED", errors.getvalue())
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN}, clear=True), \
             redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(publication_entrypoint.main(["publish", "decree"]), 1)
        self.assertIn("EMBEDDING_PROVIDER_NOT_CONFIGURED", errors.getvalue())

    def test_wrong_target_or_model_fails_closed(self):
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": "postgresql://postgres.other@host.invalid/postgres"}, clear=True), \
             redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(publication_entrypoint.main(["counts"]), 1)
        self.assertIn("DATABASE_TARGET_UNVERIFIED", errors.getvalue())
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN,
                                     "OPENAI_API_KEY": "fake", "OPENAI_EMBEDDING_MODEL": "other"}, clear=True), \
             redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(publication_entrypoint.main(["preflight"]), 1)
        self.assertIn("EMBEDDING_MODEL_MISMATCH", errors.getvalue())

    def test_quality_failure_stops_before_connection(self):
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN,
                                     "OPENAI_API_KEY": "fake"}, clear=True), \
             patch.object(publication_entrypoint, "_stage",
                          side_effect=publication_entrypoint.PilotError("PILOT_QUALITY_OR_IDENTITY_CHANGED")), \
             patch.object(publication_entrypoint, "configured_publication_adapter",
                          side_effect=AssertionError("database opened")), \
             redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(publication_entrypoint.main(["preflight"]), 1)
        self.assertIn("PILOT_QUALITY_OR_IDENTITY_CHANGED", errors.getvalue())

    def test_idempotency_compares_exact_units_read_only(self):
        doc = fixture(1)
        adapter = PublicationAdapter(lambda: None)
        row, units, _ = adapter.prepare(doc)

        class Cursor:
            def __init__(self, document_rows, unit_rows=()):
                self.responses = [document_rows, unit_rows]
                self.queries = []

            def execute(self, sql, params):
                self.queries.append(sql)

            def fetchall(self):
                return self.responses.pop(0)

        self.assertEqual(publication_entrypoint._identity(Cursor([]), doc, adapter), "NOT_PRESENT")
        document_row = [(row["id"], row["title"], row["document_type"], row["number"],
                         row["expediente"], "ready", "completed")]
        unit_row = [(units[0]["id"], units[0]["sequence"], units[0]["content_hash"],
                     units[0]["unit_type"], units[0]["unit_number"], units[0]["page_start"],
                     units[0]["page_end"], 1536)]
        cursor = Cursor(document_row, unit_row)
        self.assertEqual(publication_entrypoint._identity(cursor, doc, adapter),
                         "ALREADY_PRESENT_AND_IDENTICAL")
        self.assertTrue(all(query.lstrip().startswith("select") for query in cursor.queries))
        self.assertEqual(publication_entrypoint._identity(Cursor(document_row, []), doc, adapter), "CONFLICT")
        self.assertEqual(publication_entrypoint._identity(
            Cursor([(row["id"], row["title"], row["document_type"], row["number"],
                     row["expediente"], "processing", "processing")]), doc, adapter), "CONFLICT")

    def test_preflight_and_counts_use_safe_summary(self):
        @contextmanager
        def database(_adapter):
            yield None, object()
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN,
                                     "OPENAI_API_KEY": "fake"}, clear=True), \
             patch.object(publication_entrypoint, "_stage", side_effect=[fixture(5), fixture(10)]), \
             patch.object(publication_entrypoint, "_database", database), \
             patch.object(publication_entrypoint, "_counts", return_value=(0, 0, 0, 0)), \
             patch.object(publication_entrypoint, "configured_publication_adapter", return_value=object()), \
             redirect_stdout(io.StringIO()) as output:
            self.assertEqual(publication_entrypoint.main(["preflight"]), 0)
            self.assertEqual(publication_entrypoint.main(["counts"]), 0)
        self.assertIn("DECREE=PUBLISHABLE UNITS=5 AUTO=PUBLISHABLE UNITS=10", output.getvalue())
        self.assertIn("legal_ingestion_runs=0", output.getvalue())
        self.assertNotIn(self.DSN, output.getvalue())

    def test_preflight_refuses_nonempty_database(self):
        @contextmanager
        def database(_adapter):
            yield None, object()
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN,
                                     "OPENAI_API_KEY": "fake"}, clear=True), \
             patch.object(publication_entrypoint, "_stage", side_effect=[fixture(5), fixture(10)]), \
             patch.object(publication_entrypoint, "_database", database), \
             patch.object(publication_entrypoint, "_counts", return_value=(1, 5, 0, 1)), \
             patch.object(publication_entrypoint, "configured_publication_adapter", return_value=object()), \
             redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(publication_entrypoint.main(["preflight"]), 1)
        self.assertIn("DATABASE_NOT_EMPTY", errors.getvalue())

    def test_database_checks_schema_and_real_transaction_mode(self):
        class Connection:
            autocommit = False
            def __init__(self, schema):
                self.schema = schema
                self.rolled_back = False
                self.closed = False
            def cursor(self):
                return self
            def execute(self, sql):
                self.sql = sql
            def fetchone(self):
                return self.schema
            def rollback(self):
                self.rolled_back = True
            def close(self):
                self.closed = True

        good = Connection((True,) * 6)
        with publication_entrypoint._database(SimpleNamespace(connection_factory=lambda: good)):
            pass
        self.assertTrue(good.rolled_back and good.closed)
        self.assertIn("match_legal_knowledge_v2", good.sql)
        bad = Connection((False,) + (True,) * 5)
        with self.assertRaisesRegex(publication_entrypoint.PilotError, "DATABASE_V2_SCHEMA_MISSING"):
            with publication_entrypoint._database(SimpleNamespace(connection_factory=lambda: bad)):
                pass
        self.assertTrue(bad.rolled_back and bad.closed)
        transactional = Connection((True,) * 6)
        transactional.autocommit = True
        with self.assertRaisesRegex(publication_entrypoint.PilotError, "AUTOCOMMIT"):
            with publication_entrypoint._database(SimpleNamespace(connection_factory=lambda: transactional)):
                pass

    def test_publish_maps_only_selected_document_to_existing_adapter(self):
        doc = fixture(1)
        @contextmanager
        def database(_adapter):
            yield None, None
        adapter = PublicationAdapter(lambda: self.fail("real database opened"))
        result = PublicationResult(doc.document_id, "run-id", 1, 1, 0, 0)
        provider = SimpleNamespace(MODEL=publication_entrypoint.MODEL,
                                   generate_embeddings=lambda texts: [[0.1] * 1536 for _ in texts])
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN,
                                     "OPENAI_API_KEY": "fake"}, clear=True), \
             patch.object(publication_entrypoint, "_stage", return_value=doc) as stage, \
             patch.object(publication_entrypoint, "_database", database), \
             patch.object(publication_entrypoint, "_identity", return_value="NOT_PRESENT"), \
             patch.object(publication_entrypoint, "configured_publication_adapter", return_value=adapter), \
             patch.object(adapter, "publish", return_value=result) as publish, \
             patch.dict(sys.modules, {"app.services.embedding_service":
                                      SimpleNamespace(EmbeddingService=lambda: provider)}), \
             redirect_stdout(io.StringIO()) as output:
            self.assertEqual(publication_entrypoint.main(["publish", "decree"]), 0)
        stage.assert_called_once_with("decree")
        self.assertIs(publish.call_args.args[0], doc)
        self.assertEqual(len(publish.call_args.kwargs["embeddings"]), 1)
        self.assertEqual(publish.call_args.kwargs["relations"], ())
        self.assertIn("STATUS=COMPLETED", output.getvalue())
        self.assertNotIn(self.DSN, output.getvalue())

    def test_idempotency_cli_never_invokes_provider_or_publish(self):
        @contextmanager
        def database(_adapter):
            yield None, None
        adapter = PublicationAdapter(lambda: self.fail("database opened"))
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN}, clear=True), \
             patch.object(publication_entrypoint, "_stage", return_value=fixture(1)), \
             patch.object(publication_entrypoint, "_database", database), \
             patch.object(publication_entrypoint, "_identity", return_value="ALREADY_PRESENT_AND_IDENTICAL"), \
             patch.object(publication_entrypoint, "configured_publication_adapter", return_value=adapter), \
             patch.object(adapter, "publish", side_effect=AssertionError("publish called")), \
             redirect_stdout(io.StringIO()) as output:
            self.assertEqual(publication_entrypoint.main(["idempotency-check", "auto"]), 0)
        self.assertIn("ALREADY_PRESENT_AND_IDENTICAL", output.getvalue())

    def test_invalid_vectors_stop_before_publication(self):
        doc = fixture(1)
        @contextmanager
        def database(_adapter):
            yield None, None
        adapter = PublicationAdapter(lambda: self.fail("database publication opened"))
        for vector in ([0.0] * 10, [float("nan")] * 1536, [float("inf")] * 1536):
            provider = SimpleNamespace(MODEL=publication_entrypoint.MODEL,
                                       generate_embeddings=lambda _texts, v=vector: [v])
            with self.subTest(length=len(vector), first=vector[0]), \
                 patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN,
                                      "OPENAI_API_KEY": "fake"}, clear=True), \
                 patch.object(publication_entrypoint, "_stage", return_value=doc), \
                 patch.object(publication_entrypoint, "_database", database), \
                 patch.object(publication_entrypoint, "_identity", return_value="NOT_PRESENT"), \
                 patch.object(publication_entrypoint, "configured_publication_adapter", return_value=adapter), \
                 patch.dict(sys.modules, {"app.services.embedding_service":
                                      SimpleNamespace(EmbeddingService=lambda: provider)}), \
                 redirect_stderr(io.StringIO()):
                self.assertEqual(publication_entrypoint.main(["publish", "decree"]), 1)

    def test_unexpected_error_never_prints_secret(self):
        with patch.object(publication_entrypoint, "_run",
                          side_effect=RuntimeError("password=private-value")), \
             redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(publication_entrypoint.main(["counts"]), 1)
        self.assertEqual(errors.getvalue().strip(), "ERROR=RuntimeError")


class SearchCommandTests(unittest.TestCase):
    DSN = PublicationEntrypointTests.DSN

    @staticmethod
    def _provider(vector):
        calls = []
        def generate(text):
            calls.append(text)
            return vector
        return SimpleNamespace(MODEL=publication_entrypoint.MODEL,
                               generate_embedding=generate), calls

    @staticmethod
    def _database(rows=()):
        class Cursor:
            def __init__(self):
                self.sql = None
                self.params = None
            def execute(self, sql, params):
                self.sql, self.params = sql, params
            def fetchall(self):
                return rows
        cursor = Cursor()
        read_only_flags = []
        @contextmanager
        def database(_adapter, *, read_only=False):
            read_only_flags.append(read_only)
            yield None, cursor
        return database, cursor, read_only_flags

    def test_empty_query_and_invalid_top_k_stop_before_provider(self):
        for args, code in ((["search", "  "], "SEARCH_QUERY_EMPTY"),
                           (["search", "consulta", "--top-k", "0"], "SEARCH_TOP_K_INVALID"),
                           (["search", "consulta", "--top-k", "51"], "SEARCH_TOP_K_INVALID")):
            with self.subTest(args=args), redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(publication_entrypoint.main(args), 1)
                self.assertIn(code, errors.getvalue())

    def test_search_requires_both_process_credentials(self):
        with patch.dict(os.environ, {}, clear=True), redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(publication_entrypoint.main(["search", "consulta"]), 1)
        self.assertIn("DATABASE_NOT_CONFIGURED", errors.getvalue())
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN}, clear=True), \
             redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(publication_entrypoint.main(["search", "consulta"]), 1)
        self.assertIn("EMBEDDING_PROVIDER_NOT_CONFIGURED", errors.getvalue())

    def test_wrong_dimension_nan_and_infinity_never_open_database(self):
        for vector in ([0.1] * 3, [float("nan")] * 1536, [float("inf")] * 1536):
            provider, calls = self._provider(vector)
            with self.subTest(length=len(vector), first=vector[0]), \
                 patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN,
                                      "OPENAI_API_KEY": "test-key"}, clear=True), \
                 patch.dict(sys.modules, {"app.services.embedding_service":
                                      SimpleNamespace(EmbeddingService=lambda: provider)}), \
                 patch.object(publication_entrypoint, "_database",
                              side_effect=AssertionError("database opened")), \
                 redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(publication_entrypoint.main(["search", "consulta"]), 1)
                self.assertNotIn("test-key", errors.getvalue())
            self.assertEqual(calls, ["consulta"])

    def test_rpc_mapping_filters_json_and_read_only(self):
        provider, calls = self._provider([0.1] * 1536)
        row = ("unit-uuid", "document-uuid", "Título de prueba", "order", "foundation",
               "3", "Fundamento", "Extracto", 2, 3, 0.82, 0.13, None)
        database, cursor, flags = self._database([row])
        with patch.dict(os.environ, {"MYKE_LEGAL_DATABASE_URL": self.DSN,
                                     "OPENAI_API_KEY": "test-key"}, clear=True), \
             patch.dict(sys.modules, {"app.services.embedding_service":
                                      SimpleNamespace(EmbeddingService=lambda: provider)}), \
             patch.object(publication_entrypoint, "configured_publication_adapter", return_value=object()), \
             patch.object(publication_entrypoint, "_database", database), \
             patch.object(PublicationAdapter, "publish", side_effect=AssertionError("published")), \
             redirect_stdout(io.StringIO()) as output:
            status = publication_entrypoint.main(["search", "  agravio constitucional  ",
                "--top-k", "3", "--document-type", "order", "--rama", "constitucional",
                "--expediente", "04810-2024-PA/TC", "--json"])
        self.assertEqual(status, 0)
        self.assertEqual(calls, ["agravio constitucional"])
        self.assertEqual(flags, [True])
        self.assertTrue(cursor.sql.lstrip().startswith("select"))
        self.assertIn("public.match_legal_knowledge_v2", cursor.sql)
        self.assertEqual(cursor.params[1:], ("agravio constitucional", 3, "order",
                                              "constitucional", "04810-2024-PA/TC"))
        self.assertTrue(cursor.params[0].startswith("["))
        result = __import__("json").loads(output.getvalue())
        self.assertEqual(result["results"][0]["rank"], 1)
        self.assertEqual(result["results"][0]["unit_id"], "unit-uuid")
        self.assertEqual(result["results"][0]["lexical_score"], 0.13)
        self.assertNotIn(self.DSN, output.getvalue())
        self.assertNotIn("test-key", output.getvalue())
        self.assertNotIn(cursor.params[0], output.getvalue())

    def test_read_only_connection_is_requested_before_any_sql(self):
        class Connection:
            autocommit = False
            def __init__(self):
                self.calls = []
            def set_session(self, *, readonly):
                self.calls.append(("set_session", readonly))
            def cursor(self):
                return self
            def execute(self, sql):
                self.calls.append(("execute", sql))
            def fetchone(self):
                return (True,) * 6
            def rollback(self):
                self.calls.append(("rollback",))
            def close(self):
                self.calls.append(("close",))
        connection = Connection()
        with publication_entrypoint._database(
                SimpleNamespace(connection_factory=lambda: connection), read_only=True):
            pass
        self.assertEqual(connection.calls[0], ("set_session", True))
        self.assertEqual(connection.calls[1][0], "execute")
        self.assertEqual(connection.calls[-2:], [("rollback",), ("close",)])


if __name__ == "__main__":
    unittest.main()
