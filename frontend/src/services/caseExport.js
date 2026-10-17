import { requestJson } from './taskService.js'

export function prepareCaseExport(caseId, taskId, request = requestJson) {
  if (!caseId || !taskId) throw new Error('Identidad de tarea incompleta.')
  return request('/export/prepare', { method: 'POST',
    body: JSON.stringify({ case_id: caseId, task_id: taskId, tool: 'case' }) })
}
