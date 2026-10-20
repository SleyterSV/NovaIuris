import assert from 'node:assert/strict'
import { test } from 'node:test'
import { readFileSync } from 'node:fs'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { editorialCitations, resultCitationNumber, sourceForCitation } from '../src/utils/searchEditorial.js'

const docA = '11111111-1111-4111-8111-111111111111'
const unitA = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
const unitB = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
const sourceA = { source_id: 'SRC-aaaaaaaaaaaaaaaaaaaaaaaa', source_scope: 'public_legal', provenance_version: 'v2', document_id: docA, unit_id: unitA, chunk_id: unitA, title: 'Documento A', court: 'Tribunal A', unit_type: 'foundation', unit_number: '4' }
const sourceB = { ...sourceA, source_id: 'SRC-bbbbbbbbbbbbbbbbbbbbbbbb', unit_id: unitB, chunk_id: unitB, title: 'Documento B' }
const sourceUnused = { ...sourceA, source_id: 'SRC-cccccccccccccccccccccccc', unit_id: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc', chunk_id: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc', title: 'Documento adicional' }
const citations = [
  { citation_id: 'CIT-A', source_id: sourceA.source_id, label: '[1]' },
  { citation_id: 'CIT-B', source_id: sourceB.source_id, label: '[2]' },
  { citation_id: 'CIT-A2', source_id: sourceA.source_id, label: '[3]' }
]

test('citations follow first appearance, reuse source numbers, and exclude uncited or invalid sources', () => {
  const presentation = editorialCitations('Primero [2], luego [1], otra vez [3], huérfana [9].', citations, [sourceA, sourceB, sourceUnused])
  assert.equal(presentation.answer, 'Primero [1], luego [2], otra vez [2], huérfana .')
  assert.deepEqual(presentation.used.map(item => item.source.source_id), [sourceB.source_id, sourceA.source_id])
  assert.deepEqual(presentation.citations.map(item => item.label), ['[1]', '[2]'])
  assert.equal(resultCitationNumber({ document_id: docA, unit_id: unitB }, presentation), 1)
  assert.equal(resultCitationNumber({ document_id: docA, unit_id: sourceUnused.unit_id }, presentation), null)
  assert.equal(sourceForCitation(presentation.citations[0], presentation)?.unit_id, unitB)
  assert.equal(sourceForCitation({ source_id: sourceUnused.source_id }, presentation), null)
  assert.equal(presentation.sources.some(item => item.source_id === sourceUnused.source_id), false)
  assert.equal(sourceA.unit_id, unitA)
})

test('unverified provenance cannot become an inline citation or used source', () => {
  const invalid = { ...sourceA, provenance_version: 'v1' }
  const presentation = editorialCitations('Conclusión [1]', [citations[0]], [invalid])
  assert.equal(presentation.answer, 'Conclusión ')
  assert.equal(presentation.used.length, 0)
})

test('NovaSearch presentation renders editorial sections, five stages and preserves source and Case actions', async () => {
  const server = await createServer({ server: { middlewareMode: true, hmr: false, port: 0 }, appType: 'custom', logLevel: 'error', optimizeDeps: { noDiscovery: true, include: [] } })
  try {
    const load = async name => (await server.ssrLoadModule(`/src/components/novasearch/${name}.vue`)).default
    const [Answer, Progress, Analysis, Results] = await Promise.all(['NovaSearchAnswer', 'NovaSearchProgress', 'NovaSearchAnalysis', 'NovaSearchResults'].map(load))
    const render = (component, props) => renderToString(createSSRApp({ render: () => h(component, props) }))
    const answer = await render(Answer, { answer: 'Criterio [2] y [1].', sources: [sourceA, sourceB, sourceUnused], citations, rama: 'Laboral', totalResults: 3 })
    assert.match(answer, /Rama jurídica/)
    assert.match(answer, /Laboral/)
    assert.match(answer, /Respuesta jurídica/)
    assert.match(answer, /Fuentes utilizadas/)
    assert.match(answer, /Documento B/)
    assert.match(answer, /Documento A/)
    assert.doesNotMatch(answer, /Documento adicional|SRC-|11111111-1111/)
    assert.doesNotMatch(answer, /Tiempo total de búsqueda/)
    assert.match(answer, /síntesis generada/)
    const progress = await render(Progress, { stage: 'reranking', progress: 45 })
    assert.match(progress, /Buscando en el corpus jurídico/)
    assert.equal((progress.match(/class="step-mark"/g) || []).length, 5)
    assert.match(progress, /Cancelar búsqueda/)
    const analysis = await render(Analysis, { analysis: { rama: 'Civil', intent: 'Identificar la regla aplicable.' }, normalizedQuery: 'Texto del usuario' })
    assert.match(analysis, /Interpretación jurídica/)
    assert.doesNotMatch(analysis, /Texto del usuario/)
    const result = { source: sourceUnused, document_id: docA, unit_id: sourceUnused.unit_id, titulo: 'Documento adicional', tipo_documento: 'judgment', organo_emisor: 'Tribunal A', unit_type: 'foundation', unit_number: '7', page_start: 2, resumen_ia: 'Extracto recuperado.' }
    const results = await render(Results, { results: [result], citationPresentation: editorialCitations('Criterio [1].', citations, [sourceA]) })
    assert.match(results, /Fuentes jurídicas relevantes/)
    assert.match(results, /Documento adicional/)
    assert.match(results, /Extracto recuperado/)
    assert.match(results, /Analizar en NovaCase/)
    assert.match(results, /Ver fuente/)
    assert.doesNotMatch(results, /SRC-|aaaaaaaa-aaaa/)
  } finally { await server.close() }
})

test('view keeps filters and fallback controls in a single column without a time KPI', () => {
  const view = readFileSync(new URL('../src/views/NovaSearchView.vue', import.meta.url), 'utf8')
  assert.match(view, /class="filter-toggle"/)
  assert.match(view, /NovaSearchFilters/)
  assert.match(view, /NovaSearchError/)
  assert.match(view, /NovaSearchFallback/)
  assert.match(view, /NovaSearchEmptyState/)
  assert.match(view, /SearchCaseDialog/)
  assert.match(view, /display: block;/)
  assert.doesNotMatch(view, /class="novasearch-sidebar"|:search-time="searchTime"/)
})
