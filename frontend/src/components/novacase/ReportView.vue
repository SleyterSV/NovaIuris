<template>
  <section class="report-view" aria-labelledby="report-title">
    <header class="report-header">
      <div class="report-heading">
        <p class="eyebrow">NOVACASE · INFORME JURÍDICO</p>
        <h2 id="report-title">{{ title }}</h2>
        <p class="intro">Documento de análisis preparado para revisión profesional.</p>
        <div v-if="report" class="report-meta">
          <span v-if="generatedDate">Generado: {{ generatedDate }}</span>
          <span>{{ wordCount }} palabras</span>
        </div>
      </div>
    </header>

    <div v-if="report" class="toolbar" aria-label="Acciones del informe">
      <button type="button" class="action secondary" @click="copyReport" :disabled="actionBusy">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="8" y="8" width="11" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h2"/></svg>
        {{ copied ? 'Copiado' : 'Copiar informe' }}
      </button>
      <button type="button" class="action secondary" @click="printReport" :disabled="actionBusy">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 9V3h12v6M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 15h12v6H6z"/></svg>
        Imprimir
      </button>
      <button type="button" class="action primary" @click="saveFile('pdf')"
        :disabled="!caseId || !taskId || actionBusy">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 3v12m-4-4 4 4 4-4M4 17v4h16v-4"/></svg>
        {{ exportBusy === 'pdf' ? 'Descargando PDF…' : 'Descargar PDF' }}
      </button>
      <button type="button" class="action secondary" @click="saveFile('docx')"
        :disabled="!caseId || !taskId || actionBusy">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 3v12m-4-4 4 4 4-4M4 17v4h16v-4"/></svg>
        {{ exportBusy === 'docx' ? 'Descargando DOCX…' : 'Descargar DOCX' }}
      </button>
    </div>
    <p v-if="actionMessage" class="action-message" role="alert">{{ actionMessage }}</p>
    <p v-if="reportStatus === 'failed'" class="action-message" role="status">
      {{ reportError?.message || 'No se pudo preparar el informe final. El análisis estructurado permanece disponible.' }}
    </p>

    <article v-if="report" class="report-paper">
      <MarkdownRenderer :content="displayReport" :citations="usedCitations" :sources="usedSources"
        :case-id="caseId" @select-citation="openCitation" />
      <section v-if="referenceGroups.length" class="report-references" aria-labelledby="references-title">
        <h3 id="references-title">Fuentes utilizadas</h3>
        <p>Documentos del caso y fuentes jurídicas citadas en el informe.</p>
        <div v-for="group in referenceGroups" :key="group.label" class="reference-group">
          <h4>{{ group.label }}</h4>
          <ol>
            <li v-for="entry in group.items" :key="entry.source.source_id">
              <span class="reference-number">{{ entry.label }}</span>
              <button type="button" class="reference-action" @click="selectedSource = entry.source">
                <strong>{{ entry.source.display_title || entry.source.title }}</strong>
                <small v-if="entry.detail">{{ entry.detail }}</small>
              </button>
            </li>
          </ol>
        </div>
      </section>
    </article>
    <div v-else class="empty-report" role="status">
      <h3>{{ reportStatus === 'failed' ? 'El informe no está disponible' : 'No hay informe disponible' }}</h3>
      <p>El análisis estructurado del caso permanece disponible en las demás secciones.</p>
    </div>
    <SourceModal :source="selectedSource" :case-id="caseId" @close="selectedSource = null" />
    <span class="sr-only" aria-live="polite">{{ copyMessage }}</span>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import SourceModal from '@/components/common/SourceModal.vue'
import { normalizeSources } from '@/utils/sourceContract.js'
import { sourceHumanLabel, presentableText } from '@/utils/novacasePresentation.js'
import { reportForReading, reportUsedSources } from '@/utils/caseReportPresentation.js'
import { prepareCaseExport, downloadCasePdf, downloadCaseDocx } from '@/services/caseExport.js'

