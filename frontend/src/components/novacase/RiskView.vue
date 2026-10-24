<template>
  <main class="risk-editorial" aria-labelledby="risk-title">
    <header class="risk-header">
      <div>
        <p class="risk-eyebrow"><span aria-hidden="true"></span> MYKE · NOVACASE</p>
        <div class="risk-heading-row">
          <div>
            <h2 id="risk-title">Evaluación de riesgos</h2>
            <p class="risk-subtitle">Identificación de contingencias jurídicas, procesales y probatorias que pueden afectar la viabilidad del caso.</p>
          </div>
        </div>
      </div>
    </header>

    <section v-if="summaryMetrics.length" class="risk-summary" aria-label="Síntesis de riesgos">
      <div v-for="metric in summaryMetrics" :key="metric.key" class="summary-metric" :class="{ 'summary-overall': metric.key === 'overall' }">
        <span>{{ metric.label }}</span>
        <strong v-if="metric.key === 'overall'" :class="levelClass(metric.value)">{{ metric.value }}</strong>
        <strong v-else>{{ metric.value }}</strong>
      </div>
    </section>

    <p v-if="executiveConclusion" class="risk-conclusion">{{ executiveConclusion }}</p>

    <section v-if="criticalRisks.length" class="risk-priority" aria-labelledby="priority-title">
      <header class="risk-section-heading">
        <p class="risk-kicker">ATENCIÓN PRIORITARIA</p>
        <h3 id="priority-title">Riesgos prioritarios</h3>
        <p>Contingencias que requieren atención antes de definir o ejecutar la estrategia procesal.</p>
      </header>
      <ol class="priority-list">
        <li v-for="(item,index) in criticalRisks" :key="item.key" class="priority-row">
          <span class="risk-number" aria-hidden="true">{{ number(index + 1) }}</span>
          <div class="risk-copy">
            <div class="risk-row-heading">
              <h4>{{ item.title || 'Riesgo prioritario' }}</h4>
              <span v-if="item.severityLabel" class="severity-badge" :class="levelClass(item.severityLabel)">{{ item.severityLabel }}</span>
            </div>
            <p v-if="item.duplicateSection" class="risk-cross-reference">
              El desarrollo completo se presenta en <a :href="`#risk-section-${item.duplicateSection.key}`">{{ item.duplicateSection.title.toLocaleLowerCase() }}</a>.
            </p>
            <p v-else-if="item.text" class="risk-description">{{ item.text }}</p>
            <p v-if="item.impact" class="risk-detail"><strong>Impacto</strong><span>{{ item.impact }}</span></p>
            <p v-if="item.mitigation && !item.duplicateSection" class="risk-mitigation"><strong>Mitigación</strong><span>{{ item.mitigation }}</span></p>
          </div>
        </li>
      </ol>
    </section>

    <section v-for="section in detailedSections" :id="`risk-section-${section.key}`" :key="section.key" class="risk-category" :aria-labelledby="`risk-heading-${section.key}`">
      <header class="risk-section-heading">
        <p class="risk-kicker">{{ section.eyebrow }}</p>
        <h3 :id="`risk-heading-${section.key}`">{{ section.title }}</h3>
        <p v-if="section.description">{{ section.description }}</p>
      </header>
      <ol class="risk-list">
        <li v-for="(item,index) in section.items" :key="item.key" class="risk-row">
          <span class="risk-number" aria-hidden="true">{{ number(index + 1) }}</span>
          <div class="risk-copy">
            <div class="risk-row-heading">
              <h4 v-if="item.title">{{ item.title }}</h4>
              <span v-if="item.severityLabel" class="severity-badge" :class="levelClass(item.severityLabel)">{{ item.severityLabel }}</span>
            </div>
            <p v-if="item.text" class="risk-description">{{ item.text }}</p>
            <p v-if="item.impact" class="risk-detail"><strong>Impacto</strong><span>{{ item.impact }}</span></p>
            <p v-if="item.mitigation" class="risk-mitigation"><strong>Mitigación</strong><span>{{ item.mitigation }}</span></p>
          </div>
        </li>
      </ol>
    </section>

    <section v-if="recommendationGroups.length" class="risk-plan" aria-labelledby="risk-plan-title">
      <header class="risk-section-heading">
        <p class="risk-kicker">ACCIONES PARA REDUCIR CONTINGENCIAS</p>
        <h3 id="risk-plan-title">Plan de mitigación</h3>
        <p>Acciones recomendadas para atender los riesgos identificados y fortalecer la posición jurídica.</p>
      </header>
      <section v-for="group in recommendationGroups" :key="group.key" class="mitigation-group">
        <h4 v-if="group.title">{{ group.title }}</h4>
        <ol class="recommendation-list">
          <li v-for="(item,index) in group.items" :key="item.key">
            <span class="risk-number" aria-hidden="true">{{ number(index + 1) }}</span>
            <div class="risk-copy"><p>{{ item.text }}</p></div>
          </li>
        </ol>
      </section>
    </section>

    <p v-if="!hasRiskData" class="risk-empty" role="status">No se identificó información suficiente para evaluar riesgos.</p>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { presentableText } from '@/utils/novacasePresentation.js'

