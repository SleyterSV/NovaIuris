<template>
  <main class="counter-editorial" aria-labelledby="counter-title">
    <header class="counter-header">
      <p class="counter-eyebrow"><span aria-hidden="true"></span> MYKE · NOVACASE</p>
      <h2 id="counter-title">Contraargumentos previsibles</h2>
      <p>Principales objeciones que podría formular la parte contraria y respuestas disponibles en el análisis.</p>
    </header>

    <section v-if="summary" class="counter-summary" aria-labelledby="counter-summary-title">
      <h3 id="counter-summary-title">Lectura estratégica</h3>
      <MarkdownRenderer citation-numbers-only :content="summary" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" />
    </section>

    <section v-for="section in displaySections" :key="section.key" class="counter-section" :aria-labelledby="`counter-${section.key}`">
      <header class="counter-section-heading"><p class="counter-group-eyebrow">OBJECIONES PREVISIBLES</p><h3 :id="`counter-${section.key}`">{{ section.title }}</h3></header>
      <ol class="counter-list">
        <li v-for="(item,index) in section.items" :key="item.key" class="counter-entry">
          <span class="counter-number" aria-hidden="true">{{ formatNumber(index + 1) }}</span>
          <div class="counter-content">
            <h4 v-if="item.title">{{ item.title }}</h4>
            <div class="counter-objection"><h5>Contraargumento</h5><MarkdownRenderer citation-numbers-only :content="item.body" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" /></div>
            <div v-if="item.response" class="counter-response"><h5>Respuesta jurídica</h5><MarkdownRenderer citation-numbers-only :content="item.response.body" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" />
              <SourceActions v-if="item.response.sources.length" :items="item.response.sources" :citations="citations" :sources="sourcePool" :case-id="caseId" @select="selectSource" />
            </div>
            <SourceActions v-if="item.sources.length" :items="item.sources" :citations="citations" :sources="sourcePool" :case-id="caseId" @select="selectSource" />
          </div>
        </li>
      </ol>
    </section>

    <section v-if="unmatchedResponses.length" class="counter-section" aria-labelledby="responses-title">
      <header class="counter-section-heading"><p class="counter-group-eyebrow">RÉPLICA</p><h3 id="responses-title">Respuestas jurídicas</h3></header>
      <ol class="response-list"><li v-for="(item,index) in unmatchedResponses" :key="item.key" class="response-entry">
        <span class="counter-number" aria-hidden="true">{{ formatNumber(index + 1) }}</span>
        <div><h4 v-if="item.title">{{ item.title }}</h4><MarkdownRenderer citation-numbers-only :content="item.body" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" />
          <SourceActions v-if="item.sources.length" :items="item.sources" :citations="citations" :sources="sourcePool" :case-id="caseId" @select="selectSource" />
        </div>
      </li></ol>
    </section>

    <p v-if="!sections.length && !unmatchedResponses.length && !summary" class="counter-empty" role="status">No se identificaron objeciones o respuestas adicionales con la información disponible.</p>
    <p v-if="sections.length || unmatchedResponses.length" class="counter-note">Los contraargumentos son escenarios posibles y deben valorarse junto con las circunstancias del caso y el criterio profesional.</p>
  </main>
</template>

<script setup>
import { computed, defineComponent, h } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import { presentableText, verifiedArgumentSources, sourceHumanLabel, argumentCitationForSource } from '@/utils/novacasePresentation.js'
import { normalizeSource, normalizeSources } from '@/utils/sourceContract.js'

