<template>
  <main class="court-evidence" aria-labelledby="court-evidence-title">
    <header class="evidence-page-header">
      <div>
        <p class="evidence-page-eyebrow"><span aria-hidden="true"></span> MYKE · NOVACOURT</p>
        <h2 id="court-evidence-title">Análisis probatorio</h2>
        <p>Evaluación de los documentos, medios probatorios, fortalezas, limitaciones y elementos pendientes de acreditación del caso.</p>
      </div>
      <span v-if="!loading && hasResult" class="evidence-status">Evidencia analizada</span>
    </header>

    <EvidenceView
      class="evidence-module"
      :evidence="evidenceForView"
      :analysis="analysisData"
      :fact-groups="factGroups"
      :facts="displayFacts"
      :issues="records(result.issues)"
      :evidence-links="evidenceLinksForView"
      :document-count="documentCount"
      :sources="sources"
      :citations="citations"
      :case-id="result.case_id"
      @select-source="selectedSource = $event"
    />

    <section v-if="weaknesses.length" class="weakness-section" aria-labelledby="weakness-title">
      <header class="section-heading">
        <p class="section-kicker">ASPECTOS POR CORROBORAR</p>
        <h3 id="weakness-title">Debilidades y vacíos probatorios</h3>
      </header>
      <ul class="editorial-list"><li v-for="(item, index) in weaknesses" :key="`weakness-${index}`"><span aria-hidden="true">{{ number(index + 1) }}</span><p>{{ item }}</p></li></ul>
    </section>

    <section v-if="digitalEvidence.length" class="digital-evidence-section" aria-labelledby="digital-evidence-title">
      <header class="section-heading">
        <p class="section-kicker">MEDIOS DOCUMENTALES</p>
        <h3 id="digital-evidence-title">Evidencia digital</h3>
      </header>
      <article v-for="(item, index) in digitalEvidence" :key="`digital-${index}`" class="digital-evidence-item">
        <h4 v-if="item.title">{{ item.title }}</h4>
        <div v-if="item.description" class="digital-evidence-note"><strong>Descripción</strong><MarkdownRenderer citation-numbers-only :content="item.description" :citations="citations" :sources="sources" :case-id="result.case_id" @select-citation="openCitation" /></div>
        <div v-if="item.value" class="digital-evidence-note"><strong>Valor probatorio</strong><MarkdownRenderer citation-numbers-only :content="item.value" :citations="citations" :sources="sources" :case-id="result.case_id" @select-citation="openCitation" /></div>
        <div v-if="item.limitations" class="digital-evidence-note limitation"><strong>Limitaciones</strong><MarkdownRenderer citation-numbers-only :content="item.limitations" :citations="citations" :sources="sources" :case-id="result.case_id" @select-citation="openCitation" /></div>
        <div v-if="item.sources.length" class="digital-source-list">
          <span>Fuente</span>
          <button v-for="source in item.sources" :key="source.source_id" type="button" class="source-action" @click="selectedSource = source">
            <span v-if="citationFor(source)" class="novacase-citation-badge">{{ citationFor(source).label.slice(1, -1) }}</span>
            <span>Ver documento{{ source.page_start ? ` · pág. ${source.page_start}` : '' }}</span><span aria-hidden="true">↗</span>
          </button>
        </div>
      </article>
    </section>

    <section v-if="pendingDocumentation.length" class="pending-section" aria-labelledby="pending-documentation-title">
      <header class="section-heading">
        <p class="section-kicker">ELEMENTOS POR COMPLETAR</p>
        <h3 id="pending-documentation-title">Documentación y actuaciones pendientes</h3>
      </header>
      <ul class="editorial-list"><li v-for="(item, index) in pendingDocumentation" :key="`pending-${index}`"><span aria-hidden="true">{{ number(index + 1) }}</span><p>{{ item }}</p></li></ul>
    </section>

    <section v-if="nextSteps.length" class="next-steps-section" aria-labelledby="next-steps-title">
      <header class="section-heading">
        <p class="section-kicker">ORIENTACIÓN DOCUMENTAL</p>
        <h3 id="next-steps-title">Próximos pasos probatorios</h3>
      </header>
      <ul class="next-steps-list"><li v-for="(item, index) in nextSteps" :key="`step-${index}`"><span aria-hidden="true">✓</span><p>{{ item }}</p></li></ul>
    </section>

    <SourceModal :source="selectedSource" :case-id="result.case_id" @close="selectedSource = null" />
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import EvidenceView from '@/components/novacase/EvidenceView.vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import SourceModal from '@/components/common/SourceModal.vue'
import { argumentCitationForSource, presentableText } from '@/utils/novacasePresentation.js'
import { normalizeSources } from '@/utils/sourceContract.js'