const props = defineProps({ risk: { type: Object, default: () => ({}) } })

const severityLabels = {
  high: 'Alto', alta: 'Alto', alto: 'Alto',
  medium: 'Medio', media: 'Medio', medio: 'Medio',
  low: 'Bajo', baja: 'Bajo', bajo: 'Bajo',
  critical: 'Crítico', critica: 'Crítico', crítico: 'Crítico',
  severe: 'Grave', grave: 'Grave',
  unknown: 'No determinado', desconocido: 'No determinado', desconocida: 'No determinada',
  'not identified': 'No identificado', not_identified: 'No identificado'
}
const categoryConfig = [
  { key: 'procedural', title: 'Riesgos procesales', eyebrow: 'VÍA Y PLAZOS', description: 'Contingencias relacionadas con la procedencia, los plazos y los requisitos procesales.' },
  { key: 'evidentiary', title: 'Riesgos probatorios', eyebrow: 'ACREDITACIÓN', description: 'Vacíos documentales que pueden afectar la acreditación de los hechos centrales del caso.' },
  { key: 'legal', title: 'Riesgos jurídicos', eyebrow: 'INTERPRETACIÓN', description: 'Cuestiones de interpretación jurídica que pueden afectar la pretensión.' }
]

function cleanText(value) {
  if (typeof value !== 'string') return ''
  return presentableText(value).replace(/\s{2,}/g, ' ').trim()
}
function levelLabel(value) {
  if (typeof value !== 'string') return ''
  const key = value.toLocaleLowerCase().trim()
  return severityLabels[key] || cleanText(value)
}
function isKnownLevel(value) {
  return typeof value === 'string' && Object.hasOwn(severityLabels, value.toLocaleLowerCase().trim())
}
function levelClass(value) {
  const key = String(value || '').toLocaleLowerCase()
  if (['alto', 'alta', 'high'].includes(key)) return 'severity-high'
  if (['crítico', 'critica', 'critical', 'grave', 'severe'].includes(key)) return 'severity-critical'
  if (['medio', 'media', 'medium'].includes(key)) return 'severity-medium'
  if (['bajo', 'baja', 'low'].includes(key)) return 'severity-low'
  return 'severity-neutral'
}
function asList(value) { return Array.isArray(value) ? value : value == null || value === '' ? [] : [value] }
function extractMitigation(text) {
  const match = text.match(/(?:[;.]\s*|\n\s*)(?:Mitigación|Medida de mitigación):\s*([\s\S]+)$/i)
  return match ? { text: text.slice(0, match.index).replace(/[;,.\s]+$/, ''), mitigation: cleanText(match[1]) } : { text, mitigation: '' }
}
function normalizeRisk(value, key) {
  const source = value && typeof value === 'object' && !Array.isArray(value) ? value : { text: value }
  const rawText = cleanText(source.risk || source.description || source.text || source.detail || '')
  const parsed = extractMitigation(rawText)
  const rawImpact = cleanText(source.impact || '')
  const impactIsLevel = isKnownLevel(rawImpact)
  const severity = levelLabel(source.severity || source.level || source.risk_level || source.priority || (impactIsLevel ? rawImpact : ''))
  return {
    key,
    title: cleanText(source.title || source.name || ''),
    text: parsed.text,
    severityLabel: severity && severity !== cleanText(source.title || '') ? severity : '',
    impact: rawImpact && !impactIsLevel ? rawImpact : '',
    mitigation: cleanText(source.mitigation || source.recommendation || parsed.mitigation)
  }
}
function identityText(value) { return cleanText(value).toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim() }
function number(value) { return String(value).padStart(2, '0') }

const overallLevel = computed(() => {
  const raw = props.risk.risk_level || props.risk.summary || ''
  const level = levelLabel(raw)
  return level && !['No determinado', 'No identificado'].includes(level) ? level : ''
})
const criticalRisks = computed(() => asList(props.risk.strategic || props.risk.critical_risks)
  .map((item, index) => normalizeRisk(item, `critical-${index}`)).filter(item => item.text || item.title)
  .map(item => {
    const duplicateSection = categoryConfig.map(section => ({
      ...section,
      items: asList(props.risk[section.key] || props.risk[`${section.key === 'procedural' ? 'procedural' : section.key}_risks`])
        .map((value, index) => normalizeRisk(value, `${section.key}-${index}`))
    })).find(section => section.items.some(detail =>
      (item.text && identityText(detail.text) === identityText(item.text)) ||
      (item.title && identityText(detail.title) === identityText(item.title))))
    return { ...item, duplicateSection: duplicateSection ? { key: duplicateSection.key, title: duplicateSection.title } : null }
  }))
