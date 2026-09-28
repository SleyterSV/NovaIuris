<template>

    <section class="nova-case-analysis">

        <!-- ===================================================
             CABECERA PRINCIPAL
        ==================================================== -->

        <header class="analysis-header">

            <div class="analysis-heading">

                <div class="analysis-eyebrow">

                    <span class="eyebrow-line"></span>

                    NOVACASE · ANÁLISIS JURÍDICO

                </div>

                <h2>
                    Análisis Jurídico
                </h2>

                <p>
                    Evaluación estructurada de los elementos jurídicos
                    relevantes identificados durante el análisis del caso.
                </p>

            </div>


            <div class="analysis-status">

                <span class="status-dot"></span>

                <span>
                    Análisis completado
                </span>

            </div>

        </header>


        <!-- ===================================================
             SECCIONES DEL ANÁLISIS
        ==================================================== -->

        <section
            class="analysis-grid"
            aria-label="Secciones del análisis jurídico"
        >

            <article
                v-for="(section, index) in sections"
                :key="section.id"
                class="analysis-card"
                :style="{ '--card-index': index }"
            >

                <!-- CABECERA -->

                <header class="card-header">

                    <div class="card-heading">

                        <span
                            class="card-number"
                            aria-hidden="true"
                        >
                            {{ formatNumber(index + 1) }}
                        </span>


                        <div class="card-title-group">

                            <span class="card-kicker">
                                {{ section.category }}
                            </span>

                            <h3>
                                {{ section.title }}
                            </h3>

                        </div>

                    </div>


                    <span class="card-status">

                        <span
                            class="card-status-icon"
                            aria-hidden="true"
                        >

                            <svg
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            >

                                <path d="M5 12.5l4 4L19 7" />

                            </svg>

                        </span>

                        Completado

                    </span>

                </header>


                <!-- CONTENIDO -->

                <div class="card-body">

                    <MarkdownRenderer
                        :content="section.content"
                    />

                </div>


                <!-- PIE -->

                <footer class="card-footer">

                    <span>
                        NovaCase Intelligence
                    </span>

                    <span class="card-footer-mark">
                        {{ formatNumber(index + 1) }}
                    </span>

                </footer>

            </article>

        </section>


        <!-- ===================================================
             PROCESO DE ANÁLISIS
        ==================================================== -->

        <section v-if="processSteps.length" class="analysis-process">

            <header class="process-header">

                <div>

                    <div class="process-eyebrow">

                        <span class="eyebrow-line"></span>

                        METODOLOGÍA

                    </div>

                    <h3>
                        Proceso de Análisis
                    </h3>

                    <p>
                        Etapas ejecutadas por NovaCase para estructurar
                        y evaluar jurídicamente la información del caso.
                    </p>

                </div>


                <div class="process-count">

                    <strong>
                        {{ formatNumber(processSteps.length) }}
                    </strong>

                    <span>
                        etapas
                    </span>

                </div>

            </header>


            <!-- TIMELINE -->

            <div
                class="process-timeline"
                aria-label="Etapas del análisis"
            >

                <div
                    v-for="(step, index) in processSteps"
                    :key="step.id"
                    class="process-step"
                    :style="{ '--step-index': index }"
                >

                    <!-- CONECTOR -->

                    <div
                        v-if="index < processSteps.length - 1"
                        class="timeline-line"
                        aria-hidden="true"
                    ></div>


                    <!-- MARCADOR -->

                    <div
                        class="process-marker"
                        aria-hidden="true"
                    >

                        <span>
                            {{ formatNumber(step.id) }}
                        </span>

                    </div>


                    <!-- CONTENIDO -->

                    <div class="process-content">

                        <div class="process-content-top">

                            <span class="process-label">
                                ETAPA {{ formatNumber(step.id) }}
                            </span>


                            <span class="process-completed" :class="`stage-${step.status}`">{{ stageStatus(step.status) }}</span>

                        </div>


                        <h4>
                            {{ step.title }}
                        </h4>


                        <p>
                            {{ step.description }}
                        </p>

                    </div>

                </div>

            </div>

        </section>

    </section>

