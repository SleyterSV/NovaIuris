<template>
  <section class="executive-summary" aria-labelledby="summary-title">
    <header class="summary-header">
      <div>
        <p class="eyebrow">SÍNTESIS DEL CASO</p>
        <h2 id="summary-title">Resumen ejecutivo</h2>
        <p>Síntesis de los elementos disponibles para revisión jurídica.</p>
      </div>
      <span class="summary-badge">{{ partial ? 'Análisis parcial' : 'Análisis completado' }}</span>
    </header>

    <section v-if="executiveText" class="summary-lead">
      <h3>Resumen ejecutivo</h3>
      <p>{{ executiveText }}</p>
    </section>

    <dl class="summary-facts">
      <div v-for="item in particulars" :key="item.label">
        <dt>{{ item.label }}</dt><dd>{{ item.value }}</dd>
      </div>
    </dl>

    <section v-if="keyFacts.length" class="summary-section">
      <h3>Hechos clave</h3>
      <ol><li v-for="(fact, index) in keyFacts" :key="index">{{ fact }}</li></ol>
    </section>
    <section v-if="legalIssue" class="summary-section">
      <h3>Problema jurídico</h3><p>{{ legalIssue }}</p>
    </section>
    <section v-if="mainFinding" class="summary-section">
      <h3>Hallazgo principal</h3><p>{{ mainFinding }}</p>
    </section>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { presentableText } from '@/utils/novacasePresentation.js'

const props = defineProps({
  summary: { type:Object, default:() => ({}) },
  analysis: { type:Object, default:() => ({}) },
  facts: { type:Array, default:() => [] },
  partial: { type:Boolean, default:false }
})
const readable = value => typeof value === 'string' ? presentableText(value).trim() : ''
const executiveText = computed(() => readable(props.summary.resumen || props.summary.resumen_ejecutivo ||
  (typeof props.analysis.summary === 'string' ? props.analysis.summary : '')))
const particulars = computed(() => [
  ['Rama del derecho', props.summary.rama],
  ['Tipo de proceso', props.summary.proceso || props.summary.tipo_proceso],
  ['Nivel de riesgo', props.summary.riesgo],
  ['Nivel de evidencia', props.summary.evidencia],
  ['Documentos del caso', props.summary.documentos ?? 0],
  ['Fuentes jurídicas recuperadas', props.summary.fuentes_juridicas ?? 0]
].map(([label, raw]) => ({ label, value:typeof raw === 'number' ? String(raw) : readable(raw) || 'No determinado' })))
const keyFacts = computed(() => props.facts.slice(0, 5).map(fact => readable(fact?.text || fact))
  .filter(Boolean))
const legalIssue = computed(() => readable(props.summary.problema_juridico || props.analysis.problema_juridico ||
  (Array.isArray(props.analysis.issues) ? props.analysis.issues[0] : props.analysis.issues)))
const mainFinding = computed(() => readable(props.summary.hallazgo_principal || props.summary.hallazgo))
</script>

<style scoped>
.executive-summary{display:grid;gap:26px;min-width:0;color:#26384b}.summary-header{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;padding-bottom:19px;border-bottom:1px solid #dce5ee}.eyebrow{margin:0 0 8px;color:#97774b;font-size:.69rem;font-weight:750;letter-spacing:.12em}.summary-header h2{margin:0;color:#17375e;font:600 clamp(1.55rem,2.7vw,2rem)/1.3 Georgia,serif}.summary-header p:last-child{margin:8px 0 0;color:#64758a;line-height:1.5}.summary-badge{flex:none;padding:7px 11px;border:1px solid #cdded3;border-radius:999px;background:#f3f8f4;color:#345b48;font-size:.75rem;font-weight:700}.summary-lead{max-width:82ch;padding:0 0 20px;border-bottom:1px solid #e4eaf0}.summary-lead h3,.summary-section h3{margin:0 0 9px;color:#17375e;font:600 1.15rem Georgia,serif}.summary-lead p,.summary-section p{margin:0;line-height:1.7;white-space:pre-line}.summary-facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));margin:0;border-block:1px solid #dce5ee}.summary-facts>div{min-width:0;padding:16px 18px 16px 0;border-bottom:1px solid #e8edf2}.summary-facts dt{margin-bottom:7px;color:#66788c;font-size:.72rem;font-weight:750;letter-spacing:.05em;text-transform:uppercase}.summary-facts dd{margin:0;color:#193653;font-size:.98rem;line-height:1.45;overflow-wrap:anywhere}.summary-section{max-width:82ch;padding-bottom:18px;border-bottom:1px solid #e4eaf0}.summary-section ol{margin:0;padding-left:22px;display:grid;gap:9px;line-height:1.6}@media(max-width:850px){.summary-facts{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.summary-header{flex-direction:column}.summary-facts{grid-template-columns:1fr}}
</style>
