"""Short, authenticated voice input for the MYKE composer."""

from io import BytesIO

from flask import Blueprint, current_app, g, jsonify, request

from ..utils.api_response import api_error


voice_bp = Blueprint('voice', __name__)
MAX_AUDIO_BYTES = 10 * 1024 * 1024
MIME_EXTENSIONS = {
    'audio/webm': 'webm', 'audio/ogg': 'ogg', 'audio/mp4': 'mp4',
    'audio/mpeg': 'mp3', 'audio/wav': 'wav',
}


def _transcribe(audio, extension):
    from openai import OpenAI

    api_key = current_app.config.get('OPENAI_API_KEY') or current_app.config.get('EMBEDDING_API_KEY')
    if not api_key:
        raise RuntimeError('Voice provider is unavailable')
    client = OpenAI(api_key=api_key, timeout=30.0, max_retries=0)
    return client.audio.transcriptions.create(
        model='gpt-4o-mini-transcribe',
        file=(f'voice.{extension}', BytesIO(audio), f'audio/{extension}'),
        language='es',
    ).text


@voice_bp.post('/voice/transcribe')
def transcribe_voice():
    request.max_content_length = MAX_AUDIO_BYTES + 65536
    if request.content_length is not None and request.content_length > MAX_AUDIO_BYTES + 65536:
        return api_error('VOICE_TOO_LARGE', 'La grabación es demasiado larga.', g.request_id, 413)
    uploaded = request.files.get('audio')
    if uploaded is None:
        return api_error('VOICE_EMPTY', 'Graba un mensaje antes de transcribir.', g.request_id, 400)
    mime = uploaded.mimetype.lower()
    extension = MIME_EXTENSIONS.get(mime)
    if extension is None:
        return api_error('VOICE_FORMAT', 'El formato de audio no es compatible.', g.request_id, 415)
    try:
        audio = uploaded.stream.read(MAX_AUDIO_BYTES + 1)
    finally:
        uploaded.close()
    if not audio:
        return api_error('VOICE_EMPTY', 'La grabación está vacía.', g.request_id, 400)
    if len(audio) > MAX_AUDIO_BYTES:
        return api_error('VOICE_TOO_LARGE', 'La grabación es demasiado larga.', g.request_id, 413)
    try:
        transcript = _transcribe(audio, extension)
    except Exception:
        return api_error('VOICE_UNAVAILABLE', 'No fue posible transcribir la grabación. Inténtalo nuevamente.', g.request_id, 503)
    if not isinstance(transcript, str) or not transcript.strip():
        return api_error('VOICE_EMPTY_TRANSCRIPT', 'No se detectó voz en la grabación.', g.request_id, 422)
    return jsonify({'success': True, 'text': transcript.strip()[:10000]})
