import { runAnalysisTask, requestJson } from './taskService.js'
export function analyzeNovaCourtCase(caseText, options = {}) {
  return runAnalysisTask('court', caseText, options)
}
export function getNovaCourtResult(taskId, caseId) {
  if (!caseId) throw new Error('Se requiere el identificador del caso.')
  return requestJson(`/tasks/${encodeURIComponent(taskId)}?case_id=${encodeURIComponent(caseId)}`)
}
export default { analyzeCase:analyzeNovaCourtCase, getResult:getNovaCourtResult }
