import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { runSearchTask } from '../src/services/searchTasks.js'

const response = (data, status = 200) => ({ ok: status < 400, status, json: async () => data })

test('search task performs one sequential poll loop and reports backend stages', async () => {
  const calls = []
  let active = 0
  let maxActive = 0
  let statusIndex = 0
  const fetcher = async (url, options) => {
    calls.push({ url, options })
    active++
    maxActive = Math.max(maxActive, active)
    await Promise.resolve()
    active--
    if (url.endsWith('/search/tasks')) return response({ success: true, task_id: 'TASK-1', tool: 'search', status: 'queued' }, 202)
    statusIndex++
    if (statusIndex === 1) return response({ success: true, task_id: 'TASK-1', tool: 'search', status: 'running',
      stage: 'retrieval', progress: 30, counts: { retrieved_count: 18 }, stages: [{ id: 'retrieval', status: 'running' }] })
    return response({ success: true, task_id: 'TASK-1', tool: 'search', status: 'completed',
      final_result: { result_status: 'no_results', documents: [], metadata: { timings_ms: { total: 7 } } } })
  }
  const updates = []
  const result = await runSearchTask({ query: 'consulta legal', filters: { modulo: 'Civil', solo_vigentes: true },
    pollInterval: 0, onProgress: task => updates.push(task) }, fetcher)
  assert.equal(result.result_status, 'no_results')
  assert.equal(maxActive, 1)
  assert.deepEqual(JSON.parse(calls[0].options.body).filtros, { modulo: 'Civil', solo_vigentes: true })
  assert.equal(updates[0].stage, 'intake')
  assert.equal(updates[1].counts.retrieved_count, 18)
})

test('search task keeps infrastructure failure distinct from no results', async () => {
  const fetcher = async url => url.endsWith('/search/tasks')
    ? response({ success: true, task_id: 'TASK-FAIL', tool: 'search' }, 202)
    : response({ success: true, task_id: 'TASK-FAIL', tool: 'search', status: 'failed',
      error: { code: 'SEARCH_FAILED', message: 'No se pudo consultar el repositorio jurídico.' } })
  await assert.rejects(runSearchTask({ query: 'consulta legal', filters: {}, pollInterval: 0 }, fetcher), error => {
    assert.equal(error.code, 'SEARCH_FAILED')
    return true
  })
})

test('aborting a search polling loop requests cooperative backend cancellation', async () => {
  const controller = new AbortController()
  const urls = []
  const fetcher = async (url) => {
    urls.push(url)
    if (url.endsWith('/search/tasks')) return response({ success: true, task_id: 'TASK-CANCEL', tool: 'search' }, 202)
    if (url.endsWith('/cancel')) return response({ success: true, status: 'cancelled' })
    return response({ success: true, task_id: 'TASK-CANCEL', tool: 'search', status: 'running', progress: 0 })
  }
  const running = runSearchTask({ query: 'consulta legal', filters: {}, signal: controller.signal,
    pollInterval: 1000, onProgress: task => { if (task.status === 'running') controller.abort() } }, fetcher)
  await assert.rejects(running, { name: 'AbortError' })
  assert.ok(urls.some(url => url.endsWith('/search/tasks/TASK-CANCEL/cancel')))
})

test('NovaSearch has no timer-driven progress and consumes route query without auto-submit', async () => {
  const composable = await readFile(new URL('../src/composables/useNovaSearch.js', import.meta.url), 'utf8')
  const view = await readFile(new URL('../src/views/NovaSearchView.vue', import.meta.url), 'utf8')
  const filters = await readFile(new URL('../src/components/novasearch/NovaSearchFilters.vue', import.meta.url), 'utf8')
  assert.ok(!composable.includes('setInterval'))
  assert.ok(composable.includes('progressStages'))
  assert.match(view, /route\.query\.q/)
  assert.ok(!view.includes('performSearch()'))
  assert.ok(filters.includes("update('modulo'"))
  assert.ok(filters.includes("update('solo_vigentes'"))
  assert.ok(!filters.includes('tipoDocumento'))
  assert.ok(!filters.includes('fecha'))
})
