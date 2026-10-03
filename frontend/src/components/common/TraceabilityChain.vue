<script setup>
defineProps({ issue:{ type:Object, default:null }, facts:{ type:Array, default:() => [] }, sources:{ type:Array, default:() => [] } })
const emit = defineEmits(['select-source'])
</script>

<template>
  <div v-if="issue || facts.length || sources.length" class="chain" aria-label="Cadena de trazabilidad">
    <span v-if="issue" class="node">Problema jurídico <strong>{{ issue.text }}</strong></span>
    <template v-for="fact in facts" :key="fact.fact_id"><span class="arrow" aria-hidden="true">→</span><span class="node">Hecho <strong>{{ fact.text }}</strong></span></template>
    <template v-for="source in sources" :key="source.source_id"><span class="arrow" aria-hidden="true">→</span><button class="node source" type="button" @click="emit('select-source',source)">Fuente <strong>{{ source.title }}</strong><small v-if="source.page_start">pág. {{ source.page_start }}</small><small v-if="source.section">{{ source.section }}</small></button></template>
  </div>
</template>

<style scoped>
.chain{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin:12px 0;color:#445b72}.node{display:inline-flex;align-items:baseline;gap:5px;max-width:100%;padding:5px 8px;border:1px solid #dae2e8;border-radius:5px;background:#f8fafb;font-size:11px}.node strong{font-weight:600;overflow-wrap:anywhere}.node small{color:#738396}.arrow{color:#ad8c59}.source{color:#183d61;text-align:left;cursor:pointer}.source:hover{text-decoration:underline}.source:focus-visible{outline:2px solid #b68a3a}
</style>