const props = defineProps({
  counterArguments: { type: Object, default: () => ({}) },
  responses: { type: Array, default: () => [] },
  sources: { type: Array, default: () => [] }, citations: { type: Array, default: () => [] },
  caseId: { type: String, default: null }
})
const emit = defineEmits(['select-source'])
const sourcePool = computed(() => normalizeSources(props.sources, props.caseId))
const sectionDefinitions = [
  { key: 'procedural', aliases: ['procedural','procedural_exceptions'], title: 'Objeciones procesales' },
  { key: 'evidence', aliases: ['evidence','attacks_on_evidence'], title: 'Cuestionamientos probatorios' },
  { key: 'legal', aliases: ['legal','legal_defenses'], title: 'Objeciones de interpretación jurídica' },
  { key: 'jurisprudence', aliases: ['jurisprudence','attacks_on_jurisprudence'], title: 'Criterios jurisprudenciales contrarios' }
]
function rawItems(value) { return (Array.isArray(value) ? value : value == null || value === '' ? [] : [value]).filter(item => item != null && item !== '') }
function clean(value) { return typeof value === 'string' ? presentableText(value).trim() : '' }
function isTechnicalOnly(value) { return /^(?:SRC|FACT|ISSUE)-[a-f0-9]{12,}$|^[0-9a-f-]{36}$/i.test(value.trim()) }
function mapEntry(raw, key, index) {
  const entry = typeof raw === 'string' ? { text: raw } : raw && typeof raw === 'object' ? raw : { text: String(raw) }
  const body = key === 'response'
    ? clean(entry.response || entry.reply || entry.answer || entry.text || entry.content || entry.argument)
    : clean(entry.counterargument || entry.objection || entry.argument || entry.text || entry.content || entry.description)
  const title = clean(entry.title || entry.name || entry.heading)
  const sources = verifiedArgumentSources(entry, sourcePool.value, props.caseId, props.citations)
  return { key: entry.response_id || entry.id || entry.counterargument_id || `${key}-${index}-${body.slice(0,25)}`, title, body, sources,
    relationId: entry.counterargument_id || entry.objection_id || entry.related_counterargument_id || entry.id || null,
    relationText: normalizeRelation(entry.counterargument || entry.objection || entry.title || entry.name), raw: entry }
}
function normalizeRelation(value) { return clean(value).toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim() }
const sections = computed(() => sectionDefinitions.flatMap(definition => {
  const raw = definition.aliases.map(key => props.counterArguments?.[key]).find(value => value != null)
  const items = rawItems(raw).map((item,index)=>mapEntry(item,definition.key,index)).filter(item => (item.body || item.title) && !isTechnicalOnly(item.body || item.title))
  return items.length ? [{key:definition.key,title:definition.title,items}] : []
}))
const objectionEntries = computed(() => sections.value.flatMap(section => section.items))
const responseEntries = computed(() => rawItems(props.responses).map((item,index)=>mapEntry(item,'response',index)).filter(item => (item.body || item.title) && !isTechnicalOnly(item.body || item.title)))
const pairedByObjection = computed(() => {
  const used = new Set()
  const pairs = new Map()
  for (const objection of objectionEntries.value) {
    const responseIndex = responseEntries.value.findIndex((response,index) => !used.has(index) && (
      (response.relationId && response.relationId === objection.relationId) ||
      (response.relationText && objection.relationText && response.relationText === objection.relationText)
    ))
    if (responseIndex >= 0) { used.add(responseIndex); pairs.set(objection.key,responseEntries.value[responseIndex]) }
  }
  return { pairs, used }
})
const displaySections = computed(() => sections.value.map(section => ({ ...section, items: section.items.map(item => ({
  ...item, response: pairedByObjection.value.pairs.get(item.key) || null
})) })))
const unmatchedResponses = computed(() => responseEntries.value.filter((_,index)=>!pairedByObjection.value.used.has(index)))
const summary = computed(() => { const value=props.counterArguments?.summary; return typeof value === 'string' ? clean(value) : '' })
function selectSource(value) { const safe=normalizeSource(value,props.caseId); if(safe) emit('select-source',safe) }
function openCitation(citation) { const source=sourcePool.value.find(item=>item.source_id===citation?.source_id); if(source) selectSource(source) }
function formatNumber(value) { return String(value).padStart(2,'0') }

const SourceActions = defineComponent({
  props:{items:{type:Array,default:()=>[]},citations:{type:Array,default:()=>[]},sources:{type:Array,default:()=>[]},caseId:{type:String,default:null}},
  emits:['select'],
  setup(sourceProps,{emit:sourceEmit}) {
    return () => h('ul',{class:'counter-sources'},sourceProps.items.map(source=>{
      const label=argumentCitationForSource(source,sourceProps.citations,sourceProps.sources,sourceProps.caseId)?.label
      return h('li',{key:source.source_id},[
        h('div',{class:'source-main'},[
          label ? h('button',{type:'button',class:'source-label novacase-citation-badge','aria-label':`Ver fuente ${label.slice(1,-1)}`,onClick:()=>sourceEmit('select',source)},label.slice(1,-1)) : null,
          h('span',{class:'source-detail'},[
            h('strong',source.display_title||source.title||''),
            h('small',sourceHumanLabel({...source,display_title:'',title:''}))
          ])
        ]),
        h('button',{type:'button',class:'source-open','aria-label':`Ver fuente ${label?.replace(/[\[\]]/g,'')||sourceHumanLabel(source)}`,onClick:()=>sourceEmit('select',source)},'Ver fuente ↗')
      ])
    }))
  }
})
</script>

