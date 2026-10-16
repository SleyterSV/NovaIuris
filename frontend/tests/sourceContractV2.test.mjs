import assert from 'node:assert/strict'
import { normalizeSource, resolveCitations } from '../src/utils/sourceContract.js'

const publicUnit = {
  source_id: 'SRC-aaaaaaaaaaaaaaaaaaaaaaaa', source_scope: 'public_legal', provenance_version: 'v2',
  document_id: '11111111-1111-4111-8111-111111111111', unit_id: '22222222-2222-4222-8222-222222222222',
  chunk_id: '22222222-2222-4222-8222-222222222222',
  title: 'STC Exp. 00001-2024-PA/TC', excerpt: 'Texto canónico íntegro.',
  official_url: 'https://tc.gob.pe/source.pdf', metadata: { unit_type: 'foundation' }
}
assert.equal(normalizeSource(publicUnit)?.unit_id, publicUnit.unit_id)
assert.equal(normalizeSource(publicUnit)?.official_url, 'https://tc.gob.pe/source.pdf')
const privateOtherCase = { source_id: 'SRC-private', source_scope: 'case', case_id: 'CASE-B',
  document_id: 'private-b', chunk_id: 'chunk-b', excerpt: 'Privado' }
assert.equal(normalizeSource(privateOtherCase, 'CASE-A'), null)
assert.equal(normalizeSource({ ...privateOtherCase, source_scope: 'private_case' }, 'CASE-A'), null)
assert.equal(normalizeSource({ ...privateOtherCase, source_scope: 'private_case' }, 'CASE-B')?.official_url, null)
assert.deepEqual(resolveCitations([{ citation_id: 'CIT-1', source_id: publicUnit.source_id }],
  [publicUnit, privateOtherCase], 'CASE-A').sources.map(source => source.source_id), [publicUnit.source_id])
