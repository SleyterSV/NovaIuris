<template>
  <main class="case-sources" aria-labelledby="case-sources-title">
    <header class="sources-header">
      <div>
        <p class="sources-eyebrow">MYKE · NOVACASE</p>
        <h2 id="case-sources-title">Fuentes del caso</h2>
        <p class="sources-subtitle">Documentos aportados y fuentes jurídicas verificadas utilizadas durante el análisis del expediente.</p>
      </div>
      <span v-if="legalDocuments.length" class="verified-status"><span aria-hidden="true"></span>Fuentes verificadas</span>
    </header>

    <dl v-if="privateDocuments.length || legalDocuments.length" class="sources-summary" aria-label="Resumen de fuentes">
      <div v-if="privateDocuments.length"><dt>Documentos del expediente</dt><dd>{{ privateDocuments.length }}</dd></div>
      <div v-if="legalUnitCount"><dt>Fuentes jurídicas</dt><dd>{{ legalUnitCount }} <span>unidades verificadas</span></dd></div>
      <div v-if="legalDocuments.length"><dt>Documentos jurídicos</dt><dd>{{ legalDocuments.length }}</dd></div>
      <div v-if="commonCourt"><dt>Órgano</dt><dd class="summary-court">{{ commonCourt }}</dd></div>
    </dl>

    <section v-if="privateDocuments.length" class="source-section" aria-labelledby="private-sources-title">
      <header class="section-heading">
        <p class="section-eyebrow">DOCUMENTACIÓN DEL CASO</p>
        <h3 id="private-sources-title">Documentos del expediente</h3>
        <p>Documentación incorporada al caso y utilizada como soporte fáctico.</p>
      </header>
      <ol class="document-list">
        <li v-for="(group, index) in privateDocuments" :key="group.key" class="document-row">
          <span class="row-number" aria-hidden="true">{{ number(index + 1) }}</span>
          <div class="document-content">
            <h4>{{ group.title }}</h4>
            <p class="document-meta">
              <span>{{ group.kind }}</span>
              <span v-if="group.pagesUsed">{{ group.pagesUsed }} {{ group.pagesUsed === 1 ? 'página utilizada' : 'páginas utilizadas' }}</span>
            </p>
            <p class="document-origin">Documento aportado al expediente</p>
            <ul v-if="group.sources.length" class="unit-list private-unit-list">
              <li v-for="source in group.sources" :key="source.source_id">
                <span class="unit-citation" v-if="citationFor(source)">{{ citationFor(source) }}</span>
                <span class="unit-location">{{ pageLabel(source) || 'Documento' }}</span>
                <button type="button" class="source-action" :aria-label="`Abrir ${group.title}, ${pageLabel(source) || 'documento'}`" @click="selectSource(source)">Abrir <span aria-hidden="true">↗</span></button>
              </li>
            </ul>
          </div>
        </li>
      </ol>
    </section>

    <section v-if="legalDocuments.length" class="source-section legal-section" aria-labelledby="legal-sources-title">
      <header class="section-heading">
        <p class="section-eyebrow">CORPUS JURÍDICO V2</p>
        <h3 id="legal-sources-title">Fuentes jurídicas verificadas</h3>
        <p>Jurisprudencia y normativa verificadas desde Legal Knowledge V2, agrupadas por documento y unidad consultada.</p>
      </header>
      <ol class="legal-document-list">
        <li v-for="(group, index) in legalDocuments" :key="group.key" class="legal-document-row">
          <span class="row-number" aria-hidden="true">{{ number(index + 1) }}</span>
          <div class="legal-document-content">
            <header class="legal-document-header">
              <div>
                <h4>{{ group.title }}</h4>
                <p v-if="group.court" class="court-name">{{ group.court }}</p>
              </div>
              <span class="unit-count">{{ group.sources.length }} {{ group.sources.length === 1 ? 'unidad consultada' : 'unidades consultadas' }}</span>
            </header>
            <p class="document-kind">{{ group.kind }}</p>
            <ul class="unit-list legal-unit-list" aria-label="Unidades consultadas">
              <li v-for="source in group.sources" :key="unitIdentity(source)">
                <span class="unit-citation" v-if="citationFor(source)">{{ citationFor(source) }}</span>
                <span class="legal-unit-name">{{ unitLabel(source) }}</span>
                <span class="unit-page">{{ pageLabel(source) }}</span>
                <button type="button" class="source-action" :aria-label="`Abrir ${group.title}, ${unitLabel(source)}${pageLabel(source) ? `, ${pageLabel(source)}` : ''}`" @click="selectSource(source)">Abrir <span aria-hidden="true">↗</span></button>
              </li>
            </ul>
          </div>
        </li>
      </ol>
    </section>

    <p v-if="!privateDocuments.length && !legalDocuments.length" class="sources-empty">No se identificaron fuentes verificadas para este caso.</p>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { argumentCitationForSource, sourceUnitLabel } from '@/utils/novacasePresentation.js'
import { normalizeSources } from '@/utils/sourceContract.js'

