import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { appendTranscript, useVoiceInput } from '../src/composables/useVoiceInput.js'

test('transcript preserves existing draft for user review', () => {
  assert.equal(appendTranscript('Primera cuestión', 'Segunda cuestión'), 'Primera cuestión\nSegunda cuestión')
  assert.equal(appendTranscript('', 'Consulta jurídica'), 'Consulta jurídica')
})

test('voice lifecycle records, transcribes, and inserts text without sending', async () => {
  let instance, requested = 0, transcriptions = 0
  let finishTranscription
  class Recorder {
    static isTypeSupported(type) { return type === 'audio/webm' }
    constructor() { this.state = 'inactive'; instance = this }
    start() { this.state = 'recording' }
    stop() {
      this.state = 'inactive'
      this.ondataavailable({ data:new Blob(['voice'], { type:'audio/webm' }) })
      this.onstop()
    }
  }
  const texts = []
  const voice = useVoiceInput(text => texts.push(text), {
    Recorder,
    media:{ async getUserMedia() { requested++; return { getTracks:() => [{ stop() {} }] } } },
    transcribe(blob) { transcriptions++; assert.equal(blob.type,'audio/webm'); return new Promise(resolve => { finishTranscription = resolve }) }
  })
  await voice.start()
  assert.equal(voice.state.value,'recording')
  assert.equal(requested,1)
  voice.stop()
  assert.equal(voice.state.value,'transcribing')
  finishTranscription('Consulta jurídica')
  await new Promise(resolve => setTimeout(resolve,0))
  assert.equal(voice.state.value,'completed')
  assert.deepEqual(texts,['Consulta jurídica'])
  assert.equal(transcriptions,1)
  voice.dispose()
})

test('voice permission denial is a public Spanish error', async () => {
  const voice = useVoiceInput(() => {}, {
    Recorder:class { static isTypeSupported() { return true } },
    media:{ async getUserMedia() { throw Object.assign(new Error('raw device path'), { name:'NotAllowedError' }) } }
  })
  await voice.start()
  assert.equal(voice.state.value,'error')
  assert.match(voice.message.value,/Permite el acceso/)
  assert.doesNotMatch(voice.message.value,/raw device path/)
})

test('home discovery and voice controls are wired without exposing implementation IDs', async () => {
  const view = await readFile(new URL('../src/views/MikeView.vue',import.meta.url),'utf8')
  assert.match(view,/@pointerenter="openToolCard\(key,\$event\)"/)
  assert.match(view,/@focusin="openToolCard\(key,\$event\)"/)
  assert.match(view,/@keydown="onDiscoveryKeydown"/)
  assert.match(view,/@click="openToolDetail"/)
  assert.match(view,/voice\.state\.value === 'recording'/)
  assert.match(view,/voice\.stop\(\) : voice\.start\(\)/)
  assert.match(view,/Escribe tu consulta jurídica aquí/)
  assert.match(view,/Normativa, jurisprudencia y doctrina/)
  assert.doesNotMatch(view,/Entrada por voz próximamente/)
})