const detailedSections = computed(() => categoryConfig.map(section => ({
  ...section,
  items: asList(props.risk[section.key] || props.risk[`${section.key}_risks`])
    .map((item, index) => normalizeRisk(item, `${section.key}-${index}`))
    .filter(item => item.text || item.title)
})).filter(section => section.items.length))
const summaryMetrics = computed(() => [
  ...(overallLevel.value ? [{ key: 'overall', label: 'Nivel general', value: overallLevel.value }] : []),
  ...detailedSections.value.map(section => ({ key: section.key, label: section.title, value: section.items.length })),
  ...(criticalRisks.value.length ? [{ key: 'critical', label: 'Riesgos críticos', value: criticalRisks.value.length }] : [])
])
const executiveConclusion = computed(() => {
  const value = cleanText(props.risk.executive_summary || props.risk.summary_text || props.risk.overview || props.risk.conclusion || '')
  if (!value || identityText(value) === identityText(props.risk.risk_level)) return ''
  return value
})
const recommendationGroups = computed(() => {
  const items = asList(props.risk.recommendations).map((value, index) => {
    const source = value && typeof value === 'object' && !Array.isArray(value) ? value : { text: value }
    const text = cleanText(source.action || source.recommendation || source.text || source.description || '')
    const title = cleanText(source.category || source.objective || source.phase || source.group || '')
    return text ? { key: `recommendation-${index}`, title, text } : null
  }).filter(Boolean)
  const groups = new Map()
  for (const item of items) {
    const title = item.title || 'Acciones recomendadas'
    if (!groups.has(title)) groups.set(title, { key: title, title: item.title, items: [] })
    groups.get(title).items.push(item)
  }
  return [...groups.values()]
})
const hasRiskData = computed(() => Boolean(overallLevel.value || criticalRisks.value.length || detailedSections.value.length || recommendationGroups.value.length || executiveConclusion.value))
</script>