const props = defineProps({
  result: { type: Object, default: () => ({}) },
  simulation: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false }
})
const selectedSource = ref(null)
const result = computed(() => props.result || {})
const simulation = computed(() => props.simulation || {})
const hasResult = computed(() => Object.keys(result.value).length > 0)
const sources = computed(() => normalizeSources([
  ...records(result.value.sources),
  ...records(result.value.sources_used),
  ...records(result.value.evidence?.sources),
  ...records(result.value.research?.sources),
  ...records(simulation.value.sources)
], result.value.case_id))
const citations = computed(() => [...new Map([
  ...records(result.value.citations), ...records(simulation.value.citations)
].filter(item => item?.citation_id).map(item => [item.citation_id, item])).values()])
const evidenceData = computed(() => {
  const value = result.value.evidence || result.value.probative_analysis || result.value.evidence_analysis
  if (value && typeof value === 'object' && !Array.isArray(value)) return value
  return typeof value === 'string' && value.trim() ? { summary: value } : {}
})
const analysisData = computed(() => {
  for (const value of [result.value.analysis, result.value.evidence_analysis]) {
    if (value && typeof value === 'object' && !Array.isArray(value)) return value
  }
  return {}
})
const evidenceForView = computed(() => ({ ...evidenceData.value, missing_evidence: [], weaknesses: [], digitalEvidence: '' }))
const privateSources = computed(() => sources.value.filter(source => ['case', 'private_case'].includes(source.source_scope)))
const documentCount = computed(() => {
  if (Array.isArray(result.value.document_ids)) return new Set(result.value.document_ids).size
  return new Set(privateSources.value.map(source => source.document_id || source.metadata?.document_id || source.source_id)).size
})
const privateSourceIds = computed(() => new Set(privateSources.value.map(source => source.source_id)))
const digitalEvidence = computed(() => records(evidenceData.value.digitalEvidence).map(value => {
  const item = value && typeof value === 'object' ? value : { description: value }
  const ids = new Set([...records(item.source_ids), item.source_id].filter(Boolean))
  return {
    title: textOf(item.title || item.name || item.label),
    description: textOf(item.description || item.text || item.content),
    value: textOf(item.probative_value || item.value || item.what_it_shows),
    limitations: textOf(item.limitations || item.weaknesses || item.notes),
    sources: privateSources.value.filter(source => ids.has(source.source_id))
  }
}).filter(item => item.title || item.description || item.value || item.limitations || item.sources.length))
const evidenceLinksForView = computed(() => records(evidenceData.value.evidence_links || result.value.evidence_links).map(link => ({
  ...link,
  source_ids: records(link.source_ids).filter(id => privateSourceIds.value.has(id))
})))
const displayFacts = computed(() => records(result.value.facts).map(fact => {
  if (['alleged', 'disputed'].includes(fact?.status) && typeof fact.text === 'string') {
    return { ...fact, text: `Según lo manifestado; pendiente de corroboración: ${fact.text}` }
  }
  return fact
}))
const factGroups = computed(() => {
  const facts = displayFacts.value
  const supported = facts.filter(fact => fact.status === 'supported' && records(fact.source_ids).some(id => privateSourceIds.value.has(id)))
  const alleged = facts.filter(fact => ['alleged', 'disputed'].includes(fact.status) ||
    (fact.status === 'supported' && !records(fact.source_ids).some(id => privateSourceIds.value.has(id))))
  const pending = facts.filter(fact => !['supported', 'alleged', 'disputed'].includes(fact.status))
  return [{ key: 'supported', facts: supported }, { key: 'alleged', facts: alleged }, { key: 'pending', facts: pending }]
})
const pendingDocumentation = computed(() => uniqueTexts([
  ...records(evidenceData.value.missing_evidence),
  ...records(evidenceData.value.recommended_documents),
  ...records(evidenceData.value.recommended_evidence)
]))
const weaknesses = computed(() => uniqueTexts(evidenceData.value.weaknesses))
const nextSteps = computed(() => {
  const pending = pendingDocumentation.value.map(normalizeText)
  return uniqueTexts(records(evidenceData.value.recommendations)).filter(item => {
    const normalized = normalizeText(item)
    return !pending.some(existing => existing === normalized || existing.includes(normalized) || normalized.includes(existing))
  })
})
function records(value) { return Array.isArray(value) ? value : value == null || value === '' ? [] : [value] }
function textOf(value) {
  if (typeof value === 'string') return presentableText(value).trim()
  if (value && typeof value === 'object') return textOf(value.text || value.description || value.content || value.summary || value.title || value.name)
  return ''
}
function uniqueTexts(values) {
  const seen = new Set()
  return values.map(textOf).filter(Boolean).filter(value => {
    const key = normalizeText(value)
    if (!key || seen.has(key)) return false
    seen.add(key)
    return true
  })
}
function normalizeText(value) { return value.toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim() }
function number(value) { return String(value).padStart(2, '0') }
function citationFor(source) { return argumentCitationForSource(source, citations.value, sources.value, result.value.case_id) }
function openCitation(citation) {
  const source = sources.value.find(item => item.source_id === citation?.source_id)
  if (source) selectedSource.value = source
}
</script>

