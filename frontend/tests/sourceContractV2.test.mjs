import assert from 'node:assert/strict'
import { normalizeSource, resolveCitations } from '../src/utils/sourceContract.js'

const publicUnit = {
  source_id: 'SRC-legal-v2', source_scope: 'public_legal', provenance_version: 'v2',
  document_id: 'document-a', unit_id: 'unit-a', chunk_id: 'unit-a',
  title: 'STC Exp. 00001-2024-PA/TC', excerpt: 'Texto canónico íntegro.',
  official_url: 'https://tc.gob.pe/source.pdf', metadata: { unit_type: 'foundation' }
}
assert.equal(normalizeSource(publicUnit)?.unit_id, 'unit-a')
assert.equal(normalizeSource(publicUnit)?.official_url, 'https://tc.gob.pe/source.pdf')
const privateOtherCase = { source_id: 'SRC-private', source_scope: 'case', case_id: 'CASE-B',
  document_id: 'private-b', chunk_id: 'chunk-b', excerpt: 'Privado' }
assert.equal(normalizeSource(privateOtherCase, 'CASE-A'), null)
assert.equal(normalizeSource({ ...privateOtherCase, source_scope: 'private_case' }, 'CASE-A'), null)
assert.equal(normalizeSource({ ...privateOtherCase, source_scope: 'private_case' }, 'CASE-B')?.official_url, null)
assert.deepEqual(resolveCitations([{ citation_id: 'CIT-1', source_id: publicUnit.source_id }],
  [publicUnit, privateOtherCase], 'CASE-A').sources.map(source => source.source_id), [publicUnit.source_id])