<style scoped>
.risk-editorial{--risk-navy:#17375e;--risk-muted:#667789;--risk-line:#dce5ee;--risk-gold:#a98551;display:grid;gap:clamp(28px,3.5vw,48px);width:100%;max-width:1240px;min-width:0;margin:0 auto;color:#34485d}
.risk-header{padding:2px 0 22px;border-bottom:1px solid var(--risk-line)}
.risk-eyebrow{display:flex;align-items:center;gap:9px;margin:0 0 10px;color:#8a6a37;font-size:.64rem;font-weight:750;letter-spacing:.12em}
.risk-eyebrow span{width:22px;height:1px;background:#b08a4c}
.risk-heading-row{display:block;max-width:820px;min-width:0}
.risk-heading-row h2{margin:0;color:var(--risk-navy);font:600 clamp(1.7rem,2.3vw,2.15rem)/1.24 Georgia,'Times New Roman',serif}
.risk-subtitle{max-width:70ch;margin:12px 0 0;color:var(--risk-muted);font-size:.92rem;line-height:1.7}
.overall-risk{display:grid;gap:4px;flex:none;min-width:150px;padding:10px 14px;border:1px solid #e2e8ed;border-radius:8px;background:#fbfcfd}
.overall-risk>span{color:#788696;font-size:.68rem;font-weight:650}
.overall-risk strong{font:600 1rem Georgia,'Times New Roman',serif}
.severity-badge strong,.overall-risk strong{color:var(--risk-navy)}
.severity-critical{color:#87544f!important}.overall-risk.severity-critical,.severity-badge.severity-critical{border-color:#eadbd8;background:#fbf6f5}
.severity-high{color:#896744!important}.overall-risk.severity-high,.severity-badge.severity-high{border-color:#eadfcf;background:#fcf9f3}
.severity-medium{color:#80683d!important}.overall-risk.severity-medium,.severity-badge.severity-medium{border-color:#e9dfcc;background:#fcfaf5}
.severity-low{color:#587161!important}.overall-risk.severity-low,.severity-badge.severity-low{border-color:#dce7dd;background:#f7faf7}
.severity-neutral{color:#60748a!important}
.risk-summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.summary-metric{display:grid;align-content:start;gap:8px;min-width:0;padding:16px;border:1px solid #e3e9ee;border-radius:10px;background:#fbfcfd}
.summary-metric.summary-overall{grid-column:1/-1;padding:clamp(18px,2.5vw,26px);border-color:#dce5ee;background:#f4f7fa}
.summary-metric>span{color:#788696;font-size:.67rem;font-weight:650;line-height:1.4}
.summary-metric>strong{color:var(--risk-navy);font:600 1.08rem Georgia,'Times New Roman',serif}
.summary-metric.summary-overall>strong{max-width:95ch;font-family:inherit;font-size:.94rem;font-weight:500;line-height:1.75;overflow-wrap:anywhere}
.risk-conclusion{margin:-20px 0 0;padding:14px 17px;border-left:2px solid #b69a6a;background:#faf8f2;color:#4d6071;font-size:.88rem;line-height:1.7}
.risk-priority{padding:22px clamp(16px,2.2vw,26px);border:1px solid #e6e1d7;border-left:3px solid #b08a4c;border-radius:9px;background:#fdfcf9}
.risk-section-heading{margin:0 0 16px}
.risk-kicker{margin:0 0 7px;color:#8a6a37;font-size:.61rem;font-weight:750;letter-spacing:.1em}
.risk-section-heading h3{margin:0;color:var(--risk-navy);font:600 1.34rem/1.32 Georgia,'Times New Roman',serif}
.risk-section-heading>p:last-child:not(.risk-kicker){max-width:800px;margin:7px 0 0;color:var(--risk-muted);font-size:.84rem;line-height:1.65}
.priority-list,.risk-list,.recommendation-list{margin:0;padding:0;list-style:none}
.priority-row,.risk-row,.recommendation-list>li{display:grid;grid-template-columns:38px minmax(0,1fr);gap:14px;min-width:0;padding:17px 0;border-top:1px solid #e7ecf0}
.priority-row:first-child,.risk-list>li:first-child,.recommendation-list>li:first-child{border-top:0;padding-top:2px}
.risk-number{padding-top:2px;color:#a17c43;font:600 .88rem Georgia,'Times New Roman',serif;letter-spacing:.03em}
.risk-copy{min-width:0;max-width:960px}
.risk-row-heading{display:flex;align-items:center;justify-content:space-between;gap:14px}
.risk-row-heading h4{margin:0;color:#263d55;font:600 1.02rem/1.45 Georgia,'Times New Roman',serif;overflow-wrap:break-word}
.severity-badge{flex:none;padding:3px 8px;border:1px solid #e2e8ed;border-radius:999px;background:#fafbfd;font-size:.66rem;font-weight:650;white-space:nowrap}
.risk-description,.risk-copy>p{margin:7px 0 0;color:#405469;font-size:.88rem;line-height:1.72;word-break:normal;overflow-wrap:break-word}
.risk-detail,.risk-mitigation{display:grid;grid-template-columns:95px minmax(0,1fr);gap:8px;margin-top:12px!important}
.risk-detail strong,.risk-mitigation strong{color:#718094;font-size:.69rem;font-weight:750;letter-spacing:.06em;text-transform:uppercase}
.risk-detail span,.risk-mitigation span{color:#405469;font-size:.83rem;line-height:1.65}
.risk-mitigation{padding-top:9px;border-top:1px solid #ece8df}
.risk-cross-reference{color:#708092!important;font-size:.78rem!important}
.risk-cross-reference a{color:#315c83;font-weight:650;text-decoration:underline;text-decoration-color:#b9cbd9;text-underline-offset:3px}
.risk-cross-reference a:hover{color:#17375e}
.risk-cross-reference a:focus-visible{outline:2px solid var(--risk-gold);outline-offset:2px}
.risk-list{border-top:1px solid #e4eaf0}
.risk-list .risk-row{border-color:#e7ecf0}
.risk-plan{padding-top:22px;border-top:1px solid var(--risk-line)}
.mitigation-group+.mitigation-group{margin-top:21px}
.mitigation-group>h4{margin:0 0 6px;color:#52697f;font-size:.72rem;font-weight:750;letter-spacing:.07em;text-transform:uppercase}
.recommendation-list>li{padding:11px 0}
.recommendation-list .risk-copy p{margin:0;color:#405469;font-size:.87rem;line-height:1.7}
.risk-empty{margin:0;padding:14px 16px;border-left:2px solid #d4c29e;background:#faf9f5;color:#637286;font-size:.86rem;line-height:1.65}
@media(max-width:1439px){.risk-priority{padding-inline:18px}}
@media(max-width:760px){.risk-editorial{gap:26px}.risk-heading-row{align-items:flex-start;flex-direction:column;gap:13px}.overall-risk{min-width:0}.risk-summary{grid-template-columns:repeat(2,minmax(0,1fr))}.priority-row,.risk-row,.recommendation-list>li{grid-template-columns:30px minmax(0,1fr);gap:10px}.risk-detail,.risk-mitigation{grid-template-columns:minmax(0,1fr);gap:3px}}
@media(max-width:440px){.risk-summary{grid-template-columns:1fr}.risk-row-heading{align-items:flex-start;flex-direction:column;gap:6px}}
</style>
