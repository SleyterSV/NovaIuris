import { computed, getCurrentInstance, onUnmounted, ref } from 'vue'
import { transcribeAudio } from '../services/voiceService.js'

const MAX_SECONDS = 60
const MAX_BYTES = 10 * 1024 * 1024
const TYPES = ['audio/webm;codecs=opus', 'audio/mp4', 'audio/ogg;codecs=opus', 'audio/webm', 'audio/ogg']

export function appendTranscript(draft, transcript) {
  return [String(draft || '').trim(), String(transcript || '').trim()].filter(Boolean).join(draft?.trim() ? '\n' : '')
}

export function useVoiceInput(onTranscript, dependencies = {}) {
  const state = ref('idle'), seconds = ref(0), message = ref('')
  const transcribe = dependencies.transcribe || transcribeAudio
  const media = dependencies.media || (typeof navigator === 'undefined' ? null : navigator.mediaDevices)
  const Recorder = dependencies.Recorder || globalThis.MediaRecorder
  let recorder, stream, interval, controller, disposed = false
  const elapsed = computed(() => `${String(Math.floor(seconds.value / 60)).padStart(2,'0')}:${String(seconds.value % 60).padStart(2,'0')}`)
  function release() {
    if (interval) clearInterval(interval)
    interval = null
    stream?.getTracks().forEach(track => track.stop())
    stream = null
  }
  function error(text) { release(); state.value = 'error'; message.value = text }
  async function start() {
    if (disposed) return
    if (state.value === 'recording' || state.value === 'requesting_permission' || state.value === 'transcribing') return
    message.value = ''
    if (!media?.getUserMedia || !Recorder) { error('Este navegador no permite grabar audio.'); return }
    const mimeType = TYPES.find(type => Recorder.isTypeSupported?.(type))
    if (!mimeType) { error('Este navegador no ofrece un formato de audio compatible.'); return }
    state.value = 'requesting_permission'
    try {
      stream = await media.getUserMedia({ audio:true })
      if (disposed) { release(); return }
      recorder = new Recorder(stream, { mimeType })
      const chunks = []
      recorder.ondataavailable = event => { if (event.data?.size) chunks.push(event.data) }
      recorder.onerror = () => error('La grabación se interrumpió. Inténtalo nuevamente.')
      recorder.onstop = async () => {
        if (state.value === 'error' || disposed) { release(); return }
        release()
        const blob = new Blob(chunks, { type:mimeType.split(';')[0] })
        if (!blob.size) { error('La grabación está vacía. Inténtalo nuevamente.'); return }
        if (blob.size > MAX_BYTES) { error('La grabación es demasiado larga.'); return }
        state.value = 'transcribing'
        controller = new AbortController()
        try {
          const text = await transcribe(blob, controller.signal)
          if (!text) { error('No se detectó voz en la grabación.'); return }
          onTranscript(text)
          state.value = 'completed'
          message.value = 'Texto añadido. Revísalo antes de enviarlo.'
        } catch (cause) {
          if (cause?.name !== 'AbortError') error(cause?.message || 'No fue posible transcribir la grabación.')
        }
      }
      seconds.value = 0
      recorder.start()
      state.value = 'recording'
      interval = setInterval(() => {
        seconds.value++
        if (seconds.value >= MAX_SECONDS) stop()
      }, 1000)
    } catch (cause) {
      error(cause?.name === 'NotAllowedError' ? 'Permite el acceso al micrófono para dictar tu consulta.' : 'No se pudo acceder al micrófono.')
    }
  }
  function stop() { if (recorder?.state === 'recording') recorder.stop() }
  function dispose() {
    disposed = true
    controller?.abort()
    if (recorder?.state === 'recording') {
      recorder.onstop = null
      recorder.stop()
    }
    release()
  }
  if (getCurrentInstance()) onUnmounted(dispose)
  return { state, seconds, elapsed, message, start, stop, dispose }
}
