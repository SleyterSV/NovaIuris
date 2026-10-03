import { ref, onBeforeUnmount } from 'vue'
import { analyzeNovaCourtCase } from '@/services/novaCourtService'
export function useNovaCourt() {
  const caseText = ref(''), isAnalyzing = ref(false), error = ref('')
  const progress = ref(0), currentStage = ref(''), stages = ref([]), result = ref(null), warnings = ref([])
  let controller
  let generation = 0
  const cancel = () => controller?.abort()
  onBeforeUnmount(cancel)
  async function analyzeCase(text = caseText.value, taskOptions = {}) {
    if (isAnalyzing.value) return null
    const currentGeneration = ++generation
    caseText.value = String(text ?? '').trim()
    if (!caseText.value) { error.value = 'Ingresa el caso jurídico.'; return null }
    controller = new AbortController()
    isAnalyzing.value = true; error.value = ''; result.value = null
    progress.value = 0; stages.value = []; warnings.value = []
    try {
      const completed = await analyzeNovaCourtCase(caseText.value, {
        signal:controller.signal,
        documentIds:taskOptions.documentIds || [],
        caseId:taskOptions.caseId,
        reuseTaskId:taskOptions.reuseTaskId,
        onProgress(task) {
          if (currentGeneration !== generation) return
          if (task.task_id) taskOptions.onTask?.(task.task_id)
          progress.value = task.progress; currentStage.value = task.message
          stages.value = task.stages; warnings.value = task.warnings
          if (task.partial_result?.success) result.value = task.partial_result
        }
      })
      if (currentGeneration !== generation) return null
      result.value = completed
      return result.value
    } catch (failure) {
      if (currentGeneration !== generation) return null
      error.value = failure.name === 'AbortError' ? 'Tarea cancelada.' : failure.message
      return null
    } finally { if (currentGeneration === generation) { isAnalyzing.value = false; controller = null } }
  }
  function resetAnalysis() {
    generation++; cancel(); controller = null; isAnalyzing.value = false
    caseText.value = ''; result.value = null; error.value = ''; progress.value = 0
    currentStage.value = ''; stages.value = []; warnings.value = []
  }
  return { caseText, isAnalyzing, error, progress, currentStage, stages, warnings, result,
    analyzeCase, cancel, resetAnalysis, clearError:() => { error.value = '' } }
}
