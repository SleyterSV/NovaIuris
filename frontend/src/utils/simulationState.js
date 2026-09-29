const statuses = new Set(['not_requested', 'running', 'ready', 'failed', 'timeout'])

const asRecord = value => (
  value && typeof value === 'object' && !Array.isArray(value) ? value : {}
)

// NovaCourt renders only the stable result.simulation contract.
export function normalizeSimulationState(simulation) {
  const source = asRecord(simulation)
  const status = statuses.has(source.status) ? source.status : 'not_requested'

  return {
    ...source,
    status,
    prosecutor: asRecord(source.prosecutor),
    defense: asRecord(source.defense),
    judge: asRecord(source.judge),
    judicial_analysis: asRecord(source.judicial_analysis),
    decision: asRecord(source.decision),
    projection: asRecord(source.projection),
    sources: Array.isArray(source.sources) ? source.sources : [],
    citations: Array.isArray(source.citations) ? source.citations : [],
    metadata: asRecord(source.metadata),
    message: typeof source.message === 'string' ? source.message : ''
  }
}