</template>


<script setup>

import { computed } from "vue"

import MarkdownRenderer
    from "@/components/common/MarkdownRenderer.vue"


/* =========================================================
   PROPS
========================================================= */

const props = defineProps({

    analysis: {
        type: Object,
        required: true
    },
    stages: {
        type: Array,
        default: () => []
    }

})


/* =========================================================
   SECCIONES DEL ANÁLISIS
========================================================= */

const sections = computed(() => [

    {

        id: "summary",

        category: "VISIÓN GENERAL",

        title: "Resumen Ejecutivo",

        content:
            props.analysis.summary ||
            "No identificado con la información disponible."

    },

    {

        id: "facts",

        category: "BASE FÁCTICA",

        title: "Hechos Relevantes",

        content:
            props.analysis.facts ||
            "No identificado con la información disponible."

    },

    {

        id: "issues",

        category: "ANÁLISIS",

        title: "Problemas Jurídicos",

        content:
            props.analysis.issues ||
            "No identificado con la información disponible."

    },

    {

        id: "law",

        category: "MARCO NORMATIVO",

        title: "Normativa preliminar identificada",

        content:
            props.analysis.law ||
            "No identificado con la información disponible."

    },

    {

        id: "jurisprudence",

        category: "PRECEDENTES",

        title: "Jurisprudencia",

        content:
            props.analysis.jurisprudence ||
            "No identificado con la información disponible."

    },

    {

        id: "observations",

        category: "VALORACIÓN",

        title: "Observaciones",

        content:
            props.analysis.observations ||
            "No identificado con la información disponible."

    }

])


/* =========================================================
   PROCESO DE ANÁLISIS
========================================================= */

const processSteps = computed(() => props.stages.map((stage, index) => ({
    id: stage.id || stage.key || index,
    title: stage.title || stage.label || stage.key || "Etapa",
    description: stage.description || "",
    status: stage.status || "pending"
})))

function stageStatus(status) {
    return ({ completed: "Completado", skipped: "No requerido", failed: "No completado",
        processing: "En curso", running: "En curso", pending: "Pendiente" })[status] || "Pendiente"
}


/* =========================================================
   UTILIDADES
========================================================= */

function formatNumber(value) {

    return String(value).padStart(2, "0")

}

</script>


<style scoped>

/* =========================================================
   NOVACASE — ANALYSIS VIEW
   Identidad:
   Azul institucional · Dorado jurídico · Blanco · Gris
========================================================= */

.nova-case-analysis {

    width: 100%;

    display: flex;

    flex-direction: column;

    gap: 30px;

    padding: 30px;

    background:
        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FCFDFE 100%
        );

    border:
        1px solid
        #DCE4EC;

    border-radius: 14px;

    box-shadow:
        0 10px 28px
        rgba(
            23,
            55,
            94,
            .045
        );

    animation:
        novaCaseAnalysisEnter
        .4s
        ease-out;

}


/* =========================================================
   CABECERA PRINCIPAL
========================================================= */

.analysis-header {

    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 24px;

    padding:
        0
        4px
        21px;

    border-bottom:
        1px solid
        #DCE5EE;

}


.analysis-heading {

    min-width: 0;

}


.analysis-eyebrow,
.process-eyebrow {

    display: flex;

    align-items: center;

    gap: 8px;

    margin-bottom: 9px;

    color: #8A6A37;

    font-size: .61rem;

    font-weight: 800;

    letter-spacing: 1.4px;

}


.eyebrow-line {

    width: 22px;

    height: 1px;

    flex-shrink: 0;

    background: #B08A4C;

}


.analysis-heading h2 {

    margin:
        0
        0
        8px;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.65rem;

    font-weight: 600;

    line-height: 1.3;

}


.analysis-heading p {

    max-width: 720px;

    margin: 0;

    color: #697888;

    font-size: .87rem;

    line-height: 1.7;

}


/* =========================================================
   ESTADO PRINCIPAL
========================================================= */

