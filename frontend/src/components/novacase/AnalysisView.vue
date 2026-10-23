<template>
  <main class="analysis-editorial" aria-labelledby="analysis-title">
    <header class="analysis-header">
      <div>
        <p class="analysis-eyebrow"><span aria-hidden="true"></span> NOVACASE · ANÁLISIS JURÍDICO</p>
        <h2 id="analysis-title">Análisis jurídico</h2>
        <p class="analysis-intro">Evaluación estructurada de los elementos jurídicos relevantes del caso.</p>
      </div>
      <span v-if="completed" class="analysis-status"><span aria-hidden="true"></span>Análisis completado</span>
    </header>

    <p v-if="!hasAnalysisContent" class="analysis-empty" role="status">No se identificó información suficiente para esta sección.</p>

    <section v-if="overview.length" class="analysis-section analysis-overview" aria-labelledby="overview-title">
      <div class="section-heading"><p class="section-eyebrow">CONTEXTO DEL CASO</p><h3 id="overview-title">Visión general</h3></div>
      <dl class="overview-strip">
        <div v-for="item in overview" :key="item.label" class="overview-item">
          <dt>{{ item.label }}</dt><dd>{{ item.value }}</dd>
        </div>
      </dl>
    </section>

    <section v-if="factGroups.some(group => group.items.length)" class="analysis-section" aria-labelledby="facts-title">
      <div class="section-heading"><p class="section-eyebrow">HECHOS Y RESPALDO</p><h3 id="facts-title">Base fáctica del caso</h3>
        <p>Hechos identificados a partir de la documentación aportada y del relato del caso.</p></div>
      <section v-for="group in factGroups" v-show="group.items.length" :key="group.key" class="fact-editorial-group">
        <header class="subsection-heading"><span class="fact-state-mark" :class="`state-${group.key}`" aria-hidden="true"></span><div><h4>{{ group.title }}</h4><p>{{ group.note }}</p></div></header>
        <ol class="fact-list">
          <li v-for="(item, index) in group.items" :key="item.key" class="fact-row">
            <span class="editorial-number" aria-hidden="true">{{ formatNumber(index + 1) }}</span>
            <div class="fact-copy">
              <MarkdownRenderer :content="item.text" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" />
              <span v-if="group.key !== 'supported'" class="fact-pending">{{ item.statusLabel || 'Pendiente de corroboración' }}</span>
              <div v-if="item.sources.length" class="fact-source-list">
                <span class="source-prefix">Fuente:</span>
                <button v-for="source in item.sources" :key="source.source_id" class="source-reference" type="button" @click="selectSource(source)">
                  {{ sourceTitle(source) }}<span v-if="source.page_start"> · pág. {{ source.page_start }}</span><span aria-hidden="true"> ↗</span>
                </button>
              </div>
            </div>
          </li>
        </ol>
      </section>
    </section>

    <div class="analysis-two-column">
      <section v-if="issues.length" class="analysis-section" aria-labelledby="issues-title">
        <div class="section-heading"><p class="section-eyebrow">CONTROVERSIA</p><h3 id="issues-title">Problemas jurídicos</h3></div>
        <ol class="editorial-question-list"><li v-for="(item, index) in issues" :key="item.key"><span class="editorial-number" aria-hidden="true">{{ formatNumber(index + 1) }}</span><MarkdownRenderer :content="item.text" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" /></li></ol>
      </section>

      <section v-if="norms.length" class="analysis-section" aria-labelledby="law-title">
        <div class="section-heading"><p class="section-eyebrow">FUENTES NORMATIVAS</p><h3 id="law-title">Marco normativo aplicable</h3></div>
        <div class="norm-list"><article v-for="item in norms" :key="item.key" class="norm-row"><span class="norm-mark" aria-hidden="true">§</span><div><h4>{{ item.title }}</h4><MarkdownRenderer v-if="item.description" :content="item.description" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" /></div></article></div>
      </section>
    </div>

    <section v-if="jurisprudence.length" class="analysis-section" aria-labelledby="jurisprudence-title">
      <div class="section-heading"><p class="section-eyebrow">CRITERIOS JURISPRUDENCIALES</p><h3 id="jurisprudence-title">Jurisprudencia relevante</h3></div>
      <div class="jurisprudence-list"><article v-for="group in jurisprudence" :key="group.key" class="jurisprudence-row">
        <div class="jurisprudence-main"><h4>{{ group.title }}</h4><p v-if="group.court" class="jurisprudence-court">{{ group.court }}</p>
          <p v-if="group.units.length" class="jurisprudence-locator"><span>Fundamentos relevantes</span>{{ group.units.join(' · ') }}</p>
          <p v-if="group.pages.length" class="jurisprudence-locator"><span>Páginas</span>{{ pageRange(group.pages) }}</p>
        </div>
        <button v-if="group.source" class="source-reference" type="button" @click="selectSource(group.source)">Ver fuente <span aria-hidden="true">↗</span></button>
      </article></div>
    </section>

    <section v-if="observations.length" class="analysis-section" aria-labelledby="observations-title">
      <div class="section-heading"><p class="section-eyebrow">PUNTOS DE ATENCIÓN</p><h3 id="observations-title">Observaciones y elementos por verificar</h3><p>Elementos que requieren revisión adicional según la información disponible.</p></div>
      <div class="observation-list"><article v-for="item in observations" :key="item.key" class="observation-row"><span aria-hidden="true">•</span><MarkdownRenderer :content="item.text" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" /></article></div>
    </section>

    <section v-if="timeline.length" class="analysis-section" aria-labelledby="timeline-title">
      <div class="section-heading"><p class="section-eyebrow">SECUENCIA TEMPORAL</p><h3 id="timeline-title">Cronología del caso</h3><p>Fechas relevantes identificadas a partir de la documentación y del relato disponible.</p></div>
      <ol class="case-timeline">
        <li v-for="event in timeline" :key="event.key" class="timeline-event" :class="{ 'is-alleged': !event.documented }">
          <span class="timeline-marker" aria-hidden="true"></span>
          <time :datetime="event.isoDate">{{ event.displayDate }}</time>
          <span class="timeline-status">{{ event.documented ? 'Documentado' : 'Pendiente de corroboración' }}</span>
          <div class="timeline-copy"><MarkdownRenderer :content="event.text" :citations="citations" :sources="sources" :case-id="caseId" @select-citation="openCitation" />
            <button v-for="source in event.sources" :key="source.source_id" class="source-reference" type="button" @click="selectSource(source)">{{ sourceTitle(source) }}<span v-if="source.page_start"> · pág. {{ source.page_start }}</span><span aria-hidden="true"> ↗</span></button>
          </div>
        </li>
      </ol>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import { groupedJurisprudence, presentableText } from '@/utils/novacasePresentation.js'
