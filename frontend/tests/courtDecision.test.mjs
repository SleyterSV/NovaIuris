import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { normalizeSimulationState } from '../src/utils/simulationState.js'

const caseId = 'CASE-DECISION-1'
const privateSource = { source_id: 'SRC-private-doc-page-one', source_scope: 'private_case', case_id: caseId,
  document_id: '44444444-4444-4444-8444-444444444444', title: 'Contrato CAS N.º 015-2021-MDSE/ORH',
  display_title: 'Contrato CAS N.º 015-2021-MDSE/ORH', page_start: 1 }
const legalSource = { source_id: 'SRC-aaaaaaaaaaaaaaaaaaaaaaaa', source_scope: 'public_legal', provenance_version: 'v2',
  document_id: '11111111-1111-4111-8111-111111111111', unit_id: '22222222-2222-4222-8222-222222222222',
  chunk_id: '22222222-2222-4222-8222-222222222222', title: 'STC Exp. 02047-2025-PA/TC',
  display_title: 'STC Exp. 02047-2025-PA/TC', court: 'Tribunal Constitucional', unit_type: 'foundation', unit_number: '11', page_start: 5, page_end: 6 }

test('NovaCourt simulated decision presents existing reasoning, canonical sources and qualified conclusions', async () => {
  const server = await createServer({ server: { middlewareMode: true, hmr: false, port: 0 }, appType: 'custom', logLevel: 'error', optimizeDeps: { noDiscovery: true, include: [] } })
  try {
    const component = (await server.ssrLoadModule('/src/components/novacourt/CourtSimulation.vue')).default
    const decisionSource = await readFile(new URL('../src/components/novacourt/CourtDecision.vue', import.meta.url), 'utf8')
    const simulation = normalizeSimulationState({
      status: 'ready', sources: [privateSource, legalSource],
      citations: [
        { citation_id: 'DEC-CIT-1', source_id: privateSource.source_id, label: '[1]' },
        { citation_id: 'DEC-CIT-4', source_id: 'legal-alias', source_scope: 'public_legal', provenance_version: 'v2', document_id: legalSource.document_id, unit_id: legalSource.unit_id, label: '[4]' }
      ],
      prosecutor: { content: '## Tesis principal\nLa demandante sostiene que la no renovación fue arbitraria por falta de motivación suficiente. Señala indicios de funciones permanentes y renovaciones sucesivas. Cuestiona que exista una razón funcional o presupuestal suficiente para la decisión.' },
      defense: { content: '## Tesis principal\nLa demandada sostiene que el vínculo concluyó por vencimiento del plazo contractual. Añade que no se ha acreditado la permanencia de las funciones. Considera que la documentación disponible no demuestra condiciones para sostener la continuidad del CAS.' },
      judge: { citations: [
        { citation_id: 'DEC-CIT-1', source_id: privateSource.source_id, label: '[1]' },
        { citation_id: 'DEC-CIT-4', source_id: 'legal-alias', source_scope: 'public_legal', provenance_version: 'v2', document_id: legalSource.document_id, unit_id: legalSource.unit_id, label: '[4]' }
      ] },
      judicial_analysis: { content: `## I. Identificación de la Controversia\nSi el vencimiento del plazo CAS justifica por sí mismo la no renovación.\n\n## II. Hechos relevantes\n1. Se celebró el contrato CAS [1].\n2. Se comunicó la no renovación.\n\n## III. Valoración de la Prueba y Fuentes\nEl contrato acredita el vínculo inicial, pero no las renovaciones sucesivas. [1]\n\n## IV. Fundamentos Jurídicos\n### Motivación suficiente\nEl acto debe exponer razones verificables. [4]\n\n### Naturaleza del régimen CAS\nEl régimen tiene carácter temporal conforme al fundamento citado. [4]\n\n## V. Razonamiento de la decisión\nLa documentación acredita la contratación inicial. La continuidad de las funciones permanece pendiente de corroboración.\n\n## VI. Límites\nLa falta de adendas limita la verificación de renovaciones posteriores.\n\n## VII. Condición relevante\nLa pretensión depende de acreditar la continuidad del servicio.\n\n## VIII. Conclusión\nLa no renovación presenta indicios de motivación insuficiente, sujeto a la acreditación de la continuidad contractual. [4]` }
    })
    const html = await renderToString(createSSRApp({ render: () => h(component, { simulation, caseId, mode: 'decision' }) }))
    const visible = html.replace(/<[^>]*>/g, ' ')

    for (const text of [
      'Decisión simulada', 'Simulación completada', 'No constituye una resolución judicial real ni sustituye la evaluación profesional',
      'RESULTADO DE LA SIMULACIÓN', 'La no renovación presenta indicios de motivación insuficiente',
      'CONTROVERSIA JURÍDICA', 'Cuestión central sometida a evaluación', 'Posiciones consideradas',
      'PARTE DEMANDANTE', 'PARTE DEMANDADA', 'Hechos relevantes para la decisión',
      'Valoración probatoria', 'Fundamentos jurídicos', 'Razonamiento de la decisión',
      'Condicionantes de la decisión', 'Fuentes utilizadas',
      'Documentos del caso', 'Fuentes jurídicas consideradas', 'Contrato CAS N.º 015-2021-MDSE/ORH',
      'STC Exp. 02047-2025-PA/TC', 'Ver documento', 'Ver fuente'
    ]) assert.ok(visible.toLocaleLowerCase('es').includes(text.toLocaleLowerCase('es')), `Expected visible decision text: ${text}`)

    assert.match(visible, /La demandante sostiene que la no renovación fue arbitraria por falta de motivación suficiente\. Señala indicios de funciones permanentes y renovaciones sucesivas\./)
    assert.match(visible, /La demandada sostiene que el vínculo concluyó por vencimiento del plazo contractual\. Añade que no se ha acreditado la permanencia de las funciones\./)
    assert.doesNotMatch(visible, /PARTE DEMANDANTE[^.]*\.\.\.|PARTE DEMANDADA[^.]*\.\.\./)
    assert.match(visible, /La no renovación presenta indicios de motivación insuficiente, sujeto a la acreditación de la continuidad contractual\./)
    assert.doesNotMatch(decisionSource, /line-clamp|text-overflow:\s*ellipsis/i)

    assert.match(html, /citation-inline[^>]*data-numeric[^>]*data-citation-id="DEC-CIT-1"[^>]*>1</)
    assert.match(html, /citation-inline[^>]*data-numeric[^>]*data-citation-id="DEC-CIT-4"[^>]*>4</)
    assert.match(html, /novacase-citation-badge[^>]*>1</)
    assert.match(html, /novacase-citation-badge[^>]*>4</)
    assert.doesNotMatch(visible, /\[\d+\]|\(Fuente:\s*\[|##|\*\*|SRC-|FACT-|ISSUE-|source_id|unit_id|document_id|private_case|public_legal|GANADOR|PERDEDOR|CASO GANADO|PROBABILIDAD DE ÉXITO|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i)
    const courtSimulation = await (await server.ssrLoadModule('/src/components/novacourt/CourtSimulation.vue')).default
    const position = await renderToString(createSSRApp({ render: () => h(courtSimulation, { simulation, caseId, mode: 'positions' }) }))
    assert.match(position, /Posiciones de las partes/)
    assert.doesNotMatch(position, /Razonamiento de la decisión/)
  } finally { await server.close() }
})
