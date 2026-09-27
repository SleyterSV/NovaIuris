import { runAnalysisTask } from './taskService.js'
export function analyzeCase(caseText, options = {}) {
  return runAnalysisTask('case', caseText, options)
}
