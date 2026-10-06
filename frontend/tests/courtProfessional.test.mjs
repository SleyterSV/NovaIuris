import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { runAnalysisTask } from '../src/services/taskService.js'
import { normalizeSimulationState } from '../src/utils/simulationState.js'

test('detaching Court observation leaves the backend task running', async () => {
  const original = globalThis.fetch
  const calls = []
  const controller = new AbortController()
  globalThis.fetch = async (url) => {
    calls.push(String(url))
    if (String(url).endsWith('/novacourt/analyze')) return Response.json({ success:true, task_id:'TASK-A', case_id:'CASE-A' })
    return Response.json({ success:true, task_id:'TASK-A', case_id:'CASE-A', tool:'court', status:'processing' })
  }
  try {
    await assert.rejects(runAnalysisTask('court', 'Caso', {
      caseId:'CASE-A', onTask:() => controller.abort('detach'), signal:controller.signal
    }), { name:'AbortError' })
    assert.equal(calls.filter(url => url.endsWith('/cancel')).length, 0)
  } finally { globalThis.fetch = original }
})

test('transient Court status failure resumes the same task', async () => {
  const original = globalThis.fetch
  let polls = 0, starts = 0
  globalThis.fetch = async (url) => {
    if (String(url).endsWith('/novacourt/analyze')) {
      starts++
      return Response.json({ success:true, task_id:'TASK-A', case_id:'CASE-A' })
    }
    polls++
    if (polls === 1) return Response.json({ success:false }, { status:503 })
    return Response.json({ success:true, task_id:'TASK-A', case_id:'CASE-A', tool:'court',
      status:'completed', final_result:{ success:true, case_id:'CASE-A' } })
  }
  try {
    const result = await runAnalysisTask('court', 'Caso', { caseId:'CASE-A', pollInterval:0 })
    assert.equal(result.case_id, 'CASE-A')
    assert.equal(starts, 1)
    assert.equal(polls, 2)
  } finally { globalThis.fetch = original }
})
test('Court sends explicit reuse identity and polls once; independent case sends no reuse', async () => {
  const original = globalThis.fetch
  const payloads = []
  let inFlight = 0, maximum = 0
  globalThis.fetch = async (url, options) => {
    if (url.endsWith('/novacourt/analyze')) {
      payloads.push(JSON.parse(options.body))
      return Response.json({success:true, task_id:`TASK-${payloads.length}`,case_id:payloads.at(-1).case_id})
    }
    inFlight++; maximum = Math.max(maximum, inFlight)
    await new Promise(resolve => setTimeout(resolve, 2))
    inFlight--
    const item = payloads.at(-1)
    return Response.json({success:true, task_id:`TASK-${payloads.length}`,case_id:item.case_id,
      tool:'court',status:'completed',final_result:{success:true,case_id:item.case_id,
        simulation:{status:'not_requested'},graph:{status:'failed'}}})
  }
  try {
    await runAnalysisTask('court','Case A',{caseId:'CASE-A',documentIds:['DOC-A'],reuseTaskId:'TASK-CASE'})
    await runAnalysisTask('court','Case B',{caseId:'CASE-B'})
    assert.deepEqual(payloads[0],{case_text:'Case A',case_id:'CASE-A',document_ids:['DOC-A'],reuse_task_id:'TASK-CASE'})
    assert.deepEqual(payloads[1],{case_text:'Case B',case_id:'CASE-B',document_ids:[]})
    assert.equal(maximum,1)
  } finally { globalThis.fetch = original }
})

test('Court panels show adaptive roles, simulated decision, grounded sources and failure', async () => {
  const server = await createServer({server:{middlewareMode:true,hmr:false},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const source = {source_id:'SRC-CASE001',source_scope:'case',case_id:'CASE-A',title:'Contrato',
      source_type:'case_document',excerpt:'Cláusula existente',document_id:'DOC-A'}
    const citation = {citation_id:'CIT-abc123',source_id:'SRC-CASE001',label:'[1]'}
    const simulation = normalizeSimulationState({status:'ready',prosecutor:{role_label:'Parte demandante',content:'Tesis [1]'},
      defense:{role_label:'Parte demandada',content:'Objeción'},judicial_analysis:{content:'Decisión simulada'},
      sources:[source],citations:[citation]})
    const component = (await server.ssrLoadModule('/src/components/novacourt/CourtSimulation.vue')).default
    const ready = await renderToString(createSSRApp({render:()=>h(component,{simulation,caseId:'CASE-A'})}))
    assert.match(ready,/Parte demandante/)
    assert.match(ready,/Parte demandada/)
    assert.doesNotMatch(ready,/Decisión simulada/)
    assert.match(ready,/Contrato/)
    assert.doesNotMatch(ready,/Fiscalía|probabilidad|Proyección orientativa|SRC-CASE001/)
    const decision = await renderToString(createSSRApp({render:()=>h(component,{simulation,caseId:'CASE-A',mode:'decision'})}))
    assert.match(decision,/Decisión simulada/)
    assert.doesNotMatch(decision,/Parte demandante|Parte demandada/)
    const failed = await renderToString(createSSRApp({render:()=>h(component,{simulation:{status:'failed'}})}))
    assert.match(failed,/Simulación no disponible/)
    assert.doesNotMatch(failed,/Tesis|Estrategia/)
    const report = (await server.ssrLoadModule('/src/components/novacourt/CourtReport.vue')).default
    const reportHtml = await renderToString(createSSRApp({render:()=>h(report,{content:'## Decisión simulada\n\nTexto [1]',
      sources:[source],citations:[citation],caseId:'CASE-A'})}))
    assert.match(reportHtml,/Copiar simulación/)
    assert.match(reportHtml,/PDF.*próximamente/)
    assert.match(reportHtml,/Contrato/)
    assert.doesNotMatch(reportHtml,/SRC-CASE001/)
  } finally { await server.close() }
})

test('Court view keeps simulation separate from strategy and has no fake role progress', async () => {
  const view = await readFile(new URL('../src/views/NovaCourtView.vue',import.meta.url),'utf8')
  const caseView = await readFile(new URL('../src/views/NovaCaseView.vue',import.meta.url),'utf8')
  assert.match(view,/reuseTaskId/)
  assert.match(view,/Nueva simulación independiente/)
  assert.match(view,/:graph-data="graphData"/)
  assert.match(view,/<CourtSimulation/)
  assert.doesNotMatch(view,/simulation\s*\|\|\s*strategy|simulation\s*\?\?\s*final_strategy/)
  assert.match(caseView,/reuseTaskId:completedTaskId\.value/)
})
