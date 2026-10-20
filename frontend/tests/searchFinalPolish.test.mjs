import assert from 'node:assert/strict'
import { test } from 'node:test'
import { readFileSync } from 'node:fs'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { editorialCitations, sourceForCitation } from '../src/utils/searchEditorial.js'

const source = { source_id: 'SRC-aaaaaaaaaaaaaaaaaaaaaaaa', source_scope: 'public_legal', provenance_version: 'v2',
  document_id: '11111111-1111-4111-8111-111111111111', unit_id: '22222222-2222-4222-8222-222222222222',
  chunk_id: '22222222-2222-4222-8222-222222222222', title: 'Resolución de prueba' }
const citation = { citation_id: 'CIT-A', source_id: source.source_id, label: '[4]' }

test('Search-only filters are scoped by active workspace tool and wider thread stays local', () => {
  const shell = readFileSync(new URL('../src/views/MikeView.vue', import.meta.url), 'utf8')
  const view = readFileSync(new URL('../src/views/NovaSearchView.vue', import.meta.url), 'utf8')
  assert.match(shell, /searchActive: activeTool === 'search'/)
  assert.match(shell, /turn\.tool === 'search'/)
  assert.match(shell, /thread\.search-thread/)
  assert.match(view, /v-if="searchActive" class="filter-toolbar"/)
  assert.match(view, /v-if="searchActive && filtersOpen"/)
  assert.match(view, /NovaSearchFilters/)
  assert.match(view, /:class="\{ active: filters\.modulo !== 'Todos' \|\| filters\.vigencia_explicit \}"/)
  assert.doesNotMatch(view, /Tiempo total de búsqueda/)
})

test('inline citation retains source identity and repeated references keep one used source', () => {
  const presentation = editorialCitations('Afirmación [4]. Reiteración [4].', [citation], [source])
  assert.equal(presentation.answer, 'Afirmación [1]. Reiteración [1].')
  assert.equal(presentation.used.length, 1)
  assert.equal(sourceForCitation(presentation.citations[0], presentation)?.unit_id, source.unit_id)
})

test('real analysis fields and editorial source controls render without fabricated conclusions or technical IDs', async () => {
  const server = await createServer({ server: { middlewareMode: true, hmr: false, port: 0 }, appType: 'custom', logLevel: 'error', optimizeDeps: { noDiscovery: true, include: [] } })
  try {
    const load = async name => (await server.ssrLoadModule(`/src/components/novasearch/${name}.vue`)).default
    const [Analysis, Answer, Results] = await Promise.all(['NovaSearchAnalysis', 'NovaSearchAnswer', 'NovaSearchResults'].map(load))
    const render = (component, props) => renderToString(createSSRApp({ render: () => h(component, props) }))
    const real = await render(Analysis, { analysis: { rama: 'Laboral', intencion: 'buscar_jurisprudencia', organo: 'Tribunal', keywords: ['contrato', 'reposición'] } })
    assert.match(real, /Laboral|Jurisprudencia|Tribunal|contrato|reposición/)
    assert.doesNotMatch(real, /consulta_general|normalized_query|SRC-/)
    const thin = await render(Analysis, { analysis: { rama: 'Laboral' } })
    assert.doesNotMatch(thin, /Interpretación jurídica/)
    const answer = await render(Answer, { answer: 'Regla [4].', sources: [source], citations: [citation], totalResults: 1 })
    assert.match(answer, /role="note"/)
    assert.match(answer, /Fuentes utilizadas/)
    assert.doesNotMatch(answer, /SRC-|11111111-1111/)
    const results = await render(Results, { results: [{ source, source_id: source.source_id, document_id: source.document_id,
      unit_id: source.unit_id, titulo: source.title, resumen_ia: 'Extracto real del resultado.' }] })
    assert.match(results, /Ver fuente/)
    assert.match(results, /Analizar en NovaCase/)
    assert.doesNotMatch(results, /Próximamente|SRC-|22222222-2222/)
  } finally { await server.close() }
})
