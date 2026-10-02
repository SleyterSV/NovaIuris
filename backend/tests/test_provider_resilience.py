import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx
from openai import BadRequestError, RateLimitError, InternalServerError

from app.services.embedding_service import EmbeddingService, bounded_attempts
from app.utils.cancellation import CancellationToken, OperationCancelled


def status_error(kind, status):
    request = httpx.Request('POST', 'https://example.test/embeddings')
    return kind('synthetic provider failure', response=httpx.Response(status, request=request), body=None)


class ProviderResilienceTests(unittest.TestCase):
    def service(self, effects):
        service = EmbeddingService.__new__(EmbeddingService)
        service.MODEL = 'synthetic'
        service._cache = {}
        service.client = SimpleNamespace(embeddings=SimpleNamespace(create=Mock(side_effect=effects)))
        return service

    @patch('app.services.embedding_service.time.sleep')
    def test_429_retries_once_then_succeeds(self, sleep):
        service = self.service([status_error(RateLimitError, 429),
                                SimpleNamespace(data=[SimpleNamespace(embedding=[0.1])])])
        self.assertEqual(service.generate_embedding('texto', retries=2), [0.1])
        self.assertEqual(service.client.embeddings.create.call_count, 2)

    @patch('app.services.embedding_service.time.sleep')
    def test_400_does_not_retry_and_error_is_safe(self, sleep):
        service = self.service(status_error(BadRequestError, 400))
        with self.assertRaisesRegex(RuntimeError, 'No fue posible generar'):
            service.generate_embedding('texto', retries=3)
        self.assertEqual(service.client.embeddings.create.call_count, 1)
        sleep.assert_not_called()

    @patch('app.services.embedding_service.time.sleep')
    def test_5xx_exhausts_bounded_attempts(self, sleep):
        service = self.service(status_error(InternalServerError, 503))
        with self.assertRaises(RuntimeError):
            service.generate_embedding('texto', retries=999)
        self.assertEqual(service.client.embeddings.create.call_count, 3)
        self.assertEqual(bounded_attempts(999), 3)

    def test_cancel_prevents_call(self):
        service = self.service([])
        token = CancellationToken()
        token.cancel()
        with self.assertRaises(OperationCancelled):
            service.generate_embedding('texto', cancellation_token=token)
        service.client.embeddings.create.assert_not_called()

    @patch('app.services.embedding_service.time.sleep')
    def test_timeout_retries_bounded(self, sleep):
        service = self.service(TimeoutError('synthetic timeout'))
        with self.assertRaises(RuntimeError):
            service.generate_embedding('texto', retries=2)
        self.assertEqual(service.client.embeddings.create.call_count, 2)

    @patch('app.services.embedding_service.time.sleep')
    def test_cancel_during_backoff_prevents_next_call(self, sleep):
        token = CancellationToken()
        sleep.side_effect = lambda duration: token.cancel()
        service = self.service(status_error(RateLimitError, 429))
        with self.assertRaises(OperationCancelled):
            service.generate_embedding('texto', retries=3, cancellation_token=token)
        self.assertEqual(service.client.embeddings.create.call_count, 1)


if __name__ == '__main__':
    unittest.main()