import { normalizeSource, normalizeSources } from '@/utils/sourceContract.js'

const props = defineProps({
  analysis: { type: Object, required: true },
  summary: { type: Object, default: () => ({}) },
  facts: { type: Array, default: () => [] },
  timelineData: { type: Array, default: () => [] },
  sources: { type: Array, default: () => [] },
  citations: { type: Array, default: () => [] },
  caseId: { type: String, default: null },
  documentCount: { type: Number, default: 0 },
  publicSourceCount: { type: Number, default: null },
  completed: { type: Boolean, default: true }
})
const emit = defineEmits(['select-source'])

const safeSources = computed(() => normalizeSources(props.sources, props.caseId))
const publicSources = computed(() => safeSources.value.filter(source => source.source_scope === 'public_legal'))
const sourceById = computed(() => new Map(safeSources.value.map(source => [source.source_id, source])))

function clean(value) {
  if (typeof value === 'string') return presentableText(value).trim()
  if (typeof value === 'number') return String(value)
  return ''
}
function contentItems(value, prefix) {
  const list = Array.isArray(value) ? value : value ? [value] : []
  return list.map((item, index) => {
    const record = item && typeof item === 'object' && !Array.isArray(item) ? item : null
    const text = clean(record ? (record.text || record.question || record.description || record.content || record.name || record.title || '') : item)
    return text ? { key: record?.issue_id || record?.fact_id || `${prefix}-${index}-${text.slice(0, 24)}`, text, record } : null
  }).filter(Boolean)
}
function linkedPrivateSources(fact) {
  return (Array.isArray(fact?.source_ids) ? fact.source_ids : []).map(id => sourceById.value.get(id)).filter(source =>
    source && ['case', 'private_case'].includes(source.source_scope) && source.case_id === props.caseId)
}
function sourceTitle(source) { return source.display_title || source.title || 'Documento del caso' }
function selectSource(source) {
  const safe = normalizeSource(source, props.caseId)
  if (safe) emit('select-source', safe)
}
function openCitation(citation) {
  const source = sourceById.value.get(citation?.source_id)
  if (source) selectSource(source)
}
function formatNumber(value) { return String(value).padStart(2, '0') }

