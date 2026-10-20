<script setup>
import { computed } from 'vue'
import { legalTypeLabel } from '@/utils/legalSearchPresentation.js'

const props = defineProps({ analysis: { type: Object, default: () => ({}) }, normalizedQuery: { type: String, default: '' } })
const intentLabels = { buscar_norma: 'Normativa', buscar_jurisprudencia: 'Jurisprudencia', buscar_doctrina: 'Doctrina' }
const fields = computed(() => {
  const analysis = props.analysis || {}
  const entries = []
  if (analysis.rama) entries.push({ label: 'Rama jurídica', value: String(analysis.rama) })
  if (analysis.tema) entries.push({ label: 'Tema', value: String(analysis.tema) })
  if (analysis.problema_juridico) entries.push({ label: 'Problema identificado', value: String(analysis.problema_juridico) })
  const focus = intentLabels[analysis.intencion] || (typeof analysis.intent === 'string' && !analysis.intent.includes('_') ? analysis.intent : '')
  if (focus) entries.push({ label: 'Enfoque de búsqueda', value: focus })
  if (analysis.organo) entries.push({ label: 'Órgano identificado', value: String(analysis.organo) })
  if (analysis.tipo_documento) entries.push({ label: 'Tipo de documento', value: legalTypeLabel(analysis.tipo_documento) })
  if (analysis.enfoque) entries.push({ label: 'Criterio de búsqueda', value: String(analysis.enfoque) })
  return entries
})
const terms = computed(() => Array.isArray(props.analysis?.keywords)
  ? [...new Set(props.analysis.keywords.filter(value => typeof value === 'string' && value.trim().length > 3))].slice(0, 6)
  : Array.isArray(props.analysis?.entities) ? props.analysis.entities.slice(0, 6) : [])
// A lone branch is already in the context strip; avoid repeating it in an empty section.
const hasAnalysis = computed(() => fields.value.some(field => field.label !== 'Rama jurídica') || terms.value.length > 0)
</script>

<template>
  <section v-if="hasAnalysis" class="search-analysis" aria-labelledby="analysis-title">
    <header><h2 id="analysis-title">Interpretación jurídica</h2><p>Elementos identificados en la consulta para orientar la búsqueda jurídica.</p></header>
    <dl class="analysis-fields"><div v-for="field in fields" :key="field.label"><dt>{{ field.label }}</dt><dd>{{ field.value }}</dd></div></dl>
    <div v-if="terms.length" class="concepts"><h3>Conceptos identificados</h3><ul><li v-for="term in terms" :key="term">{{ term }}</li></ul></div>
  </section>
</template>

<style scoped>
.search-analysis{border-top:1px solid #dce3e9;margin-top:52px;padding-top:34px;color:#24364b}.search-analysis h2{font:500 clamp(1.6rem,2.4vw,2.1rem)/1.2 Georgia,serif;color:#17375e;margin:0 0 9px}.search-analysis header p{margin:0;color:#667587;line-height:1.6}.analysis-fields{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:20px 30px;margin:26px 0 0}.analysis-fields>div{min-width:0;border-left:2px solid #d7c29c;padding-left:13px}.analysis-fields dt,.concepts h3{margin:0;color:#798798;font-size:.68rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}.analysis-fields dd{margin:7px 0 0;overflow-wrap:anywhere;color:#213b57;font-size:.91rem;line-height:1.5}.concepts{margin-top:24px}.concepts ul{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0;margin:10px 0 0}.concepts li{border:1px solid #dce4eb;border-radius:5px;padding:5px 10px;font-size:.78rem;color:#315c97}@media(max-width:600px){.analysis-fields{grid-template-columns:1fr;gap:16px}}
.search-analysis{margin-top:44px;padding-top:30px}
</style>
