import { ref, onBeforeUnmount } from 'vue'
import { analyzeNovaCourtCase } from '@/services/novaCourtService'
export function useNovaCourt() {
  const caseText = ref(''), isAnalyzing = ref(false), error = ref('')
  const progress = ref(0), currentStage = ref(''), stages = ref([]), result = ref(null), warnings = ref([])
  const taskId = ref(null), taskStatus = ref('idle')
  let controller
  let generation = 0
  const cancel = () => controller?.abort('user')
  onBeforeUnmount(() => { generation++; controller?.abort('detach') })
  async function analyzeCase(text = caseText.value, taskOptions = {}) {
    if (isAnalyzing.value) return null
    const currentGeneration = ++generation
    caseText.value = String(text ?? '').trim()
    if (!caseText.value && !taskOptions.existingTaskId) { error.value = 'Ingresa el caso jurídico.'; return null }
    controller = new AbortController()
    isAnalyzing.value = true; error.value = ''; result.value = null
    taskId.value = taskOptions.existingTaskId || null
    taskStatus.value = taskOptions.existingTaskId ? 'restoring' : 'starting'
    currentStage.value = taskOptions.existingTaskId ? 'Recuperando tarea existente…' : ''
    progress.value = 0; stages.value = []; warnings.value = []
    try {
      const completed = await analyzeNovaCourtCase(caseText.value, {
        signal:controller.signal,
        documentIds:taskOptions.documentIds || [],
        caseId:taskOptions.caseId,
        reuseTaskId:taskOptions.reuseTaskId,
        existingTaskId:taskOptions.existingTaskId,
        onTask(task) {
          if (currentGeneration !== generation) return
          taskId.value = task.task_id
          taskOptions.onTask?.(task.task_id)
        },
        onProgress(task) {
          if (currentGeneration !== generation) return
          taskStatus.value = task.status
          progress.value = task.progress; currentStage.value = task.message
          stages.value = task.stages; warnings.value = task.warnings
          if (task.partial_result?.success) result.value = task.partial_result
        }
      })
      if (currentGeneration !== generation) return null
      result.value = completed
      taskStatus.value = 'completed'
      return result.value
    } catch (failure) {
      if (currentGeneration !== generation) return null
      result.value = null
      taskStatus.value = failure?.code === 'COURT_TASK_INTERRUPTED' ? 'interrupted'
        : failure?.code === 'COURT_TASK_CANCELLED' || failure?.name === 'AbortError' ? 'cancelled'
        : failure?.status === 404 || failure?.code === 'TASK_IDENTITY_MISMATCH' ? 'not_found' : 'failed'
      error.value = failure.name === 'AbortError' ? 'Tarea cancelada.' : failure.message
      return null
    } finally { if (currentGeneration === generation) { isAnalyzing.value = false; controller = null } }
  }
  function resetAnalysis() {
    generation++; controller?.abort('detach'); controller = null; isAnalyzing.value = false
    caseText.value = ''; result.value = null; error.value = ''; progress.value = 0
    taskId.value = null; taskStatus.value = 'idle'
    currentStage.value = ''; stages.value = []; warnings.value = []
  }
  function restoreHistoricalResult(snapshot, historicalTaskId = null) {
    generation++
    controller?.abort('historical-restore')
    controller = null
    isAnalyzing.value = false
    error.value = ''
    result.value = snapshot && typeof snapshot === 'object' ? snapshot : null
    taskId.value = historicalTaskId
    taskStatus.value = result.value ? 'completed' : 'not_found'
    progress.value = result.value ? 100 : 0
    currentStage.value = ''
    stages.value = []
    warnings.value = []
    caseText.value = String(result.value?.case || '')
    return result.value
  }
  return { caseText, isAnalyzing, error, progress, currentStage, stages, warnings, result, taskId, taskStatus,
    analyzeCase, cancel, resetAnalysis, restoreHistoricalResult, clearError:() => { error.value = '' } }
}
