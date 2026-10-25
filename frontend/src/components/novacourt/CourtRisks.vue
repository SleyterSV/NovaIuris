<template>
  <main class="court-risks" aria-labelledby="court-risks-title">
    <header class="risk-page-header">
      <div>
        <p class="risk-eyebrow"><span aria-hidden="true"></span> MYKE · NOVACOURT</p>
        <h2 id="court-risks-title">Evaluación de riesgos</h2>
        <p>Identificación y valoración de las contingencias procesales, probatorias y jurídicas que pueden afectar la viabilidad del caso.</p>
      </div>
      <span v-if="!loading && hasData" class="completed-badge"><span aria-hidden="true">✓</span> Evaluación completada</span>
    </header>

    <div v-if="loading" class="risk-loading" role="status"><span class="loading-mark" aria-hidden="true"></span><div><strong>Evaluando las contingencias del caso</strong><p>NovaCourt está organizando los factores procesales, probatorios y jurídicos.</p></div></div>

    <template v-else-if="hasData">
      <section class="risk-overview" aria-labelledby="risk-overview-title">
        <div class="overall-panel" :class="levelTone">
          <p class="section-kicker">PANORAMA DE RIESGO</p>
          <h3 id="risk-overview-title">Nivel general</h3>
          <strong class="overall-level">{{ overallLevel || 'No determinado' }}</strong>
          <p v-if="overviewText" class="overall-explanation">{{ overviewText }}</p>
        </div>
        <div class="factor-panel">
          <span class="factor-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4 7v5c0 5 3.4 8 8 9 4.6-1 8-4 8-9V7z"/><path d="M12 8v5m0 3h.01"/></svg></span>
          <div><strong>{{ factorCount }} {{ factorCount === 1 ? 'factor identificado' : 'factores identificados' }}</strong><p>Factores considerados en la evaluación del caso.</p></div>
        </div>
      </section>

      <section v-if="priorities.length" class="priority-section" aria-labelledby="priority-title">
        <header class="section-heading"><p class="section-kicker">ATENCIÓN PRIORITARIA</p><h3 id="priority-title">Riesgos prioritarios</h3></header>
        <ol class="editorial-risk-list">
          <li v-for="(risk, index) in priorities" :key="risk.key" class="priority-row">
            <span class="risk-number" aria-hidden="true">{{ number(index + 1) }}</span>
            <div class="risk-copy"><div class="risk-row-heading"><h4>{{ risk.title || 'Contingencia identificada' }}</h4><span v-if="risk.severity" class="severity-chip" :class="toneFor(risk.severity)">{{ risk.severity }}</span></div>
              <p v-if="risk.text" class="risk-description">{{ risk.text }}</p>
              <p v-if="risk.impact" class="risk-detail"><strong>Impacto</strong><span>{{ risk.impact }}</span></p>
              <p v-if="risk.mitigation" class="risk-mitigation"><strong>Mitigación</strong><span>{{ risk.mitigation }}</span></p>
            </div>
          </li>
        </ol>
      </section>

      <section v-if="riskCategories.some(category => category.items.length)" class="matrix-section" aria-labelledby="matrix-title">
        <header class="section-heading"><p class="section-kicker">LECTURA POR MATERIA</p><h3 id="matrix-title">Matriz de riesgos</h3></header>
        <div class="risk-matrix">
          <article v-for="category in riskCategories.filter(item => item.items.length)" :key="category.key" class="category-panel" :class="`category-${category.key}`">
            <header class="category-heading"><span class="category-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path :d="category.icon" /></svg></span><div><h4>{{ category.title }}</h4><span>{{ category.items.length }} {{ category.items.length === 1 ? 'riesgo' : 'riesgos' }}</span></div></header>
            <ol class="category-list"><li v-for="risk in category.items.slice(0, 4)" :key="risk.key"><strong v-if="risk.title">{{ risk.title }}</strong><p>{{ risk.text || risk.title }}</p><p v-if="risk.mitigation" class="category-mitigation"><b>Mitigación</b> {{ risk.mitigation }}</p></li></ol>
            <details v-if="category.items.length > 4" class="more-risks"><summary>Ver todos ({{ category.items.length }})</summary><ol class="category-list"><li v-for="risk in category.items.slice(4)" :key="risk.key"><strong v-if="risk.title">{{ risk.title }}</strong><p>{{ risk.text || risk.title }}</p><p v-if="risk.mitigation" class="category-mitigation"><b>Mitigación</b> {{ risk.mitigation }}</p></li></ol></details>
          </article>
        </div>
      </section>

      <section v-if="observations.length" class="observations-section" aria-labelledby="observations-title">
        <header class="section-heading"><p class="section-kicker">REVISIÓN DEL CASO</p><h3 id="observations-title">Puntos de control judicial</h3><p>Aspectos que previsiblemente requerirán especial acreditación o argumentación.</p></header>
        <ul class="observations-list"><li v-for="(item, index) in observations" :key="`observation-${index}`"><span aria-hidden="true">✓</span><p>{{ item }}</p></li></ul>
      </section>

      <section v-if="strengths.length || weaknesses.length" class="comparison-section" aria-label="Fortalezas y debilidades del caso">
        <article v-if="strengths.length" class="comparison-panel strengths-panel"><header><span aria-hidden="true">✓</span><h3>Fortalezas del caso</h3></header><ul><li v-for="(item, index) in strengths" :key="`strength-${index}`">{{ item }}</li></ul></article>
        <article v-if="weaknesses.length" class="comparison-panel weaknesses-panel"><header><span aria-hidden="true">!</span><h3>Debilidades del caso</h3></header><ul><li v-for="(item, index) in weaknesses" :key="`weakness-${index}`">{{ item }}</li></ul></article>
      </section>

      <section v-if="missingDocumentation.length" class="missing-section" aria-labelledby="missing-title">
        <header class="section-heading"><p class="section-kicker">SOPORTE POR COMPLETAR</p><h3 id="missing-title">Documentación crítica pendiente</h3></header>
        <ol class="compact-list"><li v-for="(item, index) in missingDocumentation" :key="`missing-${index}`"><span aria-hidden="true">{{ number(index + 1) }}</span><p>{{ item }}</p></li></ol>
      </section>

      <section v-if="recommendations.length" class="mitigation-section" aria-labelledby="mitigation-title">
        <header class="section-heading"><p class="section-kicker">ACCIONES RECOMENDADAS</p><h3 id="mitigation-title">Plan de mitigación</h3></header>
        <ol class="compact-list"><li v-for="(item, index) in recommendations" :key="`recommendation-${index}`"><span aria-hidden="true">{{ number(index + 1) }}</span><p>{{ item }}</p></li></ol>
      </section>
    </template>

    <p v-else class="risk-empty" role="status">No se identificó información suficiente para evaluar riesgos.</p>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { presentableText } from '@/utils/novacasePresentation.js'

