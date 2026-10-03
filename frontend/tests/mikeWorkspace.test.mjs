import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createWorkspace, createTurn, normalizeTool, caseReuseContext } from '../src/utils/mikeWorkspace.js'
import { authHeaders } from '../src/config/authSession.js'
import { authState, startAuth, signOut, stopAuth } from '../src/config/supabaseSession.js'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { createRouter, createMemoryHistory } from 'vue-router'

test('workspace tool normalization and New Chat isolate Case A from Case B', () => {
  assert.equal(normalizeTool('case'),'case')
  assert.equal(normalizeTool('unknown'),null)
  const a = createWorkspace('A')
  a.documentIds = ['private-A']
  a.caseTaskId = 'task-A'
  a.courtTaskId = 'court-A'
  a.caseReuse = { caseId:a.caseId }
  a.turns.push(createTurn('assistant','case','',{ caseId:a.caseId, documentIds:['private-A'], taskId:'task-A' }))
  const b = createWorkspace('B')
  assert.notEqual(a.caseId,b.caseId)
  assert.deepEqual(b.documentIds,[])
  assert.deepEqual(b.turns,[])
  assert.equal(b.caseTaskId,null)
  assert.equal(b.courtTaskId,null)
  assert.equal(b.caseReuse,null)
  assert.equal(a.turns[0].task_id,'task-A')
})

test('Case to Court reuse preserves canonical case, documents, text and task', () => {
  assert.deepEqual(caseReuseContext({ case_id:'case-A', document_ids:['doc-A'] },'task-A','hechos'),
    { caseId:'case-A', caseText:'hechos', documentIds:['doc-A'], reuseTaskId:'task-A' })
  assert.equal(caseReuseContext({ case_id:'case-A' },null),null)
})

test('auth startup, token update, and logout clear Bearer state', async () => {
  let notify
  const fake = { auth:{
    onAuthStateChange(callback) { notify=callback; return { data:{ subscription:{ unsubscribe() {} } } } },
    async getSession() { return { data:{ session:{ access_token:'initial', user:{ id:'A' } } }, error:null } },
    async signOut() { notify('SIGNED_OUT',null); return { error:null } }
  } }
  await startAuth(fake)
  assert.equal(authState.user.id,'A')
  assert.equal(authHeaders().Authorization,'Bearer initial')
  notify('TOKEN_REFRESHED',{ access_token:'refreshed', user:{ id:'A' } })
  assert.equal(authHeaders().Authorization,'Bearer refreshed')
  await signOut()
  assert.deepEqual(authHeaders(),{})
  assert.equal(authState.user,null)
  stopAuth()
})

test('routes enter MYKE and turns retain embedded panels', async () => {
  const router = await readFile(new URL('../src/router/index.js',import.meta.url),'utf8')
  const view = await readFile(new URL('../src/views/MikeView.vue',import.meta.url),'utf8')
  assert.match(router,/path: "\/"[\s\S]*?component: MikeView/)
  assert.match(router,/path: "\/mike"[\s\S]*?redirect: to =>/)
  for (const path of ['/novasearch','/novacase','/novacourt']) assert.ok(router.includes(`path: "${path}"`))
  assert.match(router,/path:'\/about'/)
  assert.match(view,/v-for="turn in workspace.turns"/)
  assert.match(view,/:request="turn.request"/)
  assert.match(view,/@reuse-case="reuseCase"/)
  assert.match(view,/workspace.value.activeTool = tool/)
  assert.match(view,/@click="selectTool\(key\)"/)
  assert.match(view,/@use="selectTool\(detailTool,false\); detailTool = null"/)
  assert.match(view,/@click="detailTool = key"/)
  assert.match(view,/aria-haspopup="listbox" :aria-expanded="selectorOpen"/)
  assert.match(view,/if \(!canSend.value\) return/)
})

test('MYKE home SSR renders controls without activating a tool request', async () => {
  const server = await createServer({ server:{ middlewareMode:true, hmr:false, port:0 }, appType:'custom',
    logLevel:'error', optimizeDeps:{ noDiscovery:true, include:[] } })
  try {
    const component = (await server.ssrLoadModule('/src/views/MikeView.vue')).default
    const router = createRouter({ history:createMemoryHistory(), routes:[{ path:'/', component }] })
    await router.push('/')
    await router.isReady()
    const app = createSSRApp({ render:() => h(component) })
    app.use(router)
    const html = await renderToString(app)
    assert.match(html,/Nuevo chat/)
    assert.match(html,/Hola, soy/)
    assert.match(html,/MYKE/)
    assert.match(html,/Buscar jurisprudencia/)
    assert.match(html,/Analizar un expediente/)
    assert.match(html,/Simular un caso/)
    assert.match(html,/Escribe tu consulta jurídica aquí/)
  } finally { await server.close() }
})

test('TraceabilityChain renders only explicit relation IDs and source selection affordance', async () => {
  const server = await createServer({ server:{ middlewareMode:true, hmr:false, port:0 }, appType:'custom',
    logLevel:'error', optimizeDeps:{ noDiscovery:true, include:[] } })
  try {
    const component = (await server.ssrLoadModule('/src/components/common/TraceabilityChain.vue')).default
    const empty = await renderToString(createSSRApp({ render:() => h(component) }))
    assert.doesNotMatch(empty,/Cadena de trazabilidad/)
    const linked = await renderToString(createSSRApp({ render:() => h(component,{
      issue:{ issue_id:'issue-A', text:'Despido' }, facts:[{ fact_id:'fact-A', text:'Carta recibida' }],
      sources:[{ source_id:'source-A', title:'Expediente', page_start:14 }]
    }) }))
    assert.match(linked,/Problema jurídico/)
    assert.match(linked,/Carta recibida/)
    assert.match(linked,/Expediente/)
    assert.match(linked,/pág. 14/)
  } finally { await server.close() }
})
