const statuses = new Set(['not_requested', 'building', 'ready', 'empty', 'failed', 'timeout'])

// One boundary for legacy and current Court graph payloads.
export function normalizeGraphState(graph, previous = null) {
  const source = graph && typeof graph === 'object' && !Array.isArray(graph) ? graph : {}
  const prior = previous && typeof previous === 'object' ? previous : null
  const caseId = source.case_id ?? prior?.case_id ?? null
  const graphId = source.graph_id ?? prior?.graph_id ?? null
  const version = Number.isInteger(source.version) && source.version >= 0 ? source.version : 0
  if (prior && prior.case_id === caseId &&
      (prior.graph_id === graphId || !prior.graph_id || !graphId) && version < prior.version) return prior
  const nodes = Array.isArray(source.nodes) ? source.nodes : []
  const edges = Array.isArray(source.edges) ? source.edges : []
  const status = statuses.has(source.status) ? source.status : 'not_requested'
  return {
    ...source,
    status, graph_id: graphId, case_id: caseId, version,
    stage: source.stage ?? null, is_final: source.is_final ?? ['ready', 'empty', 'failed', 'timeout'].includes(status),
    nodes, edges,
    counts: source.counts ?? { node_count: nodes.length, edge_count: edges.length },
    warnings: Array.isArray(source.warnings) ? source.warnings : [],
    error: source.error ?? null,
    message: typeof source.message === 'string' ? source.message : '',
    metadata: source.metadata && typeof source.metadata === 'object' ? source.metadata : {}
  }
}
