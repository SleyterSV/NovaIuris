import assert from 'node:assert/strict'
import { test } from 'node:test'
import { publicUnitReference, startSearchCaseHandoff, listOwnedCases } from '../src/services/searchCaseHandoff.js'
import { runAnalysisTask } from '../src/services/taskService.js'
import { applySearchCaseHandoff, createWorkspace } from '../src/utils/mikeWorkspace.js'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'

const document_id = '22222222-2222-4222-8222-222222222222'
const unit_id = '11111111-1111-4111-8111-111111111111'
const result = { document_id, unit_id, title:'STC', texto:'FORGED TEXT', official_url:'https://example.invalid' }
const response = (payload, status=200) => ({ ok:status < 400, status, json:async () => payload })

test('only the selected V2 locator crosses Search to Case; browser text is discarded', async () => {
  const original = globalThis.fetch
  const requests = []
  globalThis.fetch = async (_url, options) => {
    requests.push(JSON.parse(options.body))
    return response({ success:true, task_id:'task-a', case_id:'CASE-A', tool:'case' }, 202)
  }
  try {
    assert.deepEqual(publicUnitReference(result), { source_scope:'public_legal', document_id, unit_id })
    assert.equal(publicUnitReference({ ...result, unit_id:'bad' }), null)
    const started = await startSearchCaseHandoff({ result, caseMode:'existing', caseId:'CASE-A', caseText:'A'.repeat(60) })
    assert.equal(started.task_id, 'task-a')
    assert.deepEqual(requests[0].public_source_references, [{ source_scope:'public_legal', document_id, unit_id }])
    assert.equal(JSON.stringify(requests[0]).includes('FORGED TEXT'), false)
    assert.equal(requests[0].case_id, 'CASE-A')
    await startSearchCaseHandoff({ result, caseMode:'new', caseText:'N'.repeat(60) })
    assert.equal('case_id' in requests[1], false)
    await assert.rejects(() => startSearchCaseHandoff({ result, caseMode:'existing', caseText:'A'.repeat(60) }))
    assert.equal(requests.length, 2)
  } finally { globalThis.fetch = original }
})

test('owned cases are read from server and the chosen case becomes active explicitly', async () => {
  const original = globalThis.fetch
  globalThis.fetch = async () => response({ success:true, cases:[{case_id:'CASE-A'}] })
  try { assert.deepEqual(await listOwnedCases(), [{case_id:'CASE-A'}]) }
  finally { globalThis.fetch = original }
  const workspace = createWorkspace('workspace-a')
  const oldCase = workspace.caseId
  assert.equal(applySearchCaseHandoff(workspace, null), null)
  assert.equal(workspace.caseId, oldCase)
  assert.deepEqual(applySearchCaseHandoff(workspace,
    { case_id:'CASE-A', task_id:'task-a', caseText:'A'.repeat(60), tool:'case' }),
    { caseId:'CASE-A', documentIds:[], existingTaskId:'task-a' })
  assert.equal(workspace.activeTool, 'case')
  assert.equal(workspace.caseId, 'CASE-A')
})

test('NovaCase resumes the exact task without creating a second analysis', async () => {
  const original = globalThis.fetch
  const paths = []
  globalThis.fetch = async (url) => {
    paths.push(url)
    return response({ success:true, task_id:'task-a', case_id:'CASE-A', tool:'case', status:'completed',
      final_result:{ success:true, case_id:'CASE-A', case:'A'.repeat(60) } })
  }
  try {
    const result = await runAnalysisTask('case', 'A'.repeat(60), { caseId:'CASE-A', existingTaskId:'task-a' })
    assert.equal(result.case_id, 'CASE-A')
    assert.equal(paths.length, 1)
    assert.match(paths[0], /\/tasks\/task-a\?case_id=CASE-A$/)
  } finally { globalThis.fetch = original }
})

test('relevant results expose canonical source detail without a Case CTA; handoff service and dialog remain available', async () => {
  const server = await createServer({ server:{ middlewareMode:true, hmr:false, port:0 },
    appType:'custom', logLevel:'error', optimizeDeps:{ noDiscovery:true, include:[] } })
  try {
    const Results = (await server.ssrLoadModule('/src/components/novasearch/NovaSearchResults.vue')).default
    const Dialog = (await server.ssrLoadModule('/src/components/novasearch/SearchCaseDialog.vue')).default
    const verifiedResult = { ...result, source: { source_id:'SRC-aaaaaaaaaaaaaaaaaaaaaaaa', source_scope:'public_legal',
      provenance_version:'v2', document_id, unit_id, chunk_id:unit_id, title:'STC' } }
    const html = await renderToString(createSSRApp({ render:() => h(Results, { results:[verifiedResult], totalResults:1 }) }))
    assert.match(html, /Ver fuente/)
    assert.doesNotMatch(html, /Analizar en NovaCase/)
    const noLocator = await renderToString(createSSRApp({ render:() => h(Results, { results:[{ title:'Legacy' }], totalResults:1 }) }))
    assert.doesNotMatch(noLocator, /Analizar en NovaCase/)
    const dialog = await renderToString(createSSRApp({ render:() => h(Dialog, { result }) }))
    assert.match(dialog, /Crear caso nuevo/)
    assert.match(dialog, /Usar un caso existente/)
    assert.match(dialog, /Iniciar análisis/)
  } finally { await server.close() }
})
