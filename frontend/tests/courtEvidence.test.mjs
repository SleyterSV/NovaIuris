import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'

const caseId = 'CASE-COURT-1'
const contractSource = {
  source_id: 'SRC-aaaaaaaaaaaaaaaaaaaaaaaa', source_scope: 'private_case', case_id: caseId,
  document_id: '44444444-4444-4444-8444-444444444444', title: 'Contrato CAS N.º 015-2021',
  display_title: 'Contrato CAS N.º 015-2021', page_start: 1
}
const memoSource = {
  source_id: 'SRC-bbbbbbbbbbbbbbbbbbbbbbbb', source_scope: 'private_case', case_id: caseId,
  document_id: '55555555-5555-4555-8555-555555555555', title: 'Memorando de no renovación',
  display_title: 'Memorando de no renovación', page_start: 2
}
const publicSource = {
  source_id: 'SRC-cccccccccccccccccccccccc', source_scope: 'public_legal', provenance_version: 'v2',
  document_id: '11111111-1111-4111-8111-111111111111', unit_id: '22222222-2222-4222-8222-222222222222',
  chunk_id: '22222222-2222-4222-8222-222222222222', title: 'STC Exp. 02047-2025-PA/TC',
  display_title: 'STC Exp. 02047-2025-PA/TC', court: 'Tribunal Constitucional', unit_type: 'foundation', unit_number: '5', page_start: 4
}

test('NovaCourt evidence presents real evidence in Spanish and preserves canonical source actions', async () => {
  const server = await createServer({
    server: { middlewareMode: true, hmr: false, port: 0 }, appType: 'custom', logLevel: 'error',
    optimizeDeps: { noDiscovery: true, include: [] }
  })
  try {
    const component = (await server.ssrLoadModule('/src/components/novacourt/CourtEvidence.vue')).default
    const props = {
      loading: false,
      simulation: { citations: [{ citation_id: 'CIT-3', source_id: publicSource.source_id, label: '[3]' }] },
      result: {
        case_id: caseId, document_ids: [contractSource.document_id, memoSource.document_id],
        sources: [contractSource, memoSource, publicSource],
        citations: [
          { citation_id: 'CIT-1', source_id: contractSource.source_id, label: '[1]' },
          { citation_id: 'CIT-2', source_id: memoSource.source_id, label: '[2]' }
        ],
        evidence: {
          level: 'low',
          strengths: ['El contrato identifica las funciones pactadas.'],
          weaknesses: ['No acredita por sí solo su permanencia efectiva.'],
          missing_evidence: ['Adendas y planillas que permitan verificar la continuidad del vínculo.'],
          recommended_documents: ['Adendas y planillas que permitan verificar la continuidad del vínculo.'],
          recommendations: ['Solicitar las planillas del periodo controvertido.'],
          digitalEvidence: [{ title: 'Constancia de recepción', description: 'Consta la fecha y hora de notificación.',
            probative_value: 'Indicia la fecha y hora de recepción.', limitations: 'No se cuenta con un cargo independiente.', source_ids: [memoSource.source_id] }],
          evidence_links: [{ title: 'Vínculo inicial', source_ids: [contractSource.source_id],
            what_it_supports: 'Acredita la existencia del vínculo inicial y las funciones pactadas.',
            limitations: 'No acredita las renovaciones sucesivas.' }]
        },
        analysis: { evidence_strength: 'low' },
        facts: [
          { fact_id: 'FACT-aaaaaaaaaaaaaaaaaaaaaaaa', status: 'supported', text: 'El contrato acredita las funciones pactadas.', source_ids: [contractSource.source_id] },
          { fact_id: 'FACT-bbbbbbbbbbbbbbbbbbbbbbbb', status: 'alleged', text: 'Las labores continuaron de forma permanente.', source_ids: [] }
        ]
      }
    }
    const html = await renderToString(createSSRApp({ render: () => h(component, props) }))
    const visible = html.replace(/<[^>]*>/g, ' ')

    for (const text of [
      'Análisis probatorio', 'Evidencia analizada', 'Documentos aportados', 'Contrato CAS N.º 015-2021',
      'Acredita la existencia del vínculo inicial', 'Limitaciones', 'Hechos acreditados documentalmente',
      'Hechos pendientes de corroboración', 'Según lo manifestado; pendiente de corroboración',
      'Evidencia digital', 'Valor probatorio', 'No se cuenta con un cargo independiente',
      'Fuentes jurídicas de apoyo', 'no constituyen prueba de los hechos del caso',
      'Documentación y actuaciones pendientes', 'Próximos pasos probatorios', 'Fortalezas', 'Debilidades'
    ]) assert.ok(visible.includes(text), `Expected visible text: ${text}`)

    assert.match(html, /novacase-citation-badge[^>]*>1</)
    assert.match(html, /novacase-citation-badge[^>]*>2</)
    assert.match(html, /novacase-citation-badge[^>]*>3</)
    assert.match(html, /Ver documento/)
    assert.match(html, /Ver fuente/)
    assert.doesNotMatch(visible, /\[\d+\]|SRC-[a-f0-9]{12,}|FACT-[a-f0-9]{12,}|ISSUE-[a-f0-9]{12,}|source_id|fact_id|issue_id|document_id|unit_id|private_case|public_legal/i)
    assert.doesNotMatch(visible, /Available evidence|Digital evidence|Documents|Evidence links|Evidence strength|Missing evidence|Recommendations|Recommended documents|Recommended evidence|Strengths|Weaknesses|Summary/i)

    const componentSource = await readFile(new URL('../src/components/novacourt/CourtEvidence.vue', import.meta.url), 'utf8')
    assert.match(componentSource, /argumentCitationForSource\(source, citations\.value, sources\.value, result\.value\.case_id\)/)
    assert.match(componentSource, /width:max-content/)
    assert.doesNotMatch(componentSource, /\.novacase-citation-badge\s*\{[^}]*width:\s*100%/s)
    const viewSource = await readFile(new URL('../src/views/NovaCourtView.vue', import.meta.url), 'utf8')
    assert.match(viewSource, /<template #evidence>\s*<CourtEvidence/)
    assert.match(viewSource, /<template #risks>[\s\S]*?<CourtAnalysis/)
  } finally {
    await server.close()
  }
})
