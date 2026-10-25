import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { resolveCitations } from '../src/utils/sourceContract.js'

const caseId = 'CASE-NOVA-1'
const documentId = '11111111-1111-4111-8111-111111111111'
const unitOne = '22222222-2222-4222-8222-222222222222'
const unitTwo = '33333333-3333-4333-8333-333333333333'
const publicOne = { source_id:'SRC-aaaaaaaaaaaaaaaaaaaaaaaa', source_scope:'public_legal', provenance_version:'v2',
  document_id:documentId, unit_id:unitOne, chunk_id:unitOne, source_type:'judgment', title:'STC Exp. 02047-2025-PA/TC',
  court:'Tribunal Constitucional', unit_type:'foundation', unit_number:'5', page_start:4 }
const publicTwo = { ...publicOne, source_id:'SRC-bbbbbbbbbbbbbbbbbbbbbbbb', unit_id:unitTwo, chunk_id:unitTwo,
  unit_number:'11', page_start:5 }
const privateSource = { source_id:'SRC-PRIVATE001', source_scope:'case', case_id:caseId, title:'Contrato CAS N.º 014', page_start:1 }
const citations = [
  { citation_id:'CIT-000000000000000000000004', source_id:publicOne.source_id, label:'[4]' },
  { citation_id:'CIT-000000000000000000000006', source_id:'SRC-cccccccccccccccccccccccc',
    source_scope:'public_legal', provenance_version:'v2', document_id:documentId,
    unit_id:unitTwo, chunk_id:unitTwo, label:'[6]' },
  { citation_id:'CIT-000000000000000000000001', source_id:privateSource.source_id, label:'[1]' }
]

test('NovaCourt arguments present structured content and resolve public/private sources canonically', async () => {
  const server = await createServer({ server:{ middlewareMode:true, hmr:false, port:0 }, appType:'custom', logLevel:'error', optimizeDeps:{ noDiscovery:true, include:[] } })
  try {
    const component = (await server.ssrLoadModule('/src/components/novacourt/CourtArguments.vue')).default
    const argumentData = { main_arguments:[{
      argument_id:'ARG-INTERNAL-1', title:'Control de validez del acto administrativo',
      argument:'El acto debe superar el control de legalidad [4] y el estándar de motivación [6].',
      legal_basis:['La jurisprudencia distingue ambos fundamentos [4] [6].'],
      supporting_fact_ids:['FACT-111111111111111111111111','FACT-222222222222222222222222'],
      source_ids:[publicOne.source_id,publicTwo.source_id,privateSource.source_id]
    }],
    possible_counterarguments:[{ counterargument_id:'COUNTER-INTERNAL-1', argument_id:'ARG-INTERNAL-1', objection:'La entidad podría sostener que el acto fue debidamente motivado.' }],
    counterargument_responses:[{ counterargument_id:'COUNTER-INTERNAL-1', argument_id:'ARG-INTERNAL-1', response:'La respuesta debe contrastarse con las razones expresadas en el acto.' }],
    secondary_arguments:[{ title:'Respaldo documental', argument:'El expediente incluye el contrato [1].', source_ids:[privateSource.source_id] }] }
    const facts = [
      { fact_id:'FACT-111111111111111111111111', status:'supported', text:'El expediente registra la fecha de notificación.' },
      { fact_id:'FACT-222222222222222222222222', status:'alleged', text:'La parte refiere que no recibió respuesta.' }
    ]
    const result = { case_id:caseId, sources:[publicOne,publicTwo,privateSource], citations, arguments:argumentData, facts }
    const html = await renderToString(createSSRApp({ render:() => h(component, {
      argumentData, facts, result, simulation:{ status:'ready' }, caseId,
      content:'Contenido alternativo [4]'
    }) }))
    assert.match(html,/MYKE · NOVACOURT/)
    assert.match(html,/Argumentos jurídicos/)
    assert.match(html,/Control de validez del acto administrativo/)
    assert.match(html,/Fundamento jurídico/)
    assert.match(html,/El expediente registra la fecha de notificación/)
    assert.match(html,/Según lo manifestado; requiere corroboración: La parte refiere que no recibió respuesta/)
    assert.match(html,/Posición contraria/)
    assert.match(html,/La entidad podría sostener que el acto fue debidamente motivado/)
    assert.match(html,/Respuesta \/ réplica/)
    assert.match(html,/La respuesta debe contrastarse con las razones expresadas en el acto/)
    assert.match(html,/Fuentes jurídicas/)
    assert.match(html,/Documentos del caso/)
    assert.match(html,/STC Exp\. 02047-2025-PA\/TC/)
    assert.match(html,/Tribunal Constitucional/)
    assert.match(html,/Fundamento 5 · Tribunal Constitucional · pág\. 4/)
    assert.match(html,/Contrato CAS N\.º 014/)
    assert.match(html,/Documento aportado · pág\. 1/)
    assert.match(html,/Ver fuente/)
    assert.match(html,/Ver documento/)
    assert.match(html,/class="citation-inline"[^>]*data-citation-id/)
    assert.match(html,/>4<\/button>/)
    assert.match(html,/>6<\/button>/)
    assert.doesNotMatch(html.replace(/<[^>]*>/g,' '),/\[(?:1|4|6)\]|SRC-|FACT-|ISSUE-|ARG-INTERNAL|document_id|unit_id|strength|risk/i)
    const resolved = resolveCitations(citations, [publicOne,publicTwo,privateSource], caseId)
    assert.deepEqual(resolved.citations.map(item => item.source_id), [publicOne.source_id,publicTwo.source_id,privateSource.source_id])
    assert.notEqual(resolved.citations[0].source_id, resolved.citations[1].source_id)
    const source = await readFile(new URL('../src/components/novacourt/CourtArguments.vue',import.meta.url),'utf8')
    assert.match(source,/@select-citation="openCitation"/)
    assert.match(source,/sources\.value\.find\(source => source\.source_id === citation\?\.source_id\)/)
    assert.match(source,/\.source-citation\{[^}]*width:max-content/)
    assert.doesNotMatch(source,/\.source-citation\{[^}]*width:\s*100%/)
    assert.match(source,/source_scope === 'public_legal'/)
    assert.match(source,/source_scope\)/)
    const citationCss = await readFile(new URL('../src/styles/novacaseCitations.css',import.meta.url),'utf8')
    assert.match(citationCss,/\.citation-inline\[data-numeric\][\s\S]*?height:22px;min-width:22px;width:max-content/)
    assert.match(source,/\.argument-entry\{[^}]*grid-template-columns:38px minmax\(0,1fr\)/)
  } finally { await server.close() }
})