const props = defineProps({ risk: { type: [Object, String, Array], default: () => ({}) }, loading: { type: Boolean, default: false } })
const risk = computed(() => typeof props.risk === 'string' ? { summary_text: props.risk } : (props.risk && typeof props.risk === 'object' && !Array.isArray(props.risk) ? props.risk : {}))
const clean = value => typeof value === 'string' ? presentableText(value).replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, '').replace(/\s{2,}/g, ' ').trim() : ''
const records = value => Array.isArray(value) ? value : value == null || value === '' ? [] : [value]
const itemText = value => {
  if (typeof value === 'string') return clean(value)
  if (!value || typeof value !== 'object') return ''
  return clean(value.description || value.risk || value.text || value.detail || value.action || value.recommendation || value.name || value.title || '')
}
const identity = value => clean(value).toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim()
function uniqueItems(values) {
  const seen = new Set()
  return values.map(itemText).filter(text => {
    const key = identity(text)
    if (!key || seen.has(key)) return false
    seen.add(key)
    return true
  })
}
function normalizeRisk(value, index, category) {
  const item = value && typeof value === 'object' && !Array.isArray(value) ? value : { text: value }
  const text = clean(item.risk || item.description || item.text || item.detail || '')
  const title = clean(item.title || item.name || '')
  const severity = severityLabel(item.severity || item.level || item.risk_level || item.priority)
  return { key: `${category}-${index}`, title, text, severity, impact: clean(item.impact), mitigation: clean(item.mitigation || item.recommendation || item.recommended_action) }
}
function severityLabel(value) {
  const key = clean(value).toLocaleLowerCase()
  return ({ critical: 'Crítico', high: 'Alto', alta: 'Alto', alto: 'Alto', medium: 'Medio', media: 'Medio', medio: 'Medio', low: 'Bajo', baja: 'Bajo', bajo: 'Bajo', severe: 'Grave', grave: 'Grave' })[key] || (['Crítico', 'Alto', 'Medio', 'Bajo', 'Grave'].includes(value) ? value : '')
}
const overallLevel = computed(() => {
  const raw = clean(risk.value.risk_level || risk.value.overall_level || '')
  const key = raw.toLocaleLowerCase()
  if (/\b(low|bajo|baja)\b/.test(key)) return 'Bajo'
  if (/\b(medium|medio|media)\b/.test(key)) return 'Medio'
  if (/\b(high|alto|alta)\b/.test(key)) return 'Alto'
  if (/\b(critical|crítico|crítica)\b/.test(key)) return 'Crítico'
  return ''
})
const levelTone = computed(() => ({ Bajo: 'tone-low', Medio: 'tone-medium', Alto: 'tone-high', Crítico: 'tone-high' })[overallLevel.value] || 'tone-neutral')
const overviewText = computed(() => uniqueItems([risk.value.executive_summary, risk.value.summary_text, risk.value.overview, risk.value.conclusion])[0] || '')
const categoryDefinitions = [
  { key: 'procedural', title: 'Riesgos procesales', fields: ['procedural', 'procedural_risks'], icon: 'M12 8v5l3 2m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z' },
  { key: 'evidentiary', title: 'Riesgos probatorios', fields: ['evidentiary', 'evidentiary_risks'], icon: 'M6 3h9l4 4v14H6zM14 3v5h5M9 13h7m-7 4h7' },
  { key: 'legal', title: 'Riesgos jurídicos', fields: ['legal', 'legal_risks'], icon: 'M12 3 4 7v5c0 5 3.4 8 8 9 4.6-1 8-4 8-9V7zm-5 6h10m-8 3h6' }
]
const riskCategories = computed(() => categoryDefinitions.map(category => {
  const all = category.fields.flatMap(field => records(risk.value[field]))
  const seen = new Set()
  const priorityKeys = new Set(priorities.value.map(item => [identity(item.title), identity(item.text)].filter(Boolean).join('|')))
  const items = all.map((item, index) => normalizeRisk(item, index, category.key)).filter(item => {
    const id = [identity(item.title), identity(item.text)].filter(Boolean).join('|')
    if (!id || seen.has(id) || priorityKeys.has(id)) return false
    seen.add(id)
    return true
  })
  return { ...category, items }
}))
const priorities = computed(() => {
  const all = [...records(risk.value.critical_risks), ...records(risk.value.strategic)]
  const seen = new Set()
  return all.map((item, index) => normalizeRisk(item, index, 'priority')).filter(item => {
    const id = [identity(item.title), identity(item.text)].filter(Boolean).join('|')
    if (!id || seen.has(id)) return false
    seen.add(id)
    return true
  })
})
const factorCount = computed(() => {
  const explicit = records(risk.value.factors)
  if (explicit.length) return uniqueItems(explicit).length
  return priorities.value.length + riskCategories.value.reduce((sum, category) => sum + category.items.length, 0)
})
const observations = computed(() => uniqueItems(risk.value.judge_observations || risk.value.judicial_observations))
const strengths = computed(() => uniqueItems(risk.value.strengths))
const weaknesses = computed(() => uniqueItems(risk.value.weaknesses))
const missingDocumentation = computed(() => uniqueItems([
  ...records(risk.value.missing_documents), ...records(risk.value.missing_evidence), ...records(risk.value.missing_information)
]))
const recommendations = computed(() => uniqueItems(risk.value.recommendations))
const hasData = computed(() => Boolean(overallLevel.value || overviewText.value || priorities.value.length || riskCategories.value.some(category => category.items.length) || observations.value.length || strengths.value.length || weaknesses.value.length || missingDocumentation.value.length || recommendations.value.length))
function number(value) { return String(value).padStart(2, '0') }
function toneFor(value) { return ({ Bajo: 'tone-low', Medio: 'tone-medium', Alto: 'tone-high', Crítico: 'tone-high', Grave: 'tone-high' })[value] || 'tone-neutral' }
</script>

