<template>
  <main class="court-arguments" aria-labelledby="court-arguments-title">
    <header class="arguments-header">
      <p class="arguments-eyebrow"><span aria-hidden="true"></span> MYKE · NOVACOURT</p>
      <h2 id="court-arguments-title">Argumentos jurídicos</h2>
      <p>Posiciones, fundamentos y fuentes relevantes identificadas para la simulación del caso.</p>
    </header>

    <p v-if="loading" class="arguments-state" role="status">Organizando los argumentos del caso…</p>

    <template v-else-if="sections.length">
      <section v-for="section in sections" :key="section.key" class="argument-section" :aria-labelledby="`argument-group-${section.key}`">
        <header class="group-heading">
          <p class="group-eyebrow">ESTRATEGIA ARGUMENTATIVA</p>
          <h3 :id="`argument-group-${section.key}`">{{ section.label }}</h3>
        </header>
        <ol class="argument-list">
          <li v-for="(entry, index) in section.items" :key="entry.key" class="argument-entry">
            <span class="argument-number" aria-hidden="true">{{ formatNumber(index + 1) }}</span>
            <article class="argument-content">
              <h4 v-if="entry.title">{{ entry.title }}</h4>
              <MarkdownRenderer v-if="entry.body" class="argument-prose" :content="entry.body" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />

              <section v-if="entry.foundation.length" class="argument-subsection">
                <h5>Fundamento jurídico</h5>
                <MarkdownRenderer v-for="(text, index) in entry.foundation" :key="`${entry.key}-basis-${index}`" :content="text" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
              </section>

              <section v-if="entry.facts.length" class="argument-subsection argument-facts">
                <h5>Hechos relacionados</h5>
                <ul><li v-for="(fact, index) in entry.facts" :key="`${entry.key}-fact-${index}`"><span aria-hidden="true">✓</span><MarkdownRenderer :content="fact" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></li></ul>
              </section>

              <section v-if="entry.counterargument" class="linked-position linked-position--opposed">
                <h5>Posición contraria</h5>
                <MarkdownRenderer :content="entry.counterargument" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
              </section>
              <section v-if="entry.response" class="linked-position linked-position--response">
                <h5>Respuesta / réplica</h5>
                <MarkdownRenderer :content="entry.response" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
              </section>

              <div v-if="entry.publicSources.length" class="argument-sources">
                <h5>Fuentes jurídicas</h5>
                <ul><li v-for="source in entry.publicSources" :key="source.source_id">
                  <div class="source-main">
                    <button v-if="citationLabel(source)" type="button" class="source-citation novacase-citation-badge" :aria-label="`Ver fuente ${citationLabel(source).slice(1, -1)}`" @click="selectSource(source)">{{ citationLabel(source).slice(1, -1) }}</button>
                    <span class="source-detail"><strong>{{ sourceTitle(source) }}</strong><small>{{ sourceDetails(source) }}</small></span>
                  </div>
                  <button type="button" class="source-open" @click="selectSource(source)">Ver fuente <span aria-hidden="true">↗</span></button>
                </li></ul>
              </div>

              <div v-if="entry.privateSources.length" class="argument-sources">
                <h5>Documentos del caso</h5>
                <ul><li v-for="source in entry.privateSources" :key="source.source_id">
                  <div class="source-main">
                    <button v-if="citationLabel(source)" type="button" class="source-citation novacase-citation-badge" :aria-label="`Ver documento ${citationLabel(source).slice(1, -1)}`" @click="selectSource(source)">{{ citationLabel(source).slice(1, -1) }}</button>
                    <span class="source-detail"><strong>{{ sourceTitle(source) }}</strong><small>{{ privateSourceDetails(source) }}</small></span>
                  </div>
                  <button type="button" class="source-open" @click="selectSource(source)">Ver documento <span aria-hidden="true">↗</span></button>
                </li></ul>
              </div>
              <p v-if="entry.needsVerification" class="verification-note">El fundamento requiere verificación documental o jurídica adicional.</p>
            </article>
          </li>
        </ol>
      </section>
    </template>

    <section v-else-if="content" class="argument-fallback" aria-label="Argumentos del análisis">
      <MarkdownRenderer :content="content" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
    </section>
    <p v-else class="arguments-state" role="status">{{ status || 'No se identificaron argumentos con la información disponible.' }}</p>

    <SourceModal :source="selectedSource" :case-id="caseId" @close="selectedSource = null" />
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import SourceModal from '@/components/common/SourceModal.vue'
import { argumentCitationForSource, argumentNeedsVerification, presentableText, relatedFactTexts, sourceUnitLabel, verifiedArgumentSources } from '@/utils/novacasePresentation.js'
import { normalizeSource, normalizeSources, resolveCitations } from '@/utils/sourceContract.js'

