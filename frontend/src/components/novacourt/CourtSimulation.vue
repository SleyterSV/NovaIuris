<template>
<section class="court-simulation">
  <h2>Simulación jurídica</h2>
  <p v-if="simulation.status !== 'ready'" role="status">{{ simulation.message || 'Simulación no disponible. El análisis del caso permanece disponible.' }}</p>
  <template v-else>
    <p v-if="mode === 'decision' && !participants.length" role="status">Decisión simulada no disponible.</p>
    <p>Esta simulación argumentativa se prepara para revisión profesional; no predice una resolución real.</p>
    <section v-for="participant in participants" :key="participant.title">
      <h3>{{ participant.title }}</h3>
      <MarkdownRenderer :content="participant.content" :citations="participant.citations"
        :sources="visibleSources" :case-id="caseId" @select-citation="openCitation" />
    </section>
    <SourcesList :sources="visibleSources" :citations="visibleCitations"
      :case-id="caseId" @select="selectedSource = $event" @select-citation="openCitation" />
    <SourceModal :source="selectedSource" :case-id="caseId" @close="selectedSource = null" />
  </template>
</section>
</template>
<script setup>
import { computed, ref } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import SourcesList from '@/components/common/SourcesList.vue'
import SourceModal from '@/components/common/SourceModal.vue'
const props = defineProps({ simulation: {type:Object, default:() => ({status:'not_requested'})},
  caseId: {type:String, default:null}, mode: {type:String, default:'positions'} })
const selectedSource = ref(null)
const openCitation = citation => { selectedSource.value = visibleSources.value.find(source => source.source_id === citation.source_id) || null }
const visibleCitations = computed(() => {
  const sections = props.mode === 'decision' ? [props.simulation.judge] : [props.simulation.prosecutor, props.simulation.defense]
  const sectionCitations = sections.flatMap(section => Array.isArray(section?.citations) ? section.citations : [])
  const candidates = sections.some(section => Array.isArray(section?.citations))
    ? sectionCitations : (props.simulation.citations || [])
  return [...new Map(candidates.map(citation => [citation.citation_id, citation])).values()]
})
const visibleSources = computed(() => {
  const ids = new Set(visibleCitations.value.map(citation => citation.source_id))
  return (props.simulation.sources || []).filter(source => ids.has(source.source_id))
})
const participants = computed(() => [
  { title:props.simulation.prosecutor?.role_label || 'Parte promotora', content:props.simulation.prosecutor?.content,
    citations:props.simulation.prosecutor?.citations || visibleCitations.value },
  { title:props.simulation.defense?.role_label || 'Parte contraria', content:props.simulation.defense?.content,
    citations:props.simulation.defense?.citations || visibleCitations.value },
  { title:'Decisión simulada', content:props.simulation.judicial_analysis?.content || props.simulation.judge?.content,
    citations:props.simulation.judge?.citations || visibleCitations.value }
].filter((participant, index) => participant.content && (props.mode === 'decision' ? index === 2 : index < 2)))
</script>
<style scoped>

/* =====================================================
   NOVACOURT · SIMULACIÓN JUDICIAL

   IDENTIDAD VISUAL

   JURÍDICA
   INSTITUCIONAL
   EDITORIAL
   SOBRIA

   PALETA

   Azul principal  #17375E
   Azul secundario #315C97
   Dorado          #B08A4C
   Fondo           #FFFFFF
   Texto           #24364A
===================================================== */


/* =====================================================
   CONTENEDOR PRINCIPAL
===================================================== */

.court-simulation {

    width: 100%;

    box-sizing: border-box;

    margin: 0;

    padding:
        42px
        48px
        48px;

    background: #FFFFFF;

}


/* =====================================================
   ENCABEZADO
===================================================== */

.simulation-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 32px;

    padding-bottom: 30px;

    border-bottom:
        1px solid
        #D9E0E8;

}


.simulation-heading {

    flex: 1;

    min-width: 0;

    max-width: 900px;

}


/* =====================================================
   EYEBROW
===================================================== */

.section-eyebrow {

    display: block;

    margin-bottom: 16px;

    color: #315C97;

    font-size: .68rem;

    font-weight: 700;

    letter-spacing: 1.45px;

    line-height: 1.2;

}


/* =====================================================
   TÍTULO PRINCIPAL
===================================================== */

.simulation-heading h2 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 2rem;

    font-weight: 500;

    line-height: 1.25;

    letter-spacing: -.25px;

}


/* =====================================================
   ACENTO
===================================================== */

.title-accent {

    width: 46px;

    height: 2px;

    margin:
        18px
        0;

    background: #315C97;

}


/* =====================================================
   DESCRIPCIÓN
===================================================== */

