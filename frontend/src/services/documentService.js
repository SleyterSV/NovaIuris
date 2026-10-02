import { API_BASE_URL } from '../config/api.js'
import { authHeaders, publicApiError } from '../config/authSession.js'

function delay(signal, milliseconds) {
  return new Promise((resolve, reject) => {
    const abort = () => { clearTimeout(timer); reject(new DOMException('Cancelado', 'AbortError')) }
    const timer = setTimeout(() => { signal?.removeEventListener('abort', abort); resolve() }, milliseconds)
    signal?.addEventListener('abort', abort, { once:true })
    if (signal?.aborted) abort()
  })
}

export async function uploadCaseDocuments(files, caseId, { onProgress = () => {}, onTaskProgress = () => {}, signal } = {}) {
  const started = await new Promise((resolve, reject) => {
    const body = new FormData()
    for (const file of files) body.append('files', file, file.name)
    const request = new XMLHttpRequest()
    const abort = () => request.abort()
    const cleanup = () => signal?.removeEventListener('abort', abort)
    request.open('POST', `${API_BASE_URL}/api/cases/${encodeURIComponent(caseId)}/documents`)
    for (const [key, value] of Object.entries(authHeaders())) request.setRequestHeader(key, value)
    request.upload.onprogress = event => {
      if (event.lengthComputable) onProgress(Math.round(event.loaded / event.total * 100))
    }
    request.upload.onload = () => onProgress(100, 'uploaded')
    request.onerror = () => { cleanup(); reject(new Error('No se pudo conectar con el servidor de documentos.')) }
    request.onabort = () => { cleanup(); reject(new DOMException('Cancelado', 'AbortError')) }
    request.onload = () => {
      cleanup()
      let data
      try { data = JSON.parse(request.responseText) } catch { return reject(new Error('El servidor devolvió una respuesta no válida.')) }
      if (request.status < 200 || request.status >= 300) return reject(publicApiError({ status: request.status }, data))
      if (data.case_id !== caseId || !data.task_id || data.status !== 'queued') return reject(new Error('La tarea documental no corresponde al caso enviado.'))
      resolve(data)
    }
    if (signal?.aborted) return reject(new DOMException('Cancelado', 'AbortError'))
    signal?.addEventListener('abort', abort, { once:true })
    request.send(body)
  })

  for (;;) {
    const response = await fetch(`${API_BASE_URL}/api/cases/${encodeURIComponent(caseId)}/document-tasks/${encodeURIComponent(started.task_id)}`, { signal, headers: authHeaders() })
    let task
    try { task = await response.json() } catch { throw new Error('El servidor devolvió un estado de tarea no válido.') }
    if (!response.ok) throw publicApiError(response, task)
    if (task.case_id !== caseId || task.task_id !== started.task_id || task.tool !== 'documents') {
      throw new Error('El estado no corresponde a la tarea documental del caso.')
    }
    onTaskProgress(task)
    if (['completed', 'failed', 'cancelled', 'interrupted'].includes(task.status)) {
      if (task.status !== 'completed') throw new Error(task.error?.message || 'No se pudo completar la ingesta documental.')
      return task.documents || []
    }
    await delay(signal, 650)
  }
}

export async function listCaseDocuments(caseId) {
  const response = await fetch(`${API_BASE_URL}/api/cases/${encodeURIComponent(caseId)}/documents`, { headers: authHeaders() })
  let data
  try { data = await response.json() } catch { throw new Error('No se pudo leer el corpus de este caso.') }
  if (!response.ok) throw publicApiError(response, data)
  if (data.case_id !== caseId) throw new Error('El corpus recibido no corresponde al caso solicitado.')
  return data.documents || []
}