const props = defineProps({
  content: { type: [String, Object, Array], default: '' },
  argumentData: { type: Object, default: () => ({}) },
  facts: { type: Array, default: () => [] },
  result: { type: Object, default: () => ({}) },
  simulation: { type: Object, default: () => ({}) },
  caseId: { type: String, default: null },
  loading: { type: Boolean, default: false },
  status: { type: String, default: '' }
})

const selectedSource = ref(null)
const argumentGroups = [
  ['main_arguments', 'Argumentos principales'],
  ['secondary_arguments', 'Argumentos complementarios'],
  ['constitutional_arguments', 'Argumentos constitucionales'],
  ['procedural_arguments', 'Argumentos procesales'],
  ['normative_arguments', 'Argumentos normativos']
]
const rawSources = computed(() => [
  ...(Array.isArray(props.result.sources) ? props.result.sources : []),
  ...(Array.isArray(props.result.sources_used) ? props.result.sources_used : []),
  ...(Array.isArray(props.result.research?.sources) ? props.result.research.sources : []),
  ...(Array.isArray(props.simulation.sources) ? props.simulation.sources : [])
])
const sources = computed(() => normalizeSources(rawSources.value, props.caseId))
const citations = computed(() => {
  const records = [
    ...(Array.isArray(props.result.citations) ? props.result.citations : []),
    ...(Array.isArray(props.simulation.citations) ? props.simulation.citations : [])
  ]
  const unique = [...new Map(records.filter(item => item?.citation_id).map(item => [item.citation_id, item])).values()]
  return resolveCitations(unique, sources.value, props.caseId).citations
})
const supportedFacts = computed(() => props.facts.flatMap(fact => {
  if (fact?.status === 'supported' && fact.text) return [fact]
  if (fact?.status === 'alleged' && fact.text) return [{
    ...fact,
    text: `Según lo manifestado; requiere corroboración: ${fact.text}`
  }]
  return []
}))

