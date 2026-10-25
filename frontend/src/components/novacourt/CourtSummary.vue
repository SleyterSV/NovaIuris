<template>
  <section class="court-summary">
    <header class="summary-header">
      <div class="summary-header-content">
        <span class="section-eyebrow">RESUMEN JUDICIAL</span>
        <h2>Panorama del caso</h2>
        <p>Síntesis estructurada del escenario judicial y de los principales factores identificados durante la simulación.</p>
      </div>
    </header>

    <dl class="summary-information" aria-label="Indicadores del análisis judicial">
      <div v-for="item in summaryItems" :key="item.label" class="summary-card" :class="`summary-card--${item.tone}`">
        <span class="summary-card-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path :d="item.icon" /></svg>
        </span>
        <dt>{{ item.label }}</dt>
        <dd>{{ item.value }}</dd>
      </div>
    </dl>

    <section v-if="panoramaText" class="legal-overview" aria-labelledby="legal-overview-title">
      <span class="section-eyebrow">PANORAMA JURÍDICO</span>
      <h3 id="legal-overview-title">Síntesis del caso</h3>
      <p>{{ panoramaText }}</p>
    </section>
  </section>
</template>


<script setup>

import {
    computed
} from "vue"


/* =========================================
   PROPS
========================================= */

const props = defineProps({

    summary: {

        type: Object,

        default: () => ({})

    },
    courtStatus: { type: String, default: '' },
    graphStatus: { type: String, default: '' },
    simulationStatus: { type: String, default: '' },
    issueCount: { type: Number, default: 0 }

})


/* =========================================
   INFORMACIÓN RESUMIDA
========================================= */

const summaryItems = computed(() => [
    {
        label: "Tipo de proceso",
        value: props.summary.proceso || "No identificado con la información disponible.",
        tone: "process",
        icon: "M3 7.5A1.5 1.5 0 0 1 4.5 6H9l2 2h8.5A1.5 1.5 0 0 1 21 9.5v8a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z"
    },
    {
        label: "Problemas jurídicos",
        value: String(props.issueCount),
        tone: "issues",
        icon: "M12 3 4 7v5c0 5 3.4 8 8 9 4.6-1 8-4 8-9V7zm-3 9 2 2 4-4"
    },
    {
        label: "Simulación jurídica",
        value: props.simulationStatus === 'ready' ? 'Disponible' : 'No disponible',
        tone: props.simulationStatus === 'ready' ? 'available' : 'simulation',
        icon: "M4 18V6m0 12h16M7 15l4-4 3 2 5-6"
    },
    {
        label: 'Grafo jurídico',
        value: props.graphStatus === 'ready' ? 'Disponible' : 'No disponible',
        tone: 'graph',
        icon: 'M7 7 17 6M7 8l4 8m2 0 4-9M6 5a2 2 0 1 0 0 4 2 2 0 0 0 0-4m12-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4m-6 12a2 2 0 1 0 0 4 2 2 0 0 0 0-4'
    }
])

const panoramaText = computed(() => {
    const value = props.summary
    if (typeof value === 'string') return value.trim()
    if (!value || typeof value !== 'object' || Array.isArray(value)) return ''
    const text = value.resumen || value.resumen_ejecutivo || value.overview || value.summary
    return typeof text === 'string' ? text.trim() : ''
})

</script>


<style scoped>
.court-summary{display:grid;gap:24px;min-width:0;width:100%;color:#26384b}
.summary-header{position:relative;padding:0 0 20px 17px;border-bottom:1px solid #dce5ee}
.summary-header::before{position:absolute;top:2px;bottom:20px;left:0;width:3px;border-radius:3px;background:linear-gradient(180deg,#b08a4c,#d9c59e);content:''}
.summary-header-content{max-width:790px;min-width:0}
.section-eyebrow{display:block;margin:0 0 8px;color:#987544;font-size:.68rem;font-weight:750;letter-spacing:.12em;line-height:1.3}
.summary-header h2{margin:0;color:#17375e;font:600 clamp(1.7rem,2.7vw,2.15rem)/1.23 Georgia,'Times New Roman',serif}
.summary-header p{max-width:68ch;margin:10px 0 0;color:#61748a;font-size:.92rem;line-height:1.65}
.summary-information{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:0;padding:0}
.summary-card{display:grid;grid-template-columns:40px minmax(0,1fr);column-gap:13px;align-content:start;min-width:0;padding:17px 16px;border:1px solid #dfe6ec;border-radius:12px;background:#fff;box-shadow:0 3px 12px #17375e05}
.summary-card-icon{grid-row:1 / span 2;display:grid;place-items:center;box-sizing:border-box;width:40px;height:40px;border:1px solid var(--icon-border);border-radius:11px;background:var(--icon-tint);color:var(--icon-color)}
.summary-card-icon svg{width:21px;height:21px}
.summary-card dt{align-self:end;color:#61748a;font-size:.66rem;font-weight:750;letter-spacing:.035em;line-height:1.45;text-transform:uppercase}
.summary-card dd{min-width:0;margin:7px 0 0;color:#17375e;font:600 1.02rem/1.45 Georgia,'Times New Roman',serif;overflow-wrap:break-word;word-break:normal;hyphens:none}
.summary-card--process{--icon-color:#9b742e;--icon-tint:#fcf6e9;--icon-border:#efe2c5}
.summary-card--issues{--icon-color:#346da3;--icon-tint:#edf5fc;--icon-border:#d9e9f6}
.summary-card--simulation{--icon-color:#7d62a4;--icon-tint:#f3effa;--icon-border:#e5dcf2}
.summary-card--available{--icon-color:#3b8067;--icon-tint:#edf7f1;--icon-border:#d9eade}
.summary-card--graph{--icon-color:#467b9c;--icon-tint:#edf7fa;--icon-border:#d7eaf1}
.summary-card--issues dd{font-size:1.45rem;line-height:1.15}
.legal-overview{padding-top:18px;border-top:1px solid #e5eaf0}
.legal-overview h3{margin:5px 0 8px;color:#17375e;font:600 1.15rem/1.35 Georgia,'Times New Roman',serif}
.legal-overview p{max-width:78ch;margin:0;color:#4f6378;font-size:.91rem;line-height:1.7;white-space:pre-line;overflow-wrap:anywhere}
@media(max-width:960px){.summary-information{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:620px){.court-summary{gap:20px}.summary-header{padding:0 0 17px 14px}.summary-header p{font-size:.88rem}.summary-information{grid-template-columns:minmax(0,1fr);gap:10px}.summary-card{padding:15px}.legal-overview{padding-top:15px}}
</style>