const props = defineProps({
  report: { type: String, default: '' },
  reportDocument: { type: Object, default: () => ({}) },
  citations: { type: Array, default: () => [] },
  sources: { type: Array, default: () => [] },
  caseId: { type: String, default: null },
  taskId: { type: String, default: null },
  reportStatus: { type: String, default: 'not_requested' },
  reportError: { type: Object, default: null },
  documentCount: { type: Number, default: 0 },
  publicSourceCount: { type: Number, default: 0 }
})
const selectedSource = ref(null)
const copied = ref(false)
const copyMessage = ref('')
const actionMessage = ref('')
const exportBusy = ref('')
const actionBusy = computed(() => Boolean(exportBusy.value))
let copyReset
onBeforeUnmount(() => clearTimeout(copyReset))

const reportData = computed(() => props.reportDocument || {})
const title = computed(() => presentableText(reportData.value.title || 'Informe jurídico'))
const allCitations = computed(() => Array.isArray(reportData.value.citations) ? reportData.value.citations : props.citations)
const allSources = computed(() => Array.isArray(reportData.value.sources) ? reportData.value.sources : props.sources)
const displayReport = computed(() => reportForReading(props.report))
const usedCitations = computed(() => allCitations.value.filter(item =>
  /^\[\d+\]$/.test(item?.label || '') && displayReport.value.includes(item.label)))
const usedSources = computed(() => normalizeSources(
  reportUsedSources(usedCitations.value, allSources.value), props.caseId))