function textOf(value) {
  if (Array.isArray(value)) return value.map(textOf).filter(Boolean)
  if (typeof value === 'string') return presentableText(value).trim()
  if (value && typeof value === 'object') return textOf(value.text || value.description || value.content || value.title)
  return ''
}
function recordsOf(value) { return (Array.isArray(value) ? value : value == null || value === '' ? [] : [value]).filter(item => item != null && item !== '') }
function linkedText(entry, fields) {
  for (const field of fields) {
    const value = entry?.[field]
    if (typeof value === 'string') return textOf(value)
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      const relation = value.argument_id || value.related_argument_id
      if (!relation || relation === entry.argument_id || relation === entry.id) return textOf(value.text || value.content || value.argument || value.response || value.reply || value.objection)
    }
  }
  return ''
}
function relatedCounterargument(entry) {
  const id = entry?.argument_id || entry?.id
  if (!id) return null
  return recordsOf(props.argumentData?.possible_counterarguments).find(item =>
    item?.argument_id === id || item?.related_argument_id === id) || null
}
function relatedResponse(counterargument, entry) {
  const counterId = counterargument?.counterargument_id || counterargument?.objection_id || counterargument?.id
  const argumentId = entry?.argument_id || entry?.id
  return recordsOf(props.argumentData?.counterargument_responses).find(item =>
    (counterId && (item?.counterargument_id === counterId || item?.related_counterargument_id === counterId)) ||
    (argumentId && item?.argument_id === argumentId)) || null
}
function sourceList(entry) {
  const foundation = recordsOf(entry.legal_basis || entry.foundation || entry.legal_foundation).map(textOf).join(' ')
  const verifiedEntry = { ...entry, argument: [entry.argument, entry.text, foundation].map(textOf).filter(Boolean).join(' '), legal_basis: foundation }
  const verified = verifiedArgumentSources(verifiedEntry, sources.value, props.caseId, citations.value)
  const identities = new Set([
    ...(Array.isArray(entry.source_ids) ? entry.source_ids : []),
    ...(Array.isArray(entry.jurisprudence) ? entry.jurisprudence : []),
    entry.source_id, entry.unit_id,
    ...citations.value.filter(citation => citation.label && verifiedEntry.argument.includes(citation.label)).map(citation => citation.source_id)
  ].filter(Boolean))
  const caseDocuments = sources.value.filter(source => source.source_scope === 'case' &&
    [source.source_id, source.unit_id, source.chunk_id].some(identity => identity && identities.has(identity)))
  return [...new Map([...verified, ...caseDocuments].map(source => [source.source_id, source])).values()]
}
function argumentEntry(raw, sectionKey, index) {
  const entry = typeof raw === 'string' ? { text: raw } : raw && typeof raw === 'object' ? raw : { text: String(raw) }
  const title = textOf(entry.title || entry.name || entry.heading)
  const body = textOf(entry.argument || entry.text || entry.content || entry.description)
  const foundation = recordsOf(entry.legal_basis || entry.foundation || entry.legal_foundation)
    .map(item => textOf(typeof item === 'string' ? item : item?.text || item?.description || item?.title)).filter(Boolean)
  const linkedFacts = relatedFactTexts(entry, supportedFacts.value).map(textOf).filter(Boolean)
  const usedSources = sourceList(entry)
  const counterargument = relatedCounterargument(entry)
  const response = relatedResponse(counterargument, entry)
  return {
    key: entry.argument_id || entry.id || `${sectionKey}-${index}-${title || body.slice(0, 28)}`,
    title, body, foundation, facts: linkedFacts,
    counterargument: linkedText(entry, ['counterargument', 'counter_argument', 'objection']) ||
      textOf(counterargument?.argument || counterargument?.counterargument || counterargument?.objection || counterargument?.text),
    response: linkedText(entry, ['response', 'reply', 'answer', 'rebuttal']) ||
      textOf(response?.response || response?.reply || response?.answer || response?.text || response?.content),
    publicSources: usedSources.filter(source => source.source_scope === 'public_legal'),
    privateSources: usedSources.filter(source => ['case', 'private_case'].includes(source.source_scope)),
    needsVerification: argumentNeedsVerification(entry, sources.value, props.caseId, citations.value) &&
      (foundation.length > 0 || Boolean(entry.jurisprudence?.length) || ['normative_arguments', 'constitutional_arguments'].includes(sectionKey))
  }
}
const sections = computed(() => argumentGroups.flatMap(([key, label]) => {
  const items = recordsOf(props.argumentData?.[key]).map((entry, index) => argumentEntry(entry, key, index))
    .filter(entry => entry.title || entry.body || entry.foundation.length || entry.facts.length || entry.publicSources.length || entry.privateSources.length)
  return items.length ? [{ key, label, items }] : []
}))
function citationLabel(source) { return argumentCitationForSource(source, citations.value, sources.value, props.caseId)?.label || '' }
function sourceTitle(source) { return presentableText(source.display_title || source.title).trim() }
function sourceDetails(source) {
  return [sourceUnitLabel(source), source.court || source.issuer || source.entity,
    source.page_start ? `pág. ${source.page_start}` : ''].filter(Boolean).join(' · ')
}
function privateSourceDetails(source) {
  return ['Documento aportado', source.page_start ? `pág. ${source.page_start}` : ''].filter(Boolean).join(' · ')
}
function selectSource(source) { selectedSource.value = normalizeSource(source, props.caseId) }
function openCitation(citation) {
  selectedSource.value = sources.value.find(source => source.source_id === citation?.source_id) || null
}
function formatNumber(value) { return String(value).padStart(2, '0') }
</script>

