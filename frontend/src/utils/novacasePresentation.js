import { citationLabel, normalizeSource, normalizeSources, resolveCitations } from './sourceContract.js'

export const ARGUMENT_SECTION_LABELS = Object.freeze({
  main_arguments: 'Argumentos principales',
  secondary_arguments: 'Argumentos complementarios',
  constitutional_arguments: 'Argumentos constitucionales',
  procedural_arguments: 'Argumentos procesales',
  normative_arguments: 'Argumentos normativos',
  jurisprudence_used: 'Jurisprudencia considerada',
  possible_counterarguments: 'Contraargumentos posibles',
  counterargument_responses: 'Respuestas a contraargumentos',
  general_observations: 'Observaciones generales'
})

export function researchNotice(status, publicCount = 0) {
  if (status === 'VERIFIED_SOURCES' && publicCount > 0) {
    return { tone: 'verified', text: `Investigación jurídica completada con ${publicCount} fuente${publicCount === 1 ? '' : 's'} V2 verificada${publicCount === 1 ? '' : 's'}.` }
  }
  if (status === 'ERROR') return { tone: 'error', text: 'Se produjo un error durante la investigación jurídica. No se atribuye autoridad a resultados no verificados.' }
  if (status === 'NO_RESULTS') return { tone: 'empty', text: 'Investigación jurídica completada sin fuentes verificadas en el corpus disponible.' }
  return { tone: 'unavailable', text: 'Investigación jurídica no disponible en este momento. Las referencias jurídicas requieren verificación.' }
}

export function evidenceAvailability(content, { documentCount = 0, documentary = false, verified = false } = {}) {
  if (documentary && documentCount === 0) return 'no_documents'
  const value = typeof content === 'string' ? content.trim() : Array.isArray(content) ? content.filter(Boolean).join(' ').trim() : ''
  if (!value || /^(no identificado|no se identific|no aportad|sin informaci[oó]n)/i.test(value)) {
    return 'not_identified'
  }
  return verified ? 'available' : 'requires_verification'
}

export function presentableText(value) {
  if (Array.isArray(value)) return value.map(presentableText)
  return typeof value === 'string' ? value
    .replace(/\b(?:FACT|ISSUE|SRC)-[a-f0-9]{24}\b/gi, '')
    .replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, '')
    .replace(/ {2,}/g, ' ').trim() : value
}

export const publicLegalSources = sources => normalizeSources(sources)
  .filter(source => source.source_scope === 'public_legal')

export function sourceUnitLabel(source) {
  const type = source.unit_type || source.metadata?.unit_type
  const number = source.unit_number || source.metadata?.unit_number
  const label = ({ foundation: 'Fundamento', article: 'Artículo', decision: 'Decisión',
    separate_opinion: 'Voto separado' })[type]
  if (!label) return ''
  if (number && ['foundation', 'article'].includes(type)) return `${label} ${number}`
  const heading = typeof source.section === 'string' ? source.section.trim() : ''
  if (!number && heading && heading.toLowerCase() !== label.toLowerCase()) {
    return heading.toLowerCase().startsWith(label.toLowerCase()) ? heading : `${label}: ${heading}`
  }
  return label
}

export function sourceHumanLabel(source) {
  return [source.display_title || source.title, sourceUnitLabel(source),
    source.court || source.issuer || source.entity,
    source.page_start ? `pág. ${source.page_start}` : null].filter(Boolean).join(' · ')
}

export function factAllegationOrigin(fact, privateSources = []) {
  return fact?.status === 'alleged' && privateSources.length === 0 ? 'Relato proporcionado' : ''
}

export function groupedJurisprudence(sources) {
  const groups = new Map()
  for (const source of publicLegalSources(sources).filter(source =>
    ['judgment', 'jurisprudence', 'cassation'].includes(source.source_type) ||
    /^(STC|Casaci[oó]n|Sentencia)/i.test(source.display_title || source.title))) {
    const key = source.document_id || source.display_title || source.title
    if (!groups.has(key)) groups.set(key, { title: source.display_title || source.title,
      court: source.court || source.issuer || source.entity, units: [], pages: new Set() })
    const group = groups.get(key)
    const unit = sourceUnitLabel(source)
    if (unit && !group.units.includes(unit)) group.units.push(unit)
    if (source.page_start) group.pages.add(source.page_start)
    if (source.page_end) group.pages.add(source.page_end)
  }
  return [...groups.values()].map(group => ({ ...group, pages: [...group.pages].sort((a,b) => a-b) }))
}

export function jurisprudenceMarkdown(sources) {
  return groupedJurisprudence(sources).map(group =>
    `**${group.title}**\n${[group.court, group.units.join(', '),
      group.pages.length ? `pág. ${group.pages.join(', ')}` : null].filter(Boolean).join(' · ')}`)
    .join('\n\n')
}

export function argumentNeedsVerification(argument, sources, caseId = null, citations = []) {
  return verifiedArgumentSources(argument, sources, caseId, citations).length === 0
}

export function relatedFactTexts(argument, facts = []) {
  const ids = new Set(Array.isArray(argument?.supporting_fact_ids) ? argument.supporting_fact_ids : [])
  return facts.filter(fact => ids.has(fact.fact_id)).map(fact => fact.text).filter(Boolean)
}

export function argumentCitationForSource(source, citations = [], sources = [], caseId = null) {
  const canonical = normalizeSource(source, caseId)
  if (!canonical) return null
  const resolved = resolveCitations(citations, sources, caseId)
  const numbered = resolved.citations.filter(citation => citationLabel(citation))
  const exact = numbered.find(citation => citation.source_id === canonical.source_id)
  if (exact) return exact
  if (canonical.source_scope === 'public_legal') {
    const unitMatch = numbered.find(citation => {
    const citedSource = resolved.sourceById.get(citation.source_id)
    return citedSource?.source_scope === 'public_legal' &&
      citedSource.document_id === canonical.document_id && citedSource.unit_id === canonical.unit_id
    })
    if (unitMatch) return unitMatch
  }
  // Some authorized source records carry their citation number directly.
  // It is part of the shared citation contract, not a presentation index.
  const sourceLabel = citationLabel(canonical)
  return sourceLabel ? { ...canonical, label: sourceLabel } : null
}

export function verifiedArgumentSources(argument, sources = [], caseId = null, citations = []) {
  const ids = new Set([...(Array.isArray(argument?.source_ids) ? argument.source_ids : []),
    ...(Array.isArray(argument?.jurisprudence) ? argument.jurisprudence : []),
    argument?.source_id, argument?.unit_id].filter(Boolean))
  const text = [argument?.argument, argument?.text, argument?.legal_basis]
    .flat().filter(value => typeof value === 'string').join(' ')
  for (const citation of citations) {
    if (citation?.label && text.includes(citation.label)) ids.add(citation.source_id)
  }
  return sources.filter(source => ids.has(source.source_id) || ids.has(source.unit_id) ||
    ids.has(source.chunk_id))
    .map(source => normalizeSource(source, caseId))
    .filter(source => source && ['public_legal', 'private_case'].includes(source.source_scope))
}

export function verifiedPublicArgumentSources(argument, sources = []) {
  return verifiedArgumentSources(argument, sources).filter(source => source.source_scope === 'public_legal')
}

export function canAttachDocumentsToCase(targetCaseId, workspaceCaseId, turnActive) {
  return Boolean(turnActive && typeof targetCaseId === 'string' && targetCaseId &&
    targetCaseId === workspaceCaseId)
}
