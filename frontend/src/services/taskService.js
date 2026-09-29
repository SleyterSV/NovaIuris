import { API_URL } from '../config/api.js'
import { normalizeCaseResult } from '../utils/caseContract.js'
export async function requestJson(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options, headers: { 'Content-Type': 'application/json', ...options.headers }
  })
  const data = await response.json()
  if (!response.ok || data.success === false) throw new Error(data.error?.message || data.message || 'No fue posible completar la solicitud.')
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
    for (;;) {
      if (options.signal?.aborted) throw new DOMException('Cancelado', 'AbortError')
      const task = await requestJson(`/tasks/${encodeURIComponent(taskId)}?case_id=${encodeURIComponent(caseId)}`, { signal:options.signal })
      if (task.case_id !== caseId || task.task_id !== taskId || task.tool !== tool) throw new Error('La respuesta no corresponde al caso enviado.')
      options.onProgress?.(task)
      if (task.status === 'completed') {
        if (task.final_result?.case_id !== caseId) throw new Error('El resultado no corresponde al caso enviado.')
        return normalizeCaseResult(task.final_result)
      }
      if (task.status === 'failed' || task.status === 'cancelled') throw new Error(task.error?.message || 'No fue posible completar el análisis.')
      await pause(options.signal, options.pollInterval ?? 1500)
    }
  } catch (error) {
    if (taskId) {
      try { await requestJson(`/tasks/${encodeURIComponent(taskId)}/cancel`, {
        method:'POST', body:JSON.stringify({case_id:caseId}) }) } catch { /* Server unreachable. */ }
    }
    throw error
  }
}