<style scoped>
.court-arguments{display:flex;flex-direction:column;gap:28px;width:100%;min-width:0;color:#304357}
.arguments-header{max-width:900px;padding-bottom:21px;border-bottom:1px solid #dce5ee}
.arguments-eyebrow,.group-eyebrow{display:flex;align-items:center;gap:8px;margin:0 0 9px;color:#92713c;font-size:.66rem;font-weight:750;letter-spacing:.12em}
.arguments-eyebrow span{width:20px;height:1px;background:#b08a4c}
.arguments-header h2,.group-heading h3{margin:0;color:#17375e;font-family:Georgia,'Times New Roman',serif;font-weight:600}
.arguments-header h2{font-size:clamp(1.7rem,2.5vw,2.15rem);line-height:1.25}
.arguments-header>p:last-child{max-width:78ch;margin:8px 0 0;color:#69798a;font-size:.91rem;line-height:1.65}
.argument-section{min-width:0}
.group-heading{margin-bottom:12px}.group-eyebrow{margin-bottom:5px;font-size:.59rem}.group-heading h3{font-size:1.22rem;line-height:1.4}
.argument-list{margin:0;padding:0;border-top:1px solid #e4eaf0;list-style:none}
.argument-entry{display:grid;grid-template-columns:38px minmax(0,1fr);gap:13px;padding:22px 0;border-bottom:1px solid #e4eaf0}
.argument-number{padding-top:3px;color:#a17c43;font-family:Georgia,serif;font-size:.9rem;font-weight:600}
.argument-content{min-width:0;max-width:1000px}.argument-content>h4{margin:0 0 12px;color:#203a55;font:600 1.12rem/1.45 Georgia,'Times New Roman',serif;overflow-wrap:break-word;hyphens:none}
.argument-prose :deep(.markdown-body),.argument-subsection :deep(.markdown-body),.linked-position :deep(.markdown-body),.argument-fallback :deep(.markdown-body){width:100%;min-width:0;color:#3d4e60;font-size:.94rem;line-height:1.72;overflow-wrap:break-word;word-break:normal}
.argument-prose :deep(p),.argument-subsection :deep(p),.linked-position :deep(p),.argument-fallback :deep(p){margin:0 0 10px}.argument-prose :deep(p:last-child),.argument-subsection :deep(p:last-child),.linked-position :deep(p:last-child),.argument-fallback :deep(p:last-child){margin-bottom:0}
.argument-subsection,.argument-sources{margin-top:18px}.argument-subsection h5,.argument-sources h5,.linked-position h5{margin:0 0 8px;color:#806d49;font-size:.69rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}
.argument-facts ul,.argument-sources ul{display:grid;gap:0;margin:0;padding:0;list-style:none}
.argument-facts li{display:grid;grid-template-columns:16px minmax(0,1fr);gap:8px;align-items:start;padding:5px 0}.argument-facts li>span{padding-top:2px;color:#63806e;font-size:.84rem}
.argument-facts :deep(.markdown-body){font-size:.88rem;line-height:1.65}
.argument-sources ul{border-top:1px solid #edf0f3}.argument-sources li{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:8px 14px;padding:10px 0;border-bottom:1px solid #edf0f3}
.source-main{display:flex;align-items:flex-start;gap:10px;min-width:0}.source-citation{flex:0 0 auto;width:max-content;min-width:22px;align-self:flex-start;margin:1px 0 0}
.source-detail{display:grid;gap:2px;min-width:0;line-height:1.5;overflow-wrap:break-word;word-break:normal}.source-detail strong{color:#263f59;font-size:.87rem;font-weight:650}.source-detail small{color:#708094;font-size:.75rem}
.source-open{justify-self:end;padding:4px 6px;border:0;border-radius:5px;background:transparent;color:#315c83;font:600 .75rem/1.4 system-ui,sans-serif;white-space:nowrap;cursor:pointer}.source-open:hover{background:#edf3f7;color:#17375e}.source-open:focus-visible{outline:2px solid #b08a4c;outline-offset:2px}
.linked-position{margin-top:16px;padding:12px 14px;border-left:2px solid #c5b38e;background:#fbfaf7}.linked-position--response{border-left-color:#9ab0c2;background:#f6f8fa}.linked-position--response h5{color:#31536f}
.verification-note{margin:14px 0 0;padding-left:11px;border-left:2px solid #b08a4c;color:#806b49;font-size:.8rem;line-height:1.55}
.arguments-state{margin:0;color:#64758a;font-size:.9rem;line-height:1.6}.argument-fallback{min-width:0;max-width:1000px}
@media(max-width:680px){.court-arguments{gap:23px}.argument-entry{grid-template-columns:30px minmax(0,1fr);gap:8px;padding:18px 0}.argument-content>h4{font-size:1.03rem}.argument-sources li{grid-template-columns:minmax(0,1fr);gap:4px}.source-open{justify-self:start}.linked-position{padding:10px 11px}}
</style>
