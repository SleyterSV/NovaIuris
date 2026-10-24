<template>
  <section class="executive-summary" aria-labelledby="summary-title">
    <header class="summary-header">
      <div>
        <p class="eyebrow">SÍNTESIS DEL CASO</p>
        <h2 id="summary-title">Resumen ejecutivo</h2>
        <p class="summary-subtitle">Síntesis de los elementos jurídicos relevantes del caso para revisión profesional.</p>
      </div>
      <span class="summary-badge">{{ partial ? 'Análisis parcial' : 'Análisis completado' }}</span>
    </header>
    <p class="summary-lead">{{ executiveText || 'Información insuficiente para elaborar una síntesis ejecutiva.' }}</p>
    <dl class="summary-facts" aria-label="Indicadores del caso">
      <div v-for="item in particulars" :key="item.key" class="summary-card" :class="'summary-card--' + item.key">
        <span class="card-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path :d="item.icon" /></svg></span>
        <dt>{{ item.label }}</dt><dd>{{ item.value }}</dd>
      </div>
    </dl>
    <div class="summary-insights">
      <section class="summary-insight summary-insight--facts" aria-labelledby="summary-facts-title">
        <h3 id="summary-facts-title">Hechos clave</h3>
        <ul v-if="keyFacts.length"><li v-for="(fact, index) in keyFacts" :key="index">{{ fact }}</li></ul>
        <p v-else>Información insuficiente para identificar hechos clave.</p>
      </section>
      <section class="summary-insight summary-insight--issue" aria-labelledby="summary-issue-title">
        <h3 id="summary-issue-title">Problema jurídico</h3>
        <p>{{ legalIssue || 'No identificado con la información disponible.' }}</p>
      </section>
      <section class="summary-insight summary-insight--finding" aria-labelledby="summary-finding-title">
        <h3 id="summary-finding-title">Hallazgo principal</h3>
        <p>{{ mainFinding || 'Información insuficiente para establecer un hallazgo principal.' }}</p>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { presentableText } from '@/utils/novacasePresentation.js'
const props = defineProps({
  summary: { type: Object, default: () => ({}) },
  analysis: { type: Object, default: () => ({}) },
  facts: { type: Array, default: () => [] },
  reportDocument: { type: Object, default: () => ({}) },
  sources: { type: Array, default: () => [] },
  caseId: { type: String, default: null },
  partial: { type: Boolean, default: false }
})
const readable = value => typeof value === 'string' ? presentableText(value).trim() : ''
const firstReadable = (...values) => values.map(readable).find(Boolean) || ''
const levelLabel = value => {
  const raw = readable(value)
  const labels = {
    low: 'Bajo', baja: 'Baja', bajo: 'Bajo', medium: 'Medio', media: 'Media', medio: 'Medio',
    high: 'Alto', alta: 'Alta', alto: 'Alto', critical: 'Crítico', crítica: 'Crítica', crítico: 'Crítico',
    unknown: 'No identificado', desconocida: 'No identificado', desconocido: 'No identificado'
  }
  return labels[raw.toLocaleLowerCase('es')] || raw || 'No identificado'
}
const consolidatedRisk = computed(() => {
  const match = readable(props.summary.riesgo).match(/^(?:(?:nivel(?: general)?(?: de riesgo)?|riesgo)\s*:?\s*)?(baj[oa]|low|medi[oa]|medium|alt[oa]|high)\b/i)
  if (!match) return 'No identificado'
  const level = match[1].toLocaleLowerCase('es')
  return /^(baj|low)/.test(level) ? 'Bajo' : /^(med)/.test(level) ? 'Medio' : 'Alto'
})
const reportParagraph = pattern => {
  const sections = Array.isArray(props.reportDocument.sections) ? props.reportDocument.sections : []
  const section = sections.find(item => pattern.test(item?.title || '') && typeof item?.content === 'string')
  return readable(section?.content?.split(/\n\s*\n/).find(part => part.trim())?.replace(/\[\d+\]/g, ''))
}
const executiveText = computed(() => firstReadable(props.summary.resumen, props.summary.resumen_ejecutivo,
  typeof props.analysis.summary === 'string' ? props.analysis.summary : '',
  reportParagraph(/resumen ejecutivo|objeto y alcance|síntesis/i),
  props.summary.pretension, props.analysis.pretension_principal))