.simulation-heading p {

    max-width: 820px;

    margin: 0;

    color: #5E6D7E;

    font-size: .97rem;

    font-weight: 400;

    line-height: 1.85;

    letter-spacing: .01em;

}


/* =====================================================
   ESTADO
===================================================== */

.simulation-status {

    display: inline-flex;

    align-items: center;

    gap: 9px;

    flex-shrink: 0;

    margin-top: 3px;

    padding:
        8px
        0;

    border-bottom:
        1px solid
        currentColor;

    font-size: .75rem;

    font-weight: 700;

    line-height: 1.4;

    white-space: nowrap;

}


.status-dot {

    width: 7px;

    height: 7px;

    flex-shrink: 0;

    border-radius: 50%;

}


/* =====================================================
   STATUS · PROCESSING
===================================================== */

.status-processing {

    color: #315C97;

}


.status-processing .status-dot {

    background: #315C97;

    animation:
        pulse
        1.5s
        ease-in-out
        infinite;

}


/* =====================================================
   STATUS · COMPLETED
===================================================== */

.status-completed,
.status-success {

    color: #35664B;

}


.status-completed .status-dot,
.status-success .status-dot {

    background: #4D8A66;

}


/* =====================================================
   STATUS · WARNING
===================================================== */

.status-warning {

    color: #8B6A2F;

}


.status-warning .status-dot {

    background: #B08A4C;

}


/* =====================================================
   STATUS · ERROR
===================================================== */

.status-error {

    color: #9B3A3A;

}


.status-error .status-dot {

    background: #B94A4A;

}


/* =====================================================
   LOADING
===================================================== */

.simulation-loading {

    display: flex;

    align-items: flex-start;

    gap: 20px;

    min-height: 150px;

    padding:
        30px
        0;

    border-bottom:
        1px solid
        #E1E6EC;

}


.loading-indicator {

    width: 42px;

    height: 42px;

    display: flex;

    align-items: center;

    justify-content: center;

    flex-shrink: 0;

    border:
        1px solid
        #D4DDE6;

}


.loading-spinner {

    width: 20px;

    height: 20px;

    border:
        2px solid
        #DCE4EC;

    border-top-color:
        #315C97;

    border-radius: 50%;

    animation:
        spin
        .85s
        linear
        infinite;

}


.loading-content {

    display: flex;

    flex-direction: column;

    gap: 6px;

    padding-top: 1px;

}


.loading-label {

    color: #315C97;

    font-size: .65rem;

    font-weight: 700;

    letter-spacing: 1.25px;

}


.loading-content strong {

    color: #17375E;

    font-size: .97rem;

    font-weight: 700;

    line-height: 1.5;

}


.loading-content p {

    max-width: 620px;

    margin: 0;

    color: #647487;

    font-size: .9rem;

    line-height: 1.75;

}


/* =====================================================
   RESULTADO GENERAL
===================================================== */

.simulation-overview {

    display: grid;

    grid-template-columns:
        minmax(0, 1.5fr)
        minmax(280px, .85fr);

    gap: 42px;

    margin-top: 36px;

    padding-bottom: 36px;

    border-bottom:
        1px solid
        #D9E0E8;

}


/* =====================================================
   RESULTADO PRINCIPAL
===================================================== */

.overview-result {

    position: relative;

    padding-left: 22px;

}


.overview-result::before {

    content: "";

    position: absolute;

    top: 3px;

    bottom: 3px;

    left: 0;

    width: 2px;

    background: #315C97;

}


.overview-label {

    display: block;

    margin-bottom: 9px;

    color: #6F7C8B;

    font-size: .69rem;

    font-weight: 700;

    letter-spacing: 1.15px;

    text-transform: uppercase;

}


.overview-value {

    display: block;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.5rem;

    font-weight: 500;

    line-height: 1.45;

}


/* =====================================================
   MÉTRICAS
===================================================== */

.overview-metrics {

    display: grid;

    grid-template-columns:
        1fr
        1fr;

    border-left:
        1px solid
        #D9E0E8;

}


.overview-metric {

    padding:
        2px
        22px;

}


.overview-metric
    + .overview-metric {

    border-left:
        1px solid
        #D9E0E8;

}


.overview-metric span {

    display: block;

    margin-bottom: 8px;

    color: #7A8795;

    font-size: .68rem;

    font-weight: 700;

    line-height: 1.5;

}


.overview-metric strong {

    color: #315C97;

    font-size: 1.08rem;

    font-weight: 700;

    line-height: 1.4;

}


/* =====================================================
   SECCIONES
===================================================== */

.simulation-section {

    margin-top: 40px;

}


