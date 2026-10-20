<script setup>
import { computed, ref } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import SourcesList from '@/components/common/SourcesList.vue'
import SourceModal from '@/components/common/SourceModal.vue'
import { editorialCitations, sourceForCitation } from '@/utils/searchEditorial.js'

const props = defineProps({
  answer: { type: String, default: '' },
  sources: { type: Array, default: () => [] },
  citations: { type: Array, default: () => [] },
  sourceWarnings: { type: Array, default: () => [] },
  totalResults: { type: Number, default: 0 },
  rama: { type: String, default: '' }
})
const selectedSource = ref(null)
const presentation = computed(() => editorialCitations(props.answer, props.citations, props.sources))
function openCitation(citation) {
  selectedSource.value = sourceForCitation(citation, presentation.value)
}
</script>

<template>
  <section v-if="answer" class="search-answer" aria-labelledby="search-answer-title">
    <div class="context-strip" aria-label="Contexto del análisis">
      <div v-if="rama"><span>Rama jurídica</span><strong>{{ rama }}</strong></div>
      <div><span>Estado</span><strong>Análisis completado</strong></div>
      <div><span>Fuentes relevantes</span><strong>{{ totalResults }}</strong></div>
    </div>
    <header class="section-heading"><span class="eyebrow">ANÁLISIS JURÍDICO</span><h2 id="search-answer-title">Respuesta jurídica</h2>
      <p>Síntesis estructurada de la información jurídica recuperada y analizada por MYKE.</p></header>
    <div class="answer-body"><MarkdownRenderer :content="presentation.answer" :sources="presentation.sources" :citations="presentation.citations" @select-citation="openCitation" /></div>
    <p v-if="!presentation.used.length" class="citation-warning">La respuesta no incluyó citas verificables.</p>
    <p v-for="warning in sourceWarnings.filter(item => item?.code === 'VIGENCIA_FILTER_UNAVAILABLE')" :key="warning.code" class="citation-warning">{{ warning.message }}</p>
    <div class="disclaimer"><span aria-hidden="true">ⓘ</span><p>La respuesta es una síntesis generada a partir de las fuentes recuperadas por NovaSearch y debe ser contrastada con la normativa y jurisprudencia aplicable al caso concreto.</p></div>
    <SourcesList :sources="presentation.sources" :citations="presentation.citations" @select="selectedSource = $event" @select-citation="openCitation" />
    <SourceModal :source="selectedSource" @close="selectedSource = null" />
  </section>
</template>

<style scoped>
.search-answer{min-width:0;color:#152b44}.context-strip{display:flex;gap:0;flex-wrap:wrap;border-block:1px solid #dce3e9;padding:17px 0;margin-bottom:56px}.context-strip>div{display:grid;gap:5px;min-width:0;padding:0 26px;border-right:1px solid #dce3e9}.context-strip>div:first-child{padding-left:0}.context-strip>div:last-child{border:0}.context-strip span{font-size:.68rem;font-weight:700;letter-spacing:.11em;text-transform:uppercase;color:#758493}.context-strip strong{font-size:.9rem;font-weight:650;color:#183653}.section-heading h2{font:500 clamp(2rem,3vw,2.7rem)/1.15 Georgia,serif;margin:9px 0 12px}.eyebrow{font-size:.68rem;letter-spacing:.15em;font-weight:750;color:#a0824b}.section-heading p{margin:0;color:#657485;line-height:1.6}.answer-body{max-width:850px;margin:28px 0 32px;font-size:1.06rem;line-height:1.72}.answer-body :deep(.markdown-body){font-size:inherit;line-height:inherit}.answer-body :deep(.citation-inline){border:1px solid #d4e0ec;border-radius:5px;padding:1px 6px;background:#eef3f8;color:#173b61;font-size:.82em;font-weight:650;cursor:pointer;white-space:nowrap}.answer-body :deep(.citation-inline:focus-visible){outline:2px solid #315c97;outline-offset:2px}.disclaimer{display:flex;align-items:flex-start;gap:10px;padding:11px 14px;background:#faf8f3;border-left:2px solid #c2a774;color:#626a71;font-size:.78rem;line-height:1.5}.disclaimer p{margin:0}.citation-warning{color:#805d2a;font-size:.78rem}.search-answer :deep(.sources-list){margin-top:44px;border-top:1px solid #dce3e9;padding-top:24px}.search-answer :deep(.sources-list h3){font:500 1.35rem Georgia,serif;margin-bottom:18px}.search-answer :deep(.sources-list li){border-bottom:1px solid #e7ebef}.search-answer :deep(.source-entry){padding:12px 0}.search-answer :deep(.source-copy strong){font-size:.88rem}.search-answer :deep(.source-copy small){font-size:.76rem}@media(max-width:620px){.context-strip{margin-bottom:36px}.context-strip>div{padding:7px 13px}.context-strip>div:first-child{padding-left:0}.answer-body{font-size:1rem}}
</style>
