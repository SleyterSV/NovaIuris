import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { normalizeCaseResult } from '../src/utils/caseContract.js'
import { normalizeSource, resolveCitations } from '../src/utils/sourceContract.js'
import {
  ARGUMENT_SECTION_LABELS, canAttachDocumentsToCase, evidenceAvailability,
  factAllegationOrigin, presentableText, researchNotice, relatedFactTexts, verifiedArgumentSources,
  groupedJurisprudence, jurisprudenceMarkdown, argumentNeedsVerification, argumentCitationForSource,
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

test('numeric citation badges preserve canonical click targets and compact screen styling', async () => {
  const server=await createServer({server:{middlewareMode:true,hmr:false,port:0},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const component=(await server.ssrLoadModule('/src/components/common/MarkdownRenderer.vue')).default
    const second={...source,source_id:'SRC-bbbbbbbbbbbbbbbbbbbbbbbb',
      unit_id:'33333333-3333-4333-8333-333333333333',chunk_id:'33333333-3333-4333-8333-333333333333'}
    const privateSource={source_id:'private-one',source_scope:'private_case',case_id:'CASE-A',title:'Contrato'}
    const citations=[
      {...source,citation_id:'CIT-one',source_id:'source-alias',label:'[4]'},
      {...second,citation_id:'CIT-two',label:'[5]'},
      {citation_id:'CIT-private',source_id:privateSource.source_id,label:'[6]'}
    ]
    const props={content:'Criterio [4], reiterado [4], otra unidad [5], contrato [6].',
      citations,sources:[source,second,privateSource],caseId:'CASE-A',citationNumbersOnly:true}
    const selected=[]
    let bindings
    const probe={...component,setup(values,context){
      bindings=component.setup(values,{...context,emit:(_event,citation)=>selected.push(citation.source_id)})
      return bindings
    }}
    const html=await renderToString(createSSRApp({render:()=>h(probe,props)}))
    assert.equal((html.match(/data-citation-id="CIT-one"/g)||[]).length,2)
    for (const n of [4,5,6]) assert.match(html,new RegExp('data-numeric[^>]*>'+n+'<'))
    assert.doesNotMatch(html.replace(/<[^>]*>/g,''),/\[\d+\]|SRC-|private-one/)
    for (const id of ['CIT-one','CIT-two','CIT-private']) {
      bindings.handleCitationClick({target:{closest:()=>({dataset:{citationId:id}})}})
    }
    assert.deepEqual(selected,[source.source_id,second.source_id,privateSource.source_id])
    assert.deepEqual(citations.map(c=>c.label),['[4]','[5]','[6]'])
    const css=await readFile(new URL('../src/styles/novacaseCitations.css',import.meta.url),'utf8')
    for (const rule of ['width:max-content','flex:0 0 auto','justify-self:start','height:22px',
      'background:#142f4d','color:#fff',':focus-visible']) assert.ok(css.includes(rule),rule)
    const report=await readFile(new URL('../src/components/novacase/ReportView.vue',import.meta.url),'utf8')
    assert.match(report,/@media print \{\.report-paper :deep\(\.citation-inline\)/)
  } finally { await server.close() }
})

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
  assert.equal(verifiedArgumentSources({source_ids:[source.document_id]},[source],'CASE-A').length,0,
    'a document-only reference must not expand to every legal unit in that document')
})

test('argument source rows reuse canonical citation numbers per legal unit and private source', () => {
  const foundation13={...source,source_id:'SRC-bbbbbbbbbbbbbbbbbbbbbbbb',unit_id:'33333333-3333-4333-8333-333333333333',
    chunk_id:'33333333-3333-4333-8333-333333333333',unit_number:'13',page_start:6}
  const privateDocument={source_id:'SRC-private-case-page-1',source_scope:'private_case',case_id:'CASE-A',
    title:'Memorando de no renovación',display_title:'Memorando de no renovación',page_start:1}
  const citationPool=[source,foundation13,privateDocument]
  const citations=[
    {citation_id:'CIT-FOUNDATION-5',source_id:source.source_id,label:'[4]'},
    {citation_id:'CIT-FOUNDATION-13',source_id:foundation13.source_id,label:'[7]'},
    {citation_id:'CIT-PRIVATE-1',source_id:privateDocument.source_id,label:'[1]'}
  ]
  assert.equal(argumentCitationForSource(source,citations,citationPool,'CASE-A').label,'[4]')
  assert.equal(argumentCitationForSource(foundation13,citations,citationPool,'CASE-A').label,'[7]')
  assert.equal(argumentCitationForSource(privateDocument,citations,citationPool,'CASE-A').label,'[1]')
  const publicAlias={...foundation13,source_id:'SRC-cccccccccccccccccccccccc'}
  assert.equal(argumentCitationForSource(publicAlias,citations,[...citationPool,publicAlias],'CASE-A').label,'[7]',
    'a public source alias resolves only through the exact document and unit pair')
  const differentUnit={...foundation13,source_id:'SRC-dddddddddddddddddddddddd',unit_id:'44444444-4444-4444-8444-444444444444',chunk_id:'44444444-4444-4444-8444-444444444444'}
  assert.equal(argumentCitationForSource(differentUnit,citations,[...citationPool,differentUnit],'CASE-A'),null,
    'a different unit in the same judgment must not inherit the citation')
})

test('argument citation registry resolves runtime citation numbers by canonical V2 unit identity', async () => {
  const foundation11={...source,unit_number:'11',citation_number:11}
  const foundation13={...source,source_id:'SRC-bbbbbbbbbbbbbbbbbbbbbbbb',unit_id:'33333333-3333-4333-8333-333333333333',
    chunk_id:'33333333-3333-4333-8333-333333333333',unit_number:'13',page_start:6,citation_number:13}
  const privateDocument={source_id:'SRC-private-case-page-1',source_scope:'private_case',case_id:'CASE-A',
    title:'Memorando de no renovación',display_title:'Memorando de no renovación',page_start:1,citation_number:3}
  const sourcePool=[foundation11,foundation13,privateDocument]
  const citations=[
    {citation_id:'CIT-11',source_id:foundation11.source_id,source_scope:'public_legal',provenance_version:'v2',
      document_id:foundation11.document_id,unit_id:foundation11.unit_id,citation_number:11},
    {citation_id:'CIT-13-ALIAS',source_id:'SRC-cccccccccccccccccccccccc',source_scope:'public_legal',provenance_version:'v2',
      document_id:foundation13.document_id,unit_id:foundation13.unit_id,citation_number:13},
    {citation_id:'CIT-PRIVATE',source_id:privateDocument.source_id,citation_number:3}
  ]

  const registry=resolveCitations(citations,sourcePool,'CASE-A')
  assert.deepEqual(registry.citations.map(item=>item.source_id),sourcePool.map(item=>item.source_id),
    'public citation aliases resolve to the authorized source identity for that exact unit')
  assert.equal(argumentCitationForSource(foundation11,citations,sourcePool,'CASE-A').label,'[11]')
  assert.equal(argumentCitationForSource(foundation13,citations,sourcePool,'CASE-A').label,'[13]')
  assert.equal(argumentCitationForSource({...foundation13},citations,sourcePool,'CASE-A').label,'[13]',
    'the same unit reuses its registry number')
  assert.equal(argumentCitationForSource(privateDocument,citations,sourcePool,'CASE-A').label,'[3]')

  const server=await createServer({server:{middlewareMode:true,hmr:false,port:0},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const component=(await server.ssrLoadModule('/src/components/novacase/ArgumentsView.vue')).default
    const html=await renderToString(createSSRApp({render:()=>h(component,{
      arguments:{main_arguments:[
        {title:'Fundamento 11',text:'Primera consideración.',source_ids:[foundation11.source_id]},
        {title:'Fundamento 13',text:'Segunda consideración.',source_ids:[foundation13.source_id]},
        {title:'Reiteración del fundamento 13',text:'La misma unidad se reitera.',source_ids:[foundation13.source_id]},
        {title:'Documento del caso',text:'Comunicación privada.',source_ids:[privateDocument.source_id]}
      ]},sources:sourcePool,citations,caseId:'CASE-A'
    })}))
    assert.match(html,/source-reference-label[^>]*>11</)
    assert.equal((html.match(/source-reference-label[^>]*>13</g)||[]).length,2)
    assert.match(html,/source-reference-label[^>]*>3</)
    const canonicalRows=(html.match(/class="argument-source-list"/g)||[]).length
    const numberedRows=(html.match(/source-reference-label[^>]*>\d+</g)||[]).length
    assert.equal(numberedRows,canonicalRows,'no citation-backed canonical source row is left unnumbered')
    assert.equal(numberedRows,4)
    assert.match(html,/aria-label="Ver fuente 13"/)
  } finally { await server.close() }
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
    assert.match(argumentsHtml,/El fundamento requiere verificación documental o jurídica adicional/)
    assert.match(argumentsHtml,/Cese comunicado al trabajador/)
    assert.ok(!argumentsHtml.includes(factId) && !argumentsHtml.includes(issueId))

    const argumentData={main_arguments:[{title:'Insuficiencia de motivación del memorando',
      argument:'El acto se limitó a invocar el vencimiento del plazo.',legal_basis:['El criterio constitucional exige valorar la causa del cese. [1]'],
      supporting_fact_ids:[factId],source_ids:[source.source_id],risk:'Alto',strength:'Alta'}],
      constitutional_arguments:[{title:'Tutela constitucional',text:'La controversia compromete el derecho al trabajo.'}],
      jurisprudence_used:[source.source_id],general_observations:['']}
    const argumentsEditorial=await render('novacase/ArgumentsView',{
      arguments:argumentData,facts:[{fact_id:factId,text:'El memorando comunicó la no renovación.'}],
      sources:[source],caseId:'CASE-A',citations:[{citation_id:'citation-one',label:'[1]',source_id:source.source_id}]
    })
    assert.match(argumentsEditorial,/MYKE · NOVACASE/)
    assert.match(argumentsEditorial,/Argumentos jurídicos/)
    assert.match(argumentsEditorial,/Argumentos principales/)
    assert.match(argumentsEditorial,/Argumentos constitucionales/)
    assert.match(argumentsEditorial,/El acto se limitó a invocar el vencimiento del plazo/)
    assert.match(argumentsEditorial,/Fundamento jurídico/)
    assert.match(argumentsEditorial,/Hechos que respaldan este argumento/)
    assert.match(argumentsEditorial,/aria-label="Ver fuente 1"/)
    assert.match(argumentsEditorial,/Ver fuente/)
    assert.doesNotMatch(argumentsEditorial,/>Riesgo<|>Solidez<|>Alto<|>Alta<|Jurisprudencia considerada|Observaciones generales|case_document|public_legal|private_case|source_id|unit_id|\bSRC-[a-f0-9]{24}/i)
    assert.doesNotMatch(argumentsEditorial,/<span class="field-label">Argumento<\/span>/)
    assert.equal(argumentData.main_arguments[0].risk,'Alto')
    const argumentComponentSource=await readFile(new URL('../src/components/novacase/ArgumentsView.vue',import.meta.url),'utf8')
    assert.doesNotMatch(argumentComponentSource,/argument-grid|repeat\(auto-fit|minmax\(min\(100%,310px\)/)
    assert.match(argumentComponentSource,/grid-template-columns:40px minmax\(0,1fr\)/)
    assert.match(argumentComponentSource,/\.argument-content\{min-width:0;max-width:960px\}/)
    assert.match(argumentComponentSource,/argument-content>h4[^}]*overflow-wrap:break-word;hyphens:none/)
    assert.match(argumentComponentSource,/\.argument-prose :deep\(\.markdown-body\)[^}]*word-break:normal;overflow-wrap:break-word/)
    assert.doesNotMatch(argumentComponentSource,/word-break:\s*break-all/)
    const counterComponentSource=await readFile(new URL('../src/components/novacase/CounterArgumentsView.vue',import.meta.url),'utf8')
    assert.match(counterComponentSource,/grid-template-columns:40px minmax\(0,1fr\)/)
    assert.match(counterComponentSource,/\.counter-content,\.response-entry>div\{min-width:0;max-width:960px\}/)
    assert.match(counterComponentSource,/\.counter-editorial :deep\(\.markdown-body\)\{[^}]*word-break:normal;overflow-wrap:break-word/)
    assert.doesNotMatch(counterComponentSource,/word-break:\s*break-all/)
    const editorialStyles=await readFile(new URL('../src/styles/novacaseEditorial.css',import.meta.url),'utf8')
    assert.doesNotMatch(editorialStyles,/\.novacase-page \.argument-number\s*\{[^}]*position:\s*absolute/)
    assert.match(editorialStyles,/\.novacase-page \.argument-card \.argument-number\s*\{[^}]*position:\s*absolute/)

    const foundation13={...source,source_id:'SRC-bbbbbbbbbbbbbbbbbbbbbbbb',unit_id:'33333333-3333-4333-8333-333333333333',
      chunk_id:'33333333-3333-4333-8333-333333333333',unit_number:'13',page_start:6}
    const privateDocument={source_id:'SRC-private-case-page-1',source_scope:'private_case',case_id:'CASE-A',
      title:'Memorando de no renovación',display_title:'Memorando de no renovación',page_start:1}
    const numberedArguments=await render('novacase/ArgumentsView',{
      arguments:{main_arguments:[{title:'Regla del fundamento 5',argument:'Primera consideración.',source_ids:[source.source_id]},
        {title:'Regla del fundamento 13',argument:'Segunda consideración.',source_ids:[foundation13.source_id]}],
        secondary_arguments:[{title:'Aplicación del fundamento 13',argument:'La misma unidad vuelve a sustentar el análisis.',source_ids:[foundation13.source_id]}],
        procedural_arguments:[{title:'Comunicación privada',argument:'El memorando comunicó la decisión.',source_ids:[privateDocument.source_id]}]},
      sources:[source,foundation13,privateDocument],caseId:'CASE-A',citations:[
        {citation_id:'CIT-FOUNDATION-5',source_id:source.source_id,label:'[4]'},
        {citation_id:'CIT-FOUNDATION-13',source_id:foundation13.source_id,label:'[7]'},
        {citation_id:'CIT-PRIVATE-1',source_id:privateDocument.source_id,label:'[1]'}
      ]
    })
    assert.match(numberedArguments,/>4<.*STC Exp\. 00001-2024-PA\/TC.*Fundamento 7/s)
    assert.equal((numberedArguments.match(/source-reference-label[^>]*>7</g)||[]).length,2,
      'the same canonical unit must reuse its existing citation label across arguments')
    assert.match(numberedArguments,/source-reference-label[^>]*>1</)
    assert.equal((numberedArguments.match(/class="argument-source-list"/g)||[]).length,
      (numberedArguments.match(/source-reference-label[^>]*>\d+</g)||[]).length,
      'every linked source row in the citation contract must have a citation badge')
    assert.match(argumentComponentSource,/@click="selectSource\(source\)"/)
    assert.match(argumentComponentSource,/emit\('select-source', safe\)/)

    const counterEditorial=await render('novacase/CounterArgumentsView',{
      counterArguments:{procedural:[{id:'OBJECTION-1',title:'Vencimiento contractual',
        text:'La entidad alegaría que el vínculo concluyó al vencer el plazo.',risk:'HIGH',strength:'LOW',source_ids:[source.source_id]}],
        summary:'La objeción debe contrastarse con las circunstancias documentadas.'},
      responses:[{id:'RESPONSE-1',counterargument_id:'OBJECTION-1',response:'El vencimiento no excluye el control de la causa alegada.',source_ids:[source.source_id]}],
      sources:[source],caseId:'CASE-A',citations:[{citation_id:'citation-one',label:'[1]',source_id:source.source_id}]
    })
    assert.match(counterEditorial,/Contraargumentos previsibles/)
    assert.match(counterEditorial,/La entidad alegaría que el vínculo concluyó/)
    assert.match(counterEditorial,/Respuesta jurídica/)
    assert.match(counterEditorial,/El vencimiento no excluye el control/)
    assert.match(counterEditorial,/aria-label="Ver fuente 1"/)
    assert.match(counterEditorial,/source-label[^>]*>1</)
    assert.doesNotMatch(counterEditorial,/>Riesgo<|>Solidez<|>HIGH<|>LOW<|source_id|unit_id|public_legal|private_case/i)
    const emptyCounter=await render('novacase/CounterArgumentsView',{counterArguments:{procedural:['','   ']},responses:[]})
    assert.doesNotMatch(emptyCounter,/<li[^>]*>\s*<span[^>]*>0[1-9]<\/span>/)
    assert.match(emptyCounter,/No se identificaron objeciones/)
    assert.ok(!argumentsHtml.includes('Supporting fact ids'))

    const evidenceHtml=await render('novacase/EvidenceView',{evidence:{documents:'Contrato alegado'},documentCount:0})
    assert.match(evidenceHtml,/No se identificaron documentos incorporados al caso/)
    assert.match(evidenceHtml,/Agregar documentos al caso/)
    assert.match(evidenceHtml,/No se identificaron testimonios, peritajes ni evidencia digital/)
    assert.doesNotMatch(evidenceHtml,/Motor de anÃ¡lisis|MYKE \/ NovaCase/)
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
    assert.match(legalEvidence,/no constituyen prueba de los hechos del caso/)
    assert.equal((legalEvidence.match(/STC Exp. 00001-2024-PA\/TC/g) || []).length,1)

    const privateEvidenceSource={source_id:'SRC-private-doc-page-one',source_scope:'private_case',case_id:'CASE-A',
      document_id:'44444444-4444-4444-8444-444444444444',title:'Contrato CAS (SRC-aaaaaaaaaaaaaaaaaaaaaaaa)',
      display_title:'Contrato CAS (SRC-aaaaaaaaaaaaaaaaaaaaaaaa)',page_start:1}
    const privateEvidenceSourcePage2={...privateEvidenceSource,source_id:'SRC-private-doc-page-two',page_start:2}
    const privateMemo={source_id:'SRC-private-memo-page-one',source_scope:'private_case',case_id:'CASE-A',
      document_id:'55555555-5555-4555-8555-555555555555',title:'Memorando de no renovación',display_title:'Memorando de no renovación',page_start:1}
    const factualRecord={fact_id:'FACT-cccccccccccccccccccccccc',text:'El contrato acredita las funciones pactadas y la jornada institucional.',
      status:'supported',source_ids:[privateEvidenceSource.source_id]}
    const allegedRecord={fact_id:'FACT-dddddddddddddddddddddddd',text:'Se alega que las labores continuaron de forma permanente.',status:'alleged',source_ids:[]}
    const evidenceSources=[source,privateEvidenceSource,privateEvidenceSourcePage2,privateMemo]
    const evidenceCitations=[
      {citation_id:'EVIDENCE-CIT-1',source_id:privateEvidenceSource.source_id,label:'[1]'},
      {citation_id:'EVIDENCE-CIT-2',source_id:privateEvidenceSourcePage2.source_id,label:'[2]'},
      {citation_id:'EVIDENCE-CIT-3',source_id:privateMemo.source_id,label:'[3]'},
      {citation_id:'EVIDENCE-CIT-4',source_id:source.source_id,label:'[4]'}
    ]
    const professionalEvidence=await render('novacase/EvidenceView',{
      evidence:{summary:'La documentación acredita el vínculo y la comunicación de no renovación. Documento rotulado como "ficticio" en el entorno QA.'},
      analysis:{nivel_evidencia:'MEDIUM'},documentCount:2,caseId:'CASE-A',sources:evidenceSources,citations:evidenceCitations,
      facts:[factualRecord,allegedRecord],factGroups:[
        {key:'supported',facts:[factualRecord]},{key:'alleged',facts:[allegedRecord]},{key:'pending',facts:[]}
      ],issues:[{issue_id:issueId,title:'Permanencia de las funciones',text:'¿Las labores desempeñadas fueron permanentes?'}],
      evidenceLinks:[{evidence_id:'EVIDENCE-1',issue_id:issueId,fact_ids:[factId],source_ids:[privateEvidenceSource.source_id,privateEvidenceSourcePage2.source_id],
        what_it_supports:'El contrato identifica las funciones administrativas y logísticas.\n\nTambién consigna la jornada y supervisión institucional.',
        limitations:'No acredita por sí solo la permanencia efectiva de las labores.\n\nFalta corroboración con las adendas posteriores.'}]
    })
    assert.match(professionalEvidence,/Análisis probatorio/)
    assert.match(professionalEvidence,/Evaluación probatoria/)
    assert.match(professionalEvidence,/>Media</)
    assert.match(professionalEvidence,/Documentos aportados/)
    assert.match(professionalEvidence,/Hechos acreditados documentalmente/)
    assert.match(professionalEvidence,/Hechos pendientes de corroboración/)
    assert.match(professionalEvidence,/Pendiente de corroboración/)
    assert.match(professionalEvidence,/Fuentes jurídicas de apoyo/)
    assert.match(professionalEvidence,/no constituyen prueba de los hechos del caso/)
    assert.match(professionalEvidence,/Evidencia vinculada a las cuestiones jurídicas/)
    assert.match(professionalEvidence,/Limitaciones/)
    assert.match(professionalEvidence,/Contrato CAS · pág\. 1/)
    assert.match(professionalEvidence,/Documento contractual · 2 páginas utilizadas/)
    assert.doesNotMatch(professionalEvidence,/01_Contrato_CAS|01\s+<span class="row-number"|•\s*\[1\]/)
    const supportNoteStart=professionalEvidence.indexOf('class="document-note"')
    const supportBodyStart=professionalEvidence.indexOf('class="document-note-content"',supportNoteStart)
    const supportFirst=professionalEvidence.indexOf('El contrato identifica las funciones administrativas y logísticas.',supportBodyStart)
    const supportSecond=professionalEvidence.indexOf('También consigna la jornada y supervisión institucional.',supportBodyStart)
    const limitationsLabel=professionalEvidence.indexOf('Limitaciones</strong>',supportSecond)
    const limitationsBody=professionalEvidence.indexOf('class="document-note-content"',limitationsLabel)
    const limitationsFirst=professionalEvidence.indexOf('No acredita por sí solo la permanencia efectiva de las labores.',limitationsBody)
    const limitationsSecond=professionalEvidence.indexOf('Falta corroboración con las adendas posteriores.',limitationsBody)
    assert.ok(supportNoteStart < supportBodyStart && supportBodyStart < supportFirst && supportFirst < supportSecond && supportSecond < limitationsLabel)
    assert.ok(limitationsLabel < limitationsBody && limitationsBody < limitationsFirst && limitationsFirst < limitationsSecond)
    assert.equal((professionalEvidence.slice(supportBodyStart,limitationsLabel).match(/<p[ >]/g) || []).length,2)
    assert.equal((professionalEvidence.slice(limitationsBody,professionalEvidence.indexOf('document-pages',limitationsBody)).match(/<p[ >]/g) || []).length,2)
    for (const number of ['1','2','3']) assert.match(professionalEvidence,new RegExp('novacase-citation-badge[^>]*>'+number+'<'))
    assert.match(professionalEvidence,/Fundamento 7/)
    assert.match(professionalEvidence,/Ver documento/)
    assert.doesNotMatch(professionalEvidence,/SRC-[a-f0-9]{12,}|source_id|document_id|unit_id|private_case|public_legal|Motor de análisis|ficticio|entorno QA|Consultar fuente documental/i)

    const evidenceViewSource=await readFile(new URL('../src/components/novacase/EvidenceView.vue',import.meta.url),'utf8')
    assert.match(evidenceViewSource,/@click="selectSource\(source\)"/)
    assert.match(evidenceViewSource,/emit\('select-source', source\)/)
    assert.match(evidenceViewSource,/\.evidence-editorial\{[^}]*max-width:1240px/s)
    assert.match(evidenceViewSource,/\.document-list,[^}]*list-style:none/s)
    assert.match(evidenceViewSource,/\.source-action\{display:inline-flex/)
    assert.match(evidenceViewSource,/\.evidence-context dl\{display:grid;grid-template-columns:repeat\(5,minmax\(0,1fr\)\)/)
    assert.match(evidenceViewSource,/<div v-if="group\.supports\.length" class="document-note">\s*<strong>Acredita<\/strong>\s*<div class="document-note-content"><MarkdownRenderer citation-numbers-only v-for=/)
    assert.match(evidenceViewSource,/<div v-if="group\.limitations\.length" class="document-note limitation-note">\s*<strong>Limitaciones<\/strong>\s*<div class="document-note-content"><MarkdownRenderer citation-numbers-only v-for=/)
    assert.match(evidenceViewSource,/grid-template-columns:minmax\(90px,105px\) minmax\(0,1fr\)/)
    assert.match(evidenceViewSource,/\.document-note-content\{min-width:0;word-break:normal;overflow-wrap:break-word\}/)
    assert.match(evidenceViewSource,/@media\(max-width:680px\)\{[\s\S]*?\.document-note\{grid-template-columns:minmax\(0,1fr\)/)
    const privateSource={source_id:'SRC-private-analysis',source_scope:'private_case',case_id:'CASE-A'}
    const analysisHtml=await render('novacase/AnalysisView',{
      analysis:{rama_derecho:'Laboral',tipo_proceso:'Proceso laboral',pretension_principal:'Reposición',
        nivel_evidencia:'MEDIUM',issues:['¿La no renovación requiere motivación?'],law:[{title:'Decreto Legislativo N.º 1057',description:'Régimen de contratación administrativa de servicios.'}],
        observations:['Corroborar las funciones desempeñadas.']},
      facts:[
        {fact_id:factId,text:'El contrato fue suscrito el 1 de marzo de 2021. [1]',status:'supported',source_ids:[privateSource.source_id],date:'2021-03-01'},
        {fact_id:'FACT-bbbbbbbbbbbbbbbbbbbbbbbb',text:'Se alega continuidad de las funciones.',status:'alleged',source_ids:[],date:'2021-04-01'}
      ],
      timelineData:[
        {fact_id:'FACT-bbbbbbbbbbbbbbbbbbbbbbbb',date:'2021-04-01',description:'Se alega continuidad de las funciones.'},
        {fact_id:factId,date:'2021-03-01',description:'El contrato fue suscrito el 1 de marzo de 2021. [1]',source_ids:[privateSource.source_id]}
      ],
      sources:[source,privateSource],caseId:'CASE-A',documentCount:1,publicSourceCount:1,
      citations:[{citation_id:'citation-one',label:'[1]',source_id:privateSource.source_id}]
    })
    assert.match(analysisHtml,/Análisis jurídico/)
    assert.match(analysisHtml,/Visión general/)
    assert.match(analysisHtml,/Base fáctica del caso/)
    assert.match(analysisHtml,/Hechos con respaldo documental/)
    assert.match(analysisHtml,/Hechos alegados/)
    assert.match(analysisHtml,/Pendiente de corroboración/)
    assert.match(analysisHtml,/Problemas jurídicos/)
    assert.match(analysisHtml,/Marco normativo aplicable/)
    assert.match(analysisHtml,/Jurisprudencia relevante/)
    assert.match(analysisHtml,/Observaciones y elementos por verificar/)
    assert.match(analysisHtml,/Cronología del caso/)
    assert.ok(analysisHtml.indexOf('01 MAR 2021') < analysisHtml.indexOf('01 ABR 2021'))
    assert.match(analysisHtml,/Ver fuente/)
    assert.match(analysisHtml,/aria-label="Ver fuente 1"/)
    const internalLeak = analysisHtml.match(/METODOLOGÍA|Proceso de Análisis|intake|documents|\bFACT-[a-f0-9]{24}|\bSRC-[a-f0-9]{24}|private_case|public_legal|unit_id|source_id/i)?.[0]
    assert.equal(internalLeak,undefined,`Texto interno visible: ${internalLeak || ''}`)
    assert.match(analysisHtml,/Medio/)
    assert.match(analysisHtml,/no renovación requiere motivación/i)
    assert.match(analysisHtml,/STC Exp. 00001-2024-PA\/TC/)
    assert.match(analysisHtml,/Fundamento 7/)
    const citedAnalysis=await render('novacase/AnalysisView',{
      analysis:{issues:['Criterio jurídico respaldado [1]']},sources:[source],caseId:'CASE-A',
      citations:[{citation_id:'citation-one',label:'[1]',source_id:source.source_id}]
    })
    assert.match(citedAnalysis,/aria-label="Ver fuente 1"/)
    assert.ok(!citedAnalysis.includes(source.source_id))
    assert.doesNotMatch(citedAnalysis,/METODOLOGÍA|ETAPA 01|Proceso de Análisis/)

    const repeatedCriticalText='Puede cuestionarse la idoneidad de la vía si se considera igualmente satisfactoria.'
    const riskHtml=await render('novacase/RiskView',{risk:{risk_level:'MEDIUM',summary_text:'Las principales contingencias dependen de la vía y de completar el respaldo documental.',
      strategic:[{title:'Idoneidad de la vía procesal',risk:repeatedCriticalText,impact:'HIGH'}],
      procedural:[{title:'Idoneidad de la vía procesal',risk:repeatedCriticalText,mitigation:'Preparar subsidiariamente la vía contencioso-administrativa.'}],
      evidentiary:[{title:'Renovaciones no acreditadas',description:'No se incorporaron las adendas.',impact:'Puede afectar la continuidad acreditada.',mitigation:'Recabar las adendas disponibles.'}],
      legal:[{title:'Suficiencia de la motivación',text:'La motivación del acto puede ser objeto de controversia.'}],
      recommendations:[{category:'Documentación contractual',action:'Solicitar copias de las adendas.'},{category:'Vía procesal',action:'Revisar el cómputo del plazo.'}]}})
    assert.match(riskHtml,/Evaluación de riesgos/)
    assert.match(riskHtml,/Nivel general/)
    assert.match(riskHtml,/>Medio</)
    assert.match(riskHtml,/Riesgos prioritarios/)
    assert.ok(riskHtml.indexOf('aria-labelledby="priority-title"') < riskHtml.indexOf('id="risk-section-procedural"'))
    assert.match(riskHtml,/Riesgos procesales/)
    assert.match(riskHtml,/Riesgos probatorios/)
    assert.match(riskHtml,/Riesgos jurídicos/)
    assert.match(riskHtml,/Plan de mitigación/)
    assert.match(riskHtml,/Documentación contractual/)
    assert.match(riskHtml,/Preparar subsidiariamente la vía contencioso-administrativa/)
    assert.equal((riskHtml.match(/Puede cuestionarse la idoneidad de la vía si se considera igualmente satisfactoria\./g) || []).length,1)
    assert.match(riskHtml,/Alto/)
    assert.match(riskHtml,/Impacto/)
    const visibleRiskText=riskHtml.replace(/<[^>]*>/g,' ')
    assert.doesNotMatch(visibleRiskText,/probabilidad de ganar|\b(?:70|80)%|\b(?:HIGH|MEDIUM|LOW|CRITICAL)\b/i)
    assert.doesNotMatch(riskHtml,/risk_analysis|procedural_risks|critical_risks|source_id|task_id|case_id|document_id|unit_id|SRC-[a-f0-9]{24}/i)
    const riskComponent=await readFile(new URL('../src/components/novacase/RiskView.vue',import.meta.url),'utf8')
    assert.match(riskComponent,/\.risk-editorial\{[^}]*max-width:1240px/s)
    assert.match(riskComponent,/\.risk-summary\{display:grid;grid-template-columns/)
    assert.match(riskComponent,/@media\(max-width:1439px\)/)
    assert.match(riskComponent,/criticalRisks\.value\.length/)
    assert.doesNotMatch(riskComponent,/overall_probability|win_probability|probability.*%/i)
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

test('NovaCase strategy renders one editorial plan and resolves only canonical source references', async () => {
  const server=await createServer({server:{middlewareMode:true,hmr:false,port:0},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const component=(await server.ssrLoadModule('/src/components/novacase/StrategyView.vue')).default
    const citations=[{citation_id:'CIT-STRATEGY-1',label:'[1]',citation_number:1,source_id:source.source_id,
      source_scope:'public_legal',provenance_version:'v2',document_id:source.document_id,unit_id:source.unit_id}]
    const finalStrategy={
      objective:'Reposición en el puesto o en otro de similar nivel.',
      principal_line:'Solicitar la nulidad del acto de no renovación y la reposición laboral.',
      supporting_arguments:[{title:'Motivación insuficiente del acto',argument:'El memorando invoca únicamente el vencimiento del plazo. [1]',
        legal_basis:['La motivación debe evaluarse conforme al criterio constitucional. [1]'],supporting_fact_ids:[factId],source_ids:[source.source_id],issue_id:issueId,strength:'Alta',risk:'Medio'}],
      priority_evidence:[{title:'Renovaciones del vínculo',relevance:'Permitirían verificar la continuidad temporal del CAS.',status:'pending',source_ids:[source.source_id]}],
      risks_to_mitigate:[{title:'Idoneidad de la vía',risk:'Puede cuestionarse la vía propuesta.',mitigation:'Preparar el sustento procesal.'}],
      opposing_positions:[{title:'Vía igualmente satisfactoria',argument:'La parte contraria podría objetar la idoneidad del amparo.'}],
      recommended_actions:['Recabar adendas de renovación.','Verificar el cómputo del plazo.','Recabar adendas de renovación.'],
      missing_information:['Adendas y resoluciones de renovación.']
    }
    const html=await renderToString(createSSRApp({render:()=>h(component,{
      strategy:{objective:'Reposición en el puesto o en otro de similar nivel.',claim_strategy:'Solicitar la nulidad del acto de no renovación y la reposición laboral.',
        recommended_actions:['Recabar adendas de renovación.'],missing_information:['Adendas y resoluciones de renovación.']},
      finalStrategy,arguments:{main_arguments:finalStrategy.supporting_arguments},facts:[{fact_id:factId,text:'El memorando comunicó la no renovación.'}],
      issues:[{issue_id:issueId,text:'¿La motivación del acto fue suficiente?'}],sources:[source],citations,caseId:'CASE-A',analyzed:true
    })}))
    assert.match(html,/strategy-title/)
    assert.match(html,/strategy-main-card/)
    assert.match(html,/objective-card/)
    assert.match(html,/key-condition-card/)
    assert.match(html,/objective-title/)
    assert.match(html,/main-strategy-title/)
    assert.match(html,/pending-title/)
    assert.match(html,/opposing-title/)
    assert.match(html,/evidence-title/)
    assert.match(html,/actions-title/)
    assert.match(html,/risks-title/)
    assert.match(html,/Fundamentos de la estrategia/)
    assert.match(html,/conclusion-title/)
    assert.match(html,/source-label[^>]*>1</)
    assert.match(html,/Ver fuente 1/)
    const visible=html.replace(/<[^>]*>/g, ' ')
    assert.equal((visible.match(/Recabar adendas de renovaci.n/g)||[]).length,1,"repeated recommendations are consolidated")
    assert.doesNotMatch(visible,/Missing information|Opposing positions|Principal line|Priority evidence|Recommended actions|Risks to mitigate|Supporting arguments|Issue id|Source ids|Supporting fact ids|Legal basis|Strength|Title/i)
    assert.doesNotMatch(html,/ISSUE-[a-f0-9]{24}|SRC-[a-f0-9]{24}|FACT-[a-f0-9]{24}|source_id|fact_id|issue_id|document_id|unit_id|task_id|case_id/i)
    const view=await readFile(new URL('../src/views/NovaCaseView.vue',import.meta.url),'utf8')
    assert.doesNotMatch(view,/<MarkdownRenderer\s+:content="canonicalResult\.final_strategy"/)
    assert.match(view,/:final-strategy="canonicalResult\?\.final_strategy/)
    const componentSource=await readFile(new URL('../src/components/novacase/StrategyView.vue',import.meta.url),'utf8')
    assert.match(componentSource,/grid-template-columns:minmax\(0,2fr\) minmax\(280px,1fr\)/)
    assert.doesNotMatch(componentSource,/grid-template-columns:repeat\(3,minmax\(0,1fr\)\)/)
    assert.match(componentSource,/@media\(max-width:1359px\)\{\.strategy-overview\{grid-template-columns:minmax\(0,1fr\)\}/)
  } finally { await server.close() }
})

test('Informe shows one cited source list, safe actions and no QA scope box', async () => {
  const server=await createServer({server:{middlewareMode:true,hmr:false,port:0},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const {default:ReportView}=await server.ssrLoadModule('/src/components/novacase/ReportView.vue')
    const citation={citation_id:'CIT-1',source_id:source.source_id,label:'[1]'}
    const report='# Informe jurídico\nMunicipalidad Distrital de Santa Esperanza\n\n## Objeto y alcance\nEl criterio citado [1] requiere revisión.\n## Fuentes\nListado duplicado.'
    const html=await renderToString(createSSRApp({render:()=>h(ReportView,{
      report,reportDocument:{title:'Informe jurídico',citations:[citation],sources:[source]},
      caseId:'CASE-A',taskId:'00000000-0000-4000-8000-000000000001'
    })}))
    assert.equal((html.match(/<h3[^>]*>Fuentes utilizadas<\/h3>/g)||[]).length,1)
    assert.match(html,/Ver fuente 1/)
    assert.match(html,/<p>Municipalidad Distrital de Santa Esperanza<\/p>/)
    assert.match(html,/class="citation-inline"[^>]*data-citation-id="CIT-1"[^>]*>1<\/button>/)
    assert.match(html,/class="reference-number"[^>]*>1<\/span>/)
    assert.ok(!html.includes('[1]'))
    assert.equal(citation.label,'[1]')
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
  assert.match(view,/<AnalysisView[\s\S]*?:facts="canonicalResult\?\.facts \|\| \[\]"/)
  assert.match(view,/:sources="\[\.\.\.\(canonicalResult\?\.research\?\.sources \|\| \[\]\), \.\.\.\(canonicalResult\?\.sources \|\| \[\]\)/)
  const analysis = await readFile(new URL('../src/components/novacase/AnalysisView.vue',import.meta.url),'utf8')
  assert.match(analysis,/\['case', 'private_case'\]\.includes\(source\.source_scope\) && source\.case_id === props\.caseId/)
  assert.match(analysis,/Pendiente de corroboración/)
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
      document_id:'private-document-one',title:'01_Contrato_CAS_Mariana_Torres.pdf',page_start:1}
    const privateTwo={source_id:'SRC-private-two',source_scope:'private_case',case_id:'CASE-A',
      document_id:'private-document-two',title:'02_Memorando_No_Renovacion_Mariana_Torres.pdf',page_start:1}
    const second={...source,source_id:'SRC-bbbbbbbbbbbbbbbbbbbbbbbb',
      unit_id:'33333333-3333-4333-8333-333333333333',chunk_id:'33333333-3333-4333-8333-333333333333',
      unit_number:null,metadata:{unit_type:'foundation',unit_number:null},section:'Antecedentes',page_start:3}
    const third={...source,source_id:'SRC-cccccccccccccccccccccccc',
      document_id:'44444444-4444-4444-8444-444444444444',
      unit_id:'55555555-5555-4555-8555-555555555555',chunk_id:'55555555-5555-4555-8555-555555555555',
      title:'STC Exp. 04852-2023-PA/TC',display_title:'STC Exp. 04852-2023-PA/TC',unit_number:'4'}
    const sameUnitAlias={...source,source_id:'SRC-dddddddddddddddddddddddd'}
    const citations=[privateOne,privateTwo,source,second,third].map((item,index)=>({
      citation_id:`CIT-SOURCES-${index+1}`,source_id:item.source_id,citation_number:index+1,label:`[${index+1}]`
    }))
    const html=await renderToString(createSSRApp({render:()=>h(component,{
      sources:[privateOne,privateTwo,source,second,third,sameUnitAlias,source],citations,caseId:'CASE-A'})}))
    assert.match(html,/Fuentes del caso/)
    assert.match(html,/Contrato CAS Mariana Torres/)
    assert.match(html,/Memorando No Renovacion Mariana Torres/)
    assert.match(html,/>3 <span[^>]*>unidades verificadas<\/span>/)
    assert.match(html,/1 página utilizada/)
    assert.match(html,/Fuentes jurídicas verificadas/)
    const visibleHtml=html.replace(/<[^>]*>/g,' ')
    assert.equal((visibleHtml.match(/STC Exp\. 00001-2024-PA\/TC/g)||[]).length,1)
    assert.match(html,/STC Exp\. 04852-2023-PA\/TC/)
    assert.match(html,/Fundamento 7/)
    assert.match(html,/Fundamento: Antecedentes/)
    assert.match(html,/aria-label="Abrir STC Exp\. 00001-2024-PA\/TC, Fundamento 7, pág\. 2"/)
    assert.match(html,/unit-citation[^>]*>3</)
    assert.match(html,/unit-citation[^>]*>4</)
    assert.match(html,/unit-citation[^>]*>5</)
    assert.match(html,/Abrir/)
    assert.doesNotMatch(html,/<li[^>]*>\s*<\/li>/)
    assert.doesNotMatch(html,/private_case|public_legal|source_type|SRC-|source_id|document_id|unit_id|case_id/i)
    assert.ok(!html.includes(source.unit_id) && !html.includes(second.unit_id) && !html.includes(privateOne.source_id))
    const parent=await readFile(new URL('../src/views/NovaCaseView.vue',import.meta.url),'utf8')
    assert.match(parent,/<CaseSourcesView[\s\S]*?:citations="canonicalResult\?\.citations \|\| \[\]"[\s\S]*?@select-source="selectedSource = \$event"/)
    const modal=await readFile(new URL('../src/components/common/SourceModal.vue',import.meta.url),'utf8')
    assert.match(modal,/loadLegalUnitSource\(source\.chunk_id, source\.document_id/)
    assert.match(modal,/unit\.unit_id !== source\.chunk_id \|\| unit\.document_id !== source\.document_id/)
  } finally { await server.close() }
})

test('risk overview keeps the full assessment in one summary card', async () => {
  const server=await createServer({server:{middlewareMode:true,hmr:false,port:0},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const component=(await server.ssrLoadModule('/src/components/novacase/RiskView.vue')).default
    const assessment='Medio: factores concretos, contingencias procesales y medidas de mitigación.'
    const html=await renderToString(createSSRApp({render:()=>h(component,{risk:{risk_level:assessment}})}))
    assert.equal(html.split(assessment).length-1,1)
    assert.equal(html.split('Nivel general').length-1,1)
    assert.match(html,/summary-overall/)
    assert.match(html,/Evaluación de riesgos/)
  } finally { await server.close() }
})

test('executive summary restores six real indicators and evidence-aware key facts', async () => {
  const server=await createServer({server:{middlewareMode:true,hmr:false,port:0},appType:'custom',logLevel:'error',optimizeDeps:{noDiscovery:true,include:[]}})
  try {
    const component=(await server.ssrLoadModule('/src/components/common/ExecutiveSummary.vue')).default
    for (const [riesgo, expected] of [
      ['Bajo: explicación extensa.', 'Bajo'], ['Medio: factores concretos y mitigación.', 'Medio'],
      ['Nivel de riesgo: Alto — explicación extensa.', 'Alto'], ['HIGH', 'Alto'],
      ['Información insuficiente; podría aumentar el riesgo alto.', 'No identificado']
    ]) {
      const rendered=await renderToString(createSSRApp({render:()=>h(component,{summary:{riesgo}})}))
      const card=rendered.match(/summary-card--risk[\s\S]*?<dd\b[^>]*>(.*?)<\/dd>/)
      assert.equal(card?.[1],expected)
    }
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
