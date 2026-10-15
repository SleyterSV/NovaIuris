<template>
  <Teleport to="body">
    <div v-if="safeSource" class="source-backdrop" role="presentation" @click.self="emit('close')">
      <section class="source-modal" role="dialog" aria-modal="true" aria-labelledby="source-title">
        <header><div><span class="eyebrow">FUENTE {{ ['case', 'private_case'].includes(safeSource.source_scope) ? 'DEL EXPEDIENTE' : 'JURÍDICA' }}</span><h2 id="source-title">{{ unitDetail?.display_title || safeSource.title }}</h2></div>
          <button class="close" type="button" aria-label="Cerrar ficha de fuente" @click="emit('close')">×</button></header>
        <dl>
          <div v-for="field in fields" :key="field.label"><dt>{{ field.label }}</dt><dd>{{ field.value }}</dd></div>
        </dl>
        <section v-if="presentation.loading" class="excerpt" role="status">Cargando unidad jurídica completa…</section>
        <section v-else-if="presentation.text" class="excerpt"><h3>{{ presentation.heading }}</h3><blockquote>{{ presentation.text }}</blockquote></section>
        <p v-if="presentation.warning" class="detail-error" role="alert">No se pudo cargar la unidad completa. Se muestra únicamente el fragmento citado.</p>
        <details v-if="metadataEntries.length" class="metadata"><summary>Metadata disponible</summary><dl>
          <div v-for="[key, value] in metadataEntries" :key="key"><dt>{{ humanize(key) }}</dt><dd>{{ stringify(value) }}</dd></div>
        </dl></details>
        <footer>
          <span v-if="['case', 'private_case'].includes(safeSource.source_scope)">{{ safeSource.document_id }}<template v-if="safeSource.page_start"> · pág. {{ safeSource.page_start }}</template></span>
          <a v-if="safeSource.official_url" :href="safeSource.official_url" target="_blank" rel="noopener noreferrer">ABRIR FUENTE OFICIAL <span aria-hidden="true">↗</span></a>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { normalizeSource } from '@/utils/sourceContract.js'