const overview = computed(() => {
  const a = props.analysis || {}
  const summary = props.summary || {}
  const branch = clean(a.rama_derecho || a.legal_branch || a.area_juridica || a.jurisdiction || summary.rama_derecho || summary.rama)
  const process = clean(a.tipo_proceso || a.process_type || summary.tipo_proceso || summary.proceso)
  const evidence = clean(a.nivel_evidencia || a.evidence_level || a.evidence_strength || summary.evidencia)
  const claim = clean(a.pretension_principal || a.claim || a.objective || summary.pretension_principal || summary.pretension)
  const uniquePublic = new Set(publicSources.value.map(source => source.source_id)).size
  return [
    { label: 'Pretensión principal', value: claim },
    { label: 'Tipo de proceso', value: process },
    { label: 'Rama jurídica', value: branch },
    { label: 'Nivel de evidencia', value: spanishLevel(evidence) },
    { label: 'Documentos del caso', value: String(props.documentCount) },
    { label: 'Fuentes jurídicas', value: props.publicSourceCount === null ? String(uniquePublic) : String(props.publicSourceCount) }
  ].filter(item => item.value)
})
function spanishLevel(value) {
  const key = value.toLowerCase()
  return ({ low: 'Bajo', medium: 'Medio', high: 'Alto', critical: 'Crítico', unknown: 'No identificado' })[key] || value
}

const factGroups = computed(() => {
  const facts = props.facts.length ? props.facts : contentItems(props.analysis?.facts, 'analysis-fact').map(item => ({ fact_id: item.key, text: item.text, status: 'unclear', source_ids: [] }))
  const groups = [
    { key: 'supported', title: 'Hechos con respaldo documental', note: 'Hechos vinculados a documentos autorizados del caso.', items: [] },
    { key: 'alleged', title: 'Hechos alegados', note: 'Los siguientes hechos provienen del relato del caso y aún requieren corroboración documental.', items: [] },
    { key: 'pending', title: 'Hechos pendientes de corroboración', note: 'La información disponible no permite determinar su respaldo documental.', items: [] }
  ]
  facts.forEach((fact, index) => {
    const sources = linkedPrivateSources(fact)
    const status = sources.length && fact.status === 'supported' ? 'supported'
      : ['alleged', 'disputed'].includes(fact.status) || (fact.status === 'supported' && !sources.length) ? 'alleged' : 'pending'
    const text = clean(fact.text || fact.description)
    if (!text) return
    groups.find(group => group.key === status).items.push({
      key: fact.fact_id || `fact-${index}`, text, sources,
      statusLabel: fact.status === 'disputed' ? 'Controvertido · requiere corroboración' : 'Pendiente de corroboración'
    })
  })
  return groups
})

const issues = computed(() => contentItems(props.analysis?.issues || props.analysis?.problemas_juridicos, 'issue'))
const norms = computed(() => contentItems(props.analysis?.law || props.analysis?.normas_probables, 'norm').map(item => {
  if (item.record) return { ...item, title: clean(item.record.title || item.record.name || item.record.norm || item.record.norma) || item.text,
    description: clean(item.record.description || item.record.summary || item.record.relevance || item.record.materia) }
  const [title, ...rest] = item.text.split('\n')
  return { ...item, title, description: rest.join('\n') }
}))

