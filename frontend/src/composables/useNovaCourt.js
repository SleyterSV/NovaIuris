import { ref, onBeforeUnmount } from 'vue'
import { analyzeNovaCourtCase } from '@/services/novaCourtService'
export function useNovaCourt() {
  const caseText = ref(''), isAnalyzing = ref(false), error = ref('')
  const progress = ref(0), currentStage = ref(''), stages = ref([]), result = ref(null), warnings = ref([])
  let controller
  const cancel = () => controller?.abort()
  onBeforeUnmount(cancel)
  async function analyzeCase(text = caseText.value, taskOptions = {}) {
    if (isAnalyzing.value) return null
    caseText.value = String(text ?? '').trim()
    if (!caseText.value) { error.value = 'Ingresa el caso jurídico.'; return null }
    controller = new AbortController()
    isAnalyzing.value = true; error.value = ''; result.value = null
    progress.value = 0; stages.value = []; warnings.value = []
    try {
      result.value = await analyzeNovaCourtCase(caseText.value, {
        signal:controller.signal,
        documentIds:taskOptions.documentIds || [],
        caseId:taskOptions.caseId,
        onProgress(task) {
          progress.value = task.progress; currentStage.value = task.message
          stages.value = task.stages; warnings.value = task.warnings
          if (task.partial_result?.success) result.value = task.partial_result
        }
      })
      return result.value
    } catch (failure) {
      error.value = failure.name === 'AbortError' ? 'Tarea cancelada.' : failure.message
      return null
    } finally { isAnalyzing.value = false; controller = null }
  }
  function resetAnalysis() { cancel(); caseText.value = ''; result.value = null; error.value = '' }
  return { caseText, isAnalyzing, error, progress, currentStage, stages, warnings, result,
    analyzeCase, cancel, resetAnalysis, clearError:() => { error.value = '' } }
}
