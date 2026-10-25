<template>
  <main class="arguments-editorial" aria-labelledby="arguments-title">
    <header class="arguments-header">
      <p class="arguments-eyebrow"><span aria-hidden="true"></span> MYKE · NOVACASE</p>
      <h2 id="arguments-title">Argumentos jurídicos</h2>
      <p>Argumentos, fundamentos y fuentes que sustentan las principales posiciones jurídicas del caso.</p>
    </header>

    <p v-if="!argumentSections.length && !counterPairs.length && !unmatchedResponses.length && !observations.length" class="arguments-empty" role="status">No se identificaron argumentos con la información disponible.</p>

    <section v-for="section in argumentSections" :key="section.key" class="argument-section" :aria-labelledby="`argument-group-${section.key}`">
      <header class="group-heading"><p class="group-eyebrow">ESTRATEGIA ARGUMENTATIVA</p><h3 :id="`argument-group-${section.key}`">{{ section.label }}</h3></header>
      <ol class="argument-list">
        <li v-for="(entry, index) in section.items" :key="entry.key" class="argument-entry">
          <span class="argument-number" aria-hidden="true">{{ formatNumber(index + 1) }}</span>
          <div class="argument-content">
            <h4 v-if="entry.title">{{ entry.title }}</h4>
            <MarkdownRenderer citation-numbers-only v-if="entry.body" class="argument-prose" :content="citedBody(entry)" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" />

            <section v-if="entry.foundation.length" class="argument-subsection">
              <h5>Fundamento jurídico</h5>
              <MarkdownRenderer citation-numbers-only :content="citedFoundation(entry)" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" />
            </section>

            <section v-if="entry.facts.length" class="argument-subsection argument-facts">
              <h5>Hechos que respaldan este argumento</h5>
              <ul><li v-for="(fact, factIndex) in entry.facts" :key="`${entry.key}-fact-${factIndex}`"><span aria-hidden="true">✓</span><MarkdownRenderer citation-numbers-only :content="fact" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" /></li></ul>
            </section>

            <div v-if="entry.sources.length" class="argument-source-block">
              <h5>Fuentes</h5>
              <ul class="argument-source-list"><li v-for="source in entry.sources" :key="source.source_id">
                <div class="source-main">
                  <button v-if="citationLabel(source)" type="button" class="source-reference-label novacase-citation-badge" :aria-label="`Ver fuente ${citationLabel(source).slice(1, -1)}`" @click="selectSource(source)">{{ citationLabel(source).slice(1, -1) }}</button>
                  <span class="source-human-detail"><strong>{{ source.display_title || source.title }}</strong><small v-if="sourceHumanLabel({ ...source, display_title: '', title: '' })">{{ sourceHumanLabel({ ...source, display_title: '', title: '' }) }}</small></span>
                </div>
                <button type="button" class="source-open" :aria-label="`Ver fuente ${citationLabel(source)?.replace(/[\[\]]/g, '') || sourceHumanLabel(source)}`" @click="selectSource(source)">Ver fuente <span aria-hidden="true">↗</span></button>
              </li></ul>
            </div>
            <p v-if="entry.needsVerification" class="verification-note">El fundamento requiere verificación documental o jurídica adicional.</p>
          </div>
        </li>
      </ol>
    </section>

    <section v-if="counterPairs.length || unmatchedResponses.length" class="argument-section counterargument-section" aria-labelledby="counterarguments-title">
      <header class="group-heading"><p class="group-eyebrow">LECTURA ADVERSARIAL</p><h3 id="counterarguments-title">Contraargumentos previsibles</h3><p>Principales objeciones que podría formular la parte contraria.</p></header>
      <ol class="argument-list">
        <li v-for="(item, index) in counterPairs" :key="item.key" class="argument-entry counterargument-entry">
          <span class="argument-number" aria-hidden="true">{{ formatNumber(index + 1) }}</span>
          <div class="argument-content">
            <h4 v-if="item.title">{{ item.title }}</h4>
            <div class="counterargument-copy"><h5>Contraargumento</h5><MarkdownRenderer citation-numbers-only :content="item.body" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" /></div>
            <div v-if="item.response" class="response-copy"><h5>Respuesta jurídica</h5><MarkdownRenderer citation-numbers-only :content="item.response.body" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" />
              <div v-if="item.response.sources.length" class="response-source-list"><button v-for="source in item.response.sources" :key="source.source_id" type="button" class="source-open" @click="selectSource(source)">{{ citationLabel(source) || sourceHumanLabel(source) }} · Ver fuente ↗</button></div>
            </div>
          </div>
        </li>
      </ol>
      <div v-if="unmatchedResponses.length" class="unmatched-responses">
        <h4>Respuestas jurídicas relacionadas</h4>
        <article v-for="item in unmatchedResponses" :key="item.key" class="unmatched-response">
          <h5 v-if="item.title">{{ item.title }}</h5>
          <MarkdownRenderer citation-numbers-only :content="item.body" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" />
          <div v-if="item.sources.length" class="response-source-list"><button v-for="source in item.sources" :key="source.source_id" type="button" class="source-open" @click="selectSource(source)">{{ citationLabel(source) || sourceHumanLabel(source) }} · Ver fuente ↗</button></div>
        </article>
      </div>
    </section>

    <section v-if="observations.length" class="argument-section observations-section" aria-labelledby="observations-title">
      <header class="group-heading"><p class="group-eyebrow">PUNTOS DE ATENCIÓN</p><h3 id="observations-title">Observaciones generales</h3></header>
      <ul class="observation-list"><li v-for="item in observations" :key="item.key"><MarkdownRenderer citation-numbers-only :content="item.body" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" /></li></ul>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import { presentableText, relatedFactTexts, verifiedArgumentSources, argumentNeedsVerification, sourceHumanLabel, argumentCitationForSource } from '@/utils/novacasePresentation.js'
