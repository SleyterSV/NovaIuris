const labels = {
  regulation: 'Normativa', judgment: 'Sentencia', order: 'Auto',
  cassation: 'Casación', jurisprudence: 'Jurisprudencia',
  legislation: 'Normativa', article: 'Artículo', foundation: 'Fundamento',
  decision: 'Decisión', antecedent: 'Antecedente', disposition: 'Disposición',
  sumilla: 'Sumilla', matter: 'Materia', separate_opinion: 'Voto u opinión separada'
}

export function legalTypeLabel(type, metadata = {}) {
  if (type === 'regulation' && /decreto supremo/i.test(metadata?.resolution_type || '')) {
    return 'Decreto Supremo'
  }
  return labels[type] || type || 'Documento jurídico'
}

export function sameExcerpt(summary, excerpt) {
  const normalize = value => String(value || '').replace(/\s+/g, ' ').trim().toLocaleLowerCase('es')
  return Boolean(summary && excerpt && normalize(summary) === normalize(excerpt))
}

export function legalUnitLabel(type, number) {
  return [legalTypeLabel(type), String(number || '').trim()].filter(Boolean).join(' ')
}

export function cardExcerpt(result = {}) {
  const exact = String(result.extracto_exacto || '')
  if (result.unit_id) return { primary: String(result.resumen_ia || exact), secondary: '' }
  const summary = String(result.resumen_ia || '')
  return { primary: summary, secondary: exact && !sameExcerpt(summary, exact) ? exact : '' }
}

export function sourceDetailPresentation(source, unit, status) {
  if (status === 'loading') return { loading: true, text: '', heading: '', warning: false }
  const complete = typeof unit?.text === 'string' && unit.text.length > 0
  return {
    loading: false,
    text: complete ? unit.text : String(source?.excerpt || ''),
    heading: complete ? 'Unidad jurídica completa' : 'Fragmento utilizado',
    warning: status === 'error'
  }
}
