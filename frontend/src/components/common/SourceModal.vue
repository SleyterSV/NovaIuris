<template>
  <Teleport to="body">
    <div v-if="safeSource" class="source-backdrop" role="presentation" @click.self="emit('close')">
      <section class="source-modal" role="dialog" aria-modal="true" aria-labelledby="source-title">
        <header><div><span class="eyebrow">FUENTE {{ safeSource.source_scope === 'case' ? 'DEL EXPEDIENTE' : 'JURÍDICA' }}</span><h2 id="source-title">{{ safeSource.title }}</h2></div>
          <button class="close" type="button" aria-label="Cerrar ficha de fuente" @click="emit('close')">×</button></header>
        <dl>
          <div v-for="field in fields" :key="field.label"><dt>{{ field.label }}</dt><dd>{{ field.value }}</dd></div>
        </dl>
        <section v-if="safeSource.excerpt" class="excerpt"><h3>Fragmento utilizado</h3><blockquote>{{ safeSource.excerpt }}</blockquote></section>
        <details v-if="metadataEntries.length" class="metadata"><summary>Metadata disponible</summary><dl>
          <div v-for="[key, value] in metadataEntries" :key="key"><dt>{{ humanize(key) }}</dt><dd>{{ stringify(value) }}</dd></div>
        </dl></details>
        <footer>
          <span v-if="safeSource.source_scope === 'case'">{{ safeSource.document_id }}<template v-if="safeSource.page_start"> · pág. {{ safeSource.page_start }}</template></span>
          <a v-if="safeSource.official_url" :href="safeSource.official_url" target="_blank" rel="noopener noreferrer">Abrir fuente oficial <span aria-hidden="true">↗</span></a>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { normalizeSource } from '@/utils/sourceContract.js'
const props = defineProps({ source: { type: Object, default: null }, caseId: { type: String, default: null } })
const emit = defineEmits(['close'])
const safeSource = computed(() => normalizeSource(props.source, props.caseId))
const fields = computed(() => {
  const s = safeSource.value || {}
  return [
    ['Tipo', s.source_type], ['Entidad', s.entity], ['Tribunal', s.court],
    ['Expediente', s.case_number], ['Número', s.document_number], ['Artículo', s.article],
    ['Fundamento', s.legal_basis], ['Fecha', s.date], ['Documento', s.title],
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
onUnmounted(() => window.removeEventListener('keydown', escape))
</script>

<style scoped>
.source-backdrop{position:fixed;inset:0;z-index:1200;background:#0b1d2dcc;display:grid;place-items:center;padding:20px}.source-modal{width:min(680px,100%);max-height:min(85vh,850px);overflow:auto;background:#fff;border:1px solid #dbe3eb;border-radius:12px;box-shadow:0 24px 80px #06172e55;padding:26px;color:#24364a}.source-modal header{display:flex;justify-content:space-between;gap:20px;border-bottom:1px solid #e5eaf0;padding-bottom:18px}.eyebrow{font-size:.68rem;letter-spacing:.1em;color:#8a6b37;font-weight:700}.source-modal h2{font:600 1.25rem/1.4 Georgia,serif;color:#17324f;margin:7px 0 0}.close{font-size:1.5rem;border:0;background:transparent;color:#536477;cursor:pointer}.source-modal dl{display:grid;grid-template-columns:1fr 1fr;gap:13px 20px;margin:20px 0}.source-modal dl div{min-width:0}.source-modal dt{font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:#718096}.source-modal dd{margin:3px 0 0;overflow-wrap:anywhere;color:#24364a}.excerpt{background:#f5f7f9;border-left:3px solid #b68a3a;padding:13px 16px}.excerpt h3{font-size:.8rem;margin:0 0 8px;color:#17324f}.excerpt blockquote{margin:0;white-space:pre-wrap;line-height:1.65}.metadata{margin-top:16px}.metadata summary{cursor:pointer;color:#38516c}.metadata dl{margin-bottom:0}footer{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:20px;color:#718096;font-size:.78rem}footer a{color:#244c73;font-weight:600;text-decoration:none}footer a:hover{text-decoration:underline}@media(max-width:560px){.source-modal{padding:20px}.source-modal dl{grid-template-columns:1fr}}
</style>