import { legalTypeLabel, legalUnitLabel, sourceDetailPresentation } from '@/utils/legalSearchPresentation.js'
import { loadLegalUnitSource } from '@/services/legalUnitSource.js'
const props = defineProps({ source: { type: Object, default: null }, caseId: { type: String, default: null } })
const emit = defineEmits(['close'])
const safeSource = computed(() => normalizeSource(props.source, props.caseId))
const unitDetail = ref(null)
const detailStatus = ref('idle')
let activeController = null
const isV2Unit = source => ['public', 'public_legal'].includes(source?.source_scope) && Boolean(source?.metadata?.unit_type && source?.chunk_id)
watch(() => props.source, async value => {
  activeController?.abort()
  activeController = null
  unitDetail.value = null
  detailStatus.value = 'idle'
  const source = normalizeSource(value, props.caseId)
  if (!isV2Unit(source)) return
  activeController = new AbortController()
  const controller = activeController
  detailStatus.value = 'loading'
  try {
    const unit = await loadLegalUnitSource(source.chunk_id, source.document_id, { signal: controller.signal })
    if (controller.signal.aborted) return
    if (unit.unit_id !== source.chunk_id || unit.document_id !== source.document_id || typeof unit.text !== 'string') {
      throw new Error('La unidad recuperada no corresponde a la fuente citada.')
    }
    unitDetail.value = unit
    detailStatus.value = 'ready'
  } catch (error) {
    if (!controller.signal.aborted) detailStatus.value = 'error'
  }
}, { immediate: true })
const presentation = computed(() => sourceDetailPresentation(safeSource.value, unitDetail.value, detailStatus.value))
const fields = computed(() => {
  const s = safeSource.value || {}
  if (!isV2Unit(s)) {
    return [
      ['Tipo', s.source_type], ['Entidad', s.entity], ['Tribunal', s.court],
      ['Expediente', s.case_number], ['Número', s.document_number], ['Artículo', s.article],
      ['Fundamento', s.legal_basis], ['Fecha', s.date], ['Documento', s.title],
      ['Página', s.page_start ? (s.page_end && s.page_end !== s.page_start ? `${s.page_start}–${s.page_end}` : s.page_start) : null],
      ['Sección', s.section], ['Párrafo', s.paragraph]
    ].filter(([, value]) => value !== null && value !== undefined && value !== '')
      .map(([label, value]) => ({ label, value: stringify(value) }))
  }
  const unit = unitDetail.value || {}
  const metadata = s.metadata || {}
  return [
    ['Tipo jurídico', legalTypeLabel(unit.document_type || metadata.document_type || s.source_type)],
    ['Entidad', unit.issuer || s.entity], ['Tribunal', unit.court || s.court],
    ['Expediente', s.case_number], ['Número', s.document_number], ['Artículo', s.article],
    ['Fundamento', s.legal_basis], ['Unidad', isV2Unit(s) ? legalUnitLabel(unit.unit_type || metadata.unit_type, unit.unit_number || metadata.unit_number) : null],
    ['Encabezado', unit.heading || metadata.heading], ['Fecha', s.date],
    ['Documento', isV2Unit(s) ? null : s.title],
    ['Página', s.page_start ? (s.page_end && s.page_end !== s.page_start ? `${s.page_start}–${s.page_end}` : s.page_start) : null],
    ['Sección', s.section], ['Párrafo', s.paragraph]
  ].filter(([, value]) => value !== null && value !== undefined && value !== '')
    .map(([label, value]) => ({ label, value: stringify(value) }))
})
const metadataEntries = computed(() => Object.entries(safeSource.value?.metadata || {}).filter(([, value]) => value !== null && value !== undefined && value !== ''))
const stringify = value => typeof value === 'object' ? JSON.stringify(value) : String(value)
const humanize = value => String(value).replaceAll('_', ' ')
const escape = event => { if (event.key === 'Escape' && safeSource.value) emit('close') }
onMounted(() => window.addEventListener('keydown', escape))
onUnmounted(() => { activeController?.abort(); window.removeEventListener('keydown', escape) })
</script>

<style scoped>
.source-backdrop{position:fixed;inset:0;z-index:1200;background:#0b1d2dcc;display:grid;place-items:center;padding:20px}.source-modal{width:min(680px,100%);max-height:min(85vh,850px);overflow:auto;background:#fff;border:1px solid #dbe3eb;border-radius:12px;box-shadow:0 24px 80px #06172e55;padding:26px;color:#24364a}.source-modal header{display:flex;justify-content:space-between;gap:20px;border-bottom:1px solid #e5eaf0;padding-bottom:18px}.eyebrow{font-size:.68rem;letter-spacing:.1em;color:#8a6b37;font-weight:700}.source-modal h2{font:600 1.25rem/1.4 Georgia,serif;color:#17324f;margin:7px 0 0}.close{font-size:1.5rem;border:0;background:transparent;color:#536477;cursor:pointer}.source-modal dl{display:grid;grid-template-columns:1fr 1fr;gap:13px 20px;margin:20px 0}.source-modal dl div{min-width:0}.source-modal dt{font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:#718096}.source-modal dd{margin:3px 0 0;overflow-wrap:anywhere;color:#24364a}.excerpt{background:#f5f7f9;border-left:3px solid #b68a3a;padding:13px 16px}.excerpt h3{font-size:.8rem;margin:0 0 8px;color:#17324f}.excerpt blockquote{margin:0;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.65}.detail-error{color:#8b3030;font-size:.8rem;line-height:1.4}.metadata{margin-top:16px}.metadata summary{cursor:pointer;color:#38516c}.metadata dl{margin-bottom:0}footer{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:20px;color:#718096;font-size:.78rem}footer a{color:#244c73;font-weight:600;text-decoration:none}footer a:hover{text-decoration:underline}@media(max-width:560px){.source-modal{padding:20px}.source-modal dl{grid-template-columns:1fr}}
</style>
