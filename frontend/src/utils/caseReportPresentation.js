import { presentableText } from './novacasePresentation.js'

const sourceHeading = /^##\s+Fuentes(?: utilizadas)?\s*$/i
const narrativeHeading = /^(Objeto y alcance|Marco normativo y jurisprudencial|Análisis jurídico(?: por cuestión)?|Argumentos jurídicos centrales|Contraargumentos previsibles y réplicas)$/i

export function reportForReading(report) {
  const lines = presentableText(report || '').split('\n')
  const output = []
  let section = '', skip = false
  for (const line of lines) {
    if (/^#\s+/.test(line) && !output.some(value => value.trim())) continue
    if (/^##\s+/.test(line)) {
      skip = sourceHeading.test(line)
      section = line.replace(/^##\s+/, '').trim()
    }
    if (skip) continue
    output.push(narrativeHeading.test(section) ? line.replace(/^[-*]\s+/, '') : line)
  }
  return output.join('\n').trim()
}

export function reportUsedSources(citations, sources) {
  const used = new Set((citations || []).map(item => item.source_id))
  return (sources || []).filter(item => used.has(item.source_id))
}
