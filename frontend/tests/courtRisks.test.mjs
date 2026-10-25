import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'

test('NovaCourt risk assessment summarizes and de-duplicates only supplied risk data', async () => {
  const server = await createServer({
    server: { middlewareMode: true, hmr: false, port: 0 }, appType: 'custom', logLevel: 'error',
    optimizeDeps: { noDiscovery: true, include: [] }
  })
  try {
    const component = (await server.ssrLoadModule('/src/components/novacourt/CourtRisks.vue')).default
    const repeated = { title: 'Agotamiento de la vía administrativa', text: 'No consta el estado del recurso de reconsideración.', impact: 'Posible objeción de procedencia.', mitigation: 'Obtener el cargo, la resolución o la constancia de silencio.' }
    const props = { risk: {
      risk_level: 'MEDIUM — La documentación es insuficiente para verificar continuidad y trámite administrativo.',
      summary_text: 'La viabilidad depende de acreditar el trámite administrativo y completar el respaldo documental.',
      critical_risks: [repeated], strategic: [repeated],
      procedural: [repeated], procedural_risks: [repeated, { title: 'Caducidad', text: 'Debe verificarse el cómputo del plazo.' }],
      evidentiary: [{ title: 'Continuidad contractual', text: 'No se incorporaron las adendas de renovación.' }],
      evidentiary_risks: [{ title: 'Continuidad contractual', text: 'No se incorporaron las adendas de renovación.' }, { title: 'Reemplazo', text: 'No se acreditó una contratación posterior.' }],
      legal: [{ title: 'Régimen CAS', text: 'Puede discutirse la naturaleza temporal del vínculo.' }],
      legal_risks: [{ title: 'Régimen CAS', text: 'Puede discutirse la naturaleza temporal del vínculo.' }],
      judge_observations: ['Fecha y medio de notificación', 'Motivación del acto'],
      strengths: ['Existe documentación del vínculo inicial.'],
      weaknesses: ['No hay respaldo suficiente de las renovaciones.'],
      missing_documents: ['Adendas de renovación', 'Planillas del periodo'],
      missing_evidence: ['Planillas del periodo', 'MOF y ROF'],
      missing_information: ['MOF y ROF'],
      recommendations: ['Obtener las adendas de renovación.', 'Verificar el plazo para demandar.'],
      internal_note: 'SRC-aaaaaaaaaaaaaaaaaaaaaaaa FACT-bbbbbbbbbbbbbbbbbbbbbbbb ISSUE-cccccccccccccccccccccccc 11111111-1111-4111-8111-111111111111'
    } }
    const html = await renderToString(createSSRApp({ render: () => h(component, props) }))
    const visible = html.replace(/<[^>]*>/g, ' ')

    for (const text of [
      'Evaluación de riesgos', 'PANORAMA DE RIESGO', 'Nivel general', 'Medio',
      'factores identificados', 'Riesgos prioritarios', 'Agotamiento de la vía administrativa',
      'Posible objeción de procedencia.', 'Obtener el cargo, la resolución o la constancia de silencio.',
      'Riesgos procesales', 'Riesgos probatorios', 'Riesgos jurídicos', 'Caducidad',
      'Continuidad contractual', 'Régimen CAS', 'Puntos de control judicial',
      'Fecha y medio de notificación', 'Fortalezas del caso', 'Debilidades del caso',
      'Documentación crítica pendiente', 'Plan de mitigación'
    ]) assert.ok(visible.includes(text), `Expected visible text: ${text}`)

    assert.equal((visible.match(/Agotamiento de la vía administrativa/g) || []).length, 1)
    assert.equal((visible.match(/No se incorporaron las adendas de renovación/g) || []).length, 1)
    assert.equal((visible.match(/Puede discutirse la naturaleza temporal del vínculo/g) || []).length, 1)
    assert.equal((visible.match(/Planillas del periodo/g) || []).length, 1)
    assert.match(html, /class="overall-level"[^>]*>Medio</)
    assert.doesNotMatch(visible, /MEDIUM|Critical risks|Evidentiary risks|Judge observations|Missing documents|Missing evidence|Missing information|Procedural risks|Recommendations|Risk level|Strategic|Strengths|Summary|Weaknesses/i)
    assert.doesNotMatch(visible, /SRC-|FACT-|ISSUE-|source_id|issue_id|fact_id|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i)

    const view = await readFile(new URL('../src/views/NovaCourtView.vue', import.meta.url), 'utf8')
    assert.match(view, /<template #risks>\s*<CourtRisks/)
    assert.match(view, /<template #evidence>\s*<CourtEvidence/)
    assert.match(view, /<template #arguments>\s*<CourtArguments/)
  } finally {
    await server.close()
  }
})
