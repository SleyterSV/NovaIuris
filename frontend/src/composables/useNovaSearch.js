import { ref, reactive, onBeforeUnmount } from 'vue'
import { runSearchTask } from '../services/searchTasks.js'

export function useNovaSearch() {
  const searchQuery = ref('')
  const isSearching = ref(false)
  const searchError = ref(null)
  const searchResults = ref([])
  const totalResults = ref(0)
  const searchTime = ref(null)
  const answer = ref('')
  const sources = ref([])
  const citations = ref([])
  const sourceWarnings = ref([])
  const resultStatus = ref('')
  const analysis = ref({})
  const context = ref('')
  const normalizedQuery = ref('')
  const isFallbackResponse = ref(false)
  const fallbackDisclaimer = ref('')
  const searchStage = ref('')
  const searchProgress = ref(0)
  const progressStages = ref([])
  const searchCounts = ref({})
  const filters = reactive({ modulo: 'Todos', solo_vigentes: true })
  let controller = null
  let taskId = null
  let requestId = 0

  function reset() {
    searchError.value = null
    answer.value = ''
    sources.value = []
    citations.value = []
    sourceWarnings.value = []
    resultStatus.value = ''
    analysis.value = {}
    context.value = ''
    normalizedQuery.value = ''
    searchResults.value = []
    totalResults.value = 0
    searchTime.value = null
    isFallbackResponse.value = false
    fallbackDisclaimer.value = ''
    searchStage.value = ''
    searchProgress.value = 0
    progressStages.value = []
    searchCounts.value = {}
  }

  function cancelSearch() {
    controller?.abort()
  }

  async function performSearch(onTask = null) {
    const query = searchQuery.value.trim()
    if (query.length < 5) {
      searchError.value = query ? 'Describe con mayor detalle la consulta jurídica.' : 'Escribe una consulta jurídica antes de buscar.'
      return
    }

    cancelSearch()
    reset()
    const activeId = ++requestId
    const activeController = new AbortController()
    controller = activeController
    taskId = null
    isSearching.value = true
    const startedAt = performance.now()
    try {
      const data = await runSearchTask({ query, filters: { ...filters }, signal: activeController.signal,
        onProgress: task => {
          if (activeId !== requestId) return
          if (task.task_id) { taskId = task.task_id; onTask?.(task.task_id) }
          searchStage.value = task.stage || ''
          searchProgress.value = Number.isFinite(task.progress) ? task.progress : 0
          progressStages.value = task.stages || []
          searchCounts.value = task.counts || {}
        } })
      if (activeId === requestId) {
        searchResults.value = data.documents || []
        totalResults.value = data.documents?.length || 0
        answer.value = data.answer || ''
        sources.value = data.sources || []
        citations.value = data.citations || []
        sourceWarnings.value = data.warnings || []
        resultStatus.value = data.result_status || 'completed'
        analysis.value = data.analysis || {}
        context.value = data.context || ''
        normalizedQuery.value = data.query_normalizada || query
        searchCounts.value = data.metadata?.counts || searchCounts.value
        searchTime.value = Math.max(0, Math.round((performance.now() - startedAt) / 1000))
        isFallbackResponse.value = !searchResults.value.length
        fallbackDisclaimer.value = ''
      }
    } catch (error) {
      if (error?.name !== 'AbortError' && activeId === requestId) {
        searchError.value = error?.message || 'No pudimos completar la búsqueda jurídica.'
        resultStatus.value = error?.code === 'SEARCH_FAILED' ? 'search_failed' : 'failed'
      }
    } finally {
      if (activeId === requestId) {
        isSearching.value = false
        controller = null
        taskId = null
      }
    }
  }

  function updateFilter(key, value) {
    if (Object.prototype.hasOwnProperty.call(filters, key)) filters[key] = value
  }

  function clearSearch() {
    requestId++
    cancelSearch()
    controller = null
    taskId = null
    isSearching.value = false
    searchQuery.value = ''
    reset()
  }

  onBeforeUnmount(() => { requestId++; cancelSearch() })

  return { searchQuery, isSearching, searchError, searchResults, totalResults, searchTime,
    answer, sources, citations, sourceWarnings, resultStatus, analysis, context, normalizedQuery,
    isFallbackResponse, fallbackDisclaimer, searchStage, searchProgress, progressStages,
    searchCounts, filters, performSearch, cancelSearch, updateFilter, clearSearch }
}
