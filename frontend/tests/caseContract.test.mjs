import assert from 'node:assert/strict'
import { normalizeCaseResult } from '../src/utils/caseContract.js'

const normalized = normalizeCaseResult({
  success: true,
  analysis_summary: { tipo_proceso: 'despido' },
  strategy: { claim_strategy: 'Reposición' },
  risk_analysis: { risks: ['plazo'] },
  legal_arguments: { principal: 'tutela' },
  evidence_analysis: { summary: 'contrato' }
})

assert.equal(normalized.summary.tipo_proceso, 'despido')
assert.equal(normalized.strategy.claim_strategy, 'Reposición')
assert.deepEqual(normalized.risks.risks, ['plazo'])
assert.deepEqual(normalized.arguments, { principal: 'tutela' })
assert.equal(normalized.evidence.summary, 'contrato')
assert.equal(normalized.metadata.contract_version, '1.0')
assert.equal(normalized.graph ?? null, null)
console.log('case contract OK')
