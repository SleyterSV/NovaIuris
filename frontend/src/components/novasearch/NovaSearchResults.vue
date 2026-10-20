<script setup>
import { computed, ref } from 'vue'
import { legalTypeLabel, legalUnitLabel, cardExcerpt } from '@/utils/legalSearchPresentation.js'
import { normalizeSource } from '@/utils/sourceContract.js'
import { resultCitationNumber } from '@/utils/searchEditorial.js'
import { publicUnitReference } from '@/services/searchCaseHandoff.js'
import SourceModal from '@/components/common/SourceModal.vue'

const props = defineProps({
  results: { type: Array, default: () => [] },
  sources: { type: Array, default: () => [] },
  citationPresentation: { type: Object, default: () => ({ sources: [], numberBySource: new Map() }) }
})
const emit = defineEmits(['analyze-case'])
const selectedSource = ref(null)
const rows = computed(() => props.results.map((result, index) => {
  const source = normalizeSource(result.source) || props.sources.find(item => item.document_id === result.document_id && item.unit_id === result.unit_id) || null
  return { result, index, source, citationNumber: resultCitationNumber(result, props.citationPresentation), excerpt: cardExcerpt(result) }
}))
const isBindingPrecedent = value => value === true || value === 1 || value === '1' || (typeof value === 'string' && ['true', 'si', 'sí', 'yes'].includes(value.toLowerCase().trim()))
const locator = result => [result.unit_type ? legalUnitLabel(result.unit_type, result.unit_number) : null,
  result.page_start != null ? `pág. ${result.page_start}${result.page_end != null && result.page_end !== result.page_start ? `–${result.page_end}` : ''}` : null].filter(Boolean).join(' · ')
const dateLabel = value => {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? String(value) : new Intl.DateTimeFormat('es-PE', { day: '2-digit', month: 'long', year: 'numeric' }).format(date)
}
</script>

<template>
  <section v-if="rows.length" class="search-results" aria-labelledby="relevant-sources-title">
    <header><h2 id="relevant-sources-title">Fuentes jurídicas relevantes</h2><p>Jurisprudencia y normativa recuperadas para esta consulta.</p></header>
    <ol class="result-list"><li v-for="row in rows" :key="row.result.source_id || row.result.unit_id || row.result.id || row.index" class="result-row">
      <div class="row-index"><span v-if="row.citationNumber" class="citation-number" :aria-label="`Fuente citada ${row.citationNumber}`">[{{ row.citationNumber }}]</span><span v-else :aria-label="`Resultado ${row.index + 1}`">{{ String(row.index + 1).padStart(2, '0') }}</span></div>
      <div class="row-meta"><span class="document-type">{{ legalTypeLabel(row.result.tipo_documento, row.result.metadata) }}</span><h3>{{ row.result.titulo || 'Documento jurídico' }}</h3>
        <p v-if="row.result.organo_emisor || row.result.rama">{{ [row.result.organo_emisor, row.result.rama].filter(Boolean).join(' · ') }}</p>
        <p v-if="locator(row.result)">{{ locator(row.result) }}</p>
        <p v-if="row.result.expediente || row.result.numero">{{ [row.result.expediente, row.result.numero].filter(Boolean).join(' · ') }}</p>
        <p v-if="row.result.fecha_resolucion || row.result.fecha_publicacion">{{ dateLabel(row.result.fecha_resolucion || row.result.fecha_publicacion) }}</p>
        <p v-if="row.result.materia">{{ row.result.materia }}</p>
        <span v-if="isBindingPrecedent(row.result.precedente_vinculante)" class="precedent">Precedente vinculante</span>
      </div>
      <div class="row-excerpt"><p v-if="row.excerpt.primary">{{ row.excerpt.primary }}</p><details v-if="row.excerpt.secondary"><summary>Ver extracto relevante</summary><p>{{ row.excerpt.secondary }}</p></details></div>
      <div class="row-actions"><button v-if="row.source" type="button" @click="selectedSource = row.source">Ver fuente</button><button v-if="publicUnitReference(row.result)" type="button" class="analyze-action" @click="emit('analyze-case', row.result)">Analizar en NovaCase</button></div>
    </li></ol>
    <SourceModal :source="selectedSource" @close="selectedSource = null" />
  </section>
</template>

<style scoped>
.search-results{border-top:1px solid #dce3e9;margin-top:58px;padding-top:38px;min-width:0}.search-results h2{font:500 clamp(1.6rem,2.4vw,2.1rem)/1.2 Georgia,serif;color:#17375e;margin:0 0 9px}.search-results header>p{margin:0;color:#667587;line-height:1.6}.result-list{list-style:none;margin:26px 0 0;padding:0}.result-row{display:grid;grid-template-columns:45px minmax(190px,1.1fr) minmax(220px,1.4fr) minmax(135px,.55fr);gap:20px;align-items:start;border-top:1px solid #dce3e9;padding:23px 0;min-width:0}.result-row:last-child{border-bottom:1px solid #dce3e9}.row-index{font:600 .9rem Georgia,serif;color:#9a7a42}.citation-number{color:#315c97}.document-type{font-size:.67rem;font-weight:750;letter-spacing:.1em;text-transform:uppercase;color:#9a7a42}.row-meta,.row-excerpt{min-width:0;overflow-wrap:anywhere}.row-meta h3{font:500 1.1rem/1.35 Georgia,serif;color:#17375e;margin:6px 0 10px}.row-meta p{margin:5px 0;color:#657485;font-size:.76rem;line-height:1.5}.precedent{display:inline-block;margin-top:8px;color:#836a39;font-size:.72rem;font-weight:700}.row-excerpt{border-left:1px solid #e1e7ed;padding-left:20px;color:#374a5e;font-size:.84rem;line-height:1.7}.row-excerpt p{margin:0}.row-excerpt details{margin-top:12px}.row-excerpt summary{color:#315c97;cursor:pointer}.row-excerpt details p{margin-top:8px}.row-actions{display:grid;gap:9px;justify-items:start}.row-actions button{padding:0;border:0;background:none;color:#315c97;font-family:inherit;font-size:.78rem;font-weight:650;text-align:left;cursor:pointer}.row-actions button:hover{text-decoration:underline}.row-actions button:focus-visible{outline:2px solid #315c97;outline-offset:3px}.analyze-action{white-space:normal}@media(max-width:900px){.result-row{grid-template-columns:35px minmax(0,1fr) minmax(0,1.3fr)}.row-actions{grid-column:2/-1;display:flex;flex-wrap:wrap;gap:18px}}@media(max-width:650px){.result-row{grid-template-columns:35px minmax(0,1fr);gap:10px}.row-excerpt,.row-actions{grid-column:2;border:0;padding:0}.row-actions{display:flex}}
</style>
