import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'

const caseId = 'CASE-POSITIONS-1'
const privateSource = {
  source_id: 'SRC-private-document-page-one', source_scope: 'private_case', case_id: caseId,
  document_id: '44444444-4444-4444-8444-444444444444', title: 'Contrato CAS N.º 015-2021-MDSE/ORH',
  display_title: 'Contrato CAS N.º 015-2021-MDSE/ORH', page_start: 1
}
const publicSource = {
  source_id: 'SRC-aaaaaaaaaaaaaaaaaaaaaaaa', source_scope: 'public_legal', provenance_version: 'v2',
  document_id: '11111111-1111-4111-8111-111111111111', unit_id: '22222222-2222-4222-8222-222222222222',
  chunk_id: '22222222-2222-4222-8222-222222222222', title: 'STC Exp. 02047-2025-PA/TC',
  display_title: 'STC Exp. 02047-2025-PA/TC', court: 'Tribunal Constitucional', unit_type: 'foundation', unit_number: '11', page_start: 5, page_end: 6
}

test('NovaCourt positions structure both parties and preserve canonical citations and source types', async () => {
  const server = await createServer({
    server: { middlewareMode: true, hmr: false, port: 0 }, appType: 'custom', logLevel: 'error',
    optimizeDeps: { noDiscovery: true, include: [] }
  })
  try {
    const component = (await server.ssrLoadModule('/src/components/novacourt/CourtPositions.vue')).default
    const simulation = {
      status: 'ready', sources: [privateSource, publicSource],
      citations: [
        { citation_id: 'CIT-1', source_id: privateSource.source_id, label: '[1]' },
        { citation_id: 'CIT-4', source_id: 'public-alias', source_scope: 'public_legal', provenance_version: 'v2', document_id: publicSource.document_id, unit_id: publicSource.unit_id, label: '[4]' }
      ],
      prosecutor: { content: `## Tesis principal\nLa no renovación habría sido arbitraria y carecería de motivación suficiente.\n\n## Hechos que sustentan esta posición\n- Celebración del contrato CAS [1].\n- Comunicación de no renovación.\n\n## Evidencia disponible\n- Contrato CAS N.º 015-2021-MDSE/ORH: acredita el vínculo inicial; no acredita las renovaciones sucesivas. [1]\n\n## Fundamentos jurídicos\n### Motivación suficiente\nEl acto debe expresar razones verificables. [4]\n\n## Evidencia que fortalecería esta posición\n- Adendas y resoluciones de renovación.\n\n## Vulnerabilidades de la posición\n- No se acreditan las renovaciones sucesivas.\n\n## Conclusión de la posición\nLa posición requiere respaldo sobre continuidad y motivación.`,
        citations: [{ citation_id: 'CIT-1', source_id: privateSource.source_id, label: '[1]' }, { citation_id: 'CIT-4', source_id: 'public-alias', source_scope: 'public_legal', provenance_version: 'v2', document_id: publicSource.document_id, unit_id: publicSource.unit_id, label: '[4]' }] },
      defense: { content: `## Tesis principal\nLa no renovación se habría producido al vencimiento del plazo contractual.\n\n## Fundamentos jurídicos\n### Naturaleza del vínculo CAS\nLa defensa sostiene que el plazo pactado había concluido. [4]\n\n## Conclusión\nLa defensa invoca el vencimiento del contrato.`,
        citations: [{ citation_id: 'CIT-4', source_id: 'public-alias', source_scope: 'public_legal', provenance_version: 'v2', document_id: publicSource.document_id, unit_id: publicSource.unit_id, label: '[4]' }] },
      controversies: ['¿El vencimiento contractual basta para justificar la no renovación?']
    }
    const html = await renderToString(createSSRApp({ render: () => h(component, { simulation, caseId }) }))
    const visible = html.replace(/<[^>]*>/g, ' ')

    for (const text of [
      'Posiciones de las partes', 'Simulación completada', 'PARTE DEMANDANTE', 'PARTE DEMANDADA',
      'Tesis de la parte demandante', 'Tesis de la parte demandada', 'Hechos que sustentan esta posición',
      'Evidencia disponible', 'Fundamentos jurídicos', 'Evidencia que fortalecería esta posición',
      'Vulnerabilidades de la posición', 'Conclusión de la posición', 'Contraste de posiciones',
      'Puntos centrales de controversia', 'Fuentes utilizadas', 'Documentos del caso', 'Fuentes jurídicas',
      'Ver documento', 'Ver fuente', 'Tribunal Constitucional · Fundamento 11 · pág. 5–6'
    ]) assert.ok(visible.includes(text), `Expected visible text: ${text}`)

    assert.match(html, /citation-inline[^>]*data-numeric[^>]*data-citation-id="CIT-1"[^>]*>1</)
    assert.match(html, /citation-inline[^>]*data-numeric[^>]*data-citation-id="CIT-4"[^>]*>4</)
    assert.match(html, /novacase-citation-badge[^>]*>1</)
    assert.match(html, /novacase-citation-badge[^>]*>4</)
    assert.doesNotMatch(visible, /\[\d+\]|\(Fuente:\s*\[|##|\*\*|SRC-|FACT-|ISSUE-|source_id|unit_id|document_id|private_case|public_legal|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i)
    const componentSource = await readFile(new URL('../src/components/novacourt/CourtPositions.vue', import.meta.url), 'utf8')
    assert.match(componentSource, /\.novacase-citation-badge\{[^}]*width:max-content/s)
    assert.doesNotMatch(componentSource, /\.novacase-citation-badge\{[^}]*width:100%/s)

    const simulationView = await readFile(new URL('../src/components/novacourt/CourtSimulation.vue', import.meta.url), 'utf8')
    assert.match(simulationView, /<CourtPositions v-if="mode !== 'decision'"/)
    assert.match(simulationView, /<section v-else class="court-simulation">/)
  } finally {
    await server.close()
  }
})
