<template>
  <section v-if="items.length" class="sources-list" aria-label="Fuentes utilizadas">
    <h3>Fuentes utilizadas</h3>
    <ul><li v-for="item in items" :key="item.source.source_id">
      <div class="source-entry">
        <span class="source-citations"><CitationLink v-for="citation in item.citations" :key="citation.citation_id"
          :citation="citation" :label="citation.label" @select="$emit('select-citation', $event)" /></span>
        <button type="button" class="source-copy" @click="$emit('select', item.source)">
          <strong>{{ item.source.title }}</strong><small>{{ location(item.source) }}</small>
        </button>
      </div>
    </li></ul>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { normalizeSources } from '@/utils/sourceContract.js'
import CitationLink from '@/components/common/CitationLink.vue'
const props = defineProps({ sources: { type: Array, default: () => [] }, citations: { type: Array, default: () => [] }, caseId: { type: String, default: null } })
defineEmits(['select', 'select-citation'])
const items = computed(() => {
  const sources = normalizeSources(props.sources, props.caseId)
  return sources.map(source => ({ source, citations: props.citations.filter(c => c.source_id === source.source_id) }))
})
const location = source => [source.source_type, source.article, source.legal_basis, source.page_start ? `pág. ${source.page_start}` : null, source.section].filter(Boolean).join(' · ')
</script>

<style scoped>
.sources-list{border-top:1px solid #e5eaf0;margin-top:22px;padding-top:15px}.sources-list h3{margin:0 0 9px;color:#17324f;font:600 .82rem/1.4 Inter,system-ui,sans-serif}.sources-list ul{list-style:none;margin:0;padding:0;display:grid;gap:3px}.source-entry{width:100%;display:flex;align-items:flex-start;text-align:left;gap:10px;padding:8px;border-radius:6px;color:#26384b}.source-citations{display:flex;gap:2px}.source-copy{display:grid;gap:2px;text-align:left;border:0;background:transparent;cursor:pointer;color:inherit}.source-copy:hover strong{text-decoration:underline}.source-copy:focus-visible{outline:2px solid #b68a3a}.source-copy strong{font-size:.78rem;font-weight:600}.source-copy small{color:#778598;font-size:.7rem}
</style>