.analysis-status {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    flex-shrink: 0;

    min-height: 31px;

    padding:
        0
        12px;

    background:
        #F7FAF8;

    border:
        1px solid
        #D8E7DD;

    border-radius: 999px;

    color: #587161;

    font-size: .66rem;

    font-weight: 750;

}


.status-dot {

    width: 6px;

    height: 6px;

    flex-shrink: 0;

    border-radius: 50%;

    background: #668B70;

    box-shadow:
        0 0 0 3px
        rgba(
            102,
            139,
            112,
            .10
        );

}


/* =========================================================
   GRID
========================================================= */

.analysis-grid {

    display: grid;

    grid-template-columns:
        repeat(
            2,
            minmax(
                0,
                1fr
            )
        );

    gap: 16px;

}


/* =========================================================
   TARJETAS
========================================================= */

.analysis-card {

    position: relative;

    min-width: 0;

    overflow: hidden;

    display: flex;

    flex-direction: column;

    background: #FFFFFF;

    border:
        1px solid
        #D9E2EC;

    border-radius: 11px;

    box-shadow:
        0 5px 18px
        rgba(
            23,
            55,
            94,
            .035
        );

    transition:
        transform
        .22s
        ease,

        border-color
        .22s
        ease,

        box-shadow
        .22s
        ease;

    animation:
        novaCaseCardEnter
        .4s
        ease-out
        both;

    animation-delay:
        calc(
            var(--card-index)
            * .045s
        );

}


.analysis-card:hover {

    transform:
        translateY(
            -2px
        );

    border-color:
        #C5D2DF;

    box-shadow:
        0 12px 28px
        rgba(
            23,
            55,
            94,
            .065
        );

}


/* =========================================================
   CABECERA DE TARJETA
========================================================= */

.card-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 16px;

    padding:
        17px
        19px;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #FCFDFE 100%
        );

    border-bottom:
        1px solid
        #E8EDF2;

}


.card-heading {

    display: flex;

    align-items: center;

    gap: 12px;

    min-width: 0;

}


.card-number {

    width: 34px;

    height: 34px;

    flex:
        0 0
        34px;

    display: flex;

    align-items: center;

    justify-content: center;

    background:
        #FCFDFE;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .38
        );

    border-radius: 50%;

    color: #7A6440;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: .72rem;

    font-weight: 600;

}


.card-title-group {

    min-width: 0;

}


.card-kicker {

    display: block;

    margin-bottom: 3px;

    color: #8B98A6;

    font-size: .55rem;

    font-weight: 800;

    letter-spacing: .9px;

}


.card-title-group h3 {

    overflow: hidden;

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1rem;

    font-weight: 600;

    line-height: 1.4;

    text-overflow: ellipsis;

}


/* =========================================================
   ESTADO DE TARJETA
========================================================= */

.card-status {

    display: inline-flex;

    align-items: center;

    gap: 5px;

    flex-shrink: 0;

    color: #71817A;

    font-size: .59rem;

    font-weight: 750;

}


.card-status-icon {

    width: 17px;

    height: 17px;

    display: flex;

    align-items: center;

    justify-content: center;

    border:
        1px solid
        #D8E7DD;

    border-radius: 50%;

    background: #F5F9F6;

    color: #64806D;

}


.card-status-icon svg {

    width: 10px;

    height: 10px;

}


/* =========================================================
   CUERPO
========================================================= */

.card-body {

    flex: 1;

    min-width: 0;

    padding:
        19px
        20px;

}


/* =========================================================
   MARKDOWN RENDERER
========================================================= */

.card-body :deep(p) {

    margin:
        0
        0
        11px;

    color: #536273;

    font-size: .85rem;

    line-height: 1.8;

}


.card-body :deep(p:last-child) {

    margin-bottom: 0;

}


.card-body :deep(h1),
.card-body :deep(h2),
.card-body :deep(h3),
.card-body :deep(h4) {

    margin:
        18px
        0
        8px;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-weight: 600;

    line-height: 1.4;

}


.card-body :deep(h1:first-child),
.card-body :deep(h2:first-child),
.card-body :deep(h3:first-child),
.card-body :deep(h4:first-child) {

    margin-top: 0;

}