const particulars = computed(() => [
  { key: 'branch', label: 'Rama del derecho', value: firstReadable(props.summary.rama) || 'No identificado',
    icon: 'M4 20h16M7 20V9l5-5 5 5v11M5 10h14M9 14h6' },
  { key: 'process', label: 'Tipo de proceso', value: firstReadable(props.summary.proceso, props.summary.tipo_proceso) || 'No identificado',
    icon: 'M7 3h8l4 4v14H5V3h2Zm8 0v5h4M8 12h8M8 16h8' },
  { key: 'risk', label: 'Nivel de riesgo', value: consolidatedRisk.value,
    icon: 'M12 3 2.5 20h19L12 3Zm0 6v5m0 3h.01' },
  { key: 'evidence', label: 'Nivel de evidencia', value: levelLabel(props.summary.evidencia),
    icon: 'M4 4h16v16H4zM8 9h8M8 13h8M8 17h5' },
  { key: 'documents', label: 'Documentos del caso', value: String(props.summary.documentos ?? 0),
    icon: 'M5 4h10l4 4v12H5zM15 4v5h4M8 13h8M8 17h6' },
  { key: 'sources', label: 'Fuentes jurídicas recuperadas', value: String(props.summary.fuentes_juridicas ?? 0),
    icon: 'M5 5h14M5 10h14M5 15h14M5 20h9M8 3v19' }
])
const privateSourceIds = computed(() => new Set(props.sources.filter(source =>
  ['case', 'private_case'].includes(source?.source_scope) && source.case_id === props.caseId)
  .map(source => source.source_id)))
const documented = fact => fact?.status === 'supported' && Array.isArray(fact.source_ids) &&
  fact.source_ids.some(id => privateSourceIds.value.has(id))
const keyFacts = computed(() => [...props.facts].sort((a, b) => Number(documented(b)) - Number(documented(a)))
  .map(fact => {
    const text = readable(fact?.text || fact)
    if (!text) return ''
    if (documented(fact)) return text
    if (fact?.status === 'alleged' || fact?.status === 'supported') {
      return /^se alega\b/i.test(text) ? text : 'Se alega que ' + text.charAt(0).toLocaleLowerCase('es') + text.slice(1)
    }
    return 'Pendiente de corroboración: ' + text
  }).filter(Boolean).slice(0, 5))
const firstIssue = computed(() => {
  const issues = props.analysis.issues
  if (Array.isArray(issues)) return issues.find(item => firstReadable(item?.text, item?.question, item))
  return issues
})
const legalIssue = computed(() => firstReadable(props.summary.problema_juridico,
  props.analysis.problema_juridico, firstIssue.value?.text, firstIssue.value?.question, firstIssue.value))
const mainFinding = computed(() => firstReadable(props.summary.hallazgo_principal, props.summary.hallazgo,
  reportParagraph(/conclusión|conclusion/i)))
</script>

