import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { createCaseMutationRunner, createOwnedCase, fetchCaseActivity, fetchOwnedCases, filterOwnedCases, updateOwnedCase } from '../src/services/workspaceService.js'

async function loadWorkspaceViews() {
  const server = await createServer({ server:{ middlewareMode:true, hmr:false, port:0 }, appType:'custom',
    logLevel:'error', optimizeDeps:{ noDiscovery:true, include:[] } })
  return { server, CasesView:(await server.ssrLoadModule('/src/components/workspace/CasesView.vue')).default,
    CaseDetailView:(await server.ssrLoadModule('/src/components/workspace/CaseDetailView.vue')).default,
    AccountView:(await server.ssrLoadModule('/src/components/workspace/AccountView.vue')).default }
}

test('Mis casos presenta loading, empty, populated and retryable API error states', async () => {
  const { server, CasesView } = await loadWorkspaceViews()
  try {
    const render = props => renderToString(createSSRApp({ render:() => h(CasesView, props) }))
    const loading = await render({ loading:true })
    assert.match(loading,/Cargando casos/)
    assert.doesNotMatch(loading,/Aún no tienes casos/)
    const empty = await render({ cases:[] })
    assert.match(empty,/Crear un caso/)
    assert.match(empty,/Crear un caso/)
    const populated = await render({ cases:[{ id:'case-uuid', title:'Expediente laboral', status:'active',
      created_at:'2026-10-25T00:00:00Z', updated_at:'2026-10-26T00:00:00Z' }] })
    assert.match(populated,/Expediente laboral/)
    assert.match(populated,/Última actividad/)
    assert.match(populated,/type="search"/)
    assert.match(populated,/Activos[\s\S]*Archivados[\s\S]*Todos/)
    assert.match(populated,/Renombrar/)
    assert.match(populated,/Archivar/)
    const failed = await render({ error:'No fue posible cargar tus casos. Inténtalo nuevamente.' })
    assert.match(failed,/role="alert"/)
    assert.match(failed,/Reintentar/)
    assert.match(failed,/Nuevo caso/)
  } finally { await server.close() }
})

test('case workspace fetches persisted case runs/documents through existing authorized APIs', async () => {
  const calls = []
  const cases = await fetchOwnedCases(async path => { calls.push(path); return { cases:[{ id:'case-a', title:'Caso A' }] } })
  assert.equal(cases[0].title,'Caso A')
  const activity = await fetchCaseActivity(async path => {
    calls.push(path)
    return { runs:[{ id:'run-a', tool:'court', status:'completed' }] }
  }, async id => { assert.equal(id,'case/a'); calls.push('documents'); return [{ filename:'contrato.pdf' }] }, 'case/a')
  assert.deepEqual(calls,['/cases','/cases/case%2Fa/runs','documents'])
  assert.equal(activity.runs[0].id,'run-a')
  assert.equal(activity.documents[0].filename,'contrato.pdf')
  await assert.rejects(fetchOwnedCases(async () => ({ cases:null })),/CASES_RESPONSE_INVALID/)
  await assert.rejects(fetchCaseActivity(async () => { throw new Error('offline') }, async () => [], 'case-a'),/offline/)
})

test('case management creates and updates through existing authenticated API without client ownership fields', async () => {
  const calls = []
  const request = async (path, options) => {
    calls.push([path, options])
    return { case:{ id:'case-a', title:JSON.parse(options.body).title || 'Caso A', status:JSON.parse(options.body).status || 'active' } }
  }
  const created = await createOwnedCase(request, { title:'  Caso A  ', description:'  Contexto  ' })
  assert.equal(created.title,'Caso A')
  await updateOwnedCase(request,'case/a',{ title:'  Caso B  ' })
  await updateOwnedCase(request,'case-a',{ status:'archived' })
  assert.deepEqual(calls.map(([path]) => path),['/cases','/cases/case%2Fa','/cases/case-a'])
  assert.deepEqual(JSON.parse(calls[0][1].body),{ title:'Caso A',description:'Contexto' })
  assert.deepEqual(JSON.parse(calls[1][1].body),{ title:'Caso B' })
  assert.deepEqual(JSON.parse(calls[2][1].body),{ status:'archived' })
  assert.ok(calls.every(([,options]) => !JSON.stringify(options.body).includes('created_by') && !JSON.stringify(options.body).includes('workspace_id')))
  await assert.rejects(createOwnedCase(request,{ title:'   ' }),/CASE_INPUT_INVALID/)
  await assert.rejects(updateOwnedCase(request,'case-a',{ status:'deleted' }),/CASE_INPUT_INVALID/)
})

