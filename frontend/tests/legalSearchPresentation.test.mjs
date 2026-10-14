import assert from 'node:assert/strict'
import test from 'node:test'
import { legalTypeLabel, legalUnitLabel, sameExcerpt, cardExcerpt, sourceDetailPresentation } from '../src/utils/legalSearchPresentation.js'
import { loadLegalUnitSource } from '../src/services/legalUnitSource.js'

test('V2 legal labels are Spanish presentation only', () => {
  assert.equal(legalTypeLabel('regulation'), 'Normativa')
  assert.equal(legalTypeLabel('regulation', { resolution_type: 'Decreto Supremo' }), 'Decreto Supremo')
  assert.equal(legalTypeLabel('judgment'), 'Sentencia')
  assert.equal(legalTypeLabel('order'), 'Auto')
  assert.equal(legalTypeLabel('cassation'), 'Casación')
  assert.equal(legalTypeLabel('jurisprudence'), 'Jurisprudencia')
  assert.equal(legalTypeLabel('foundation'), 'Fundamento')
  assert.equal(legalTypeLabel('decision'), 'Decisión')
  assert.equal(legalTypeLabel('disposition'), 'Disposición')
  assert.equal(legalTypeLabel('antecedent'), 'Antecedente')
  assert.equal(legalUnitLabel('disposition', 'ÚNICA'), 'Disposición ÚNICA')
  assert.equal(legalUnitLabel('foundation', 'Cuarto'), 'Fundamento Cuarto')
  assert.equal(legalTypeLabel('custom'), 'custom')
})

test('expanded excerpt is hidden only when it duplicates the preview', () => {
  assert.equal(sameExcerpt('Texto  jurídico\n exacto', 'texto jurídico exacto'), true)
  assert.equal(sameExcerpt('Texto abreviado…', 'Texto abreviado con más contenido.'), false)
})

test('V2 card shows one word-safe preview while full unit stays in source detail', () => {
  assert.deepEqual(cardExcerpt({ unit_id: 'u1', resumen_ia: 'Texto abreviado…',
    extracto_exacto: 'Texto abreviado con contenido adicional truncado en el RPC' }),
    { primary: 'Texto abreviado…', secondary: '' })
  assert.deepEqual(cardExcerpt({ resumen_ia: 'Síntesis', extracto_exacto: 'Extracto original' }),
    { primary: 'Síntesis', secondary: 'Extracto original' })
})

test('one canonical V2 unit is fetched on demand by its UUID', async () => {
  const unitId = '12345678-1234-1234-1234-123456789abc'
  const documentId = '87654321-4321-4321-4321-cba987654321'
  const fullText = 'Texto completo de la unidad jurídica. '.repeat(20)
  const calls = []
  const fetched = await loadLegalUnitSource(unitId, documentId, { fetchImpl: async (url, options) => {
    calls.push({ url, options })
    return { ok: true, json: async () => ({ success: true, unit: { unit_id: unitId, document_id: documentId, text: fullText } }) }
  } })
  assert.equal(fetched.text, fullText)
  assert.equal(calls.length, 1)
  assert.match(calls[0].url, /\/search\/sources\/12345678-1234-1234-1234-123456789abc\?document_id=87654321-4321-4321-4321-cba987654321$/)
  assert.equal(calls[0].options.method, 'GET')
  await assert.rejects(loadLegalUnitSource('not-a-uuid', documentId, { fetchImpl: () => {
    throw new Error('should not request')
  } }))
})

test('source detail shows loading, full canonical text and explicit fallback', () => {
  const source = { excerpt: 'Fragmento de 240 caracteres' }
  const full = 'Texto completo de la unidad jurídica, sin corte.'
  assert.deepEqual(sourceDetailPresentation(source, null, 'loading'),
    { loading: true, text: '', heading: '', warning: false })
  assert.deepEqual(sourceDetailPresentation(source, { text: full }, 'ready'),
    { loading: false, text: full, heading: 'Unidad jurídica completa', warning: false })
  assert.deepEqual(sourceDetailPresentation(source, null, 'error'),
    { loading: false, text: source.excerpt, heading: 'Fragmento utilizado', warning: true })
})

test('a short unit card and source modal retain separate preview and canonical text', () => {
  const preview = 'Se advierte que dicho requerimiento fue atendido…'
  const canonical = 'Se advierte que dicho requerimiento fue atendido. '.repeat(12)
  const result = { unit_id: 'unit-7', resumen_ia: preview, extracto_exacto: preview }
  assert.deepEqual(cardExcerpt(result), { primary: preview, secondary: '' })
  assert.deepEqual(sourceDetailPresentation({ excerpt: preview }, { text: canonical }, 'ready'),
    { loading: false, text: canonical, heading: 'Unidad jurídica completa', warning: false })
})
