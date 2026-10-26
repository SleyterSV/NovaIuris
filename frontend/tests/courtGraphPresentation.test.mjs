import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { graphKind, graphLabel, graphColor, graphRelation, graphSearchText,
  authorizedGraphSources, graphLocator } from '../src/utils/courtGraphPresentation.js'

const panel = readFileSync(new URL('../src/components/novacourt/GraphPanel.vue', import.meta.url), 'utf8')
const courtView = readFileSync(new URL('../src/views/NovaCourtView.vue', import.meta.url), 'utf8')

test('facts, parties and simulated judgment have human, non-color-only labels', () => {
  assert.equal(graphLabel({ entity_type: 'FACT', status: 'supported' }), 'Hecho acreditado')
  assert.equal(graphLabel({ entity_type: 'FACT', status: 'alleged' }), 'Hecho alegado')
  assert.equal(graphLabel({ entity_type: 'FACT', status: 'unclear' }), 'Hecho no determinado')
  assert.equal(graphKind({ entity_type: 'FACT', status: 'supported' }), 'accredited')
  assert.equal(graphKind({ entity_type: 'FACT', status: 'unclear' }), 'undetermined')
  assert.equal(graphLabel({ entity_type: 'PARTY', legal_role: 'claimant' }), 'Demandante')
  assert.equal(graphLabel({ entity_type: 'PARTY', legal_role: 'respondent' }), 'Demandado')
  assert.notEqual(graphColor({ entity_type: 'PARTY', legal_role: 'claimant' }),
    graphColor({ entity_type: 'PARTY', legal_role: 'respondent' }))
  assert.equal(graphLabel({ entity_type: 'JUDGE_ANALYSIS' }), 'Evaluación judicial simulada')
  assert.equal(graphLabel({ entity_type: 'DECISION' }), 'Decisión simulada')
  assert.match(panel, /Resultado de simulación; no es una resolución judicial auténtica/)
})

test('source actions accept only authorized case or canonical V2 sources', () => {
  const sources = [
    { source_id: 'PRIVATE-A', source_scope: 'private_case', case_id: 'CASE-A', document_id: 'DOC-A', title: 'Contrato' },
    { source_id: 'PRIVATE-B', source_scope: 'private_case', case_id: 'CASE-B', document_id: 'DOC-B' },
    { source_id: 'LEGAL-A', source_scope: 'public_legal', provenance_version: 'v2', document_id: 'LAW-A', unit_id: 'UNIT-A', title: 'Ley', unit_type: 'artículo', unit_number: '4' },
    { source_id: 'LEGAL-V1', source_scope: 'public_legal', provenance_version: 'v1', document_id: 'LAW-B', unit_id: 'UNIT-B' }
  ]
  const authorized = authorizedGraphSources(sources, 'CASE-A')
  assert.deepEqual([...authorized.keys()], ['PRIVATE-A', 'LEGAL-A'])
  assert.equal(graphLocator(authorized.get('LEGAL-A')), 'artículo 4')
  assert.match(panel, /authorizedGraphSources\(props.sources, props.caseId\)/)
  assert.match(panel, /<SourceModal :source="selectedSource" :case-id="caseId"/)
})

test('semantic relations and local search do not expose technical IDs', () => {
  assert.equal(graphRelation({ relation_type: 'PROVES' }), 'Acredita')
  assert.equal(graphRelation({ relation_type: 'CITES' }), 'Cita')
  assert.equal(graphRelation({ relation_type: 'LEADS_TO' }), 'Conduce a')
  assert.equal(graphRelation({ relation_type: 'REL_004' }), 'Relación jurídica')
  const node = { title: 'Reposición laboral', description: 'Contrato estable', source_ids: ['SRC-UUID'] }
  assert.match(graphSearchText(node, [{ source_id: 'SRC-UUID', title: 'Memorando' }]), /memorando/)
  assert.doesNotMatch(graphSearchText(node, []), /src-uuid/)
  assert.match(panel, /focusNode\(node\)/)
  assert.match(panel, /watch\(\[selectedTypes, complexity, activeGroup\]/)
  assert.doesNotMatch(panel, /Documento: \{\{ selectedNode.document_id \}\}/)
  assert.doesNotMatch(panel, /\{\{ selectedEdge.relation_type \}\}/)
  assert.match(panel, /<details v-if="hasGraphData" class="graph-legend">/)
  assert.match(panel, /No hay nodos para los filtros actuales/)
  assert.match(panel, /Grafo parcial/)
  assert.doesNotMatch(courtView, /\{\{\s*activeCaseId\s*\}\}/)
})

test('graph workspace preserves complete counts and exposes essential and complete views', () => {
  assert.match(panel, /\{\{ allNodes\.length \}\}/)
  assert.match(panel, /\{\{ \(graphData\?\.edges \|\| \[\]\)\.length \}\}/)
  assert.match(panel, /value="essential">Vista esencial/)
  assert.match(panel, /value="complete">Vista completa/)
  assert.match(panel, /watch\(\[selectedTypes, complexity, activeGroup\]/)
  assert.match(panel, /function clearGraphState\(\)/)
  assert.match(panel, /hasClearableGraphState/)
})

test('graph interaction is compact, keyboard accessible, source safe and branded', () => {
  assert.match(panel, /class="graph-type-filter"/)
  assert.match(panel, /closeTypeFilterOutside/)
  assert.match(panel, /handleGraphEscape/)
  assert.match(panel, /class="graph-node-tooltip" role="tooltip"/)
  assert.match(panel, /\.attr\("tabindex", 0\)/)
  assert.match(panel, /\.on\("keydown"/)
  assert.match(panel, /updateHoverStyles\(nodeSelection, linkSelection, node\.id\)/)
  assert.match(panel, /\.graph-workspace:fullscreen/)
  assert.match(panel, /graphWorkspace\.value\?\.requestFullscreen/)
  assert.match(panel, /Lista accesible de elementos/)
  assert.match(panel, /MYKE · NOVACOURT · Inteligencia jurídica/)
  assert.match(panel, /graphKind\(node\)/)
  assert.match(panel, /graphColor\(node\)/)
  assert.match(panel, /stroke-opacity:\.34/)
  assert.match(panel, /opacity:0; font-size:11px/)
  assert.match(panel, /function displayGraphText\(value\)/)
  assert.match(panel, /function displayLabels\(node\)/)
})