test('case search and status filters distinguish active, archived and no-result states', () => {
  const cases = [
    { id:'a',title:'Expediente laboral',description:'Contrato CAS',status:'active' },
    { id:'b',title:'Cobro civil',status:'archived' },
    { id:'c',title:'Otro caso',status:'active' }
  ]
  assert.deepEqual(filterOwnedCases(cases,'laboral','active').map(item => item.id),['a'])
  assert.deepEqual(filterOwnedCases(cases,'','archived').map(item => item.id),['b'])
  assert.deepEqual(filterOwnedCases(cases,'','all').map(item => item.id),['a','b','c'])
  assert.deepEqual(filterOwnedCases(cases,'sin coincidencias','all'),[])
})

test('case mutation runner prevents duplicate concurrent create/update requests', async () => {
  const run = createCaseMutationRunner()
  let complete, calls = 0
  const first = run(() => { calls += 1; return new Promise(resolve => { complete = resolve }) })
  await assert.rejects(run(async () => { calls += 1 }),/CASE_MUTATION_PENDING/)
  assert.equal(calls,1)
  complete('saved')
  assert.equal(await first,'saved')
  assert.equal(await run(async () => { calls += 1; return 'next' }),'next')
  assert.equal(calls,2)
})

test('case detail renders documents and historical links from persisted run data', async () => {
  const { server, CaseDetailView } = await loadWorkspaceViews()
  try {
    const html = await renderToString(createSSRApp({ render:() => h(CaseDetailView, {
      caseRecord:{ id:'case-1', title:'Caso de prueba', description:'Antecedentes disponibles' },
      documents:[{ document_id:'doc-1', filename:'Contrato CAS.pdf', processing_status:'Completado' }],
      runs:[{ id:'run-1', tool:'court', status:'completed', created_at:'2026-10-26T10:00:00Z' }]
    }) }))
    assert.match(html,/Caso de prueba/)
    assert.match(html,/Contrato CAS\.pdf/)
    assert.match(html,/NovaCourt/)
    assert.match(html,/run_id=run-1/)
    assert.match(html,/Continuar en NovaCase/)
    assert.match(html,/Renombrar/)
    assert.match(html,/Archivar/)
    assert.doesNotMatch(html,/user_id|workspace_id|access_token/)
  } finally { await server.close() }
})

test('archived case detail offers restoration without dropping historical data', async () => {
  const { server, CaseDetailView } = await loadWorkspaceViews()
  try {
    const html = await renderToString(createSSRApp({ render:() => h(CaseDetailView, {
      caseRecord:{ id:'case-archived', title:'Caso archivado', status:'archived' },
      runs:[{ id:'run-kept', tool:'case', status:'completed', created_at:'2026-10-26T10:00:00Z' }],
      documents:[{ id:'doc-kept', original_filename:'Expediente.pdf' }]
    }) }))
    assert.match(html,/ARCHIVADO/)
    assert.match(html,/Restaurar/)
    assert.match(html,/NovaCase/)
    assert.match(html,/Expediente\.pdf/)
  } finally { await server.close() }
})

test('profile view exposes only account fields and has loading and error recovery', async () => {
  const { server, AccountView } = await loadWorkspaceViews()
  try {
    const render = props => renderToString(createSSRApp({ render:() => h(AccountView, props) }))
    const loading = await render({ loading:true, user:{ email:'a@example.test' } })
    assert.match(loading,/Cargando perfil/)
    const profile = await render({ user:{ email:'a@example.test' }, profile:{ display_name:'Ana Torres', locale:'es' } })
    assert.match(profile,/Ana Torres/)
    assert.match(profile,/a@example\.test/)
    assert.match(profile,/Idioma/)
    const failed = await render({ user:{ email:'a@example.test' }, error:'No fue posible cargar la información del perfil.' })
    assert.match(failed,/Reintentar/)
  } finally { await server.close() }
})

test('authenticated navigation, account menu, logout and historical loading reuse the existing MYKE shell', async () => {
  const [router, view] = await Promise.all([
    readFile(new URL('../src/router/index.js',import.meta.url),'utf8'),
    readFile(new URL('../src/views/MikeView.vue',import.meta.url),'utf8')
  ])
  assert.match(router,/path: "\/cases"[\s\S]*?requiresAuth:true/)
  assert.match(router,/path: "\/cases\/:caseId"[\s\S]*?requiresAuth:true/)
  assert.match(router,/path: "\/account"[\s\S]*?requiresAuth:true/)
  assert.match(view,/class="workspace-nav-link"[\s\S]*?Mis casos/)
  assert.match(view,/role="menuitem" @click="openAccount">Mi cuenta/)
  assert.match(view,/role="menuitem" @click="logout">Cerrar sesión/)
  assert.match(view,/if \(authState\.user\) \{/)
  assert.match(view,/await loadCaseDetail\(route\.params\.caseId\)/)
  assert.match(view,/loadHistoricalRun\(runId, caseId, route\.query\.tool\)/)
})