import { normalizeSource, normalizeSources, resolveCitations } from '@/utils/sourceContract.js'

const props = defineProps({
  arguments: { type: Object, default: () => ({}) }, facts: { type: Array, default: () => [] },
  sources: { type: Array, default: () => [] }, citations: { type: Array, default: () => [] },
  caseId: { type: String, default: null }
})
const emit = defineEmits(['select-source'])
const labels = {
  main_arguments: 'Argumentos principales', secondary_arguments: 'Argumentos complementarios',
  constitutional_arguments: 'Argumentos constitucionales', procedural_arguments: 'Argumentos procesales',
  normative_arguments: 'Argumentos normativos'
}
const safeSources = computed(() => normalizeSources(props.sources, props.caseId))
const canonicalCitations = computed(() => resolveCitations(props.citations, safeSources.value, props.caseId).citations)
function textOf(value) {
  if (Array.isArray(value)) return value.map(textOf).filter(Boolean).join('\n\n')
  if (typeof value === 'string') return presentableText(value).trim()
  if (value && typeof value === 'object') return textOf(value.text || value.description || value.content || value.title)
  return ''
}
function isTechnicalReference(value) { return typeof value === 'string' && (/^(?:SRC|FACT|ISSUE)-[a-f0-9]{12,}$/i.test(value.trim()) || /^[0-9a-f-]{36}$/i.test(value.trim())) }
function recordsOf(value) { return (Array.isArray(value) ? value : value == null || value === '' ? [] : [value]).filter(item => item != null && item !== '') }
function sourceList(entry) { return verifiedArgumentSources(entry, safeSources.value, props.caseId, props.citations) }
function citationLabel(source) { return argumentCitationForSource(source, props.citations, safeSources.value, props.caseId)?.label || '' }
function missingCitation(entry) {
  if (entry.sources.length !== 1) return ''
  const source = entry.sources[0]
  const citation = canonicalCitations.value.find(item => item.source_id === source.source_id)
  if (!citation?.label || !/^\[\d+\]$/.test(citation.label)) return ''
  return [entry.body, ...entry.foundation].some(text => text.includes(citation.label)) ? '' : citation.label
}
function citedBody(entry) {
  const label = entry.body ? missingCitation(entry) : ''
  return entry.body + (label ? ` ${label}` : '')
}
function citedFoundation(entry) {
  const label = !entry.body && missingCitation(entry)
  return label ? [...entry.foundation.slice(0, -1), `${entry.foundation.at(-1)} ${label}`] : entry.foundation
}
function selectSource(source) { const safe = normalizeSource(source, props.caseId); if (safe) emit('select-source', safe) }
function openCitation(citation) { const source = safeSources.value.find(item => item.source_id === citation?.source_id); if (source) selectSource(source) }
function formatNumber(value) { return String(value).padStart(2, '0') }

function argumentEntry(raw, sectionKey, index) {
  const entry = typeof raw === 'string' ? { text: raw } : raw && typeof raw === 'object' ? raw : { text: String(raw) }
  const title = textOf(entry.title || entry.name || entry.heading)
  const body = textOf(entry.argument || entry.text || entry.content || entry.description)
  const foundation = recordsOf(entry.legal_basis || entry.foundation || entry.legal_foundation).map(item =>
    typeof item === 'string' ? textOf(item) : textOf(item?.text || item?.description || item?.title)).filter(Boolean)
  const facts = relatedFactTexts(entry, props.facts).map(textOf).filter(Boolean)
  const sources = sourceList(entry)
  return {
    key: entry.argument_id || entry.id || `${sectionKey}-${index}-${title || body.slice(0, 30)}`,
    title, body, foundation, facts, sources,
    needsVerification: argumentNeedsVerification(entry, safeSources.value, props.caseId, props.citations) &&
      (foundation.length > 0 || Boolean(entry.jurisprudence?.length) || ['normative_arguments','constitutional_arguments'].includes(sectionKey))
  }
}
const argumentSections = computed(() => Object.entries(labels).flatMap(([key, label]) => {
  const items = recordsOf(props.arguments?.[key]).map((entry, index) => argumentEntry(entry, key, index))
    .filter(entry => entry.title || entry.body || entry.foundation.length || entry.facts.length || entry.sources.length)
  return items.length ? [{ key, label, items }] : []
}))

