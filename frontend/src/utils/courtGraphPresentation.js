import { legalUnitLabel } from './legalSearchPresentation.js'

const labels = {
  CASE: 'Caso', CLAIM: 'Pretensión', LEGAL_ISSUE: 'Problema jurídico',
  EVIDENCE: 'Evidencia documental', DOCUMENT: 'Documento del expediente',
  LAW: 'Norma jurídica', JURISPRUDENCE: 'Jurisprudencia',
  ARGUMENT: 'Argumento', COUNTERARGUMENT: 'Contraargumento',
  RISK: 'Riesgo', PROCEDURAL_ACT: 'Actuación',
  JUDGE_ANALYSIS: 'Evaluación judicial simulada', DECISION: 'Decisión simulada'
}
const relations = {
  ASSERTS: 'Incluye', SUPPORTS: 'Respalda', PROVES: 'Acredita',
  CITES: 'Cita', COUNTERS: 'Se opone a', CREATES_RISK: 'Genera riesgo',
  CONTAINED_IN: 'Consta en', ARGUES: 'Argumenta sobre',
  EVALUATES: 'Valora', LEADS_TO: 'Conduce a'
}
const colors = {
  case: '#0F2747', accredited: '#2F7D62', alleged: '#64748B', undetermined: '#475569',
  evidence: '#2F7D62', legal: '#2C6680', claimant: '#2563EB',
  respondent: '#725C9A', party: '#64748B', argument: '#2563EB',
  counterargument: '#725C9A', risk: '#9A4656', judge: '#0F2747',
  decision: '#B08A4C', default: '#475569'
}

export function graphKind(node) {
  const type = node?.entity_type
  if (type === 'FACT') return ['supported', 'accredited', 'proven'].includes(node?.status) ? 'accredited' :
    node?.status === 'alleged' ? 'alleged' : 'undetermined'
  if (type === 'PARTY') return ({ claimant: 'claimant', respondent: 'respondent', court: 'judge' })[node?.legal_role] || 'party'
  if (type === 'ARGUMENT' || type === 'COUNTERARGUMENT') {
    if (['claimant', 'demandante', 'prosecution'].includes(node?.position)) return 'claimant'
    if (['respondent', 'demandado', 'defense'].includes(node?.position)) return 'respondent'
  }
  return ({ CASE: 'case', EVIDENCE: 'evidence', DOCUMENT: 'evidence',
    LAW: 'legal', JURISPRUDENCE: 'legal', ARGUMENT: 'argument',
    COUNTERARGUMENT: 'counterargument', RISK: 'risk', JUDGE_ANALYSIS: 'judge',
    DECISION: 'decision' })[type] || 'default'
}

export function graphLabel(node) {
  if (node?.entity_type === 'FACT') return graphKind(node) === 'accredited' ? 'Hecho acreditado' :
    node?.status === 'alleged' ? 'Hecho alegado' : 'Hecho no determinado'
  if (node?.entity_type === 'PARTY') return ({ claimant: 'Demandante', respondent: 'Demandado',
    court: 'Juez' })[node?.legal_role] || 'Parte'
  if (node?.entity_type === 'ARGUMENT' && graphKind(node) === 'claimant') return 'Argumento de la parte demandante'
  if (node?.entity_type === 'ARGUMENT' && graphKind(node) === 'respondent') return 'Argumento de la parte demandada'
  if (node?.entity_type === 'COUNTERARGUMENT' && graphKind(node) === 'respondent') return 'Contraargumento de la parte demandada'
  return labels[node?.entity_type] || 'Elemento del caso'
}

export function graphColor(node) { return colors[graphKind(node)] || colors.default }
export function graphRelation(edge) { return relations[edge?.relation_type] || 'Relación jurídica' }
export function graphSearchText(node, sources = []) {
  const sourceNames = sources instanceof Map ? sources :
    new Map(sources.map(source => [source.source_id, source.title || '']))
  return [node?.title, node?.name, node?.description, node?.excerpt,
    ...(node?.source_ids || []).map(id => sourceNames.get(id) || '')]
    .filter(Boolean).join(' ').toLocaleLowerCase()
}
export function authorizedGraphSources(sources, caseId) {
  return new Map((sources || []).filter(source => source?.source_id && (
    source.source_scope === 'public_legal' && source.provenance_version === 'v2' &&
      source.document_id && source.unit_id ||
    source.source_scope === 'private_case' && source.case_id === caseId && source.document_id
  )).map(source => [source.source_id, source]))
}
export function graphLocator(source) {
  if (!source) return ''
  return [source.unit_type && source.unit_number ? legalUnitLabel(source.unit_type, source.unit_number) : null,
    source.legal_basis, source.article && `Art. ${source.article}`,
    source.page_start && `pág. ${source.page_start}`,
    source.section].filter(Boolean).join(' · ')
}
