import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { runAnalysisTask } from '../src/services/taskService.js'
import { courtTaskIdentity, taskIdentityQuery } from '../src/utils/mikeWorkspace.js'

const completed = { success:true, task_id:'TASK-A', case_id:'CASE-A', tool:'court',
  status:'completed', final_result:{ success:true, case_id:'CASE-A', court_status:'completed',
    simulation:{status:'ready'}, graph:{status:'ready'} } }

test('Court publishes HTTP 202 identity before its first status request', async () => {
  const original = globalThis.fetch, events = []
  globalThis.fetch = async (url) => {
    if (String(url).endsWith('/novacourt/analyze')) {
      events.push('start')
      return Response.json({success:true, task_id:'TASK-A', case_id:'CASE-A', tool:'court'}, {status:202})
    }
    events.push('poll')
    return Response.json(completed)
  }
  try {
    const result = await runAnalysisTask('court', 'Caso', {
      caseId:'CASE-A', onTask:task => events.push(`identity:${task.case_id}:${task.task_id}`) })
    assert.equal(result.case_id, 'CASE-A')
    assert.deepEqual(events, ['start', 'identity:CASE-A:TASK-A', 'poll'])
  } finally { globalThis.fetch = original }
})

test('Court route identity contains only safe identifiers', () => {
  const query = taskIdentityQuery('court', 'CASE-A', 'TASK-A')
  assert.deepEqual(query, {tool:'court', case_id:'CASE-A', task_id:'TASK-A'})
  assert.deepEqual(courtTaskIdentity(query), {caseId:'CASE-A', taskId:'TASK-A'})
  assert.equal(courtTaskIdentity({...query, case_id:'../other'}), null)
  assert.equal(courtTaskIdentity({...query, task_id:''}), null)
})

test('reopening a completed Court task reads the same result without a POST', async () => {
  const original = globalThis.fetch, methods = [], statuses = []
  globalThis.fetch = async (url, options = {}) => {
    methods.push(options.method || 'GET')
    assert.match(String(url), /\/novacourt\/results\/TASK-A\?case_id=CASE-A$/)
    return Response.json(completed)
  }
  try {
    const result = await runAnalysisTask('court', '', {caseId:'CASE-A', existingTaskId:'TASK-A',
      onProgress:task => statuses.push(task.status)})
    assert.equal(result.court_status, 'completed')
    assert.deepEqual(statuses, ['completed'])
    assert.deepEqual(methods, ['GET'])
  } finally { globalThis.fetch = original }
})

test('reopening processing Court resumes polling of one task without a POST', async () => {
  const original = globalThis.fetch, methods = [], statuses = []
  let count = 0
  globalThis.fetch = async (url, options = {}) => {
    methods.push(options.method || 'GET')
    assert.match(String(url), /\/novacourt\/results\/TASK-A\?case_id=CASE-A$/)
    return Response.json(++count === 1 ? {...completed, status:'processing', final_result:null} : completed)
  }
  try {
    await runAnalysisTask('court', '', {caseId:'CASE-A', existingTaskId:'TASK-A',
      pollInterval:0, onProgress:task => statuses.push(task.status)})
    assert.deepEqual(statuses, ['processing', 'completed'])
    assert.deepEqual(methods, ['GET', 'GET'])
  } finally { globalThis.fetch = original }
})

test('Court terminal states and identity mismatch reject without exposing result', async () => {
  const original = globalThis.fetch
  try {
    for (const [status, code] of [['interrupted','COURT_TASK_INTERRUPTED'],
                                   ['failed','COURT_TASK_FAILED'], ['cancelled','COURT_TASK_CANCELLED']]) {
      globalThis.fetch = async () => Response.json({...completed, status, final_result:null,
        error:{message:'private provider detail'}})
      await assert.rejects(runAnalysisTask('court', '', {caseId:'CASE-A', existingTaskId:'TASK-A'}),
        error => error.code === code && !error.message.includes('private provider detail'))
    }
    globalThis.fetch = async () => Response.json({...completed, case_id:'CASE-B',
      final_result:{case_id:'CASE-B', secret:'private'}})
    await assert.rejects(runAnalysisTask('court', '', {caseId:'CASE-A', existingTaskId:'TASK-A'}),
      error => error.code === 'TASK_IDENTITY_MISMATCH' && !error.message.includes('private'))
    globalThis.fetch = async () => Response.json({success:false,
      error:{code:'TASK_NOT_FOUND',message:'No se encontró la tarea.'}}, {status:404})
    await assert.rejects(runAnalysisTask('court', '', {caseId:'CASE-A', existingTaskId:'TASK-A'}))
  } finally { globalThis.fetch = original }
})

test('local detach never cancels; explicit user cancellation sends scoped cancel', async () => {
  const original = globalThis.fetch
  try {
    for (const [reason, expectedCancels] of [['detach',0], ['user',1]]) {
      const controller = new AbortController(), calls = []
      globalThis.fetch = async (url, options = {}) => {
        calls.push({url:String(url), method:options.method || 'GET', body:options.body})
        if (String(url).endsWith('/novacourt/analyze'))
          return Response.json({success:true, task_id:'TASK-A', case_id:'CASE-A', tool:'court'}, {status:202})
        if (String(url).endsWith('/cancel')) return Response.json({success:true})
        return Response.json({...completed, status:'processing', final_result:null})
      }
      await assert.rejects(runAnalysisTask('court', 'Caso', {caseId:'CASE-A', signal:controller.signal,
        onTask:() => controller.abort(reason)}), {name:'AbortError'})
      const cancels = calls.filter(call => call.url.endsWith('/cancel'))
      assert.equal(cancels.length, expectedCancels)
      if (expectedCancels) assert.deepEqual(JSON.parse(cancels[0].body), {case_id:'CASE-A'})
    }
  } finally { globalThis.fetch = original }
})

test('Court workspace restores one request and exposes professional task states', async () => {
  const [mike, court, composable, router] = await Promise.all([
    readFile(new URL('../src/views/MikeView.vue', import.meta.url), 'utf8'),
    readFile(new URL('../src/views/NovaCourtView.vue', import.meta.url), 'utf8'),
    readFile(new URL('../src/composables/useNovaCourt.js', import.meta.url), 'utf8'),
    readFile(new URL('../src/router/index.js', import.meta.url), 'utf8')
  ])
  assert.match(mike, /courtTaskIdentity\(route\.query\)/)
  assert.match(mike, /existingTaskId:taskId/)
  assert.match(mike, /taskIdentityQuery\(state\.tool, turn\.case_id, state\.taskId\)/)
  assert.match(court, /if \(request\.existingTaskId\)/)
  assert.match(court, /restoredIdentity === identity/)
  assert.match(court, /TAREA INTERRUMPIDA|TAREA CANCELADA|TAREA NO DISPONIBLE/)
  assert.match(court, /Iniciar nueva ejecución/)
  assert.match(composable, /onTask\(task\)/)
  assert.match(composable, /controller\?\.abort\('detach'\)/)
  assert.match(composable, /controller\?\.abort\('user'\)/)
  assert.match(router, /typeof to\.query\.task_id === 'string'/)
})