<style scoped>
.court-risks{--navy:#17375e;--muted:#667789;--line:#dce5ee;--gold:#a98551;display:grid;gap:clamp(23px,2.8vw,34px);width:100%;min-width:0;color:#34485d}
.risk-page-header{display:flex;align-items:flex-start;justify-content:space-between;gap:22px;padding:0 0 20px;border-bottom:1px solid var(--line)}.risk-page-header>div{max-width:900px;min-width:0}.risk-eyebrow,.section-kicker{display:flex;align-items:center;gap:8px;margin:0 0 9px;color:#92713c;font-size:.66rem;font-weight:750;letter-spacing:.12em}.risk-eyebrow span{width:20px;height:1px;background:#b08a4c}.risk-page-header h2{margin:0;color:var(--navy);font:600 clamp(1.7rem,2.5vw,2.15rem)/1.25 Georgia,'Times New Roman',serif}.risk-page-header p:not(.risk-eyebrow){max-width:78ch;margin:8px 0 0;color:var(--muted);font-size:.91rem;line-height:1.65}.completed-badge{display:inline-flex;align-items:center;gap:7px;flex:none;margin-top:4px;padding:7px 11px;border:1px solid #d9eade;border-radius:999px;background:#f1f8f3;color:#3b6d53;font-size:.72rem;font-weight:650}.completed-badge span{font-weight:800}
.section-heading{margin:0 0 14px}.section-kicker{margin-bottom:6px;font-size:.61rem}.section-heading h3{margin:0;color:var(--navy);font:600 1.25rem/1.35 Georgia,'Times New Roman',serif}.section-heading>p:last-child:not(.section-kicker){max-width:76ch;margin:7px 0 0;color:var(--muted);font-size:.85rem;line-height:1.6}
.risk-overview{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(240px,.8fr);gap:14px}.overall-panel,.factor-panel{min-width:0;border:1px solid var(--line);border-radius:12px;background:#fff}.overall-panel{padding:clamp(18px,2.3vw,26px);border-left:3px solid #b08a4c}.overall-panel.tone-low{border-left-color:#7b9a83;background:#f7faf7}.overall-panel.tone-medium{border-left-color:#bc9b62;background:#fbf9f4}.overall-panel.tone-high{border-left-color:#bd837c;background:#fcf7f6}.overall-panel h3{margin:0;color:#69798a;font-size:.78rem;font-weight:650}.overall-level{display:block;margin-top:6px;color:var(--navy);font:600 clamp(1.7rem,3vw,2.35rem)/1.15 Georgia,'Times New Roman',serif}.overall-explanation{max-width:74ch;margin:10px 0 0;color:#526579;font-size:.87rem;line-height:1.65}.factor-panel{display:flex;align-items:center;gap:14px;padding:20px;background:#f7f9fb}.factor-icon,.category-icon{display:grid;place-items:center;flex:none;width:42px;height:42px;border:1px solid #dde6ed;border-radius:11px;background:#edf3f7;color:#456681}.factor-icon svg,.category-icon svg{width:22px;height:22px}.factor-panel strong{color:var(--navy);font:600 1rem Georgia,'Times New Roman',serif}.factor-panel p{margin:6px 0 0;color:var(--muted);font-size:.8rem;line-height:1.5}
.priority-section,.matrix-section,.observations-section,.missing-section,.mitigation-section{min-width:0;padding-top:21px;border-top:1px solid var(--line)}.editorial-risk-list,.category-list,.compact-list,.observations-list,.comparison-panel ul{margin:0;padding:0;list-style:none}.priority-row{display:grid;grid-template-columns:38px minmax(0,1fr);gap:14px;padding:17px 0;border-top:1px solid #e7ecf0}.priority-row:first-child{border-top:0;padding-top:0}.risk-number,.compact-list li>span{color:#a17c43;font:600 .84rem Georgia,serif}.risk-copy{min-width:0;max-width:1000px}.risk-row-heading{display:flex;align-items:center;justify-content:space-between;gap:14px}.risk-row-heading h4{margin:0;color:#263d55;font:600 1rem/1.45 Georgia,'Times New Roman',serif;overflow-wrap:break-word}.severity-chip{flex:none;padding:3px 8px;border:1px solid #e2e8ed;border-radius:999px;background:#fafbfd;font-size:.66rem;font-weight:650}.risk-description,.risk-detail,.risk-mitigation{margin:7px 0 0;color:#405469;font-size:.87rem;line-height:1.7;overflow-wrap:break-word;word-break:normal}.risk-detail,.risk-mitigation{display:grid;grid-template-columns:95px minmax(0,1fr);gap:8px;margin-top:12px}.risk-detail strong,.risk-mitigation strong{color:#718094;font-size:.68rem;font-weight:750;letter-spacing:.06em;text-transform:uppercase}.risk-mitigation{padding-top:9px;border-top:1px solid #ece8df}
.risk-matrix{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.category-panel{min-width:0;padding:17px 18px;border:1px solid #e2e8ed;border-radius:12px;background:#fff}.category-heading{display:flex;align-items:center;gap:11px;padding-bottom:13px;border-bottom:1px solid #e7ecf0}.category-icon{width:36px;height:36px;border-radius:10px}.category-procedural .category-icon{background:#f7f2e8;color:#9a7846}.category-evidentiary .category-icon{background:#edf4f8;color:#4d708a}.category-legal .category-icon{background:#f1eff8;color:#71678e}.category-heading h4{margin:0;color:var(--navy);font:600 .98rem Georgia,'Times New Roman',serif}.category-heading div>span{display:block;margin-top:4px;color:var(--muted);font-size:.7rem}.category-list>li{padding:12px 0;border-bottom:1px solid #edf0f2}.category-list>li:last-child{border-bottom:0}.category-list strong{color:#33495f;font-size:.82rem}.category-list p{margin:4px 0 0;color:#53677b;font-size:.8rem;line-height:1.58;overflow-wrap:break-word}.category-list .category-mitigation{padding-top:5px;color:#49654f}.category-mitigation b{font-size:.67rem;text-transform:uppercase;letter-spacing:.04em}.more-risks{padding-top:10px;border-top:1px solid #e7ecf0}.more-risks summary{color:#315c83;font-size:.78rem;font-weight:650;cursor:pointer}.more-risks summary:focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:3px}
.observations-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 24px;border-top:1px solid #e7ecf0}.observations-list li{display:grid;grid-template-columns:22px minmax(0,1fr);gap:9px;padding:11px 0;border-bottom:1px solid #e7ecf0}.observations-list li>span{display:grid;place-items:center;width:19px;height:19px;border-radius:50%;background:#eff5f1;color:#63806c;font-size:.7rem}.observations-list p,.compact-list p{min-width:0;margin:0;color:#405469;font-size:.85rem;line-height:1.62;overflow-wrap:break-word}.comparison-section{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.comparison-panel{min-width:0;padding:18px 20px;border:1px solid;border-radius:12px}.strengths-panel{border-color:#dce8df;background:#f6faf7}.weaknesses-panel{border-color:#eadfcf;background:#fcf9f4}.comparison-panel header{display:flex;align-items:center;gap:9px}.comparison-panel header span{display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:#e5efe8;color:#54735d;font-size:.78rem;font-weight:800}.weaknesses-panel header span{background:#f2eadd;color:#99743f}.comparison-panel h3{margin:0;color:var(--navy);font:600 1.08rem Georgia,'Times New Roman',serif}.comparison-panel ul{display:grid;gap:8px;margin-top:12px}.comparison-panel li{padding-top:8px;border-top:1px solid #e4eae5;color:#405469;font-size:.84rem;line-height:1.62;overflow-wrap:break-word}.compact-list{border-top:1px solid #e7ecf0}.compact-list li{display:grid;grid-template-columns:30px minmax(0,1fr);gap:9px;padding:11px 0;border-bottom:1px solid #e7ecf0}.risk-loading{display:flex;align-items:center;gap:15px;padding:22px;border:1px solid var(--line);border-radius:12px;background:#f8fafb}.risk-loading strong{color:var(--navy)}.risk-loading p{margin:5px 0 0;color:var(--muted);font-size:.85rem;line-height:1.55}.loading-mark{width:30px;height:30px;flex:none;border:3px solid #e7dfd0;border-top-color:#a98551;border-radius:50%;animation:spin 1s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}.risk-empty{margin:0;padding:15px 17px;border-left:2px solid #d4c29e;background:#faf9f5;color:#637286;font-size:.87rem;line-height:1.65}
.tone-high.severity-chip{border-color:#eadbd8;background:#fbf6f5;color:#87544f}.tone-medium.severity-chip{border-color:#e9dfcc;background:#fcfaf5;color:#80683d}.tone-low.severity-chip{border-color:#dce7dd;background:#f7faf7;color:#587161}
@media(max-width:1080px){.risk-matrix{grid-template-columns:repeat(2,minmax(0,1fr))}.risk-matrix>.category-panel:last-child:nth-child(odd){grid-column:1/-1}}
@media(max-width:760px){.court-risks{gap:24px}.risk-page-header{flex-direction:column;gap:13px}.risk-overview{grid-template-columns:minmax(0,1fr)}.risk-matrix{grid-template-columns:minmax(0,1fr)}.risk-matrix>.category-panel:last-child:nth-child(odd){grid-column:auto}.observations-list,.comparison-section{grid-template-columns:minmax(0,1fr)}.priority-row{grid-template-columns:30px minmax(0,1fr);gap:10px}.risk-detail,.risk-mitigation{grid-template-columns:minmax(0,1fr);gap:3px}}
@media(max-width:440px){.category-panel,.comparison-panel{padding:15px}.risk-row-heading{align-items:flex-start;flex-direction:column;gap:6px}}
</style>
