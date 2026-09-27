<script setup>
defineProps({ stage: { type: String, default: '' }, progress: { type: Number, default: 0 }, stages: { type: Array, default: () => [] }, counts: { type: Object, default: () => ({}) } })
defineEmits(['cancel'])
</script>

<template>
  <section class="search-progress" aria-live="polite" aria-label="Progreso de búsqueda jurídica">
    <div class="progress-top"><div><span class="eyebrow">INVESTIGACIÓN EN CURSO</span><h2>{{ stages.find(item => item.id === stage)?.label || 'Preparando la búsqueda' }}</h2></div><button type="button" @click="$emit('cancel')">Cancelar búsqueda</button></div>
    <div class="track" role="progressbar" aria-label="Etapas completadas" :aria-valuemin="0" :aria-valuemax="100" :aria-valuenow="progress"><span :style="{ width: `${progress}%` }" /></div>
    <div class="counts"><span v-if="counts.retrieved_count !== undefined">{{ counts.retrieved_count }} fuentes recuperadas</span><span v-if="counts.reranked_count !== undefined">{{ counts.reranked_count }} priorizadas</span><span v-if="counts.used_source_count !== undefined">{{ counts.used_source_count }} utilizadas</span></div>
    <ol><li v-for="item in stages" :key="item.id" :class="item.status"><span aria-hidden="true">{{ item.status === 'completed' ? '✓' : item.status === 'running' ? '●' : item.status === 'skipped' ? '–' : '○' }}</span>{{ item.label }}</li></ol>
  </section>
</template>

<style scoped>
.search-progress{padding:22px;background:#fff;border:1px solid #dfe6ed;border-radius:12px;color:#25364a}.progress-top{display:flex;align-items:center;justify-content:space-between;gap:18px}.eyebrow{font-size:.65rem;letter-spacing:.12em;font-weight:750;color:#8a7046}.progress-top h2{margin:7px 0 12px;color:#17375e;font:600 1.12rem Georgia,serif}.progress-top button{border:1px solid #cbd5df;border-radius:7px;background:white;padding:8px 12px;color:#315c97;font-family:inherit;font-size:.76rem;font-weight:600;cursor:pointer}.track{height:6px;overflow:hidden;border-radius:9px;background:#e8edf2}.track span{display:block;height:100%;background:#315c97;transition:width .2s ease}.counts{display:flex;gap:16px;flex-wrap:wrap;margin-top:10px;color:#637286;font-size:.73rem}ol{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px 18px;margin:20px 0 0;padding:0;list-style:none}li{display:flex;gap:8px;align-items:center;color:#8793a1;font-size:.76rem}li.completed{color:#32664d}li.running{color:#17375e;font-weight:700}li span{width:16px}@media(max-width:620px){.progress-top{align-items:flex-start;flex-direction:column}ol{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
