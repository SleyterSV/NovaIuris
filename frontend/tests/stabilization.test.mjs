import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { normalizeApiBase } from '../src/config/apiBase.js'
import { normalizeCaseResult } from '../src/utils/caseContract.js'
import { normalizeSimulationState } from '../src/utils/simulationState.js'
import { normalizeRenderableContent, EMPTY_CONTENT } from '../src/utils/content.js'
import { normalizeSource, normalizeSources, resolveCitations } from '../src/utils/sourceContract.js'
import { runAnalysisTask } from '../src/services/taskService.js'
import { uploadCaseDocuments } from '../src/services/documentService.js'
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
    assert.ok(url.endsWith('/tasks/TASK-A?case_id=CASE-A'))
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

test('document upload polls sequentially and returns per-file results after real stages', async () => {
  const originalFetch = globalThis.fetch
  const originalXHR = globalThis.XMLHttpRequest
  const polls=[], stages=[]
  let inFlight=0, maximum=0
  globalThis.fetch = async url => {
    assert.match(url,/CASE%20DOC\/document-tasks\/TASK-DOC/)
    inFlight++; maximum=Math.max(maximum,inFlight)
    await new Promise(resolve=>setTimeout(resolve,2)); inFlight--
    polls.push(url)
    const completed=polls.length===2
    return Response.json({success:true,task_id:'TASK-DOC',case_id:'CASE DOC',tool:'documents',
      status:completed?'completed':'running',stage:completed?'completed':'indexing',
      completed_documents:completed?2:0,total_documents:2,current_document_index:1,current_units:4,
      documents:completed?[
        {status:'ready',duplicate:false,document:{document_id:'DOC-A',case_id:'CASE DOC',filename:'a.txt',status:'ready',chunk_count:3,ocr_required:false,warnings:[]}},
        {status:'failed',filename:'b.pdf',error:{code:'parse_failed',message:'PDF inválido'}}
      ]:[{status:'uploaded'},{status:'uploaded'}]})
  }
  class FakeXHR {
    constructor() { this.upload = {}; FakeXHR.instance = this }
    open(method,url) { this.method=method; this.url=url }
    send(body) {
      this.body=body
      this.upload.onprogress({lengthComputable:true,loaded:5,total:10})
      this.upload.onload?.()
      this.status=202
      this.responseText=JSON.stringify({task_id:'TASK-DOC',case_id:'CASE DOC',status:'queued'})
      this.onload()
    }
    abort() { this.onabort?.() }
  }
  globalThis.XMLHttpRequest = FakeXHR
  try {
    const progress=[]
    const files=['a.txt','b.pdf'].map(name=>Object.assign(new Blob(['Legal text']),{name}))
    const outcomes=await uploadCaseDocuments(files,'CASE DOC',{
      onProgress:(value,phase)=>progress.push([value,phase]),
      onTaskProgress:task=>stages.push(task.stage)
    })
    assert.equal(outcomes[0].document.document_id,'DOC-A')
    assert.equal(outcomes[1].status,'failed')
    assert.match(FakeXHR.instance.url,/CASE%20DOC/)
    assert.equal(FakeXHR.instance.body.getAll('files').length,2)
    assert.deepEqual(progress,[[50,undefined],[100,'uploaded']])
    assert.deepEqual(stages,['indexing','completed'])
    assert.equal(polls.length,2)
    assert.equal(maximum,1)
  } finally { globalThis.XMLHttpRequest = originalXHR; globalThis.fetch=originalFetch }
})