<style scoped>
.counter-editorial{width:100%;min-width:0;max-width:1080px;margin:0 auto;display:flex;flex-direction:column;gap:30px;color:#304357}.counter-header{padding-bottom:22px;border-bottom:1px solid #e2e8ef}.counter-eyebrow,.counter-group-eyebrow{display:flex;align-items:center;gap:8px;margin:0 0 8px;color:#8a6a37;font-size:.62rem;font-weight:750;letter-spacing:.13em}.counter-eyebrow span{width:20px;height:1px;background:#b08a4c}.counter-header h2,.counter-section-heading h3,.counter-summary h3{margin:0;color:#17375e;font-family:Georgia,'Times New Roman',serif;font-weight:600}.counter-header h2{font-size:clamp(1.65rem,2.5vw,2.1rem);line-height:1.25}.counter-header>p:last-child{max-width:800px;margin:8px 0 0;color:#69798a;font-size:.9rem;line-height:1.65}.counter-section{min-width:0}.counter-section-heading{margin-bottom:15px}.counter-group-eyebrow{margin-bottom:6px;font-size:.57rem}.counter-section-heading h3,.counter-summary h3{font-size:1.22rem;line-height:1.4}.counter-list,.response-list{margin:0;padding:0;border-top:1px solid #e4eaf0;list-style:none}.counter-entry,.response-entry{display:grid;grid-template-columns:40px minmax(0,1fr);gap:13px;padding:20px 0;border-bottom:1px solid #e4eaf0}.counter-number{padding-top:3px;color:#a17c43;font-family:Georgia,serif;font-size:.9rem;font-weight:600}.counter-content,.response-entry>div{min-width:0;max-width:960px}.counter-content>h4,.response-entry h4{margin:0 0 12px;color:#203a55;font:600 1.06rem/1.45 Georgia,'Times New Roman',serif;overflow-wrap:break-word}.counter-objection,.counter-response{padding:11px 14px;border-left:2px solid #c5b38e;background:#fbfaf7}.counter-response{margin-top:12px;border-left-color:#9ab0c2;background:#f6f8fa}.counter-objection h5,.counter-response h5{margin:0 0 7px;color:#7d6845;font-size:.69rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}.counter-response h5{color:#31536f}.counter-editorial :deep(.markdown-body){min-width:0;width:100%;font-size:.93rem;line-height:1.75;color:#3d4e60;word-break:normal;overflow-wrap:break-word}.counter-editorial :deep(.markdown-body p){margin:0 0 9px}.counter-editorial :deep(.markdown-body p:last-child){margin-bottom:0}.counter-editorial :deep(.counter-sources){margin:11px 0 0;padding:0;border-top:1px solid #e9edf1;list-style:none}.counter-editorial :deep(.counter-sources li){display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:baseline;gap:3px 14px;padding:8px 0;border-bottom:1px solid #e9edf1}.counter-editorial :deep(.source-label:not(.novacase-citation-badge)){color:#315c83;font-size:.81rem;font-weight:650;overflow-wrap:anywhere}.counter-editorial :deep(.source-detail){grid-column:1;color:#7a8794;font-size:.74rem}.counter-editorial :deep(.source-open){justify-self:end;padding:3px 5px;border:0;border-radius:4px;background:transparent;color:#315c83;font-family:inherit;font-size:.76rem;font-weight:600;line-height:1.5;white-space:nowrap;cursor:pointer}.counter-editorial :deep(.source-open:hover){background:#edf3f7;color:#17375e}.counter-editorial :deep(.source-open:focus-visible){outline:2px solid #b08a4c;outline-offset:2px}.counter-summary{padding:0 0 17px;border-bottom:1px solid #e4eaf0}.counter-summary h3{margin-bottom:9px}.counter-empty{margin:0;color:#68798a;font-size:.88rem;line-height:1.65}.counter-note{margin:0;padding:12px 14px;border-left:2px solid #b08a4c;background:#faf8f2;color:#776748;font-size:.8rem;line-height:1.6}
.counter-editorial :deep(.counter-sources .source-main){display:flex;align-items:flex-start;gap:10px;min-width:0}
.counter-editorial :deep(.counter-sources .novacase-citation-badge){flex:0 0 auto;width:max-content;min-width:22px;justify-self:start;align-self:flex-start;margin:0}
.counter-editorial :deep(.counter-sources .source-detail){display:grid;gap:2px;min-width:0;color:#708094;font-size:.75rem;line-height:1.5;overflow-wrap:anywhere}
.counter-editorial :deep(.counter-sources .source-detail strong){color:#263f59;font-size:.86rem;font-weight:650}
.counter-editorial :deep(.counter-sources .source-detail small){color:#708094;font-size:.75rem}
@media(max-width:680px){.counter-editorial{gap:24px}.counter-entry,.response-entry{grid-template-columns:30px minmax(0,1fr);gap:8px;padding:17px 0}.counter-objection,.counter-response{padding:10px 11px}.counter-editorial :deep(.counter-sources li){grid-template-columns:minmax(0,1fr)}.counter-editorial :deep(.source-detail){grid-column:1}.counter-editorial :deep(.source-open){justify-self:start}}
</style>
