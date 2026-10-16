import { normalizeSource } from './sourceContract.js'

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
  return typeof value === 'string' ? value.replace(/\b(?:FACT|ISSUE)-[a-f0-9]{24}\b/gi, '').replace(/ {2,}/g, ' ').trim() : value
}

export function relatedFactTexts(argument, facts = []) {
  const ids = new Set(Array.isArray(argument?.supporting_fact_ids) ? argument.supporting_fact_ids : [])
  return facts.filter(fact => ids.has(fact.fact_id)).map(fact => fact.text).filter(Boolean)
}

export function verifiedArgumentSources(argument, sources = [], caseId = null) {
  const ids = new Set(Array.isArray(argument?.source_ids) ? argument.source_ids : [])
  return sources.filter(source => ids.has(source.source_id))
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