const props = defineProps({
  sources: { type: Array, default: () => [] },
  citations: { type: Array, default: () => [] },
  caseId: { type: String, default: null }
})
const emit = defineEmits(['select-source'])

const sources = computed(() => deduplicateCanonicalUnits(normalizeSources(props.sources, props.caseId)))
const privateDocuments = computed(() => groupByDocument(sources.value.filter(source =>
  ['case', 'private_case'].includes(source.source_scope)), false))
const legalDocuments = computed(() => groupByDocument(sources.value.filter(source =>
  source.source_scope === 'public_legal'), true))
const legalUnitCount = computed(() => legalDocuments.value.reduce((count, group) => count + group.sources.length, 0))
const commonCourt = computed(() => {
  const courts = [...new Set(legalDocuments.value.map(group => group.court).filter(Boolean))]
  return courts.length === 1 ? courts[0] : ''
})

function number(value) { return String(value).padStart(2, '0') }
function unitIdentity(source) {
  return source.source_scope === 'public_legal'
    ? `${source.document_id}:${source.unit_id}`
    : source.source_id
}
function deduplicateCanonicalUnits(items) {
  const seen = new Set()
  return items.filter(source => {
    const key = unitIdentity(source)
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}
function titleOf(source) {
  const raw = source.display_title || source.title || 'Documento del expediente'
  if (source.source_scope === 'public_legal') return raw.trim()
  return raw.replace(/^\s*\d+[_\s-]+/, '').replace(/\.[a-z0-9]{2,5}$/i, '')
    .replace(/_+/g, ' ').replace(/\s{2,}/g, ' ').trim() || 'Documento del expediente'
}
function groupByDocument(items, legal) {
  const groups = new Map()
  for (const source of items) {
    const title = titleOf(source)
    const key = legal ? (source.document_id || title) : (source.document_id || source.metadata?.document_id || source.source_id)
    if (!groups.has(key)) groups.set(key, {
      key,
      title,
      court: legal ? (source.court || source.issuer || source.entity || '') : '',
      kind: legal ? legalKind(source) : privateKind(title),
      sources: []
    })
    groups.get(key).sources.push(source)
  }
  return [...groups.values()].map(group => ({
    ...group,
    sources: group.sources,
    pagesUsed: legal ? 0 : uniquePageCount(group.sources)
  }))
}
function uniquePageCount(items) {
  const pages = new Set()
  for (const source of items) {
    if (source.page_start !== null && source.page_start !== undefined && Number.isFinite(Number(source.page_start))) {
      const end = Number(source.page_end || source.page_start)
      for (let page = Number(source.page_start); page <= end; page += 1) pages.add(page)
    }
  }
  return pages.size
}
function legalKind(source) {
  const type = String(source.source_type || source.metadata?.source_type || '').toLowerCase()
  if (['judgment', 'jurisprudence', 'cassation'].includes(type) || /^(stc|casación|casacion|sentencia)/i.test(titleOf(source))) {
    const authority = String(source.court || source.issuer || source.entity || '')
    return /constitucional/i.test(authority) || /^stc/i.test(titleOf(source)) ? 'Jurisprudencia constitucional' : 'Jurisprudencia'
  }
  if (['law', 'statute', 'regulation', 'norm'].includes(type)) return 'Normativa'
  return 'Fuente jurídica'
}
function privateKind(title) {
  const value = title.toLocaleLowerCase()
  if (value.includes('contrato')) return 'Documento contractual'
  if (value.includes('memorando') || value.includes('memorándum')) return 'Comunicación administrativa'
  return 'Documento del expediente'
}
function unitLabel(source) { return sourceUnitLabel(source) || source.section || 'Unidad jurídica' }
function pageLabel(source) {
  if (!source.page_start) return ''
  return source.page_end && source.page_end !== source.page_start
    ? `págs. ${source.page_start}–${source.page_end}` : `pág. ${source.page_start}`
}
function citationFor(source) {
  return argumentCitationForSource(source, props.citations, sources.value, props.caseId)?.label || ''
}
function selectSource(source) { emit('select-source', source) }
</script>

<style scoped>
.case-sources{--source-border:#dfe6ec;--source-navy:#263d55;--source-muted:#68798a;--source-blue:#315c83;display:grid;gap:36px;width:100%;max-width:1240px;margin:0 auto;color:var(--source-navy)}
.sources-header{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;padding-bottom:22px;border-bottom:1px solid var(--source-border)}
.sources-eyebrow,.section-eyebrow{margin:0 0 8px;color:#987744;font-size:.68rem;font-weight:750;letter-spacing:.13em;text-transform:uppercase}
.sources-header h2{margin:0;color:#20364f;font:600 clamp(1.75rem,2.4vw,2.25rem)/1.2 Georgia,'Times New Roman',serif}
.sources-subtitle,.section-heading>p:last-child{max-width:780px;margin:9px 0 0;color:var(--source-muted);font-size:.92rem;line-height:1.7}
.verified-status{display:inline-flex;align-items:center;gap:8px;flex:none;padding:7px 11px;border:1px solid #dce7df;border-radius:999px;background:#f8fbf8;color:#55745d;font-size:.72rem;font-weight:650}
.verified-status span{width:6px;height:6px;border-radius:50%;background:#72917a}
.sources-summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));margin:0;border-block:1px solid var(--source-border);background:#fcfbf8}
.sources-summary>div{min-width:0;padding:14px 18px;border-right:1px solid var(--source-border)}.sources-summary>div:last-child{border-right:0}
.sources-summary dt{margin:0 0 5px;color:#7e6d52;font-size:.65rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}
.sources-summary dd{margin:0;color:#263d55;font:600 1.1rem/1.35 Georgia,'Times New Roman',serif}.sources-summary dd span{font:500 .75rem/1.4 Inter,system-ui,sans-serif;color:var(--source-muted)}.sources-summary .summary-court{font:600 .88rem/1.45 Inter,system-ui,sans-serif}
.source-section{min-width:0}.section-heading{margin-bottom:18px}.section-heading h3{margin:0;color:#263d55;font:600 1.42rem/1.35 Georgia,'Times New Roman',serif}
.document-list,.legal-document-list,.unit-list{margin:0;padding:0;list-style:none}
.document-row,.legal-document-row{display:grid;grid-template-columns:42px minmax(0,1fr);gap:16px;min-width:0;padding:20px 0;border-bottom:1px solid var(--source-border)}.document-row:first-child,.legal-document-row:first-child{border-top:1px solid var(--source-border)}
.row-number{padding-top:3px;color:#a17c43;font:600 .9rem Georgia,'Times New Roman',serif}.document-content,.legal-document-content{min-width:0;max-width:1080px}
.document-content h4,.legal-document-header h4{margin:0;color:#263d55;font:600 1.08rem/1.45 Georgia,'Times New Roman',serif;overflow-wrap:break-word;word-break:normal}
.document-meta{display:flex;flex-wrap:wrap;gap:5px 13px;margin:5px 0 0;color:var(--source-muted);font-size:.8rem;line-height:1.5}.document-origin{margin:8px 0 0;color:#788696;font-size:.75rem}
.unit-list{margin-top:12px;border-top:1px solid #edf0f3}.unit-list li{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:8px 13px;min-width:0;padding:8px 0;border-bottom:1px solid #edf0f3}
.unit-citation{display:inline-flex;align-items:center;justify-content:center;min-width:25px;padding:2px 5px;border:1px solid #d7e2ec;border-radius:4px;background:#f1f5f8;color:#1b496f;font-size:.72rem;font-weight:700;line-height:1.2}
.unit-location,.legal-unit-name{min-width:0;color:#43566a;font-size:.83rem;line-height:1.45}.legal-unit-name{font-weight:600}.unit-page{color:#778594;font-size:.76rem;white-space:nowrap}
.source-action{justify-self:end;padding:4px 6px;border:0;border-radius:4px;background:transparent;color:var(--source-blue);font:600 .78rem/1.4 Inter,system-ui,sans-serif;white-space:nowrap;cursor:pointer}.source-action:hover{background:#edf3f7;color:#17375e}.source-action:focus-visible{outline:2px solid #b08a4c;outline-offset:2px}
.legal-document-row{padding-block:23px}.legal-document-header{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}.court-name{margin:3px 0 0;color:var(--source-muted);font-size:.82rem}.unit-count{flex:none;padding:4px 8px;border:1px solid #e3e8ed;border-radius:999px;background:#fafbfd;color:#647587;font-size:.69rem;line-height:1.4}.document-kind{margin:8px 0 0;color:#987744;font-size:.68rem;font-weight:700;letter-spacing:.05em;text-transform:uppercase}.legal-unit-list{margin-top:12px}.legal-unit-list li{grid-template-columns:auto minmax(0,1fr) minmax(64px,auto) auto}
.sources-empty{margin:0;padding:16px 18px;border-left:2px solid #d4c29e;background:#faf9f5;color:#637286;font-size:.88rem;line-height:1.65}
@media(max-width:700px){.case-sources{gap:28px}.sources-header{flex-direction:column;gap:13px}.sources-summary{grid-template-columns:repeat(2,minmax(0,1fr))}.sources-summary>div:nth-child(2n){border-right:0}.sources-summary>div:nth-child(n+3){border-top:1px solid var(--source-border)}.document-row,.legal-document-row{grid-template-columns:30px minmax(0,1fr);gap:10px;padding-block:17px}.legal-document-header{flex-direction:column;gap:8px}.unit-list li,.legal-unit-list li{grid-template-columns:auto minmax(0,1fr) auto;gap:7px}.unit-page{grid-column:2;grid-row:2}.source-action{grid-column:3;grid-row:1 / span 2}}
@media(max-width:420px){.unit-list li,.legal-unit-list li{grid-template-columns:auto minmax(0,1fr)}.unit-page{grid-column:2;grid-row:auto}.source-action{grid-column:2;grid-row:auto;justify-self:start;padding-left:0}.sources-summary dd{font-size:1rem}}
</style>
