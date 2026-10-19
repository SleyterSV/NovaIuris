"""Voice uploads stay bounded and provider errors remain public-safe."""

import io
import unittest
from unittest.mock import patch

from app import create_app
from app.config import Config


class VoiceConfig(Config):
    TESTING = True
    APP_ENV = 'test'
    TASK_PERSISTENCE_ENABLED = False


class VoiceInputTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app(VoiceConfig).test_client()

    def upload(self, data=b'voice', mime='audio/webm'):
        return self.client.post('/api/voice/transcribe',
            data={'audio': (io.BytesIO(data), 'voice.webm', mime)},
            content_type='multipart/form-data')

    def test_valid_audio_transcribed_without_persistence(self):
        with patch('app.api.voice._transcribe', return_value='Consulta jurídica') as provider:
            response = self.upload()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['text'], 'Consulta jurídica')
        provider.assert_called_once_with(b'voice', 'webm')

    def test_empty_invalid_and_oversized_uploads_never_reach_provider(self):
        with patch('app.api.voice._transcribe') as provider:
            self.assertEqual(self.upload(b'').status_code, 400)
            self.assertEqual(self.upload(b'voice', 'application/octet-stream').status_code, 415)
            self.assertEqual(self.upload(b'x' * (10 * 1024 * 1024 + 1)).status_code, 413)
            provider.assert_not_called()

    def test_provider_failure_is_sanitized(self):
        with patch('app.api.voice._transcribe', side_effect=RuntimeError('secret/path/key')):
            response = self.upload()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json['error']['code'], 'VOICE_UNAVAILABLE')
        self.assertNotIn('secret/path/key', response.get_data(as_text=True))
