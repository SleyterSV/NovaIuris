const asRecord = value => (
  value && typeof value === 'object' && !Array.isArray(value) ? value : {}
)

const asList = value => Array.isArray(value) ? value : []

// Defensive client-side counterpart of backend/app/utils/case_contract.py.
export function normalizeCaseResult(result) {
  const source = asRecord(result)
  if (!source.success) return source

  return {
    ...source,
    analysis: asRecord(source.analysis),
    summary: asRecord(source.summary || source.analysis_summary),
    strategy: asRecord(source.strategy),
    research: asRecord(source.research),
    arguments: asRecord(source.arguments || source.legal_arguments),
    evidence: asRecord(source.evidence || source.evidence_analysis),
    risks: asRecord(source.risks || source.risk_analysis),
    counter_arguments: asRecord(source.counter_arguments),
    timeline: asList(source.timeline),
    report: source.report ?? '',
    citations: asList(source.citations),
    metadata: {
      ...asRecord(source.metadata),
      contract_version: source.metadata?.contract_version || '1.0',
      analysis_statistics: asRecord(source.metadata?.analysis_statistics || source.analysis_statistics),
      strategy_summary: asRecord(source.metadata?.strategy_summary || source.strategy_summary),
      strategy_statistics: asRecord(source.metadata?.strategy_statistics || source.strategy_statistics)
    }
  }
}
