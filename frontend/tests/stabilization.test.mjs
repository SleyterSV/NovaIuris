import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { normalizeApiBase } from '../src/config/apiBase.js'
import { normalizeCaseResult } from '../src/utils/caseContract.js'
import { normalizeSimulationState } from '../src/utils/simulationState.js'
import { normalizeRenderableContent, EMPTY_CONTENT } from '../src/utils/content.js'
import { runAnalysisTask } from '../src/services/taskService.js'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'

test('API origins normalize legacy /api without duplicate paths', () => {
  for (const value of ['https://backend.test', 'https://backend.test/', 'https://backend.test/api/', 'https://backend.test/api/api']) {
    assert.equal(normalizeApiBase(value), 'https://backend.test')
  }
  assert.equal(normalizeApiBase(''), '')
})

const raw = {
  success:true, case_id:'CASE-A', case:'EXPEDIENTE-A',
  analysis:{ hechos:['HECHO-A'], problemas_juridicos:['PROBLEMA-A'], normas_probables:['NORMA-A'] },
  research:{ documents:[{tipo_documento:'Jurisprudencia', extracto_exacto:'FUENTE-A'}] },
  legal_arguments:{ main_arguments:[{argument:'ARGUMENTO-A'}] },
  evidence_analysis:{ documentary_evidence:['PRUEBA-A'] },
  risk_analysis:{ procedural_risks:['RIESGO-A'], risk_level:'Medio' },
  counter_arguments:{ procedural_exceptions:['EXCEPCIÓN-A'] },
  strategy:{ claim_strategy:'ESTRATEGIA-A', recommended_actions:['ACTUACIÓN-A'] },
  report:'# INFORME-A'
}

test('nested mappings preserve generated data and do not mutate original', () => {
  const before = structuredClone(raw), result = normalizeCaseResult(raw)
  assert.deepEqual(raw,before)
  assert.deepEqual(result.analysis.facts,['HECHO-A'])
  assert.deepEqual(result.evidence.documents,['PRUEBA-A'])
  assert.deepEqual(result.risks.procedural,['RIESGO-A'])
  assert.equal(result.strategy.strategy,'ESTRATEGIA-A')
  assert.deepEqual(result.counter_arguments.procedural,['EXCEPCIÓN-A'])
  assert.equal(normalizeRenderableContent({}), '')
  assert.equal(normalizeRenderableContent([]), '')
  assert.equal(normalizeSimulationState(result.simulation).status,'not_requested')
  assert.equal(normalizeSimulationState(result.simulation).prosecutor.content,undefined)
})

test('one task polling loop validates identity and returns canonical result', async () => {
  const original = globalThis.fetch
  let polls=0, inFlight=0, maximum=0
  globalThis.fetch = async (url, options) => {
    if (url.endsWith('/case/tasks')) return Response.json({success:true, task_id:'TASK-A',case_id:'CASE-A'})
    assert.ok(url.endsWith('/tasks/TASK-A'))
    inFlight++; maximum=Math.max(maximum,inFlight)
    await new Promise(resolve => setTimeout(resolve,5)); inFlight--; polls++
    return Response.json({success:true,task_id:'TASK-A',case_id:'CASE-A',tool:'case',
      status:polls===2 ? 'completed':'processing',stages:[],final_result:raw})
  }
  try {
    const result=await runAnalysisTask('case','A',{caseId:'CASE-A',pollInterval:0})
    assert.equal(result.case_id,'CASE-A'); assert.equal(polls,2); assert.equal(maximum,1)
  } finally { globalThis.fetch=original }
})

test('mismatched cases are rejected; abort cancels the backend task', async () => {
  const original=globalThis.fetch, calls=[]
  const controller=new AbortController()
  globalThis.fetch=async url => {
    calls.push(url)
    if(url.endsWith('/case/tasks')) return Response.json({success:true,task_id:'TASK-A',case_id:'CASE-A'})
    if(url.endsWith('/cancel')) return Response.json({success:true})
    return Response.json({success:true,task_id:'TASK-A',case_id:'CASE-B',tool:'case',status:'processing'})
  }
  try {
    await assert.rejects(runAnalysisTask('case','A',{caseId:'CASE-A'}),/no corresponde/)
    assert.ok(calls.some(url=>url.endsWith('/cancel')))
    calls.length=0
    await assert.rejects(runAnalysisTask('case','A',{caseId:'CASE-A',signal:controller.signal,onTask:()=>controller.abort()}),{name:'AbortError'})
    assert.ok(calls.some(url=>url.endsWith('/cancel')))
    calls.length=0
    await assert.rejects(runAnalysisTask('case','A',{caseId:'CASE-A',signal:controller.signal}),{name:'AbortError'})
    assert.equal(calls.length,0)
  } finally { globalThis.fetch=original }
})

test('actual Vue panels render canonical data and professional empty states', async () => {
  // Middleware mode transforms modules only; no listening server and no provider calls.
  const server=await createServer({server:{middlewareMode:true},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const result=normalizeCaseResult(raw)
    for(const [name,props,expected] of [
      ['novacase/AnalysisView',{analysis:result.analysis},'HECHO-A'],
      ['novacase/EvidenceView',{evidence:result.evidence},'PRUEBA-A'],
      ['novacase/RiskView',{risk:result.risks},'RIESGO-A'],
      ['novacase/CounterArgumentsView',{counterArguments:result.counter_arguments},'EXCEPCIÓN-A'],
      ['novacase/StrategyView',{strategy:result.strategy},'ESTRATEGIA-A'],
      ['novacourt/CourtSummary',{summary:{proceso:'PROCESO-A'}},'PROCESO-A'],
      ['novacourt/CourtAnalysis',{content:normalizeRenderableContent(result.arguments)},'ARGUMENTO-A'],
      ['novacourt/CourtSimulation',{simulation:{status:'ready',prosecutor:{content:'FISCAL-A'}}},'FISCAL-A'],
      ['common/ExecutiveSummary',{summary:result.summary},EMPTY_CONTENT],
      ['common/MarkdownRenderer',{content:[]},EMPTY_CONTENT]
    ]) {
      const {default:component}=await server.ssrLoadModule(`/src/components/${name}.vue`)
      const html=await renderToString(createSSRApp({render:()=>h(component,props)}))
      assert.ok(html.includes(expected),`${name} must show ${expected}`)
      assert.ok(!html.includes('[object Object]'),name)
      assert.ok(!/\b(?:undefined|null)\b/.test(html),name)
      assert.ok(!html.includes('Probabilidad de Éxito'),name)
      assert.ok(!html.includes('Nivel de confianza'),`${name} has no fabricated confidence`)
    }
    const court=await readFile(new URL('../src/views/NovaCourtView.vue',import.meta.url),'utf8')
    assert.ok(court.includes(':graph-data="graphData"'))
    assert.ok(court.includes(':summary="summaryContent"'))
    assert.ok(court.includes('<CourtSimulation'))
    assert.ok(!court.includes('<StrategyView'))
  } finally { await server.close() }
})