/* =====================================================
   CABECERA DE SECCIÓN
===================================================== */

.section-header {

    display: grid;

    grid-template-columns:
        48px
        minmax(0, 1fr);

    gap: 18px;

    margin-bottom: 24px;

}


.section-index {

    color: #B08A4C;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: .82rem;

    font-weight: 600;

    letter-spacing: .1em;

    line-height: 1.4;

}


.section-heading-content {

    min-width: 0;

}


.section-header h3 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.42rem;

    font-weight: 500;

    line-height: 1.35;

}


.section-accent {

    width: 34px;

    height: 2px;

    margin:
        13px
        0
        12px;

    background: #315C97;

}


.section-header p {

    max-width: 760px;

    margin: 0;

    color: #647487;

    font-size: .91rem;

    line-height: 1.75;

}


/* =====================================================
   ESCENARIOS
===================================================== */

.scenarios-list {

    border-top:
        1px solid
        #D9E0E8;

}


.scenario-item {

    display: grid;

    grid-template-columns:
        58px
        minmax(0, 1fr);

    gap: 20px;

    padding:
        27px
        0;

    border-bottom:
        1px solid
        #D9E0E8;

    transition:
        padding-left
        .22s
        ease,

        background
        .22s
        ease;

}


.scenario-item:hover {

    padding-left: 8px;

    background:
        linear-gradient(
            90deg,
            rgba(
                23,
                55,
                94,
                .035
            ),
            rgba(
                23,
                55,
                94,
                0
            ) 72%
        );

}


.scenario-number {

    color: #B08A4C;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: .82rem;

    font-weight: 600;

    letter-spacing: .08em;

    line-height: 1.5;

}


.scenario-content {

    min-width: 0;

}


.scenario-heading {

    display: flex;

    align-items: baseline;

    justify-content: space-between;

    gap: 20px;

}


.scenario-heading h4 {

    margin: 0;

    color: #24364A;

    font-size: 1rem;

    font-weight: 700;

    line-height: 1.5;

}


.scenario-probability {

    flex-shrink: 0;

    color: #315C97;

    font-size: .74rem;

    font-weight: 700;

    letter-spacing: .02em;

    white-space: nowrap;

}


.scenario-content > p {

    max-width: 850px;

    margin:
        10px
        0
        0;

    color: #5E6D7E;

    font-size: .91rem;

    line-height: 1.8;

}


.scenario-result {

    display: flex;

    align-items: baseline;

    gap: 11px;

    margin-top: 14px;

}


.scenario-result span {

    color: #7A8795;

    font-size: .65rem;

    font-weight: 700;

    letter-spacing: .85px;

    text-transform: uppercase;

}


.scenario-result strong {

    color: #17375E;

    font-size: .87rem;

    font-weight: 700;

}


/* =====================================================
   ARGUMENTOS
===================================================== */

.arguments-list {

    border-top:
        1px solid
        #D9E0E8;

}


.argument-item {

    display: grid;

    grid-template-columns:
        48px
        minmax(0, 1fr);

    gap: 18px;

    padding:
        22px
        0;

    border-bottom:
        1px solid
        #D9E0E8;

    transition:
        padding-left
        .22s
        ease,

        background
        .22s
        ease;

}


.argument-item:hover {

    padding-left: 8px;

    background:
        linear-gradient(
            90deg,
            rgba(
                23,
                55,
                94,
                .035
            ),
            rgba(
                23,
                55,
                94,
                0
            ) 72%
        );

}


.argument-number {

    color: #B08A4C;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: .8rem;

    font-weight: 600;

    letter-spacing: .08em;

}


.argument-content {

    min-width: 0;

}


.argument-content strong {

    display: block;

    margin-bottom: 7px;

    color: #24364A;

    font-size: .95rem;

    font-weight: 700;

    line-height: 1.5;

}


.argument-content p {

    max-width: 850px;

    margin: 0;

    color: #647487;

    font-size: .89rem;

    line-height: 1.75;

}


/* =====================================================
   CONCLUSIÓN
===================================================== */

.conclusion-section {

    padding-top: 2px;

}


.conclusion-content {

    padding:
        26px
        0
        4px;

    border-top:
        1px solid
        #D9E0E8;

}


.conclusion-content
    :deep(.markdown-container) {

    padding: 0;

}


/* =====================================================
   ESTADO VACÍO
===================================================== */

.simulation-empty {

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    min-height: 300px;

    padding:
        48px
        25px;

    text-align: center;

    border-top:
        1px solid
        #D9E0E8;

    border-bottom:
        1px solid
        #D9E0E8;

}


