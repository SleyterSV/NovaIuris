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
assert.equal(normalized.report_status, 'not_requested')
assert.deepEqual(normalized.facts, [])
assert.deepEqual(normalized.sources_used, [])
const professional = normalizeCaseResult({success:true,case_id:'CASE-A',status:'partial',
  report_status:'failed',report_error:{code:'REPORT_FAILED'},facts:[{fact_id:'FACT-A'}],
  issues:[{issue_id:'ISSUE-A'}],final_strategy:{objective:'OBJ-A'},
  report_document:{document_type:'analysis_report'},sources_used:[{source_id:'SRC-A'}]})
assert.equal(professional.case_id,'CASE-A')
assert.equal(professional.status,'partial')
assert.equal(professional.report_document.document_type,'analysis_report')
assert.equal(professional.facts[0].fact_id,'FACT-A')
assert.equal(professional.final_strategy.objective,'OBJ-A')
assert.equal(professional.sources_used[0].source_id,'SRC-A')
assert.equal(normalized.graph ?? null, null)
console.log('case contract OK')
