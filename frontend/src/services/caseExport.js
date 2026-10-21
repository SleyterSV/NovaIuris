import { requestJson } from './taskService.js'
import { API_URL } from '../config/api.js'
import { authHeaders, publicApiError } from '../config/authSession.js'

export function prepareCaseExport(caseId, taskId, request = requestJson) {
  if (!caseId || !taskId) throw new Error('Identidad de tarea incompleta.')
  return request('/export/prepare', { method: 'POST',
    body: JSON.stringify({ case_id: caseId, task_id: taskId, tool: 'case' }) })
}

export async function downloadCasePdf(caseId, taskId, fetchImpl = fetch) {
  if (!caseId || !taskId) throw new Error('Identidad de tarea incompleta.')
  const response = await fetchImpl(`${API_URL}/export/pdf`, {
    method:'POST', headers:{ 'Content-Type':'application/json', ...authHeaders() },
    body:JSON.stringify({ case_id:caseId, task_id:taskId, tool:'case' })
  })
  if (!response.ok) {
    let body = {}
    try { body = await response.json() } catch { /* Keep the public fallback. */ }
    throw publicApiError(response, body)
  }
  if (!response.headers.get('Content-Type')?.includes('application/pdf'))
    throw new Error('No fue posible preparar el PDF.')
  return response.blob()
}
