export const TOOLS = ['search', 'case', 'court']

export function normalizeTool(value) {
  return TOOLS.includes(value) ? value : null
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
