import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { fetchCaseActivity, fetchOwnedCases } from '../src/services/workspaceService.js'

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
    assert.match(empty,/Aún no tienes casos/)
    assert.match(empty,/Crear un análisis/)
    const populated = await render({ cases:[{ id:'case-uuid', title:'Expediente laboral', status:'active',
      created_at:'2026-10-25T00:00:00Z', updated_at:'2026-10-26T00:00:00Z' }] })
    assert.match(populated,/Expediente laboral/)
    assert.match(populated,/Última actividad/)
    const failed = await render({ error:'No fue posible cargar tus casos. Inténtalo nuevamente.' })
    assert.match(failed,/role="alert"/)
    assert.match(failed,/Reintentar/)
    assert.match(failed,/Nuevo análisis/)
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
    assert.doesNotMatch(html,/user_id|workspace_id|access_token/)
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