function normalizeRelated(value) { return textOf(value).toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim() }
function counterEntry(raw, key, index) {
  const item = typeof raw === 'string' ? { text: raw } : raw && typeof raw === 'object' ? raw : { text: String(raw) }
  const body = key === 'response'
    ? textOf(item.response || item.reply || item.answer || item.text || item.content || item.argument)
    : textOf(item.argument || item.counterargument || item.objection || item.text || item.content || item.description)
  const title = textOf(item.title || item.name || item.heading)
  const sources = sourceList(item)
  return { key: item.response_id || item.id || item.counterargument_id || `${key}-${index}-${body.slice(0,24)}`, title, body, sources,
    relationId: item.counterargument_id || item.objection_id || item.related_counterargument_id || item.id || null,
    relationText: normalizeRelated(item.counterargument || item.objection || item.title || item.name), raw: item }
}
const counterResponseMapping = computed(() => {
  const objections = recordsOf(props.arguments?.possible_counterarguments).map((item,index)=>counterEntry(item,'counter',index)).filter(item=>item.body || item.title)
  const responses = recordsOf(props.arguments?.counterargument_responses).map((item,index)=>counterEntry(item,'response',index)).filter(item=>item.body || item.title)
  const used = new Set()
  const pairs = objections.map(objection => {
    const responseIndex = responses.findIndex((response,index) => !used.has(index) && (
      (response.relationId && response.relationId === objection.relationId) ||
      (response.relationText && objection.relationText && response.relationText === objection.relationText)
    ))
    const response = responseIndex >= 0 ? responses[responseIndex] : null
    if (response) used.add(responseIndex)
    return { ...objection, response }
  })
  return { pairs, used, responses }
})
const counterPairs = computed(() => counterResponseMapping.value.pairs)
const unmatchedResponses = computed(() => counterResponseMapping.value.responses.filter((_, index) => !counterResponseMapping.value.used.has(index)))
const observations = computed(() => recordsOf(props.arguments?.general_observations).map((item,index) => {
  const body = textOf(typeof item === 'string' ? item : item?.text || item?.observation || item?.content || item?.description)
  return body && !isTechnicalReference(body) ? { key: item?.id || `observation-${index}`, body } : null
}).filter(Boolean))
</script>

