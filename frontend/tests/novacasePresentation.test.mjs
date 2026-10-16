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
  presentableText, researchNotice, relatedFactTexts, verifiedArgumentSources
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
    assert.match(argumentsHtml,/Fundamento jurídico preliminar/)
    assert.match(argumentsHtml,/Cese comunicado al trabajador/)
    assert.ok(!argumentsHtml.includes(factId) && !argumentsHtml.includes(issueId))
    assert.ok(!argumentsHtml.includes('Supporting fact ids'))

    const evidenceHtml=await render('novacase/EvidenceView',{evidence:{documents:'Contrato alegado'},documentCount:0})
    assert.match(evidenceHtml,/Sin documentos aportados al caso/)
    assert.match(evidenceHtml,/Agregar documentos al caso/)
    assert.match(evidenceHtml,/No aportada/)

    const riskHtml=await render('novacase/RiskView',{risk:{procedural:[{risk:'Plazo por comprobar',impact:'Alto',mitigation:'Verificar notificación'}]}})
    assert.match(riskHtml,/Riesgos procesales/)
    assert.match(riskHtml,/Mitigación/)
    assert.match(riskHtml,/Verificar notificación/)

    const summaryHtml=await render('common/ExecutiveSummary',{summary:{documentos:0,fuentes_juridicas:1}})
    assert.match(summaryHtml,/Documentos del caso/)
    assert.match(summaryHtml,/Fuentes jurídicas recuperadas/)

    const sourcesHtml=await render('common/SourcesList',{sources:[source],caseId:'CASE-A'})
    assert.match(sourcesHtml,/Tribunal Constitucional/)
    assert.match(sourcesHtml,/Fundamento 7/)
    assert.match(sourcesHtml,/pág. 2/)

    const reportHtml=await render('novacase/ReportView',{report:`# Informe ${factId}\nHecho por verificar.`,
      reportDocument:{},documentCount:0,publicSourceCount:0,caseId:'CASE-A'})
    assert.match(reportHtml,/Hechos alegados/)
    assert.match(reportHtml,/Marco jurídico preliminar/)
    assert.ok(!reportHtml.includes(factId))

    const caseView=await readFile(new URL('../src/views/NovaCaseView.vue',import.meta.url),'utf8')
    const mikeView=await readFile(new URL('../src/views/MikeView.vue',import.meta.url),'utf8')
    const summaryCss=await readFile(new URL('../src/components/common/ExecutiveSummary.vue',import.meta.url),'utf8')
    assert.match(caseView,/<ArgumentsView /)
    assert.match(caseView,/@add-documents="addDocuments"/)
    assert.match(mikeView,/@add-documents="addCaseDocuments\(turn,\$event\)"/)
    assert.match(mikeView,/canAttachDocumentsToCase\(payload\?\.caseId, workspace\.value\.caseId/)
    assert.match(summaryCss,/\.card-title\s*\{[^}]*white-space: normal/s)
  } finally { await server.close() }
})
