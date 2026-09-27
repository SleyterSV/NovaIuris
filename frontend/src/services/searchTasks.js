import { API_URL } from '../config/api.js'

async function responseJson(response) {
  const data = await response.json().catch(() => ({}))
  if (!response.ok || data.success === false) {
    const error = new Error(data.error?.message || data.message || 'No fue posible completar la búsqueda jurídica.')
    error.code = data.error?.code || data.result_status
    throw error
  }
  return data
}

function wait(signal, milliseconds) {
  return new Promise((resolve, reject) => {
    const onAbort = () => { clearTimeout(timer); reject(new DOMException('Cancelado', 'AbortError')) }
    const timer = setTimeout(() => { signal?.removeEventListener('abort', onAbort); resolve() }, milliseconds)
    signal?.addEventListener('abort', onAbort, { once: true })
    if (signal?.aborted) onAbort()
  })
}

// A single sequential loop owns status polling for each search task.
export async function runSearchTask({ query, filters, signal, onProgress, pollInterval = 900 }, fetchImpl = fetch) {
  const request = async (path, options = {}) => responseJson(await fetchImpl(`${API_URL}${path}`, options))
  const started = await request('/search/tasks', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, filtros: filters }) })
  const taskId = started.task_id
  if (!taskId || started.tool !== 'search') throw new Error('La tarea de búsqueda no es válida.')
  onProgress?.({ ...started, status: started.status || 'queued', stage: 'intake' })
  try {
    for (;;) {
      if (signal?.aborted) throw new DOMException('Cancelado', 'AbortError')
      const task = await request(`/search/tasks/${encodeURIComponent(taskId)}`, { signal })
      if (task.task_id !== taskId || task.tool !== 'search') throw new Error('La respuesta no corresponde a esta búsqueda.')
      onProgress?.(task)
      if (task.status === 'completed') return task.final_result || {}
      if (task.status === 'failed') {
        const error = new Error(task.error?.message || 'No fue posible completar la búsqueda jurídica.')
        error.code = task.error?.code
        throw error
      }
      if (task.status === 'cancelled') throw new DOMException('Cancelado', 'AbortError')
      await wait(signal, pollInterval)
    }
  } catch (error) {
    if (error?.name === 'AbortError') await cancelSearchTask(taskId, fetchImpl)
    throw error
  }
}

export async function cancelSearchTask(taskId, fetchImpl = fetch) {
  if (!taskId) return
  try { await fetchImpl(`${API_URL}/search/tasks/${encodeURIComponent(taskId)}/cancel`, { method: 'POST' }) }
  catch { /* A disconnected browser cannot cancel the server task. */ }
}
