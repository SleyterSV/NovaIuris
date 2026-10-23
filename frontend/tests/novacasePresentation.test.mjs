import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { normalizeCaseResult } from '../src/utils/caseContract.js'
import { normalizeSource } from '../src/utils/sourceContract.js'
import {
  ARGUMENT_SECTION_LABELS, canAttachDocumentsToCase, evidenceAvailability,
  factAllegationOrigin, presentableText, researchNotice, relatedFactTexts, verifiedArgumentSources,
  groupedJurisprudence, jurisprudenceMarkdown, argumentNeedsVerification,
  sourceHumanLabel, sourceUnitLabel
} from '../src/utils/novacasePresentation.js'

const factId = 'FACT-aaaaaaaaaaaaaaaaaaaaaaaa'
const issueId = 'ISSUE-bbbbbbbbbbbbbbbbbbbbbbbb'
const source = {
  source_id:'SRC-aaaaaaaaaaaaaaaaaaaaaaaa', source_scope:'public_legal', provenance_version:'v2',
  document_id:'11111111-1111-4111-8111-111111111111',
  unit_id:'22222222-2222-4222-8222-222222222222', chunk_id:'22222222-2222-4222-8222-222222222222',
  title:'STC Exp. 00001-2024-PA/TC', display_title:'STC Exp. 00001-2024-PA/TC',
  court:'Tribunal Constitucional', unit_type:'foundation', unit_number:'7', page_start:2,
  official_url:'https://tc.gob.pe/source.pdf', excerpt:'Texto canónico completo.'
}

test('research outcomes, private documents and public units remain distinct', () => {
  assert.match(researchNotice('VERIFIED_SOURCES',1).text,/completada con 1 fuente V2 verificada/)
  assert.match(researchNotice('NO_RESULTS').text,/sin fuentes verificadas/)
  assert.match(researchNotice('ERROR').text,/error/)
  assert.match(researchNotice('UNAVAILABLE').text,/no disponible/)
  const result = normalizeCaseResult({success:true,document_ids:[],summary:{documentos:8},
    research:{status:'VERIFIED_SOURCES',public_source_count:1,documents:[{document_id:'document-a'}]}})
  assert.equal(result.summary.documentos,0)
  assert.equal(result.summary.fuentes_juridicas,1)
  assert.equal(evidenceAvailability('Contrato referido',{documentCount:0,documentary:true}),'no_documents')
  assert.equal(evidenceAvailability('No identificado con la información disponible.'),'not_identified')
  assert.equal(evidenceAvailability('Testigo mencionado'),'requires_verification')
  assert.equal(evidenceAvailability('Documento enlazado',{documentCount:1,documentary:true,verified:true}),'available')
})

test('argument IDs stay internal and the document CTA is case scoped', () => {
  assert.equal(ARGUMENT_SECTION_LABELS.constitutional_arguments,'Argumentos constitucionales')
  assert.equal(ARGUMENT_SECTION_LABELS.counterargument_responses,'Respuestas a contraargumentos')
  assert.equal(presentableText(`Alegación ${factId} pendiente ${issueId}`),'Alegación pendiente')
  const argument={supporting_fact_ids:[factId],source_ids:[source.source_id]}
  assert.deepEqual(relatedFactTexts(argument,[{fact_id:factId,text:'Cese alegado'}]),['Cese alegado'])
  assert.equal(verifiedArgumentSources(argument,[source],'CASE-A').length,1)
  assert.equal(verifiedArgumentSources(argument,[{...source,source_scope:'private_case',case_id:'CASE-B'}],'CASE-A').length,0)
  assert.equal(canAttachDocumentsToCase('CASE-A','CASE-A',true),true)
  assert.equal(canAttachDocumentsToCase('CASE-B','CASE-A',true),false)
  assert.equal(canAttachDocumentsToCase('CASE-A','CASE-A',false),false)
  assert.equal(normalizeSource({...source,chunk_id:'other'}),null)
})

