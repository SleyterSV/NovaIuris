import { runAnalysisTask, requestJson } from './taskService.js'
export function analyzeNovaCourtCase(caseText, options = {}) {
  return runAnalysisTask('court', caseText, options)
}
export function getNovaCourtResult(taskId) {
  return requestJson(`/tasks/${encodeURIComponent(taskId)}`)
}
export default { analyzeCase:analyzeNovaCourtCase, getResult:getNovaCourtResult }
