const asRecord = value => (
  value && typeof value === 'object' && !Array.isArray(value) ? value : {}
)

const asList = value => Array.isArray(value) ? value : []

// Defensive client-side counterpart of backend/app/utils/case_contract.py.
export function normalizeCaseResult(result) {
  const source = asRecord(result)
  if (!source.success) return source

  const normalized = {
    ...source,
    analysis: { ...asRecord(source.analysis) },
    summary: { ...asRecord(source.summary || source.analysis_summary) },
    strategy: { ...asRecord(source.strategy) },
    research: asRecord(source.research),
    arguments: asRecord(source.arguments || source.legal_arguments),
    evidence: { ...asRecord(source.evidence || source.evidence_analysis) },
    risks: { ...asRecord(source.risks || source.risk_analysis) },
    counter_arguments: { ...asRecord(source.counter_arguments) },
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
  const mappings = [
    [normalized.analysis, { facts:'hechos', issues:'problemas_juridicos', law:'normas_probables', observations:'informacion_faltante' }],
    [normalized.evidence, { documents:'documentary_evidence', testimonies:'testimonial_evidence', expertReports:'expert_evidence', digitalEvidence:'digital_evidence', summary:'evidence_strength' }],
    [normalized.risks, { procedural:'procedural_risks', evidentiary:'evidentiary_risks', legal:'legal_risks', strategic:'critical_risks', summary:'risk_level' }],
    [normalized.counter_arguments, { procedural:'procedural_exceptions', evidence:'attacks_on_evidence', legal:'legal_defenses', jurisprudence:'attacks_on_jurisprudence', summary:'main_counterarguments' }],
    [normalized.strategy, { strategy:'claim_strategy', actions:'recommended_actions', execution:'procedural_risks', recommendations:'recommended_actions', summary:'claim_strategy' }]
  ]
  for (const [target, aliases] of mappings) {
    for (const [alias, original] of Object.entries(aliases)) target[alias] ??= target[original] ?? []
  }
  normalized.analysis.summary ??= normalized.summary
  normalized.analysis.jurisprudence ??= asList(normalized.research.documents).filter(d => /jurisprud/i.test(d.tipo_documento || ''))
  normalized.strategy.objective ??= normalized.analysis.pretension_principal || ''
  normalized.summary.proceso ??= normalized.analysis.tipo_proceso || ''
  normalized.summary.riesgo ??= normalized.risks.risk_level || ''
  normalized.summary.evidencia ??= normalized.evidence.evidence_strength || ''
  normalized.summary.documentos ??= asList(normalized.research.documents).length
  return normalized
}
