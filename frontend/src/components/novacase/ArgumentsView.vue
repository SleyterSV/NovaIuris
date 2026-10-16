<template>
  <section class="arguments-view" aria-label="Argumentos del caso">
    <header class="section-heading">
      <p class="eyebrow">MYKE · NOVACASE</p>
      <h2>Argumentos jurídicos</h2>
      <p>Se distinguen las fuentes verificadas de las hipótesis que requieren revisión profesional.</p>
    </header>

    <section v-for="section in sections" :key="section.key" class="argument-section">
      <h3>{{ section.label }}</h3>
      <div class="argument-grid">
        <article v-for="(entry, index) in section.items" :key="index" class="argument-card">
          <span class="argument-number">{{ String(index + 1).padStart(2, '0') }}</span>
          <h4 v-if="entry.title">{{ presentableText(entry.title) }}</h4>
          <div v-if="entry.argument || entry.text" class="argument-body">
            <span class="field-label">Argumento</span>
            <MarkdownRenderer :content="presentableText(entry.argument || entry.text)" />
          </div>
          <div v-if="entry.legal_basis?.length" class="argument-body">
            <span class="field-label">Fundamento jurídico</span>
            <MarkdownRenderer :content="presentableText(entry.legal_basis)" />
          </div>
          <p v-if="entry.risk" class="argument-detail"><strong>Riesgo</strong> {{ presentableText(entry.risk) }}</p>
          <p v-if="entry.strength" class="argument-detail"><strong>Solidez</strong> {{ presentableText(entry.strength) }}</p>
          <div v-if="relatedFactTexts(entry, facts).length" class="argument-body">
            <span class="field-label">Hechos de respaldo</span>
            <ul><li v-for="(fact, factIndex) in relatedFactTexts(entry, facts)" :key="factIndex">{{ presentableText(fact) }}</li></ul>
          </div>
          <div v-if="verifiedArgumentSources(entry, sources, caseId).length" class="argument-sources">
            <span class="field-label">Fuentes vinculadas</span>
            <button v-for="source in verifiedArgumentSources(entry, sources, caseId)" :key="source.source_id"
              type="button" @click="$emit('select-source', source)">
              {{ source.display_title || source.title }}<span v-if="unitLabel(source)"> · {{ unitLabel(source) }}</span><span v-if="source.page_start"> · pág. {{ source.page_start }}</span> · Ver fuente
            </button>
          </div>
          <p v-if="(entry.legal_basis?.length || entry.jurisprudence?.length ||
            ['jurisprudence_used','normative_arguments','constitutional_arguments'].includes(section.key)) &&
            !verifiedPublicArgumentSources(entry, sources).length" class="unverified">
            Fundamento jurídico preliminar — pendiente de verificación con una fuente recuperada.
          </p>
        </article>
      </div>
    </section>
    <p v-if="!sections.length" class="empty-state">No se identificaron argumentos con la información disponible.</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import { ARGUMENT_SECTION_LABELS, presentableText, relatedFactTexts, verifiedArgumentSources, verifiedPublicArgumentSources } from '@/utils/novacasePresentation.js'

const props = defineProps({
  arguments: { type: Object, default: () => ({}) },
  facts: { type: Array, default: () => [] },
  sources: { type: Array, default: () => [] },
  caseId: { type: String, default: null }
})
defineEmits(['select-source'])

const unitLabel = source => source.unit_type === 'foundation' ? `Fundamento ${source.unit_number || ''}`.trim()
  : source.unit_type === 'article' ? `Artículo ${source.unit_number || ''}`.trim()
  : source.unit_type === 'decision' ? 'Decisión'
  : source.unit_type === 'separate_opinion' ? 'Voto separado' : ''

const sections = computed(() => Object.entries(ARGUMENT_SECTION_LABELS).flatMap(([key, label]) => {
  const raw = props.arguments[key]
  const items = (Array.isArray(raw) ? raw : raw ? [raw] : []).filter(Boolean).map(item =>
    typeof item === 'string' ? { text: item } : item && typeof item === 'object' ? item : { text: String(item) })
  return items.length ? [{ key, label, items }] : []
}))
</script>

<style scoped>
.arguments-view{display:grid;gap:26px;color:#20364f;min-width:0}.section-heading h2,.argument-section h3{font-family:Georgia,serif}.section-heading h2{font-size:clamp(1.4rem,2.5vw,2rem);margin:4px 0}.section-heading p:last-child{color:#62758a;margin:8px 0 0}.eyebrow,.field-label{color:#987849;font-size:.72rem;font-weight:750;letter-spacing:.07em;text-transform:uppercase}.argument-section{display:grid;gap:14px;min-width:0}.argument-section h3{font-size:1.2rem;margin:0}.argument-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:14px;align-items:start}.argument-card{min-width:0;border:1px solid #dfe7ed;border-radius:12px;background:#fff;padding:20px;box-shadow:0 4px 16px #102d4810;overflow-wrap:anywhere}.argument-card h4{font:600 1.08rem/1.35 Georgia,serif;color:#173654;margin:8px 0 14px}.argument-number{color:#9b7740;font-size:.75rem;font-weight:750}.argument-body{margin-top:14px}.argument-body ul{padding-left:20px}.argument-detail{display:flex;gap:10px;margin:13px 0 0;color:#40566e}.argument-detail strong{min-width:58px;color:#1c3855}.argument-sources{display:grid;gap:8px;margin-top:16px}.argument-sources button{border:1px solid #b8cce0;background:#f3f8fc;color:#17446d;border-radius:7px;padding:10px;text-align:left;cursor:pointer;overflow-wrap:anywhere}.argument-sources button:hover{background:#e9f3fb}.unverified,.empty-state{border-left:3px solid #bd9556;background:#fbf8f1;padding:10px 13px;color:#6c5736;font-size:.85rem;line-height:1.5;margin:16px 0 0}
</style>
