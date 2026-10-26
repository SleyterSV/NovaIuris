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
export async function loadHistoricalRun(runId, caseId, tool) {
  const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
  if (!uuid.test(String(runId || '')) || !uuid.test(String(caseId || '')) || !['case', 'court'].includes(tool))
    throw new Error('No fue posible recuperar la ejecución solicitada.')
  const data = await requestJson(`/runs/${encodeURIComponent(runId)}/result`)
  const expected = tool === 'court' ? 'court_result' : 'case_result'
  const artifact = data.artifacts?.find(item => item.artifact_type === expected)
  if (data.run?.id !== runId || data.run?.case_id !== caseId || data.run?.tool !== tool || !artifact?.content)
    throw new Error('No fue posible recuperar la ejecución solicitada.')
  let result = artifact.content
  const graph = data.artifacts?.find(item => item.artifact_type === 'graph_snapshot')
  if (tool === 'court' && graph?.content) result = { ...result, graph:graph.content }
  return { run:data.run, result, artifacts:data.artifacts }
}
function pause(signal, milliseconds) {
  return new Promise((resolve, reject) => {
    const abort = () => { clearTimeout(timer); reject(new DOMException('Cancelado', 'AbortError')) }
    const timer = setTimeout(() => { signal?.removeEventListener('abort', abort); resolve() }, milliseconds)
    signal?.addEventListener('abort', abort, { once: true })
    if (signal?.aborted) abort()
  })
}
function taskStateError(code, message) {
  return Object.assign(new Error(message), { code })
}
// One sequential polling loop per task. Reuse always requires an explicit identity.
export async function runAnalysisTask(tool, text, options = {}) {
  if (options.signal?.aborted) throw new DOMException('Cancelado', 'AbortError')
  const caseId = options.caseId || crypto.randomUUID()
  let taskId
  try {
    const started = options.existingTaskId ?
      { task_id:options.existingTaskId, case_id:caseId, tool } :
      await requestJson(tool === 'court' ? '/novacourt/analyze' : '/case/tasks', {
        method:'POST', signal:options.signal,
        body:JSON.stringify({ case_text:text, case_id:caseId, document_ids:options.documentIds || [],
          ...(tool === 'court' && options.reuseTaskId ? {reuse_task_id:options.reuseTaskId} : {}) })
      })
    taskId = started.task_id
    if (!taskId || started.case_id !== caseId || (started.tool && started.tool !== tool))
      throw taskStateError('TASK_IDENTITY_MISMATCH', 'No fue posible registrar la tarea solicitada.')
    options.onTask?.(started)
    let statusFailures = 0
    for (;;) {
      if (options.signal?.aborted) throw new DOMException('Cancelado', 'AbortError')
      let task
      try {
        const path = tool === 'court' ? '/novacourt/results' : '/tasks'
        task = await requestJson(`${path}/${encodeURIComponent(taskId)}?case_id=${encodeURIComponent(caseId)}`, { signal:options.signal })
        statusFailures = 0
      } catch (error) {
        if (tool !== 'court' || options.signal?.aborted || error?.status && error.status < 500 && error.status !== 429) throw error
        statusFailures++
        if (statusFailures >= 5) throw new Error('La tarea continúa procesándose. No se pudo consultar su estado; vuelve a abrirla más tarde.')
        await pause(options.signal, Math.min(10000, 1000 * 2 ** statusFailures))
        continue
      }
      if (task.case_id !== caseId || task.task_id !== taskId || task.tool !== tool)
        throw tool === 'court'
          ? taskStateError('TASK_IDENTITY_MISMATCH', 'No fue posible recuperar esta tarea.')
          : new Error('La respuesta no corresponde al caso enviado.')
      options.onProgress?.(task)
      if (task.status === 'completed') {
        if (task.final_result?.case_id !== caseId) throw new Error('El resultado no corresponde al caso enviado.')
        return normalizeCaseResult(task.final_result)
      }
      if (task.status === 'interrupted') throw tool === 'court'
        ? taskStateError('COURT_TASK_INTERRUPTED', 'La tarea se interrumpió al reiniciar el servidor. Puedes iniciar una nueva ejecución.')
        : new Error('La tarea fue interrumpida y debe ejecutarse nuevamente.')
      if (task.status === 'cancelled') throw tool === 'court'
        ? taskStateError('COURT_TASK_CANCELLED', 'La tarea fue cancelada.')
        : new DOMException('Cancelado', 'AbortError')
      if (task.status === 'failed') throw tool === 'court'
        ? taskStateError('COURT_TASK_FAILED', 'No fue posible completar la tarea. Puedes intentarlo nuevamente.')
        : new Error('No fue posible completar el análisis. Inténtalo nuevamente.')
      await pause(options.signal, options.pollInterval ?? 1500)
    }
  } catch (error) {
    const userCancelled = error?.name === 'AbortError' && options.signal?.aborted && options.signal.reason === 'user'
    if (taskId && userCancelled) {
      try { await requestJson(`/tasks/${encodeURIComponent(taskId)}/cancel`, {
        method:'POST', body:JSON.stringify({case_id:caseId}) }) } catch { /* Server unreachable. */ }
    }
    throw error
  }
}
