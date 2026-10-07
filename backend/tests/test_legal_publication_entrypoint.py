"""The V2 entrypoint reads only its dedicated process variable."""
import os
import unittest
from unittest.mock import patch

from app.legal_ingestion import publication_entrypoint


class PublicationEntrypointTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
