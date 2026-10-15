import { requestJson } from './taskService.js'

export function publicUnitReference(result) {
  if (!result || typeof result.document_id !== 'string' || typeof result.unit_id !== 'string') return null
  const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  if (!uuid.test(result.document_id) || !uuid.test(result.unit_id)) return null
  return { source_scope:'public_legal', document_id:result.document_id, unit_id:result.unit_id }
}

export async function listOwnedCases() {
  const response = await requestJson('/cases')
  return Array.isArray(response.cases) ? response.cases : []
}

export async function startSearchCaseHandoff({ result, caseMode, caseId, caseText, handoffRequestId }) {
  const reference = publicUnitReference(result)
  if (!reference || !['new', 'existing'].includes(caseMode) ||
      (caseMode === 'existing' && !caseId) ||
      typeof caseText !== 'string' || caseText.trim().length < 50) {
    throw new Error('Completa el caso y selecciona una fuente jurídica válida.')
  }
  const payload = { case_mode:caseMode, case_text:caseText.trim(), public_source_references:[reference],
    handoff_request_id:handoffRequestId || crypto.randomUUID() }
  if (caseMode === 'existing') payload.case_id = caseId
  const started = await requestJson('/case/handoff', { method:'POST', body:JSON.stringify(payload) })
  if (!started.task_id || !started.case_id || started.tool !== 'case' ||
      (caseMode === 'existing' && started.case_id !== caseId)) {
    throw new Error('El traspaso no corresponde al caso seleccionado.')
  }
  return started
}
