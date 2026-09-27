const record = value => value && typeof value === 'object' && !Array.isArray(value) ? value : {}
const list = value => Array.isArray(value) ? value : []

export function normalizeSource(value, expectedCaseId = null) {
  const source = record(value)
  if (!source.source_id || !['public', 'case'].includes(source.source_scope)) return null
  if (source.source_scope === 'case' && (!source.case_id || !expectedCaseId || source.case_id !== expectedCaseId)) return null
  let officialUrl = null
  try {
    const parsed = new URL(source.official_url)
    if (['http:', 'https:'].includes(parsed.protocol)) officialUrl = parsed.href
  } catch { /* no verified URL */ }
  return {
    ...source,
    title: source.title || source.display_title || 'Fuente jurídica',
    display_title: source.display_title || source.title || 'Fuente jurídica',
    official_url: source.source_scope === 'case' ? null : officialUrl,
    metadata: record(source.metadata),
    excerpt: typeof source.excerpt === 'string' ? source.excerpt : ''
  }
}

export function normalizeSources(values, expectedCaseId = null) {
  const byId = new Map()
  for (const value of list(values)) {
    const source = normalizeSource(value, expectedCaseId)
    if (source && !byId.has(source.source_id)) byId.set(source.source_id, source)
  }
  return [...byId.values()]
}

export function normalizeCitation(value, sourceById, expectedCaseId = null) {
  const citation = record(value)
  const source = sourceById?.get(citation.source_id)
  if (!source || !citation.citation_id) return null
  if (source.source_scope === 'case' && source.case_id !== expectedCaseId) return null
  return { ...citation, label: citation.label || '', excerpt: citation.excerpt || source.excerpt || '', locator: record(citation.locator) }
}

export function resolveCitations(citations, sources, expectedCaseId = null) {
  const normalizedSources = normalizeSources(sources, expectedCaseId)
  const sourceById = new Map(normalizedSources.map(source => [source.source_id, source]))
  const normalizedCitations = list(citations)
    .map(value => normalizeCitation(value, sourceById, expectedCaseId))
    .filter(Boolean)
  const used = new Set(normalizedCitations.map(item => item.source_id))
  return {
    citations: normalizedCitations,
    sources: normalizedSources.filter(source => used.has(source.source_id)),
    sourceById
  }
}
