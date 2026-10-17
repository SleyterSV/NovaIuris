export const TOOLS = ['search', 'case', 'court']

export function normalizeTool(value) {
  return TOOLS.includes(value) ? value : null
}

export function courtTaskIdentity(query) {
  const caseId = query?.case_id, taskId = query?.task_id
  if (query?.tool !== 'court' || typeof caseId !== 'string' || typeof taskId !== 'string' ||
      !/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(caseId) || caseId.includes('..') ||
      !/^[A-Za-z0-9-]{1,128}$/.test(taskId)) return null
  return { caseId, taskId }
}

export function taskIdentityQuery(tool, caseId, taskId) {
  return { tool, case_id:caseId, task_id:taskId }
}

export function createWorkspace(id = crypto.randomUUID()) {
  return {
    id, title: 'Nueva conversación', activeTool: null, caseId: crypto.randomUUID(),
    documentIds: [], searchTaskId: null, caseTaskId: null, courtTaskId: null,
    caseReuse: null, turns: [], createdAt: new Date().toISOString()
  }
}

export function createTurn(role, tool, text, context = {}) {
  return { id:crypto.randomUUID(), role, tool, text, task_id:context.taskId || null,
    case_id:context.caseId || null, document_ids:[...(context.documentIds || [])],
    result_ref:context.resultRef || null, status:context.status || 'created',
    created_at:new Date().toISOString() }
}

export function caseReuseContext(result, taskId, caseText = '') {
  if (!result?.case_id || !taskId) return null
  return {
    caseId: result.case_id,
    caseText: String(result.case || caseText),
    documentIds: Array.isArray(result.document_ids) ? [...result.document_ids] : [],
    reuseTaskId: taskId
  }
}

export function applySearchCaseHandoff(workspace, started) {
  if (!workspace || !started?.case_id || !started?.task_id || !started?.caseText || started.tool !== 'case') return null
  workspace.caseId = started.case_id
  workspace.activeTool = 'case'
  workspace.documentIds = []
  workspace.caseReuse = null
  workspace.caseTaskId = null
  workspace.courtTaskId = null
  return { caseId:started.case_id, documentIds:[], existingTaskId:started.task_id }
}
