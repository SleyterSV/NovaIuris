const statuses = new Set(['not_requested', 'building', 'ready', 'failed', 'timeout'])

// The UI always consumes the NovaCourt graph contract and never invents graph data.
export function normalizeGraphState(graph) {
  const source = graph && typeof graph === 'object' && !Array.isArray(graph)
    ? graph
    : {}
  const status = statuses.has(source.status) ? source.status : 'not_requested'

  return {
    ...source,
    status,
    graph_id: source.graph_id ?? null,
    nodes: Array.isArray(source.nodes) ? source.nodes : [],
    edges: Array.isArray(source.edges) ? source.edges : [],
    message: typeof source.message === 'string' ? source.message : ''
  }
}