<style scoped>
.executive-summary{display:grid;gap:30px;min-width:0;width:100%;max-width:1240px;color:#26384b}
.summary-header{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;padding-bottom:25px;border-bottom:1px solid #dce5ee}
.eyebrow{margin:0 0 8px;color:#94754b;font-size:.69rem;font-weight:750;letter-spacing:.12em}
.summary-header h2{margin:0;color:#17375e;font:600 clamp(1.7rem,2.7vw,2.15rem)/1.23 Georgia,serif}
.summary-subtitle{max-width:68ch;margin:12px 0 0;color:#61748a;font-size:.94rem;line-height:1.7}
.summary-badge{flex:none;margin-top:3px;padding:8px 13px;border:1px solid #ccded3;border-radius:999px;background:#f2f8f4;color:#315b47;font-size:.74rem;font-weight:700;line-height:1.4}
.summary-lead{max-width:78ch;margin:0;color:#293f55;font-size:1.03rem;line-height:1.85;white-space:pre-line}
.summary-facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:0}
.summary-card{display:grid;grid-template-columns:40px minmax(0,1fr);column-gap:14px;align-content:start;min-width:0;min-height:112px;padding:20px;border:1px solid #dfe6ec;border-radius:12px;background:#fff;box-shadow:0 3px 12px #17375e05}
.card-icon{grid-row:1 / span 2;display:grid;place-items:center;box-sizing:border-box;width:40px;height:40px;border:1px solid var(--icon-border);border-radius:11px;background:var(--icon-tint);color:var(--icon-color)}
.card-icon svg{width:21px;height:21px}
.summary-card--branch{--icon-color:#346da3;--icon-tint:#edf5fc;--icon-border:#d9e9f6}
.summary-card--process{--icon-color:#9b742e;--icon-tint:#fcf6e9;--icon-border:#efe2c5}
.summary-card--risk{--icon-color:#b05c55;--icon-tint:#fcf0ed;--icon-border:#f0dcd7}
.summary-card--evidence{--icon-color:#7d62a4;--icon-tint:#f3effa;--icon-border:#e5dcf2}
.summary-card--documents{--icon-color:#3b8067;--icon-tint:#edf7f1;--icon-border:#d9eade}
.summary-card--sources{--icon-color:#467b9c;--icon-tint:#edf7fa;--icon-border:#d7eaf1}
.summary-card dt{align-self:end;color:#61748a;font-size:.7rem;font-weight:750;letter-spacing:.035em;text-transform:uppercase;line-height:1.5}
.summary-card dd{min-width:0;margin:8px 0 0;color:#17375e;font-size:1.04rem;font-weight:650;line-height:1.5;overflow-wrap:break-word;word-break:normal;hyphens:none}
.summary-card--documents dd,.summary-card--sources dd{font:600 1.4rem/1.25 Georgia,serif}
.summary-insights{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));align-items:start;gap:20px}
.summary-insight{min-width:0;padding:24px 26px;border:1px solid #dfe6ec;border-radius:12px;box-shadow:0 3px 12px #17375e04}
.summary-insight h3{margin:0 0 16px;color:#17375e;font:600 1.2rem/1.35 Georgia,serif}
.summary-insight p,.summary-insight li{color:#344c62;font-size:.96rem;line-height:1.8;overflow-wrap:break-word;word-break:normal}
.summary-insight p{margin:0;white-space:pre-line}.summary-insight ul{display:grid;gap:13px;max-width:90ch;margin:0;padding-left:20px}.summary-insight li{padding-left:5px}.summary-insight li::marker{color:#6589ab;font-size:.8em}
.summary-insight--facts{grid-column:1/-1;background:#f6f9fc;border-color:#dce7ef}
.summary-insight--issue{background:#fdf9f0;border-color:#e8ddc8;border-top:3px solid #d8b77b}.summary-insight--issue h3{color:#80602c}
.summary-insight--finding{background:#f1f8f5;border-color:#d4e7dd;border-top:3px solid #82b6a0}.summary-insight--finding h3{color:#2d6a54}
@media(max-width:980px){.summary-facts{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:760px){.summary-header{flex-wrap:wrap}.summary-insights{grid-template-columns:minmax(0,1fr)}}
@media(max-width:620px){.summary-header{flex-direction:column;gap:16px;padding-bottom:20px}.summary-facts,.summary-insights{grid-template-columns:minmax(0,1fr)}.summary-insight--facts{grid-column:auto}.summary-card{min-height:0;padding:18px}.summary-insight{padding:21px 20px}.executive-summary{gap:24px}}
</style>
