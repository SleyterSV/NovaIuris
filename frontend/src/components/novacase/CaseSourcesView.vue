<template>
  <section class="case-sources" aria-label="Fuentes del caso">
    <section v-if="privateDocuments.length">
      <h3>Fuentes del caso</h3>
      <ul><li v-for="group in privateDocuments" :key="group.key">
        <strong>{{ group.title }}</strong>
        <button type="button" @click="$emit('select-source', group.sources[0])">Ver documento fuente</button>
      </li></ul>
    </section>
    <section v-if="legalDocuments.length">
      <h3>Fuentes jurídicas verificadas</h3>
      <ul><li v-for="group in legalDocuments" :key="group.key">
        <strong>{{ group.title }}</strong>
        <span v-if="group.court">{{ group.court }}</span>
        <div v-for="source in group.sources" :key="source.source_id" class="legal-unit">
          <span>{{ unitLabel(source) }}</span>
          <span v-if="source.page_start">pág. {{ source.page_start }}</span>
          <button type="button" @click="$emit('select-source', source)">Ver fuente</button>
        </div>
      </li></ul>
    </section>
    <p v-if="!privateDocuments.length && !legalDocuments.length">No se identificaron fuentes verificadas para este caso.</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { normalizeSources } from '@/utils/sourceContract.js'
import { sourceUnitLabel } from '@/utils/novacasePresentation.js'

const props = defineProps({ sources: { type:Array, default:() => [] }, caseId: { type:String, default:null } })
defineEmits(['select-source'])

const sources = computed(() => normalizeSources(props.sources, props.caseId))
function groupByDocument(items) {
  const groups = new Map()
  for (const source of items) {
    const title = source.display_title || source.title
    if (!title?.trim()) continue
    const key = source.document_id || title
    if (!groups.has(key)) groups.set(key, { key, title, court:source.court || source.issuer || source.entity, sources:[] })
    groups.get(key).sources.push(source)
  }
  return [...groups.values()]
}
const privateDocuments = computed(() => groupByDocument(sources.value.filter(source =>
  ['case', 'private_case'].includes(source.source_scope))))
const legalDocuments = computed(() => groupByDocument(sources.value.filter(source =>
  source.source_scope === 'public_legal')))
function unitLabel(source) {
  return sourceUnitLabel(source) || source.section || 'Unidad jurídica'
}
</script>

<style scoped>
.case-sources{display:grid;gap:24px;color:#20364f}.case-sources h3{font:600 1.1rem Georgia,serif;margin:0 0 12px}.case-sources ul{list-style:none;padding:0;margin:0;display:grid;gap:12px}.case-sources li{display:grid;gap:5px;border:1px solid #dfe7ed;border-radius:10px;padding:15px;overflow-wrap:anywhere}.case-sources li>strong{font-weight:650}.case-sources li>span,.legal-unit span{color:#61758a;font-size:.85rem}.legal-unit{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding-top:6px}.case-sources button{justify-self:start;border:0;background:none;padding:0;color:#17446d;font:600 .85rem Inter,system-ui,sans-serif;cursor:pointer}.case-sources button:hover{text-decoration:underline}.case-sources button:focus-visible{outline:2px solid #b68a3a}
</style>