const jurisprudence = computed(() => groupedJurisprudence(safeSources.value).map((group, index) => {
  const sources = publicSources.value.filter(source => source.document_id === group.document_id ||
    (!group.document_id && (source.display_title || source.title) === group.title))
  const pages = [...new Set(group.pages)].sort((a, b) => a - b)
  return { ...group, key: group.document_id || `${group.title}-${index}`, pages,
    source: sources[0] || null }
}))
const observations = computed(() => contentItems(props.analysis?.observations || props.analysis?.informacion_faltante, 'observation'))

function parseDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}/.test(value)) return null
  const date = new Date(`${value.slice(0, 10)}T00:00:00Z`)
  return Number.isNaN(date.getTime()) ? null : date
}
function displayDate(date) { return new Intl.DateTimeFormat('es-PE', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(date).replace('.', '').toUpperCase() }
const timeline = computed(() => {
  const factsById = new Map(props.facts.map(fact => [fact.fact_id, fact]))
  const raw = props.timelineData.length ? props.timelineData : props.facts.filter(fact => fact.date).map(fact => ({ date: fact.date, description: fact.text, fact_id: fact.fact_id, source_ids: fact.source_ids }))
  const events = new Map()
  raw.forEach((event, index) => {
    const date = parseDate(event.date)
    const text = clean(event.description || event.text)
    if (!date || !text) return
    const fact = factsById.get(event.fact_id)
    const sources = linkedPrivateSources({ source_ids: event.source_ids || fact?.source_ids })
    const key = `${date.toISOString().slice(0, 10)}|${text.toLocaleLowerCase()}`
    if (!events.has(key)) events.set(key, { key: key || `timeline-${index}`, date, isoDate: date.toISOString().slice(0, 10),
      displayDate: displayDate(date), text, sources, documented: sources.length > 0 && (fact?.status === 'supported' || !fact) })
  })
  return [...events.values()].sort((a, b) => a.date - b.date)
})
function pageRange(pages) {
  if (!pages.length) return ''
  if (pages.length === 1) return String(pages[0])
  const contiguous = pages.every((page, index) => index === 0 || page === pages[index - 1] + 1)
  return contiguous ? `${pages[0]}–${pages[pages.length - 1]}` : pages.join(', ')
}
const hasAnalysisContent = computed(() => overview.value.length || factGroups.value.some(group => group.items.length) ||
  issues.value.length || norms.value.length || jurisprudence.value.length || observations.value.length || timeline.value.length)
</script>

<style scoped>
.analysis-editorial{width:100%;min-width:0;display:flex;flex-direction:column;gap:30px;padding:clamp(20px,3vw,38px);box-sizing:border-box;background:linear-gradient(180deg,#fff 0%,#fcfdfd 100%);border:1px solid #e0e7ee;border-radius:14px;color:#263b52}
.analysis-header{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;padding-bottom:22px;border-bottom:1px solid #e2e8ef}.analysis-eyebrow,.section-eyebrow{margin:0 0 9px;color:#8a6a37;font-size:.64rem;font-weight:750;letter-spacing:.12em}.analysis-eyebrow{display:flex;align-items:center;gap:9px}.analysis-eyebrow span{width:22px;height:1px;background:#b08a4c}.analysis-header h2,.section-heading h3{margin:0;color:#17375e;font-family:Georgia,'Times New Roman',serif;font-weight:600}.analysis-header h2{font-size:clamp(1.65rem,2vw,2rem);line-height:1.25}.analysis-intro,.section-heading>p:last-child{margin:8px 0 0;color:#6c7988;font-size:.9rem;line-height:1.65}.analysis-status{display:inline-flex;align-items:center;gap:8px;flex-shrink:0;padding:8px 12px;border:1px solid #d8e7dd;border-radius:999px;background:#f7faf8;color:#587161;font-size:.75rem;font-weight:650}.analysis-status span{width:7px;height:7px;border-radius:50%;background:#668b70}.analysis-empty{margin:0;color:#65768a;line-height:1.65}.analysis-section{min-width:0}.section-heading{margin-bottom:17px}.section-eyebrow{margin-bottom:7px;font-size:.59rem}.section-heading h3{font-size:1.35rem;line-height:1.35}.section-heading>p:last-child{max-width:760px;font-size:.86rem}.overview-strip{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));margin:0;border-top:1px solid #e4eaf0;border-bottom:1px solid #e4eaf0}.overview-item{min-width:0;padding:14px 18px 14px 0}.overview-item+ .overview-item{padding-left:18px;border-left:1px solid #e4eaf0}.overview-item:nth-child(n+4){border-top:1px solid #e4eaf0}.overview-item dt{margin:0 0 6px;color:#788696;font-size:.68rem;font-weight:650}.overview-item dd{margin:0;color:#17375e;font-size:.94rem;font-weight:600;line-height:1.5;overflow-wrap:anywhere}.fact-editorial-group+.fact-editorial-group{margin-top:27px}.subsection-heading{display:flex;align-items:flex-start;gap:11px;margin-bottom:5px}.subsection-heading h4{margin:0;color:#263d55;font-size:.88rem;font-weight:750;letter-spacing:.02em}.subsection-heading p{margin:4px 0 0;color:#768392;font-size:.8rem;line-height:1.55}.fact-state-mark{width:9px;height:9px;margin-top:4px;border:1.5px solid #6e8d78;border-radius:50%;flex:none}.state-alleged{border-color:#b08a4c}.state-pending{border-color:#8492a1}.fact-list,.editorial-question-list{margin:0;padding:0;list-style:none}.fact-row,.editorial-question-list li{display:grid;grid-template-columns:36px minmax(0,1fr);gap:12px;padding:16px 0;border-bottom:1px solid #e8edf2}.editorial-number{padding-top:2px;color:#a17c43;font-family:Georgia,serif;font-size:.85rem;font-weight:600;letter-spacing:.02em}.fact-copy{min-width:0}.fact-copy :deep(.markdown-body),.editorial-question-list :deep(.markdown-body),.norm-row :deep(.markdown-body),.observation-row :deep(.markdown-body),.timeline-copy :deep(.markdown-body){font-size:.92rem;line-height:1.72;color:#3f4f60}.fact-copy :deep(p),.editorial-question-list :deep(p),.norm-row :deep(p),.observation-row :deep(p),.timeline-copy :deep(p){margin:0 0 8px}.fact-copy :deep(p:last-child),.norm-row :deep(p:last-child),.timeline-copy :deep(p:last-child){margin-bottom:0}.fact-pending{display:inline-block;margin-top:5px;padding:3px 8px;border:1px solid #e8dfcb;border-radius:999px;background:#fcfaf5;color:#80683d;font-size:.69rem;font-weight:600}.fact-source-list{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-top:9px}.source-prefix{color:#798695;font-size:.76rem}.source-reference{padding:3px 5px;border:0;border-radius:4px;background:transparent;color:#315c83;font-family:inherit;font-size:.77rem;font-weight:600;line-height:1.5;text-align:left;cursor:pointer}.source-reference:hover{background:#edf3f7;color:#17375e}.source-reference:focus-visible{outline:2px solid #b08a4c;outline-offset:2px}.analysis-two-column{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:34px;align-items:start}.analysis-two-column .analysis-section{min-width:0}.editorial-question-list li{padding:13px 0}.editorial-question-list :deep(.markdown-body){color:#33485f}.norm-list,.jurisprudence-list{border-top:1px solid #e5eaf0}.norm-row,.jurisprudence-row{display:grid;grid-template-columns:26px minmax(0,1fr);gap:11px;padding:14px 0;border-bottom:1px solid #e5eaf0}.norm-mark{color:#b08a4c;font-family:Georgia,serif;font-size:1.1rem}.norm-row h4,.jurisprudence-row h4{margin:0 0 5px;color:#263d55;font-size:.9rem;font-weight:700;line-height:1.45;overflow-wrap:anywhere}.jurisprudence-row{grid-template-columns:minmax(0,1fr) auto;align-items:start;gap:16px}.jurisprudence-court{margin:0 0 10px;color:#677788;font-size:.79rem}.jurisprudence-locator{display:flex;gap:10px;margin:5px 0 0;color:#33485f;font-size:.78rem;line-height:1.5}.jurisprudence-locator span{min-width:145px;color:#7c8794}.observation-list{border-top:1px solid #e5eaf0}.observation-row{display:grid;grid-template-columns:15px minmax(0,1fr);gap:10px;padding:12px 0;border-bottom:1px solid #e8edf2}.observation-row>span{color:#b08a4c;font-size:1.1rem;line-height:1.3}.case-timeline{position:relative;display:grid;gap:0;margin:0;padding:0;list-style:none}.case-timeline::before{content:"";position:absolute;top:10px;bottom:12px;left:6px;width:1px;background:#d9e2e9}.timeline-event{position:relative;display:grid;grid-template-columns:minmax(120px,160px) auto minmax(0,1fr);align-items:start;gap:8px 16px;padding:0 0 24px 26px}.timeline-marker{position:absolute;top:5px;left:0;width:13px;height:13px;border:2px solid #789280;border-radius:50%;background:#fff;z-index:1}.timeline-event.is-alleged .timeline-marker{border-color:#b08a4c}.timeline-event time{color:#17375e;font-size:.76rem;font-weight:750;letter-spacing:.04em}.timeline-status{justify-self:start;padding:2px 7px;border:1px solid #d9e5dc;border-radius:999px;color:#627967;background:#f7faf7;font-size:.65rem;font-weight:600;white-space:nowrap}.is-alleged .timeline-status{border-color:#e8dfcb;background:#fcfaf5;color:#80683d}.timeline-copy{grid-column:1/-1;min-width:0}.timeline-copy .source-reference{margin-top:5px}.analysis-editorial :deep(.citation-inline),.analysis-editorial :deep(.citation-link){display:inline;position:relative;top:-.07em;margin:0 .13em;padding:.08em .36em;border:1px solid #d7e2ec;border-radius:4px;background:#f1f5f8;color:#1b496f;font-family:inherit;font-size:.76em;font-weight:700;line-height:1.2;white-space:nowrap;cursor:pointer}.analysis-editorial :deep(.citation-inline:hover),.analysis-editorial :deep(.citation-link:hover){background:#e3edf5;border-color:#b9cddb}.analysis-editorial :deep(.citation-inline:focus-visible),.analysis-editorial :deep(.citation-link:focus-visible){outline:2px solid #315c97;outline-offset:2px}
@media(max-width:980px){.analysis-two-column{grid-template-columns:1fr;gap:28px}.overview-strip{grid-template-columns:repeat(2,minmax(0,1fr))}.overview-item:nth-child(n+3){border-top:1px solid #e4eaf0}.overview-item:nth-child(odd){padding-left:0;border-left:0}.overview-item:nth-child(even){padding-left:16px;border-left:1px solid #e4eaf0}}
@media(max-width:640px){.analysis-editorial{gap:25px;padding:20px 16px;border-radius:10px}.analysis-header{align-items:flex-start;flex-direction:column;gap:14px}.overview-strip{grid-template-columns:1fr}.overview-item,.overview-item+ .overview-item,.overview-item:nth-child(n+3),.overview-item:nth-child(odd),.overview-item:nth-child(even){padding:12px 0;border-left:0;border-top:1px solid #e4eaf0}.overview-item:first-child{border-top:0}.fact-row,.editorial-question-list li{grid-template-columns:29px minmax(0,1fr);gap:8px}.jurisprudence-row{grid-template-columns:1fr;gap:8px}.jurisprudence-locator{display:block}.jurisprudence-locator span{display:block;min-width:0}.timeline-event{grid-template-columns:1fr;gap:7px}.timeline-copy{grid-column:1}.timeline-status{white-space:normal}}
</style>