.card-body :deep(ul),
.card-body :deep(ol) {

    margin:
        8px
        0
        12px;

    padding-left: 21px;

    color: #536273;

}


.card-body :deep(li) {

    margin-bottom: 6px;

    font-size: .84rem;

    line-height: 1.7;

}


.card-body :deep(li:last-child) {

    margin-bottom: 0;

}


.card-body :deep(strong) {

    color: #304C6C;

    font-weight: 750;

}


.card-body :deep(em) {

    color: #667585;

}


.card-body :deep(a) {

    color: #315C97;

    text-decoration:
        underline;

    text-decoration-color:
        rgba(
            49,
            92,
            151,
            .28
        );

    text-underline-offset: 3px;

}


.card-body :deep(blockquote) {

    margin:
        14px
        0;

    padding:
        11px
        14px;

    background:
        #F8FAFC;

    border-left:
        2px solid
        #B08A4C;

    border-radius:
        0
        7px
        7px
        0;

    color: #5B6876;

}


.card-body :deep(code) {

    padding:
        2px
        5px;

    background:
        #F3F6F9;

    border:
        1px solid
        #E2E8EF;

    border-radius: 4px;

    color: #315C97;

    font-size: .78rem;

}


.card-body :deep(hr) {

    margin:
        18px
        0;

    border: 0;

    border-top:
        1px solid
        #E7EDF2;

}


/* =========================================================
   FOOTER DE TARJETA
========================================================= */

.card-footer {

    display: flex;

    align-items: center;

    justify-content: space-between;

    min-height: 35px;

    padding:
        0
        19px;

    background:
        #FAFBFC;

    border-top:
        1px solid
        #EDF1F4;

    color: #9AA5B0;

    font-size: .56rem;

    font-weight: 700;

    letter-spacing: .25px;

}


.card-footer-mark {

    color: #B08A4C;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

}


/* =========================================================
   PROCESO DE ANÁLISIS
========================================================= */

.analysis-process {

    padding-top: 4px;

}


.process-header {

    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 20px;

    padding:
        0
        4px
        18px;

    border-bottom:
        1px solid
        #DCE5EE;

}


.process-header h3 {

    margin:
        0
        0
        7px;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.28rem;

    font-weight: 600;

}


.process-header p {

    max-width: 680px;

    margin: 0;

    color: #718090;

    font-size: .82rem;

    line-height: 1.65;

}


/* =========================================================
   CONTADOR
========================================================= */

.process-count {

    min-width: 67px;

    padding:
        8px
        11px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    background: #FFFFFF;

    border:
        1px solid
        #D7E0E9;

    border-radius: 8px;

}


.process-count strong {

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: .95rem;

    font-weight: 700;

}


.process-count span {

    color: #8C98A5;

    font-size: .56rem;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: .7px;

}


/* =========================================================
   TIMELINE
========================================================= */

.process-timeline {

    display: flex;

    flex-direction: column;

    margin-top: 20px;

}


.process-step {

    position: relative;

    display: grid;

    grid-template-columns:
        46px
        minmax(
            0,
            1fr
        );

    column-gap: 16px;

    padding-bottom: 20px;

    animation:
        novaCaseStepEnter
        .38s
        ease-out
        both;

    animation-delay:
        calc(
            var(--step-index)
            * .055s
        );

}


.process-step:last-child {

    padding-bottom: 0;

}


/* =========================================================
   LÍNEA
========================================================= */

.timeline-line {

    position: absolute;

    top: 46px;

    bottom: 0;

    left: 22px;

    width: 1px;

    background:
        linear-gradient(
            to bottom,
            #C9D5E1,
            #E8EDF2
        );

}


/* =========================================================
   MARCADOR
========================================================= */

.process-marker {

    position: relative;

    z-index: 2;

    width: 44px;

    height: 44px;

    display: flex;

    align-items: center;

    justify-content: center;

    background:
        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #F9FBFD 100%
        );

    border:
        1px solid
        #D4DFE9;

    border-radius: 50%;

    box-shadow:
        0 3px 10px
        rgba(
            23,
            55,
            94,
            .045
        );

}