const generatedDate = computed(() => {
  const date = new Date(reportData.value.generated_at)
  return reportData.value.generated_at && !Number.isNaN(date.valueOf())
    ? new Intl.DateTimeFormat('es-PE', { dateStyle: 'long' }).format(date) : ''
})
const wordCount = computed(() => displayReport.value ? displayReport.value.split(/\s+/).length : 0)
const referenceGroups = computed(() => {
  const byId = new Map(usedSources.value.map(source => [source.source_id, source]))
  const groups = [
    { label: 'DOCUMENTOS DEL CASO', items: [] },
    { label: 'FUENTES JURÍDICAS', items: [] }
  ]
  const seen = new Set()
  for (const citation of usedCitations.value) {
    if (seen.has(citation.source_id)) continue
    const source = byId.get(citation.source_id)
    if (!source) continue
    seen.add(citation.source_id)
    const isPrivate = ['case', 'private_case'].includes(source.source_scope)
    const detail = sourceHumanLabel({ ...source, display_title: '', title: '' })
      .replace(/^\s*·\s*/, '') || (isPrivate ? 'Documento del caso' : '')
    groups[isPrivate ? 0 : 1].items.push({ source, label: citation.label, detail })
  }
  return groups.filter(group => group.items.length)
})
function openCitation(citation) {
  selectedSource.value = usedSources.value.find(source => source.source_id === citation.source_id) || null
}
async function copyReport() {
  actionMessage.value = ''
  if (!navigator.clipboard?.writeText) {
    actionMessage.value = 'No fue posible copiar el informe en este navegador.'
    return
  }
  try {
    await navigator.clipboard.writeText(displayReport.value)
    copied.value = true
    copyMessage.value = 'Informe copiado.'
    clearTimeout(copyReset)
    copyReset = setTimeout(() => { copied.value = false }, 1800)
  } catch {
    actionMessage.value = 'No fue posible copiar el informe.'
  }
}
async function printReport() {
  actionMessage.value = ''
  try {
    if (props.taskId && props.caseId) await prepareCaseExport(props.caseId, props.taskId)
    window.print()
  } catch {
    actionMessage.value = 'No fue posible preparar el informe para imprimir.'
  }
}
async function saveFile(format) {
  if (!props.caseId || !props.taskId || actionBusy.value) return
  actionMessage.value = ''
  exportBusy.value = format
  try {
    const blob = format === 'pdf'
      ? await downloadCasePdf(props.caseId, props.taskId)
      : await downloadCaseDocx(props.caseId, props.taskId)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `informe-juridico-novacase.${format}`
    document.body.appendChild(link)
    link.click()
    link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch {
    actionMessage.value = 'No fue posible generar el documento. Inténtalo nuevamente.'
  } finally {
    exportBusy.value = ''
  }
}
</script>

<style scoped>
.report-view{width:100%;min-width:0;padding:clamp(18px,3vw,30px);border:1px solid #dce5ee;border-radius:14px;background:#fff;color:#26384b}
.action svg{width:15px;height:15px;flex:none}
.report-header{display:flex;justify-content:space-between;gap:20px;padding-bottom:20px;border-bottom:1px solid #dce5ee}.report-heading{width:100%;max-width:900px;margin:auto}.eyebrow{margin:0 0 9px;color:#92713c;font-size:.68rem;font-weight:750;letter-spacing:.1em}.report-header h2{margin:0;color:#17324f;font:600 clamp(1.45rem,3vw,2rem)/1.3 Georgia,serif;overflow-wrap:break-word}.intro{margin:9px 0;color:#65758a;font-size:.9rem}.report-meta{display:flex;flex-wrap:wrap;gap:6px 17px;margin-top:15px;color:#6b7888;font-size:.75rem}
.toolbar{display:flex;justify-content:flex-end;flex-wrap:wrap;gap:8px;max-width:900px;margin:16px auto 0}.action{display:inline-flex;align-items:center;gap:7px;border:1px solid #cfdae4;border-radius:7px;background:#fff;padding:9px 12px;color:#244a6a;font:600 .78rem/1.2 system-ui,sans-serif;cursor:pointer;transition:background .16s,border-color .16s}.action:hover{background:#f1f5f8;border-color:#aebfd0}.action.primary{border-color:#17375e;background:#17375e;color:#fff}.action.primary:hover{background:#244a72}.action:focus-visible,.reference-action:focus-visible{outline:2px solid #b68a3a;outline-offset:2px}.action:disabled{cursor:not-allowed;opacity:.55}.action-message{max-width:900px;margin:10px auto 0;padding:8px 12px;border-left:2px solid #b68a3a;background:#fbf8f0;color:#634f2b;font-size:.82rem}.report-paper{width:100%;max-width:900px;margin:24px auto 0;font-size:.98rem;line-height:1.72}.report-paper :deep(.markdown-body h1){display:none}.report-paper :deep(.markdown-body h2){font-family:Georgia,serif;font-weight:600}.report-paper :deep(.citation-inline){display:inline;position:relative;top:-.07em;margin:0 .13em;padding:.08em .36em;border:1px solid #d7e2ec;border-radius:4px;background:#f1f5f8;color:#1b496f;font-family:inherit;font-size:.76em;font-weight:700;line-height:1.2;white-space:nowrap;cursor:pointer}.report-paper :deep(.citation-inline:hover){background:#e3edf5;border-color:#b9cddb}.report-paper :deep(.citation-inline:focus-visible){outline:2px solid #315c97;outline-offset:2px}
.report-references{margin-top:35px;padding-top:25px;border-top:1px solid #dce5ee}.report-references h3{margin:0;color:#17324f;font:600 1.25rem Georgia,serif}.report-references>p{margin:6px 0 20px;color:#65758a;font-size:.86rem}.reference-group{margin-top:18px}.reference-group h4{margin:0 0 8px;color:#92713c;font:700 .7rem system-ui,sans-serif;letter-spacing:.09em}.reference-group ol{list-style:none;margin:0;padding:0}.reference-group li{display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-top:1px solid #e8edf2}.reference-number{min-width:27px;color:#244a6a;font-weight:700;font-size:.83rem}.reference-action{display:grid;gap:4px;padding:0;border:0;background:none;text-align:left;color:#26384b;cursor:pointer}.reference-action:hover strong{text-decoration:underline}.reference-action strong{font-size:.88rem;font-weight:650}.reference-action small{font-size:.75rem;color:#718096}.empty-report{min-height:220px;display:grid;align-content:center;justify-items:center;text-align:center;color:#64748b}.empty-report h3{margin:0;color:#193653;font:600 1.2rem Georgia,serif}.empty-report p{max-width:540px}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}@media(max-width:700px){.report-header{flex-direction:column}.toolbar{justify-content:flex-start}.report-view{padding:17px}}@media print{.report-view{border:0;padding:0}.report-header{border:0}.toolbar,.action-message{display:none!important}.report-paper{max-width:none}.report-references{break-before:auto}}
/* Screen-only finish: preserve the existing printed report and export content. */
@media screen {
  .report-paper :deep(.citation-inline){position:static;vertical-align:baseline;margin:0 .16em;padding:.1em .42em;border:1px solid #d6e4ef;border-radius:6px;background:#eef5fa;color:#285b82;font-size:.76em;font-weight:650;line-height:1.1;letter-spacing:0;box-shadow:0 1px 2px #17375e06;text-decoration:none}
  .report-paper :deep(.citation-inline:hover){background:#e3eff8;border-color:#b2cde1;color:#173f65}
  .report-paper :deep(.citation-inline:focus-visible){outline:2px solid #497ca3;outline-offset:3px;background:#e3eff8}
  .report-references{margin-top:40px;padding-top:28px;border-top-color:#dbe5ee}
  .report-references h3{font-size:1.3rem;line-height:1.35}
  .report-references>p{margin:9px 0 24px;color:#68798b;font-size:.88rem;line-height:1.65}
  .reference-group{margin-top:24px}
  .reference-group+.reference-group{margin-top:30px}
  .reference-group h4{display:flex;align-items:center;gap:10px;margin:0 0 12px;color:#8a6d41;font-size:.7rem;line-height:1.5;letter-spacing:.08em}
  .reference-group h4::before{content:'';flex:none;width:5px;height:16px;border-radius:3px;background:#d9c39e}
  .reference-group li{display:grid;grid-template-columns:34px minmax(0,1fr);gap:14px;align-items:start;padding:15px 10px;border-top:1px solid #e5ecf2}
  .reference-group li:last-child{border-bottom:1px solid #e5ecf2}
  .reference-number{display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;min-width:0;margin-top:2px;padding:4px 5px;border:1px solid #d6e4ef;border-radius:7px;background:#eef5fa;color:#285b82;font-size:.76rem;font-weight:700;line-height:1.35}
  .reference-action{grid-template-columns:minmax(0,1fr) auto;column-gap:18px;row-gap:5px;width:100%;min-width:0;padding:2px 4px;border-radius:6px;font-family:inherit;line-height:1.55}
  .reference-action strong{grid-column:1;min-width:0;color:#253f59;font-size:.91rem;font-weight:650;overflow-wrap:break-word;word-break:normal}
  .reference-action small{grid-column:1;min-width:0;color:#718195;font-size:.78rem;line-height:1.6;overflow-wrap:break-word}
  .reference-action::after{content:'Ver fuente ↗';grid-column:2;grid-row:1 / span 2;align-self:center;padding:4px 7px;border-radius:5px;color:#386b91;background:#f3f7fa;font-size:.74rem;font-weight:600;white-space:nowrap}
  .reference-action:hover strong{text-decoration:none;color:#285b82}
  .reference-action:hover::after{background:#e6f0f7;color:#173f65}
  .reference-action:focus-visible{outline:2px solid #497ca3;outline-offset:3px}
}
@media screen and (max-width:600px){
  .reference-group li{grid-template-columns:32px minmax(0,1fr);gap:10px;padding:14px 0}
  .reference-action{grid-template-columns:minmax(0,1fr)}
  .reference-action::after{grid-column:1;grid-row:auto;justify-self:start;margin-top:3px}
}
</style>

<style>
@media print {
  @page{size:A4;margin:2.3cm}
  body:has(.report-view) *{visibility:hidden!important}
  body:has(.report-view) .report-view,
  body:has(.report-view) .report-view *{visibility:visible!important}
  body:has(.report-view) .report-view{position:absolute;top:0;left:0;width:100%;border:0;box-shadow:none}
  body:has(.report-view) .report-view .toolbar,
  body:has(.report-view) .report-view .action-message{display:none!important}
}
</style>