<style scoped>
.court-evidence{display:grid;gap:26px;min-width:0;width:100%;color:#34485d}
.evidence-page-header{display:flex;align-items:flex-start;justify-content:space-between;gap:22px;padding:0 0 20px;border-bottom:1px solid #dce5ee}
.evidence-page-header>div{max-width:900px;min-width:0}
.evidence-page-eyebrow,.section-kicker{display:flex;align-items:center;gap:8px;margin:0 0 9px;color:#92713c;font-size:.66rem;font-weight:750;letter-spacing:.12em}
.evidence-page-eyebrow span{width:20px;height:1px;background:#b08a4c}
.evidence-page-header h2{margin:0;color:#17375e;font:600 clamp(1.7rem,2.5vw,2.15rem)/1.25 Georgia,'Times New Roman',serif}
.evidence-page-header p:not(.evidence-page-eyebrow){max-width:78ch;margin:8px 0 0;color:#69798a;font-size:.91rem;line-height:1.65}
.evidence-status{flex:none;margin-top:3px;padding:7px 11px;border:1px solid #d9eade;border-radius:999px;background:#f1f8f3;color:#3b6d53;font-size:.72rem;font-weight:650}
.section-heading{margin:0 0 14px}.section-kicker{margin-bottom:6px;font-size:.6rem}.section-heading h3{margin:0;color:#17375e;font:600 1.2rem/1.4 Georgia,'Times New Roman',serif}
.pending-section,.next-steps-section,.weakness-section{min-width:0;padding-top:20px;border-top:1px solid #dce5ee}
.digital-evidence-section{min-width:0;padding-top:20px;border-top:1px solid #dce5ee}.digital-evidence-item{display:grid;gap:13px;padding:16px 0;border-top:1px solid #e7ecf0}.digital-evidence-item h4{margin:0;color:#17375e;font-size:1rem;font-weight:700}.digital-evidence-note{display:grid;grid-template-columns:minmax(125px,180px) minmax(0,1fr);gap:14px;align-items:start;color:#405469;font-size:.88rem;line-height:1.65}.digital-evidence-note>strong,.digital-source-list>span{color:#6a7c8d;font-size:.7rem;font-weight:750;letter-spacing:.07em;text-transform:uppercase}.digital-evidence-note :deep(p){margin:0}.digital-evidence-note.limitation{padding-left:12px;border-left:2px solid #e6d4b6}.digital-source-list{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.digital-source-list .source-action{display:inline-flex;align-items:center;gap:7px;width:max-content;max-width:100%;padding:5px 0;border:0;background:none;color:#365d7c;font-size:.82rem;text-align:left;cursor:pointer}.digital-source-list .source-action:hover{color:#17375e;text-decoration:underline}.digital-source-list .source-action:focus-visible{outline:2px solid #a98551;outline-offset:3px;border-radius:4px}.digital-source-list :deep(.novacase-citation-badge){display:inline-flex;flex:none;align-items:center;justify-content:center;width:auto;min-width:22px;height:22px;padding:0 6px;border:0;border-radius:6px;background:#102b4c;color:#fff;font-size:.72rem;font-weight:750;line-height:1;white-space:nowrap}
.editorial-list,.next-steps-list{display:grid;margin:0;padding:0;border-top:1px solid #e7ecf0;list-style:none}
.editorial-list li,.next-steps-list li{display:grid;grid-template-columns:32px minmax(0,1fr);gap:10px;padding:11px 0;border-bottom:1px solid #e7ecf0}
.editorial-list li>span{padding-top:1px;color:#a17c43;font:600 .84rem Georgia,serif}.editorial-list p,.next-steps-list p{min-width:0;margin:0;color:#405469;font-size:.88rem;line-height:1.65;overflow-wrap:break-word;word-break:normal}
.next-steps-list li>span{color:#68816d;font-size:.86rem}
.court-evidence :deep(.evidence-editorial){max-width:none;gap:24px}
.court-evidence :deep(.evidence-header){display:none}
.court-evidence :deep(.evidence-context dl){grid-template-columns:repeat(4,minmax(0,1fr))}
.court-evidence :deep(.evidence-context dl>div:nth-child(5)){display:none}
.court-evidence :deep(.evidence-overview-grid){grid-template-columns:minmax(0,1fr);gap:24px}
.court-evidence :deep(.documents-empty){display:none}
.court-evidence :deep(.other-evidence-list){grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr))}
.court-evidence :deep(.other-evidence-list li:has(> strong)){display:none}
@media(max-width:1080px){.court-evidence :deep(.evidence-context dl){grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:680px){.court-evidence{gap:21px}.evidence-page-header{flex-direction:column;gap:13px}.court-evidence :deep(.evidence-context dl){grid-template-columns:repeat(2,minmax(0,1fr))}.editorial-list li,.next-steps-list li{grid-template-columns:26px minmax(0,1fr);gap:8px}}
@media(max-width:680px){.digital-evidence-note{grid-template-columns:minmax(0,1fr);gap:4px}}
@media(max-width:420px){.court-evidence :deep(.evidence-context dl){grid-template-columns:minmax(0,1fr)}}
</style>