.empty-eyebrow {

    margin-bottom: 17px;

    color: #315C97;

    font-size: .65rem;

    font-weight: 700;

    letter-spacing: 1.3px;

}


.empty-symbol {

    margin-bottom: 15px;

    color: #315C97;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 2rem;

    line-height: 1;

}


.simulation-empty h3 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.4rem;

    font-weight: 500;

    line-height: 1.35;

}


.empty-accent {

    width: 34px;

    height: 2px;

    margin:
        15px
        0;

    background: #315C97;

}


.simulation-empty p {

    max-width: 540px;

    margin: 0;

    color: #647487;

    font-size: .91rem;

    line-height: 1.8;

}


/* =====================================================
   ANIMACIONES
===================================================== */

@keyframes spin {

    to {

        transform:
            rotate(360deg);

    }

}


@keyframes pulse {

    0%,
    100% {

        transform:
            scale(1);

        opacity: 1;

    }

    50% {

        transform:
            scale(1.35);

        opacity: .55;

    }

}


/* =====================================================
   RESPONSIVE · TABLET
===================================================== */

@media (max-width: 900px) {

    .court-simulation {

        padding:
            36px
            30px
            40px;

    }


    .simulation-header {

        flex-direction: column;

        gap: 20px;

    }


    .simulation-status {

        align-self: flex-start;

        margin-top: 0;

    }


    .simulation-overview {

        grid-template-columns:
            1fr;

        gap: 28px;

    }


    .overview-metrics {

        padding-top: 24px;

        border-top:
            1px solid
            #D9E0E8;

        border-left: none;

    }


    .overview-metric:first-child {

        padding-left: 0;

    }

}


/* =====================================================
   RESPONSIVE · MOBILE
===================================================== */

@media (max-width: 576px) {

    .court-simulation {

        padding:
            28px
            20px
            32px;

    }


    .simulation-header {

        padding-bottom: 24px;

    }


    .section-eyebrow {

        margin-bottom: 13px;

        font-size: .63rem;

        letter-spacing: 1.3px;

    }


    .simulation-heading h2 {

        font-size: 1.55rem;

    }


    .simulation-heading p {

        font-size: .9rem;

        line-height: 1.75;

    }


    .simulation-status {

        font-size: .71rem;

    }


    .simulation-loading {

        gap: 15px;

        min-height: 135px;

        padding:
            24px
            0;

    }


    .loading-indicator {

        width: 38px;

        height: 38px;

    }


    .loading-spinner {

        width: 18px;

        height: 18px;

    }


    .loading-content strong {

        font-size: .91rem;

    }


    .loading-content p {

        font-size: .86rem;

        line-height: 1.7;

    }


    .simulation-overview {

        margin-top: 28px;

        padding-bottom: 28px;

    }


    .overview-value {

        font-size: 1.28rem;

    }


    .overview-metrics {

        grid-template-columns:
            1fr;

        gap: 18px;

        padding-top: 20px;

    }


    .overview-metric {

        padding: 0;

    }


    .overview-metric
        + .overview-metric {

        padding-top: 18px;

        border-top:
            1px solid
            #D9E0E8;

        border-left: none;

    }


    .simulation-section {

        margin-top: 32px;

    }


    .section-header {

        grid-template-columns:
            36px
            minmax(0, 1fr);

        gap: 14px;

        margin-bottom: 20px;

    }


    .section-header h3 {

        font-size: 1.27rem;

    }


    .section-header p {

        font-size: .87rem;

        line-height: 1.7;

    }


    .section-accent {

        width: 30px;

        margin:
            12px
            0;

    }


    .scenario-item {

        grid-template-columns:
            36px
            minmax(0, 1fr);

        gap: 13px;

        padding:
            22px
            0;

    }


    .scenario-heading {

        flex-direction: column;

        align-items: flex-start;

        gap: 6px;

    }


    .scenario-heading h4 {

        font-size: .94rem;

    }


    .scenario-content > p {

        font-size: .87rem;

        line-height: 1.72;

    }


    .scenario-result {

        flex-direction: column;

        align-items: flex-start;

        gap: 4px;

    }


    .argument-item {

        grid-template-columns:
            36px
            minmax(0, 1fr);

        gap: 13px;

        padding:
            19px
            0;

    }


    .argument-content strong {

        font-size: .91rem;

    }


    .argument-content p {

        font-size: .86rem;

        line-height: 1.7;

    }


    .conclusion-content {

        padding-top: 22px;

    }


    .simulation-empty {

        min-height: 250px;

        padding:
            38px
            20px;

    }


    .simulation-empty h3 {

        font-size: 1.25rem;

    }


    .simulation-empty p {

        font-size: .87rem;

        line-height: 1.7;

    }

}

</style>
