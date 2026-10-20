<script setup>
import { computed } from 'vue'
const props = defineProps({ stage: { type: String, default: '' }, progress: { type: Number, default: 0 }, stages: { type: Array, default: () => [] } })
defineEmits(['cancel'])
// The provider drafts before validating citations; keep the visible order truthful.
const steps = [
  { label: 'Interpretando la consulta', description: 'Identifico el problema jurídico.', ids: ['query_analysis'] },
  { label: 'Preparando búsqueda semántica', description: 'Relaciono conceptos y términos jurídicos.', ids: ['embedding'] },
  { label: 'Buscando en el corpus jurídico', description: 'Recupero y priorizo fuentes pertinentes.', ids: ['retrieval', 'fusion', 'reranking', 'context'] },
  { label: 'Redactando la síntesis', description: 'Organizo la respuesta con las fuentes recuperadas.', ids: ['answer'] },
  { label: 'Verificando referencias', description: 'Compruebo las citas y su trazabilidad.', ids: ['citations'] }
]
const currentIndex = computed(() => Math.max(0, steps.findIndex(step => step.ids.includes(props.stage))))
const visibleSteps = computed(() => steps.map((step, index) => ({ ...step, status: index < currentIndex.value ? 'completed' : index === currentIndex.value ? 'active' : 'pending' })))
const progressWidth = computed(() => Math.max(0, Math.min(100, Number(props.progress) || 0)))
</script>

<template>
  <section class="search-progress" aria-live="polite" aria-label="Progreso de búsqueda jurídica">
    <div class="progress-top"><div><span class="eyebrow">NOVA SEARCH</span><h2>{{ visibleSteps[currentIndex].label }}</h2><p>{{ visibleSteps[currentIndex].description }}</p></div><button type="button" @click="$emit('cancel')">Cancelar búsqueda</button></div>
    <div class="track" role="progressbar" aria-label="Progreso de búsqueda" aria-valuemin="0" aria-valuemax="100" :aria-valuenow="progressWidth"><span :style="{ width: `${progressWidth}%` }" /></div>
    <ol><li v-for="(item, index) in visibleSteps" :key="item.label" :class="item.status"><span class="step-mark" aria-hidden="true">{{ item.status === 'completed' ? '✓' : String(index + 1).padStart(2, '0') }}</span><div><strong>{{ item.label }}</strong><small>{{ item.description }}</small></div></li></ol>
  </section>
</template>

<style scoped>
.search-progress{padding:54px 0 36px;color:#25364a}.progress-top{display:flex;align-items:start;justify-content:space-between;gap:24px}.eyebrow{font-size:.7rem;letter-spacing:.15em;font-weight:750;color:#a0824b}.progress-top h2{margin:14px 0 12px;color:#17375e;font:500 clamp(2rem,3vw,2.7rem)/1.16 Georgia,serif}.progress-top p{margin:0 0 32px;color:#647486;line-height:1.65}.progress-top button{border:0;background:none;padding:8px;color:#315c97;font-family:inherit;font-size:.8rem;font-weight:600;cursor:pointer;white-space:nowrap}.progress-top button:focus-visible{outline:2px solid #315c97}.track{height:4px;overflow:hidden;border-radius:9px;background:#e1e8ef}.track span{display:block;height:100%;background:#aa8952;transition:width .25s ease}ol{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:15px;margin:28px 0 0;padding:0;list-style:none}li{display:flex;align-items:start;gap:9px;min-width:0;color:#85919d}.step-mark{display:grid;place-items:center;flex:none;width:26px;height:26px;border:1px solid #cbd6df;border-radius:50%;font-size:.7rem;font-weight:700}li.completed .step-mark{background:#a8844e;border-color:#a8844e;color:white}li.active .step-mark{border-color:#315c97;color:#17375e}li strong,li small{display:block;line-height:1.4}li strong{font-size:.78rem;font-weight:650}li small{font-size:.7rem;margin-top:4px}li.active strong{color:#17375e}@media(max-width:900px){ol{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:620px){.progress-top{flex-direction:column;gap:4px}ol{grid-template-columns:1fr}}
</style>