.process-marker::after {

    content: "";

    position: absolute;

    inset: 4px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .16
        );

    border-radius: 50%;

}


.process-marker span {

    position: relative;

    z-index: 1;

    color: #315C97;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: .72rem;

    font-weight: 600;

}


/* =========================================================
   CONTENIDO DEL PROCESO
========================================================= */

.process-content {

    min-width: 0;

    padding:
        2px
        0
        4px;

}


.process-content-top {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 14px;

    margin-bottom: 5px;

}


.process-label {

    color: #9AA5B0;

    font-size: .56rem;

    font-weight: 800;

    letter-spacing: .9px;

}


.process-completed {

    display: inline-flex;

    align-items: center;

    gap: 5px;

    color: #71817A;

    font-size: .58rem;

    font-weight: 700;

}


.process-completed svg {

    width: 12px;

    height: 12px;

    color: #66806D;

}


.process-content h4 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: .94rem;

    font-weight: 600;

    line-height: 1.45;

}


.process-content p {

    max-width: 780px;

    margin:
        5px
        0
        0;

    color: #718090;

    font-size: .78rem;

    line-height: 1.65;

}


/* =========================================================
   ANIMACIONES
========================================================= */

@keyframes novaCaseAnalysisEnter {

    from {

        opacity: 0;

        transform:
            translateY(
                10px
            );

    }

    to {

        opacity: 1;

        transform:
            translateY(
                0
            );

    }

}


@keyframes novaCaseCardEnter {

    from {

        opacity: 0;

        transform:
            translateY(
                10px
            );

    }

    to {

        opacity: 1;

        transform:
            translateY(
                0
            );

    }

}


@keyframes novaCaseStepEnter {

    from {

        opacity: 0;

        transform:
            translateX(
                8px
            );

    }

    to {

        opacity: 1;

        transform:
            translateX(
                0
            );

    }

}


/* =========================================================
   REDUCIR MOVIMIENTO
========================================================= */

@media(
    prefers-reduced-motion: reduce
) {

    .nova-case-analysis,
    .analysis-card,
    .process-step {

        animation: none;

    }

    .analysis-card {

        transition: none;

    }

}


/* =========================================================
   TABLET
========================================================= */

@media(max-width:1000px) {

    .analysis-grid {

        grid-template-columns: 1fr;

    }

}


/* =========================================================
   MOBILE
========================================================= */

@media(max-width:700px) {

    .nova-case-analysis {

        padding: 22px;

        gap: 24px;

    }


    .analysis-header {

        align-items: flex-start;

        flex-direction: column;

        gap: 15px;

    }


    .analysis-status {

        align-self: flex-start;

    }


    .analysis-heading h2 {

        font-size: 1.4rem;

    }


    .analysis-heading p {

        font-size: .83rem;

    }


    .card-header {

        align-items: flex-start;

        flex-direction: column;

        gap: 11px;

    }


    .card-status {

        margin-left: 46px;

    }


    .process-header {

        align-items: flex-start;

        flex-direction: column;

    }


    .process-count {

        align-self: flex-start;

    }

}


/* =========================================================
   MOBILE PEQUEÑO
========================================================= */

@media(max-width:480px) {

    .nova-case-analysis {

        padding: 17px;

        border-radius: 11px;

    }


    .analysis-grid {

        gap: 13px;

    }


    .card-header {

        padding:
            15px
            16px;

    }


    .card-body {

        padding:
            17px;

    }


    .card-footer {

        padding:
            0
            16px;

    }


    .card-status {

        margin-left: 46px;

    }


    .process-step {

        grid-template-columns:
            40px
            minmax(
                0,
                1fr
            );

        column-gap: 13px;

    }


    .process-marker {

        width: 38px;

        height: 38px;

    }


    .process-marker::after {

        inset: 3px;

    }


    .timeline-line {

        left: 19px;

        top: 40px;

    }


    .process-content-top {

        align-items: flex-start;

        flex-direction: column;

        gap: 5px;

    }


    .process-content h4 {

        font-size: .9rem;

    }


    .process-content p {

        font-size: .75rem;

    }

}

</style>