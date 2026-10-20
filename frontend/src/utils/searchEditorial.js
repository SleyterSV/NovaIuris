import { resolveCitations, normalizeSources } from './sourceContract.js'

// Presentation numbers never replace the persisted source or citation identity.
export function editorialCitations(answer, citations, sources) {
  const verified = resolveCitations(citations, sources)
  const byLabel = new Map(verified.citations.filter(c => /^\[\d+\]$/.test(c.label)).map(c => [c.label, c]))
  const bySource = new Map()
  const used = []
  const rendered = String(answer || '').replace(/\[\d+\]/g, label => {
    const citation = byLabel.get(label)
    if (!citation) return ''
    let entry = bySource.get(citation.source_id)
    if (!entry) {
      const source = verified.sourceById.get(citation.source_id)
      if (!source) return ''
      entry = { number: used.length + 1, source, citation }
      bySource.set(citation.source_id, entry)
      used.push(entry)
    }
    return `[${entry.number}]`
  })
  return {
    answer: rendered,
    used,
    sources: used.map(entry => entry.source),
    citations: used.map(entry => ({ ...entry.citation, label: `[${entry.number}]` })),
    numberBySource: new Map(used.map(entry => [entry.source.source_id, entry.number]))
  }
}

export function resultCitationNumber(result, presentation) {
  const source = normalizeSources([result])[0]
  if (source) return presentation.numberBySource.get(source.source_id) || null
  const match = presentation.sources.find(item => item.document_id === result.document_id && item.unit_id === result.unit_id)
  return match ? presentation.numberBySource.get(match.source_id) || null : null
}

export function sourceForCitation(citation, presentation) {
  return presentation.sources.find(source => source.source_id === citation?.source_id) || null
}
