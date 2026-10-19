import { API_URL } from '../config/api.js'
import { authHeaders } from '../config/authSession.js'

export async function transcribeAudio(blob, signal) {
  const body = new FormData()
  const mime = blob.type.split(';')[0]
  const extension = { 'audio/webm':'webm', 'audio/ogg':'ogg', 'audio/mp4':'mp4', 'audio/mpeg':'mp3', 'audio/wav':'wav' }[mime]
  if (!extension || !blob.size) throw new Error('La grabación no tiene un formato de audio compatible.')
  body.append('audio', blob, `voice.${extension}`)
  let response
  try {
    response = await fetch(`${API_URL}/voice/transcribe`, { method:'POST', headers:authHeaders(), body, signal })
  } catch (error) {
    if (error?.name === 'AbortError') throw error
    throw new Error('No se pudo conectar con el servicio de transcripción.')
  }
  const data = await response.json().catch(() => ({}))
  if (!response.ok || data.success === false) {
    const message = ({ VOICE_EMPTY:'La grabación está vacía.', VOICE_FORMAT:'El formato de audio no es compatible.',
      VOICE_TOO_LARGE:'La grabación es demasiado larga.', VOICE_EMPTY_TRANSCRIPT:'No se detectó voz en la grabación.' })[data?.error?.code] ||
      (response.status === 401 ? 'Tu sesión expiró. Inicia sesión nuevamente.' : 'No fue posible transcribir la grabación. Inténtalo nuevamente.')
    throw new Error(message)
  }
  if (typeof data.text !== 'string') throw new Error('No se recibió una transcripción válida.')
  return data.text.trim()
}
