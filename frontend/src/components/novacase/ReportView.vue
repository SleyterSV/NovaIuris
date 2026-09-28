<template>
  <section class="report-view" aria-labelledby="report-title">
    <header class="report-header">
      <div>
        <p class="eyebrow">NOVACASE · INFORME JURÍDICO</p>
        <h2 id="report-title">{{ reportDocument.title || 'Informe jurídico' }}</h2>
        <p class="intro">Documento de análisis preparado para revisión profesional.</p>
      </div>
      <div class="toolbar">
        <button type="button" class="primary" :disabled="!report" @click="copyReport">
          {{ copied ? 'Copiado' : 'Copiar informe' }}
        </button>
        <button type="button" :disabled="!report" @click="printReport">Imprimir</button>
        <button type="button" disabled title="Disponible en una fase posterior">PDF · próximamente</button>
        <button type="button" disabled title="Disponible en una fase posterior">DOCX · próximamente</button>
      </div>
    </header>

    <p v-if="reportStatus === 'failed'" class="partial-message" role="status">
      {{ reportError?.message || 'No se pudo preparar el informe final. El análisis estructurado permanece disponible.' }}
    </p>

    <div v-if="report" class="report-meta">
      <span v-if="reportDocument.case_id">Caso {{ reportDocument.case_id }}</span>
      <span v-if="generatedDate">Generado {{ generatedDate }}</span>
      <span>{{ wordCount }} palabras</span>
    </div>

    <article v-if="report" class="report-paper">
      <MarkdownRenderer
        :content="report"
        :citations="citations"
        :sources="sources"
        :case-id="caseId"
        @select-citation="openCitation"
      />
      <SourcesList
        :sources="sources"
        :citations="citations"
        :case-id="caseId"
        @select="selectedSource = $event"
        @select-citation="openCitation"
      />
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
import SourcesList from '@/components/common/SourcesList.vue'
import SourceModal from '@/components/common/SourceModal.vue'

const props = defineProps({
  report: { type: String, default: '' },
  reportDocument: { type: Object, default: () => ({}) },
  citations: { type: Array, default: () => [] },
  sources: { type: Array, default: () => [] },
  caseId: { type: String, default: null },
  reportStatus: { type: String, default: 'not_requested' },
  reportError: { type: Object, default: null }
})

const selectedSource = ref(null)
const copied = ref(false)
const copyMessage = ref('')
let copyReset
onBeforeUnmount(() => clearTimeout(copyReset))
const reportDocument = computed(() => props.reportDocument || {})
const citations = computed(() => Array.isArray(reportDocument.value.citations)
  ? reportDocument.value.citations : props.citations)
const sources = computed(() => Array.isArray(reportDocument.value.sources)
  ? reportDocument.value.sources : props.sources)
const generatedDate = computed(() => {
  const value = reportDocument.value.generated_at
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.valueOf()) ? '' : new Intl.DateTimeFormat('es-PE', { dateStyle: 'long' }).format(date)
})
const wordCount = computed(() => props.report.trim() ? props.report.trim().split(/\s+/).length : 0)

function openCitation(citation) {
  selectedSource.value = sources.value.find(source => source.source_id === citation.source_id) || null
}

async function copyReport() {
  if (!props.report || !navigator.clipboard?.writeText) {
    copyMessage.value = 'No fue posible copiar el informe en este navegador.'
    return
  }
  try {
    await navigator.clipboard.writeText(props.report.trim())
    copied.value = true
    copyMessage.value = 'Informe copiado.'
    clearTimeout(copyReset)
    copyReset = setTimeout(() => { copied.value = false }, 1800)
  } catch {
    copyMessage.value = 'No fue posible copiar el informe.'
  }
}

function printReport() {
  if (props.report) window.print()
}
</script>

<style scoped>
.report-view{display:grid;gap:20px;width:100%;min-width:0;padding:clamp(18px,3vw,30px);border:1px solid #dce5ee;border-radius:14px;background:#fff;color:#26384b}.report-header{display:flex;align-items:flex-start;justify-content:space-between;gap:20px}.eyebrow{margin:0 0 7px;color:#92713c;font-size:.68rem;font-weight:750;letter-spacing:.1em}.report-header h2{margin:0;color:#17324f;font:600 clamp(1.35rem,3vw,1.8rem)/1.3 Georgia,serif}.intro{margin:8px 0 0;color:#65758a;font-size:.88rem}.toolbar{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:7px}.toolbar button{border:1px solid #d6dee7;border-radius:6px;background:#fff;padding:9px 12px;color:#38516c;font:600 .75rem/1.2 system-ui,sans-serif;cursor:pointer}.toolbar button.primary{border-color:#17375e;background:#17375e;color:#fff}.toolbar button:disabled{cursor:not-allowed;opacity:.48}.partial-message{margin:0;border-left:3px solid #b68a3a;background:#fbf8f0;padding:11px 14px;color:#634f2b;font-size:.85rem}.report-meta{display:flex;flex-wrap:wrap;gap:8px 18px;border-block:1px solid #e7ebef;padding:11px 0;color:#6b7888;font-size:.76rem}.report-paper{max-width:900px;width:100%;margin-inline:auto}.empty-report{min-height:220px;display:grid;align-content:center;justify-items:center;text-align:center;color:#64748b}.empty-report h3{margin:0;color:#193653;font:600 1.2rem Georgia,serif}.empty-report p{max-width:540px}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}@media(max-width:700px){.report-header{flex-direction:column}.toolbar{justify-content:flex-start}.report-view{padding:17px}}@media print{.toolbar,.partial-message{display:none!important}.report-view{border:0;padding:0}.report-paper{max-width:none}}
</style>