test('document polling aborts cleanly and rejects task identity mismatches', async () => {
  const originalFetch=globalThis.fetch, originalXHR=globalThis.XMLHttpRequest
  class ImmediateXHR {
    constructor(){this.upload={};ImmediateXHR.last=this}
    open(){}
    send(){this.status=202;this.responseText=JSON.stringify({task_id:'TASK-A',case_id:'CASE-A',status:'queued'});this.onload()}
    abort(){this.onabort?.()}
  }
  globalThis.XMLHttpRequest=ImmediateXHR
  try {
    let polls=0
    const controller=new AbortController()
    globalThis.fetch=async()=>{
      polls++
      return Response.json({success:true,task_id:'TASK-A',case_id:'CASE-A',tool:'documents',status:'running',stage:'extracting',documents:[]})
    }
    await assert.rejects(uploadCaseDocuments([Object.assign(new Blob(['x']),{name:'x.txt'})],'CASE-A',{
      signal:controller.signal,onTaskProgress:()=>controller.abort()
    }),{name:'AbortError'})
    assert.equal(polls,1)

    globalThis.fetch=async()=>Response.json({success:true,task_id:'TASK-A',case_id:'CASE-B',tool:'documents',status:'completed',documents:[]})
    await assert.rejects(uploadCaseDocuments([Object.assign(new Blob(['x']),{name:'x.txt'})],'CASE-A'),/no corresponde/i)
  } finally { globalThis.fetch=originalFetch;globalThis.XMLHttpRequest=originalXHR }
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
    const {default:analysisPanel}=await server.ssrLoadModule('/src/components/novacase/AnalysisView.vue')
    const stageHtml=await renderToString(createSSRApp({render:()=>h(analysisPanel,{
      analysis:{facts:['HECHO-A']},stages:[{id:'report',title:'Informe',status:'failed',description:'Etapa no completada.'}]
    })}))
    assert.match(stageHtml,/No completado/)
    assert.match(stageHtml,/Etapa no completada/)
    const {default:progressPanel}=await server.ssrLoadModule('/src/components/novacase/AnalysisProgress.vue')
    const progressHtml=await renderToString(createSSRApp({render:()=>h(progressPanel,{
      loading:false,steps:[{id:'facts',title:'Hechos',status:'completed'},
        {id:'documents',title:'Documentos',status:'skipped'},
        {id:'report',title:'Informe',status:'failed'}]
    })}))
    assert.match(progressHtml,/Analisis completado con incidencias/)
    assert.match(progressHtml,/2\/3/)
    assert.match(progressHtml,/No requerido/)
    assert.match(progressHtml,/No completado/)
    const input={default:(await server.ssrLoadModule('/src/components/novacourt/NovaCourtInput.vue')).default}
    const courtInputHtml=await renderToString(createSSRApp({render:()=>h(input.default,{modelValue:'',hasDocuments:true})}))
    assert.match(courtInputHtml,/Iniciar simulaci/)
    assert.ok(!/disabled/.test(courtInputHtml),'uploaded case documents permit document-only analysis')
    const uploader=(await server.ssrLoadModule('/src/components/common/CaseDocumentUpload.vue')).default
    const uploadHtml=await renderToString(createSSRApp({render:()=>h(uploader,{caseId:'CASE-A',initialDocumentIds:['DOC-A']})}))
    assert.match(uploadHtml,/multiple/)
    const uploadSource=await readFile(new URL('../src/components/common/CaseDocumentUpload.vue',import.meta.url),'utf8')
    assert.ok(uploadSource.includes('onBeforeUnmount(() => activeController?.abort())'))
    assert.ok(!uploadSource.includes('deleteCaseDocument'))
    const court=await readFile(new URL('../src/views/NovaCourtView.vue',import.meta.url),'utf8')
    assert.ok(court.includes(':graph-data="graphData"'))
    assert.ok(court.includes(':summary="summaryContent"'))
    assert.ok(court.includes('<CourtSimulation'))
    assert.ok(!court.includes('<StrategyView'))
    assert.ok(court.includes('requestedCaseId && typeof route.query.document_ids'))
    assert.ok(court.includes(':initial-document-ids="requestedDocumentIds"'))
  } finally { await server.close() }
})