<style scoped>
.arguments-editorial{width:100%;min-width:0;max-width:1080px;margin:0 auto;display:flex;flex-direction:column;gap:32px;color:#304357}.arguments-header{padding-bottom:23px;border-bottom:1px solid #e2e8ef}.arguments-eyebrow,.group-eyebrow{display:flex;align-items:center;gap:8px;margin:0 0 9px;color:#8a6a37;font-size:.62rem;font-weight:750;letter-spacing:.13em}.arguments-eyebrow span{width:20px;height:1px;background:#b08a4c}.arguments-header h2,.group-heading h3{margin:0;color:#17375e;font-family:Georgia,'Times New Roman',serif;font-weight:600}.arguments-header h2{font-size:clamp(1.7rem,2.5vw,2.15rem);line-height:1.25}.arguments-header>p:last-child,.group-heading>p:last-child{max-width:800px;margin:8px 0 0;color:#69798a;font-size:.91rem;line-height:1.65}.arguments-empty{margin:0;color:#64758a;line-height:1.6}.argument-section{min-width:0}.group-heading{margin-bottom:16px}.group-eyebrow{margin-bottom:6px;font-size:.57rem}.group-heading h3{font-size:1.28rem;line-height:1.4}.group-heading>p:last-child{font-size:.83rem}.argument-list{margin:0;padding:0;list-style:none;border-top:1px solid #e4eaf0}.argument-entry{display:grid;grid-template-columns:40px minmax(0,1fr);gap:13px;padding:22px 0;border-bottom:1px solid #e4eaf0}.argument-number{padding-top:4px;color:#a17c43;font-family:Georgia,serif;font-size:.92rem;font-weight:600}.argument-content{min-width:0;max-width:960px}.argument-content>h4{max-width:900px;margin:0 0 13px;color:#203a55;font-family:Georgia,'Times New Roman',serif;font-size:1.12rem;font-weight:600;line-height:1.45;overflow-wrap:break-word;hyphens:none}.argument-prose :deep(.markdown-body),.argument-subsection :deep(.markdown-body),.counterargument-copy :deep(.markdown-body),.response-copy :deep(.markdown-body),.unmatched-response :deep(.markdown-body),.observation-list :deep(.markdown-body){min-width:0;width:100%;font-size:.94rem;line-height:1.78;color:#3d4e60;word-break:normal;overflow-wrap:break-word}.argument-prose :deep(p),.argument-subsection :deep(p),.counterargument-copy :deep(p),.response-copy :deep(p),.unmatched-response :deep(p),.observation-list :deep(p){margin:0 0 10px}.argument-prose :deep(p:last-child),.argument-subsection :deep(p:last-child),.counterargument-copy :deep(p:last-child),.response-copy :deep(p:last-child),.unmatched-response :deep(p:last-child),.observation-list :deep(p:last-child){margin-bottom:0}.argument-subsection{margin-top:19px}.argument-subsection h5,.argument-source-block h5,.counterargument-copy h5,.response-copy h5,.unmatched-response h5{margin:0 0 8px;color:#7d6845;font-size:.71rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}.argument-facts ul{display:grid;gap:7px;margin:0;padding:0;list-style:none}.argument-facts li{display:grid;grid-template-columns:16px minmax(0,1fr);gap:8px;align-items:start}.argument-facts li>span{padding-top:2px;color:#718e78;font-size:.83rem}.argument-facts li :deep(.markdown-body){font-size:.88rem;line-height:1.65}.argument-source-block{margin-top:19px}.argument-source-list{margin:0;padding:0;border-top:1px solid #edf0f3;list-style:none}.argument-source-list li{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:baseline;gap:3px 14px;padding:9px 0;border-bottom:1px solid #edf0f3}.source-reference-label:not(.novacase-citation-badge){min-width:0;color:#315c83;font-size:.83rem;font-weight:650;overflow-wrap:anywhere}.source-human-detail{grid-column:1;color:#7a8794;font-size:.75rem;line-height:1.5}.source-open{justify-self:end;padding:3px 5px;border:0;border-radius:4px;background:transparent;color:#315c83;font-family:inherit;font-size:.76rem;font-weight:600;line-height:1.5;white-space:nowrap;cursor:pointer}.source-open:hover{background:#edf3f7;color:#17375e}.source-open:focus-visible{outline:2px solid #b08a4c;outline-offset:2px}.verification-note{margin:15px 0 0;padding-left:11px;border-left:2px solid #b08a4c;color:#806b49;font-size:.8rem;line-height:1.55}.counterargument-section{padding-top:4px}.counterargument-entry{padding-block:20px}.counterargument-copy{padding:12px 14px;border-left:2px solid #c5b38e;background:#fbfaf7}.response-copy{margin-top:13px;padding:12px 14px;border-left:2px solid #9ab0c2;background:#f6f8fa}.response-copy h5{color:#31536f}.response-source-list{display:flex;flex-wrap:wrap;gap:5px 10px;margin-top:9px}.response-source-list .source-open{justify-self:auto}.unmatched-responses{margin-top:22px;padding-top:17px;border-top:1px solid #e5eaf0}.unmatched-responses>h4{margin:0 0 11px;color:#263e56;font-family:Georgia,serif;font-size:1rem;font-weight:600}.unmatched-response{padding:13px 0;border-bottom:1px solid #e8edf2}.unmatched-response h5{margin-bottom:6px;color:#31536f}.observation-list{display:grid;gap:0;margin:0;padding:0;border-top:1px solid #e4eaf0;list-style:none}.observation-list>li{padding:12px 0;border-bottom:1px solid #e4eaf0}
.argument-source-list .source-main{display:flex;align-items:flex-start;gap:10px;min-width:0}
.argument-source-list .source-main .novacase-citation-badge{flex:0 0 auto;width:max-content;min-width:22px;justify-self:start;align-self:flex-start;margin:0}
.argument-source-list .source-human-detail{display:grid;gap:2px;min-width:0;color:#708094;font-size:.75rem;line-height:1.5;overflow-wrap:anywhere}
.argument-source-list .source-human-detail strong{color:#263f59;font-size:.86rem;font-weight:650}
.argument-source-list .source-human-detail small{color:#708094;font-size:.75rem}
@media(max-width:680px){.arguments-editorial{gap:26px}.argument-entry{grid-template-columns:30px minmax(0,1fr);gap:8px;padding:18px 0}.argument-content>h4{font-size:1.02rem}.argument-source-list li{grid-template-columns:minmax(0,1fr)}.source-human-detail{grid-column:1}.source-open{justify-self:start}.counterargument-copy,.response-copy{padding:10px 11px}}
</style>
