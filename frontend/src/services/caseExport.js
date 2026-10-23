import { requestJson } from './taskService.js'
import { API_URL } from '../config/api.js'
import { authHeaders, publicApiError } from '../config/authSession.js'

export function prepareCaseExport(caseId, taskId, request = requestJson) {
  if (!caseId || !taskId) throw new Error('Identidad de tarea incompleta.')
  return request('/export/prepare', { method: 'POST',
    body: JSON.stringify({ case_id: caseId, task_id: taskId, tool: 'case' }) })
}

export async function downloadCaseFile(format, caseId, taskId, fetchImpl = fetch) {
  if (!['pdf', 'docx'].includes(format)) throw new Error('Formato de exportación no disponible.')
  if (!caseId || !taskId) throw new Error('Identidad de tarea incompleta.')
  const response = await fetchImpl(`${API_URL}/export/${format}`, {
    method:'POST', headers:{ 'Content-Type':'application/json', ...authHeaders() },
    body:JSON.stringify({ case_id:caseId, task_id:taskId, tool:'case' })
  })
  if (!response.ok) {
    let body = {}
    try { body = await response.json() } catch { /* Keep the public fallback. */ }
    throw publicApiError(response, body)
  }
  const expected = format === 'pdf' ? 'application/pdf' :
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  if (!response.headers.get('Content-Type')?.includes(expected))
    throw new Error('No fue posible preparar el documento.')
  const blob = await response.blob()
  if (!blob.size) throw new Error('El documento está vacío.')
  return blob
}

export const downloadCasePdf = (caseId, taskId, fetchImpl) =>
  downloadCaseFile('pdf', caseId, taskId, fetchImpl)
export const downloadCaseDocx = (caseId, taskId, fetchImpl) =>
  downloadCaseFile('docx', caseId, taskId, fetchImpl)