test('NovaCase report renders verified citations, source details and partial failure state', async () => {
  const server=await createServer({server:{middlewareMode:true},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const {default:component}=await server.ssrLoadModule('/src/components/novacase/ReportView.vue')
    const props={
      report:'# Informe jurídico\n\n## I. Análisis jurídico\nLa regla aplicable se analiza aquí [1].',
      reportDocument:{document_type:'analysis_report',title:'Informe del caso A',case_id:'CASE-A',
        generated_at:'2026-01-10T10:00:00Z',citations:[{citation_id:'CIT-abcdef0123456789abcdef01',source_id:'SRC-CASEA001',label:'[1]',excerpt:'Fragmento exacto'}],
        sources:[{source_id:'SRC-CASEA001',source_scope:'case',source_type:'case_document',case_id:'CASE-A',
          document_id:'DOC-A',chunk_id:'CH-A',title:'demanda.pdf',page_start:4,excerpt:'Fragmento exacto'}]},
      caseId:'CASE-A',reportStatus:'ready'
    }
    const html=await renderToString(createSSRApp({render:()=>h(component,props)}))
    assert.match(html,/Informe del caso A/)
    assert.match(html,/CASE-A/)
    assert.match(html,/data-citation-id=/)
    assert.match(html,/Copiar informe/)
    assert.match(html,/demanda\.pdf/)
    assert.match(html,/PDF · próximamente/)
    assert.match(html,/disabled/)
    assert.ok(!html.includes('[object Object]'))
    assert.ok(!/\b(?:undefined|null)\b/.test(html))
    const reportSource=await readFile(new URL('../src/components/novacase/ReportView.vue',import.meta.url),'utf8')
    assert.ok(reportSource.includes('navigator.clipboard.writeText(props.report.trim())'))
    assert.ok(!reportSource.includes('function exportPdf'))
    const {default:modal}=await server.ssrLoadModule('/src/components/common/SourceModal.vue')
    const context={teleports:{}}
    await renderToString(createSSRApp({render:()=>h(modal,{source:props.reportDocument.sources[0],caseId:'CASE-A'})}),context)
    assert.match(context.teleports.body,/Fragmento exacto/)
    assert.match(context.teleports.body,/<dt[^>]*>P(?:á|Ã¡)gina<\/dt><dd[^>]*>4<\/dd>/i)
    const partial=await renderToString(createSSRApp({render:()=>h(component,{
      report:'',reportStatus:'failed',reportError:{message:'El análisis permanece disponible.'},caseId:'CASE-A'
    })}))
    assert.match(partial,/El análisis permanece disponible/)
  } finally { await server.close() }
})

test('NovaCase workspace exposes sections only when corresponding result data exists', async () => {
  const source=await readFile(new URL('../src/views/NovaCaseView.vue',import.meta.url),'utf8')
  const tabs=await readFile(new URL('../src/components/novacase/CaseTabs.vue',import.meta.url),'utf8')
  assert.ok(source.includes(':available-tabs="availableTabs"'))
  assert.ok(source.includes('<template #arguments>'))
  assert.ok(source.includes('<template #sources>'))
  assert.ok(source.includes('canonicalResult?.facts?.length'))
  assert.ok(source.includes('factStatusLabel(fact.status)'))
  assert.ok(source.includes('canonicalResult?.evidence?.evidence_links?.length'))
  assert.ok(source.includes('issuesForLink(link)'))
  assert.ok(source.includes('source.case_id === canonicalResult.value?.case_id'))
  assert.ok(source.includes(':content="canonicalResult?.arguments"'))
  assert.ok(source.includes('result.sources_used?.length'))
  assert.ok(source.includes("result.report_status === \"failed\""))
  assert.ok(tabs.includes('{ id: "summary", label: "Resumen" }'))
  assert.ok(tabs.includes('{ id: "arguments", label: "Argumentos" }'))
  assert.ok(tabs.includes('{ id: "sources", label: "Fuentes" }'))
  assert.ok(source.includes('canonicalResult?.final_strategy'))
  assert.ok(source.includes(':strategy="strategy"'))
})

test('source contracts deduplicate, validate URLs and isolate private cases', () => {
  const publicSource={source_id:'SRC-PUBLIC1',source_scope:'public',source_type:'legislation',title:'Código Civil',
    official_url:'https://official.test/law',excerpt:'exact public excerpt',metadata:{article:'1969'}}
  const privateA={source_id:'SRC-PRIVATE1',source_scope:'case',case_id:'CASE-A',document_id:'DOC-A',chunk_id:'CH-A',title:'brief.pdf',excerpt:'private A'}
  assert.equal(normalizeSource({...publicSource,official_url:'javascript:alert(1)'}).official_url,null)
  assert.equal(normalizeSource(privateA,'CASE-B'),null)
  assert.equal(normalizeSource(privateA),null)
  assert.equal(normalizeSource({...privateA,official_url:'https://file.test'},'CASE-A').official_url,null)
  assert.equal(normalizeSources([publicSource,publicSource]).length,1)
  const resolved=resolveCitations([{citation_id:'CIT-abc',source_id:'SRC-PRIVATE1',label:'[1]'}],
    [privateA], 'CASE-B')
  assert.deepEqual(resolved.citations,[])
  assert.deepEqual(resolved.sources,[])
  assert.equal(normalizeSource(publicSource).official_url,'https://official.test/law')
  const caseContract=normalizeCaseResult({success:true,case_id:'CASE-A',sources:[privateA],citations:[{citation_id:'CIT-a',source_id:'SRC-PRIVATE1'}]})
  assert.equal(caseContract.sources[0].case_id,'CASE-A')
  assert.equal(caseContract.citations[0].source_id,'SRC-PRIVATE1')
})

test('shared citation renderer makes only verified labels interactive and escapes HTML', async () => {
  const server=await createServer({server:{middlewareMode:true},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const {default:MarkdownRenderer}=await server.ssrLoadModule('/src/components/common/MarkdownRenderer.vue')
    const source={source_id:'SRC-PUBLIC1',source_scope:'public',source_type:'legislation',title:'Law',excerpt:'exact',official_url:'https://official.test/law'}
    const citation={citation_id:'CIT-000000000000000000000000',source_id:source.source_id,label:'[1]',excerpt:'exact'}
    const html=await renderToString(createSSRApp({render:()=>h(MarkdownRenderer,{
      content:'**Fundamento** [1] [2] <img src=x onerror=alert(1)>',sources:[source],citations:[citation]
    })}))
    assert.match(html,/data-citation-id="CIT-000000000000000000000000"/)
    assert.match(html,/\[2\]/)
    assert.ok(!html.includes('<img'))
    const sourceModal=await readFile(new URL('../src/components/common/SourceModal.vue',import.meta.url),'utf8')
    assert.ok(sourceModal.includes('v-if="safeSource.official_url"'))
    assert.ok(sourceModal.includes('target="_blank" rel="noopener noreferrer"'))
    const sourceList=await readFile(new URL('../src/components/common/SourcesList.vue',import.meta.url),'utf8')
    assert.ok(sourceList.includes('normalizeSources(props.sources, props.caseId)'))
    const {default:SourceModal}=await server.ssrLoadModule('/src/components/common/SourceModal.vue')
    const context={}
    await renderToString(createSSRApp({render:()=>h(SourceModal,{source})}),context)
    const modalHtml=context.teleports?.body || ''
    assert.ok(modalHtml.includes('Abrir fuente oficial'))
    assert.ok(modalHtml.includes('rel="noopener noreferrer"'))
    assert.ok(!modalHtml.includes('<dt>Tribunal</dt>'))
    const {default:SourcesList}=await server.ssrLoadModule('/src/components/common/SourcesList.vue')
    const listHtml=await renderToString(createSSRApp({render:()=>h(SourcesList,{
      sources:[source,source,{source_id:'SRC-PRIVATE1',source_scope:'case',case_id:'CASE-B',title:'Private B'}],
      citations:[citation],caseId:'CASE-A'
    })}))
    assert.equal((listHtml.match(/<strong[^>]*>Law<\/strong>/g)||[]).length,1,listHtml)
    assert.ok(!listHtml.includes('Private B'))
  } finally { await server.close() }
})
