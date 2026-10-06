import { API_URL } from '../config/api.js'
import { authHeaders, publicApiError } from '../config/authSession.js'
import { normalizeCaseResult } from '../utils/caseContract.js'
export async function requestJson(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options, headers: { 'Content-Type': 'application/json', ...authHeaders(), ...options.headers }
  })
  const data = await response.json()
  if (!response.ok || data.success === false) throw publicApiError(response, data)
  return data
}
function pause(signal, milliseconds) {
  return new Promise((resolve, reject) => {
    const abort = () => { clearTimeout(timer); reject(new DOMException('Cancelado', 'AbortError')) }
    const timer = setTimeout(() => { signal?.removeEventListener('abort', abort); resolve() }, milliseconds)
    signal?.addEventListener('abort', abort, { once: true })
    if (signal?.aborted) abort()
  })
}
// One sequential polling loop per task. Reuse always requires an explicit identity.
export async function runAnalysisTask(tool, text, options = {}) {
  if (options.signal?.aborted) throw new DOMException('Cancelado', 'AbortError')
  const caseId = options.caseId || crypto.randomUUID()
  let taskId
  try {
    const started = await requestJson(tool === 'court' ? '/novacourt/analyze' : '/case/tasks', {
      method:'POST', signal:options.signal,
      body:JSON.stringify({ case_text:text, case_id:caseId, document_ids:options.documentIds || [],
        ...(tool === 'court' && options.reuseTaskId ? {reuse_task_id:options.reuseTaskId} : {}) })
    })
    taskId = started.task_id
    if (started.case_id !== caseId) throw new Error('La tarea no corresponde al caso enviado.')
    options.onTask?.(started)
    let statusFailures = 0
    for (;;) {
      if (options.signal?.aborted) throw new DOMException('Cancelado', 'AbortError')
      let task
      try {
        task = await requestJson(`/tasks/${encodeURIComponent(taskId)}?case_id=${encodeURIComponent(caseId)}`, { signal:options.signal })
        statusFailures = 0
      } catch (error) {
        if (tool !== 'court' || options.signal?.aborted || error?.status && error.status < 500 && error.status !== 429) throw error
        statusFailures++
        if (statusFailures >= 5) throw new Error('La tarea continúa procesándose. No se pudo consultar su estado; vuelve a abrirla más tarde.')
        await pause(options.signal, Math.min(10000, 1000 * 2 ** statusFailures))
        continue
      }
      if (task.case_id !== caseId || task.task_id !== taskId || task.tool !== tool) throw new Error('La respuesta no corresponde al caso enviado.')
      options.onProgress?.(task)
      if (task.status === 'completed') {
        if (task.final_result?.case_id !== caseId) throw new Error('El resultado no corresponde al caso enviado.')
        return normalizeCaseResult(task.final_result)
      }
      if (task.status === 'interrupted') throw new Error('La tarea fue interrumpida y debe ejecutarse nuevamente.')
      if (task.status === 'cancelled') throw new DOMException('Cancelado', 'AbortError')
      if (task.status === 'failed') throw new Error('No fue posible completar el análisis. Inténtalo nuevamente.')
      await pause(options.signal, options.pollInterval ?? 1500)
    }
  } catch (error) {
    if (taskId && (tool !== 'court' || error?.name === 'AbortError' && options.signal?.reason !== 'detach')) {
      try { await requestJson(`/tasks/${encodeURIComponent(taskId)}/cancel`, {
        method:'POST', body:JSON.stringify({case_id:caseId}) }) } catch { /* Server unreachable. */ }
    }
    throw error
  }
}