test('NovaCase components render Spanish labels, honest scope and verified V2 locator', async () => {
  const server=await createServer({server:{middlewareMode:true,hmr:false,port:0},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  const render=async(name,props={}) => {
    const component=(await server.ssrLoadModule(`/src/components/${name}.vue`)).default
    return renderToString(createSSRApp({render:()=>h(component,props)}))
  }
  try {
    const argumentsHtml=await render('novacase/ArgumentsView',{
      arguments:{main_arguments:[{title:'Tutela CAS',argument:`Cese alegado ${issueId}`,
        legal_basis:['Regla por verificar'],supporting_fact_ids:[factId],source_ids:[]}]},
      facts:[{fact_id:factId,text:'Cese comunicado al trabajador'}],sources:[],caseId:'CASE-A'
    })
    assert.match(argumentsHtml,/Argumentos principales/)
    assert.match(argumentsHtml,/Fundamento pendiente de verificación/)
    assert.match(argumentsHtml,/Cese comunicado al trabajador/)
    assert.ok(!argumentsHtml.includes(factId) && !argumentsHtml.includes(issueId))
    assert.ok(!argumentsHtml.includes('Supporting fact ids'))

    const evidenceHtml=await render('novacase/EvidenceView',{evidence:{documents:'Contrato alegado'},documentCount:0})
    assert.match(evidenceHtml,/Sin documentos aportados al caso/)
    assert.match(evidenceHtml,/Agregar documentos al caso/)
    assert.match(evidenceHtml,/No aportada/)
    assert.ok(!evidenceHtml.includes('Contrato alegado'))

    const verifiedHtml=await render('novacase/ArgumentsView',{
      arguments:{main_arguments:[{argument:'Tutela',legal_basis:['Hipótesis'],source_ids:[source.unit_id]}],
        jurisprudence_used:[source.unit_id]},sources:[source],caseId:'CASE-A'
    })
    assert.match(verifiedHtml,/STC Exp. 00001-2024-PA\/TC/)
    assert.match(verifiedHtml,/Fundamento 7/)
    assert.match(verifiedHtml,/Tribunal Constitucional/)
    assert.ok(!verifiedHtml.includes(source.unit_id))
    assert.ok(!verifiedHtml.includes('pendiente de verificación'))

    const legalEvidence=await render('novacase/EvidenceView',{
      evidence:{documents:'STC Exp. 00001-2024-PA/TC'},documentCount:0,sources:[source]
    })
    assert.match(legalEvidence,/Fuentes jurídicas de apoyo/)
    assert.match(legalEvidence,/No aportada/)
    assert.equal((legalEvidence.match(/STC Exp. 00001-2024-PA\/TC/g) || []).length,1)

    const analysisHtml=await render('novacase/AnalysisView',{
      analysis:{jurisprudence:'No identificado con la información disponible.'},sources:[source]
    })
    assert.match(analysisHtml,/STC Exp. 00001-2024-PA\/TC/)
    assert.match(analysisHtml,/Fundamento 7/)
    const citedAnalysis=await render('novacase/AnalysisView',{
      analysis:{summary:'Criterio jurídico respaldado [1]'},sources:[source],caseId:'CASE-A',
      citations:[{citation_id:'citation-one',label:'[1]',source_id:source.source_id}]
    })
    assert.match(citedAnalysis,/aria-label="Ver fuente 1"/)
    assert.ok(!citedAnalysis.includes(source.source_id))

    const riskHtml=await render('novacase/RiskView',{risk:{procedural:[{risk:'Plazo por comprobar',impact:'Alto',mitigation:'Verificar notificación'}]}})
    assert.match(riskHtml,/Riesgos procesales/)
    assert.match(riskHtml,/Mitigación/)
    assert.match(riskHtml,/Verificar notificación/)
    const emptyRisk=await render('novacase/RiskView',{risk:{}})
    assert.match(emptyRisk,/No se identificó información suficiente para evaluar riesgos/)
    assert.ok(!emptyRisk.includes('Riesgos procesales'))

    const summaryHtml=await render('common/ExecutiveSummary',{summary:{documentos:0,fuentes_juridicas:1}})
    assert.match(summaryHtml,/Documentos del caso/)
    assert.match(summaryHtml,/Fuentes jurídicas recuperadas/)

    const sourcesHtml=await render('common/SourcesList',{sources:[source],caseId:'CASE-A'})
    assert.match(sourcesHtml,/Tribunal Constitucional/)
    assert.match(sourcesHtml,/Fundamento 7/)
    assert.match(sourcesHtml,/pág. 2/)

    const reportHtml=await render('novacase/ReportView',{report:`# Informe ${factId}\nHecho por verificar.`,
      reportDocument:{},documentCount:0,publicSourceCount:0,caseId:'CASE-A'})
    assert.match(reportHtml,/Documento de análisis preparado para revisión profesional/)
    assert.ok(!reportHtml.includes('Hechos alegados:'))
    assert.ok(!reportHtml.includes('Marco jurídico preliminar'))
    assert.ok(!reportHtml.includes(factId))

    const caseView=await readFile(new URL('../src/views/NovaCaseView.vue',import.meta.url),'utf8')
    const mikeView=await readFile(new URL('../src/views/MikeView.vue',import.meta.url),'utf8')
    const summaryCss=await readFile(new URL('../src/components/common/ExecutiveSummary.vue',import.meta.url),'utf8')
    assert.match(caseView,/<ArgumentsView /)
    assert.match(caseView,/@add-documents="addDocuments"/)
    assert.match(mikeView,/@add-documents="addCaseDocuments\(turn,\$event\)"/)
    assert.match(mikeView,/canAttachDocumentsToCase\(payload\?\.caseId, workspace\.value\.caseId/)
    assert.match(summaryCss,/\.summary-card dd\{[^}]*overflow-wrap:break-word/s)
  } finally { await server.close() }
})

test('Informe shows one cited source list, safe actions and no QA scope box', async () => {
  const server=await createServer({server:{middlewareMode:true,hmr:false,port:0},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const {default:ReportView}=await server.ssrLoadModule('/src/components/novacase/ReportView.vue')
    const citation={citation_id:'CIT-1',source_id:source.source_id,label:'[1]'}
    const report='# Informe jurídico\n## Objeto y alcance\nEl criterio citado [1] requiere revisión.\n## Fuentes\nListado duplicado.'
    const html=await renderToString(createSSRApp({render:()=>h(ReportView,{
      report,reportDocument:{title:'Informe jurídico',citations:[citation],sources:[source]},
      caseId:'CASE-A',taskId:'00000000-0000-4000-8000-000000000001'
    })}))
    assert.equal((html.match(/<h3[^>]*>Fuentes utilizadas<\/h3>/g)||[]).length,1)
    assert.match(html,/Ver fuente 1/)
    assert.match(html,/Documento de análisis preparado para revisión profesional/)
    assert.match(html,/Descargar PDF/)
    assert.match(html,/Descargar DOCX/)
    assert.match(html,/Tribunal Constitucional/)
    assert.ok(!html.includes('Listado duplicado'))
    assert.ok(!html.includes('Hechos alegados:'))
    assert.ok(!html.includes(source.source_id))
    assert.ok(!html.includes(source.document_id))
  } finally { await server.close() }
})

test('public units group by document and argument references resolve without exposing IDs', () => {
  const second={...source,source_id:'SRC-bbbbbbbbbbbbbbbbbbbbbbbb',
    unit_id:'33333333-3333-4333-8333-333333333333',chunk_id:'33333333-3333-4333-8333-333333333333',
    unit_number:'14',page_start:7}
  assert.equal(groupedJurisprudence([source,second]).length,1)
  assert.match(jurisprudenceMarkdown([source,second]),/Fundamento 7, Fundamento 14/)
  assert.equal(argumentNeedsVerification({source_ids:[second.unit_id]},[source,second]),false)
  assert.equal(argumentNeedsVerification({argument:'Criterio [1]',source_ids:[]},[source],null,
    [{label:'[1]',source_id:source.source_id}]),false)
  assert.equal(argumentNeedsVerification({source_ids:[]},[source,second]),true)
})

test('case text remains an allegation and never adds a private document', async () => {
  const result = normalizeCaseResult({success:true,case:'Relato ingresado por el usuario',
    document_ids:[],research:{public_source_count:1},summary:{documentos:3}})
  assert.equal(result.summary.documentos,0)
  assert.equal(factAllegationOrigin({status:'alleged',source_ids:[]},[]),'Relato proporcionado')
  assert.equal(factAllegationOrigin({status:'alleged',source_ids:['SRC-private']},[{source_id:'SRC-private'}]),'')
  const view = await readFile(new URL('../src/views/NovaCaseView.vue',import.meta.url),'utf8')
  assert.match(view,/factAllegationOrigin\(fact, factSources\(fact\)\)/)
  assert.match(view,/\["case", "private_case"\]\.includes\(source\.source_scope\)/)
  assert.match(view,/:sources="\[\.\.\.\(canonicalResult\?\.research\?\.sources \|\| \[\]\)/)
})

test('canonical unit number and heading make missing-number references readable', () => {
  assert.equal(sourceUnitLabel({...source,unit_number:null,metadata:{unit_number:'5'}}),'Fundamento 5')
  const withoutNumber={...source,unit_number:null,metadata:{unit_number:null},section:'Antecedentes'}
  assert.equal(sourceUnitLabel(withoutNumber),'Fundamento: Antecedentes')
  assert.match(sourceHumanLabel(withoutNumber),/Fundamento: Antecedentes/)
  assert.ok(!sourceHumanLabel(withoutNumber).includes(source.unit_id))
})

test('Case sources tab renders private files and groups public units without empty bullets or IDs', async () => {
  const server=await createServer({server:{middlewareMode:true,hmr:false,port:0},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const component=(await server.ssrLoadModule('/src/components/novacase/CaseSourcesView.vue')).default
    const privateOne={source_id:'SRC-private-one',source_scope:'private_case',case_id:'CASE-A',
      document_id:'private-document-one',title:'01_Contrato_CAS_Mariana_Torres.pdf'}
    const privateTwo={source_id:'SRC-private-two',source_scope:'private_case',case_id:'CASE-A',
      document_id:'private-document-two',title:'02_Memorando_No_Renovacion_Mariana_Torres.pdf'}
    const second={...source,source_id:'SRC-bbbbbbbbbbbbbbbbbbbbbbbb',
      unit_id:'33333333-3333-4333-8333-333333333333',chunk_id:'33333333-3333-4333-8333-333333333333',
      unit_number:null,metadata:{unit_type:'foundation',unit_number:null},section:'Antecedentes',page_start:3}
    const third={...source,source_id:'SRC-cccccccccccccccccccccccc',
      document_id:'44444444-4444-4444-8444-444444444444',
      unit_id:'55555555-5555-4555-8555-555555555555',chunk_id:'55555555-5555-4555-8555-555555555555',
      title:'STC Exp. 04852-2023-PA/TC',display_title:'STC Exp. 04852-2023-PA/TC',unit_number:'4'}
    const html=await renderToString(createSSRApp({render:()=>h(component,{
      sources:[privateOne,privateTwo,source,second,third,source],caseId:'CASE-A'})}))
    assert.match(html,/Fuentes del caso/)
    assert.match(html,/01_Contrato_CAS_Mariana_Torres\.pdf/)
    assert.match(html,/02_Memorando_No_Renovacion_Mariana_Torres\.pdf/)
    assert.match(html,/Fuentes jurídicas verificadas/)
    assert.equal((html.match(/STC Exp\. 00001-2024-PA\/TC/g)||[]).length,1)
    assert.match(html,/STC Exp\. 04852-2023-PA\/TC/)
    assert.match(html,/Fundamento 7/)
    assert.match(html,/Fundamento: Antecedentes/)
    assert.match(html,/Ver fuente/)
    assert.doesNotMatch(html,/<li[^>]*>\s*<\/li>/)
    assert.ok(!html.includes(source.unit_id) && !html.includes(second.unit_id) && !html.includes(privateOne.source_id))
  } finally { await server.close() }
})

test('executive summary restores six real indicators and evidence-aware key facts', async () => {
  const server=await createServer({server:{middlewareMode:true,hmr:false,port:0},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const component=(await server.ssrLoadModule('/src/components/common/ExecutiveSummary.vue')).default
    const privateSource={source_id:'SRC-private-case',source_scope:'private_case',case_id:'CASE-A'}
    const facts=[
      {fact_id:'FACT-first',text:'Se contrató un reemplazo',status:'alleged',source_ids:[]},
      {fact_id:'FACT-second',text:'Memorando comunicó la no renovación',status:'supported',source_ids:[privateSource.source_id]},
      ...Array.from({length:5},(_,index)=>({fact_id:'FACT-extra-'+index,text:'Alegación adicional '+index,status:'alleged',source_ids:[]}))
    ]
    const html=await renderToString(createSSRApp({render:()=>h(component,{
      summary:{resumen:'El caso requiere revisión de la no renovación.',rama:'Derecho Laboral Público',
        proceso:'Proceso contencioso administrativo de revisión',riesgo:'HIGH',evidencia:'MEDIUM',
        documentos:2,fuentes_juridicas:14,problema_juridico:'Determinar la validez de la no renovación.',
        hallazgo_principal:'La conclusión depende de la prueba documental.'},
      facts,sources:[privateSource],caseId:'CASE-A'
    })}))
    assert.match(html,/SÍNTESIS DEL CASO/)
    assert.match(html,/Resumen ejecutivo/)
    assert.match(html,/El caso requiere revisión de la no renovación/)
    assert.equal((html.match(/<dt\b/g)||[]).length,6)
    for(const text of ['Derecho Laboral Público','Proceso contencioso administrativo de revisión',
      'Alto','Medio','Documentos del caso','Fuentes jurídicas recuperadas','Hechos clave',
      'Problema jurídico','Determinar la validez de la no renovación',
      'Hallazgo principal','La conclusión depende de la prueba documental']) assert.ok(html.includes(text),text)
    assert.match(html,/>2<\/dd>/)
    assert.match(html,/>14<\/dd>/)
    assert.ok(html.indexOf('Memorando comunicó') < html.indexOf('Se alega que se contrató'))
    assert.equal((html.match(/<li\b/g)||[]).length,5)
    assert.ok(!html.includes('FACT-') && !html.includes('SRC-'))
    assert.ok(!/>\s*(?:HIGH|MEDIUM|summary|risk|evidence|completed)\s*</i.test(html))
    const mismatchedCase=await renderToString(createSSRApp({render:()=>h(component,{
      summary:{documentos:1,fuentes_juridicas:0},facts:[facts[1]],
      sources:[{...privateSource,case_id:'CASE-B'}],caseId:'CASE-A'
    })}))
    assert.match(mismatchedCase,/Se alega que memorando comunicó la no renovación/)
    const reportBacked=await renderToString(createSSRApp({render:()=>h(component,{
      summary:{rama:'Laboral',documentos:0,fuentes_juridicas:0},
      reportDocument:{sections:[
        {title:'Objeto y alcance',content:'La controversia requiere revisión documental. [1]'},
        {title:'Conclusión',content:'La conclusión permanece condicionada a la prueba.'}
      ]}
    })}))
    assert.match(reportBacked,/La controversia requiere revisión documental/)
    assert.match(reportBacked,/La conclusión permanece condicionada a la prueba/)
    assert.ok(!reportBacked.includes('[1]'))
    const view=await readFile(new URL('../src/views/NovaCaseView.vue',import.meta.url),'utf8')
    assert.ok(!view.includes('class="research-notice"'))
    assert.match(view,/defaultTab="summary"/)
    assert.match(view,/class="summary-court-cta" @click="continueInNovaCourt"/)
  } finally { await server.close() }
})
