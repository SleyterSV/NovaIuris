<template>

    <section
        v-if="answer"
        class="nova-search-answer"
    >

        <!-- =============================================
             CABECERA
        ============================================== -->

        <header class="nova-search-answer-header">

            <div class="nova-search-answer-brand">

                <div class="nova-search-answer-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.6"
                        aria-hidden="true"
                    >
                        <path
                            d="M12 3L19 6V11C19 15.5 16.2 19.4 12 21C7.8 19.4 5 15.5 5 11V6L12 3Z"
                        />

                        <path
                            d="M8.5 11.5H15.5"
                        />

                        <path
                            d="M12 8.5V14.5"
                        />

                    </svg>

                </div>


                <div class="nova-search-answer-heading">

                    <span class="nova-search-answer-eyebrow">
                        NOVA SEARCH · ANÁLISIS JURÍDICO
                    </span>

                    <h2>
                        Respuesta jurídica
                    </h2>

                    <p>
                        Síntesis estructurada a partir de la información
                        jurídica recuperada y analizada.
                    </p>

                </div>

            </div>


            <div class="nova-search-answer-status">

                <span class="nova-search-answer-status-dot"></span>

                <span>
                    Análisis completado
                </span>

            </div>

        </header>


        <!-- =============================================
             CONTENIDO DE LA RESPUESTA
        ============================================== -->

        <div class="nova-search-answer-body">

            <div class="nova-search-answer-content">
                <MarkdownRenderer :content="answer" :sources="verifiedSources" :citations="verifiedCitations"
                    @select-citation="openCitation" />
            </div>
            <p v-if="!verifiedCitations.length" class="citation-warning">
                No se encontraron fuentes verificables para respaldar esta respuesta.
            </p>
            <SourcesList :sources="verifiedSources" :citations="verifiedCitations" @select="selectedSource = $event" @select-citation="openCitation" />

        </div>


        <!-- =============================================
             MÉTRICAS
        ============================================== -->

        <footer
            v-if="hasMetrics"
            class="nova-search-answer-footer"
        >

            <!-- Tiempo -->

            <div
                v-if="searchTime !== null"
                class="nova-search-answer-metric"
            >

                <div class="nova-search-answer-metric-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        aria-hidden="true"
                    >
                        <circle
                            cx="12"
                            cy="12"
                            r="8"
                        />

                        <path
                            d="M12 8V12L15 14"
                        />

                    </svg>

                </div>


                <div>

                    <span class="nova-search-answer-metric-label">
                        Tiempo de análisis
                    </span>

                    <strong>
                        {{ formattedSearchTime }}
                    </strong>

                </div>

            </div>


            <!-- Fuentes -->

            <div
                v-if="hasTotalResults"
                class="nova-search-answer-metric"
            >

                <div class="nova-search-answer-metric-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        aria-hidden="true"
                    >
                        <path
                            d="M5 4H19V20H5Z"
                        />

                        <path
                            d="M8 8H16"
                        />

                        <path
                            d="M8 12H16"
                        />

                        <path
                            d="M8 16H13"
                        />

                    </svg>

                </div>


                <div>

                    <span class="nova-search-answer-metric-label">
                        Fuentes recuperadas
                    </span>

                    <strong>
                        {{ totalResults }}
                    </strong>

                </div>

            </div>


            <!-- Rama jurídica -->

            <div
                v-if="rama"
                class="nova-search-answer-metric"
            >

                <div class="nova-search-answer-metric-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        aria-hidden="true"
                    >
                        <path
                            d="M12 3V21"
                        />

                        <path
                            d="M7 6H17"
                        />

                        <path
                            d="M8 6L5 11H11L8 6Z"
                        />

                        <path
                            d="M16 6L13 11H19L16 6Z"
                        />

                    </svg>

                </div>


                <div>

                    <span class="nova-search-answer-metric-label">
                        Rama jurídica
                    </span>

                    <strong>
                        {{ rama }}
                    </strong>

                </div>

            </div>

        </footer>


        <!-- =============================================
             NOTA INFORMATIVA
        ============================================== -->

        <div class="nova-search-answer-disclaimer">

            <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                aria-hidden="true"
            >
                <circle
                    cx="12"
                    cy="12"
                    r="9"
                />

                <path
                    d="M12 10V16"
                />

                <path
                    d="M12 7H12.01"
                />

            </svg>

            <p>
                La respuesta es una síntesis generada a partir de las fuentes
                recuperadas por NovaSearch y debe ser contrastada con la
                normativa y jurisprudencia aplicable al caso concreto.
            </p>

        </div>

        <SourceModal :source="selectedSource" @close="selectedSource = null" />

    </section>

</template>


<script setup>

import {
    computed,
    ref
} from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import SourcesList from '@/components/common/SourcesList.vue'
import SourceModal from '@/components/common/SourceModal.vue'
import { resolveCitations } from '@/utils/sourceContract.js'


/* =========================================================
   PROPS
========================================================= */

const props = defineProps({

    answer: {

        type: String,

        default: ''

    },

    sources: { type: Array, default: () => [] },
    citations: { type: Array, default: () => [] },
    sourceWarnings: { type: Array, default: () => [] },

    searchTime: {

        type: [
            Number,
            String
        ],

        default: null

    },

    totalResults: {

        type: [
            Number,
            String
        ],

        default: 0

    },

    rama: {

        type: String,

        default: ''

    }

})
const selectedSource = ref(null)
const verified = computed(() => resolveCitations(props.citations, props.sources))
const verifiedSources = computed(() => verified.value.sources)
const verifiedCitations = computed(() => verified.value.citations)
const openCitation = citation => {
    selectedSource.value = verifiedSources.value.find(source => source.source_id === citation.source_id) || null
}


/* =========================================================
   COMPUTED
========================================================= */

const hasTotalResults = computed(() => {

    return Number(props.totalResults) > 0

})


const hasMetrics = computed(() => {

    return (
        props.searchTime !== null ||
        hasTotalResults.value ||
        Boolean(props.rama)
    )

})


const formattedSearchTime = computed(() => {

    if (
        props.searchTime === null ||
        props.searchTime === undefined ||
        props.searchTime === ''
    ) {

        return '—'

    }


    const time = Number(props.searchTime)


    if (Number.isNaN(time)) {

        return props.searchTime

    }


    if (time < 1000) {

        return `${Math.round(time)} ms`

    }


    return `${(time / 1000).toFixed(2)} s`

})

</script>


<style scoped>

/* =========================================================
   NOVA SEARCH — ANSWER
   SISTEMA VISUAL NOVA IURIS
========================================================= */

.nova-search-answer {
    width: 100%;
    overflow: hidden;
    box-sizing: border-box;

    background:
        linear-gradient(
            145deg,
            #FFFFFF 0%,
            #FDFDFE 58%,
            #F8FAFC 100%
        );

    border:
        1px solid
        #D8E0E9;

    border-radius: 10px;

    box-shadow:
        0 10px 30px
        rgba(11, 22, 40, .055);

    animation:
        novaSearchAnswerEnter
        .4s
        ease-out;
}


/* =========================================================
   CABECERA
========================================================= */

.nova-search-answer-header {
    display: flex;

    align-items: center;
    justify-content: space-between;

    gap: 28px;

    padding:
        25px
        28px;

    border-bottom:
        1px solid
        #E3E8EE;

    background:
        linear-gradient(
            90deg,
            #FFFFFF 0%,
            #FBFCFD 100%
        );
}


.nova-search-answer-brand {
    display: flex;

    align-items: center;

    gap: 15px;

    min-width: 0;
}


/* =========================================================
   ICONO PRINCIPAL
========================================================= */

.nova-search-answer-icon {
    position: relative;

    width: 52px;
    height: 52px;

    flex:
        0 0 52px;

    display: flex;

    align-items: center;
    justify-content: center;

    background:
        #0B1628;

    color:
        #FFFFFF;

    border:
        1px solid
        rgba(201, 164, 92, .42);

    border-radius: 8px;

    box-shadow:
        0 7px 18px
        rgba(11, 22, 40, .12);
}


.nova-search-answer-icon::after {
    content: "";

    position: absolute;

    inset: 5px;

    border:
        1px solid
        rgba(201, 164, 92, .48);

    border-radius: 6px;

    pointer-events: none;
}


.nova-search-answer-icon svg {
    position: relative;

    z-index: 1;

    width: 25px;
    height: 25px;
}


/* =========================================================
   IDENTIDAD
========================================================= */

.nova-search-answer-heading {
    min-width: 0;
}


.nova-search-answer-eyebrow {
    display: block;

    margin-bottom: 5px;

    color:
        #9A7A42;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .60rem;

    font-weight:
        800;

    letter-spacing:
        1.4px;

    line-height:
        1.3;

    text-transform:
        uppercase;
}


.nova-search-answer-heading h2 {
    margin: 0;

    color:
        #0B1628;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:
        1.45rem;

    font-weight:
        500;

    line-height:
        1.25;

    letter-spacing:
        -.15px;
}


.nova-search-answer-heading p {
    margin:
        6px
        0
        0;

    color:
        #687386;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .82rem;

    line-height:
        1.55;
}


/* =========================================================
   ESTADO — ANÁLISIS COMPLETADO
========================================================= */

.nova-search-answer-status {
    display: inline-flex;

    align-items: center;

    gap: 8px;

    flex-shrink: 0;

    padding:
        7px
        11px;

    border:
        1px solid
        rgba(78, 138, 104, .24);

    border-radius:
        6px;

    background:
        rgba(78, 138, 104, .045);

    color:
        #47735A;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .62rem;

    font-weight:
        800;

    letter-spacing:
        .55px;

    text-transform:
        uppercase;
}


.nova-search-answer-status-dot {
    width: 6px;
    height: 6px;

    flex:
        0 0 6px;

    border-radius: 50%;

    background:
        #4E8A68;

    box-shadow:
        0 0 0 3px
        rgba(78, 138, 104, .10);
}


/* =========================================================
   CUERPO DE LA RESPUESTA
========================================================= */

.nova-search-answer-body {
    padding:
        28px
        30px
        30px;

    background:
        #FFFFFF;
}


.nova-search-answer-content {
    position: relative;

    max-width: 1000px;

    padding-left:
        17px;

    border-left:
        2px solid
        rgba(201, 164, 92, .48);
}


.nova-search-answer-content p {
    margin: 0;

    color:
        #334255;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .94rem;

    font-weight:
        400;

    line-height:
        1.9;

    white-space:
        pre-wrap;
}


/* =========================================================
   MÉTRICAS
========================================================= */

.nova-search-answer-footer {
    display: flex;

    align-items: stretch;

    border-top:
        1px solid
        #E3E8EE;

    background:
        #F9FAFC;
}


.nova-search-answer-metric {
    display: flex;

    align-items: center;

    gap: 10px;

    flex: 1;

    min-width: 0;

    padding:
        15px
        21px;

    border-right:
        1px solid
        #E3E8EE;

    transition:
        background
        .2s
        ease;
}


.nova-search-answer-metric:hover {
    background:
        #FFFFFF;
}


.nova-search-answer-metric:last-child {
    border-right:
        none;
}


/* =========================================================
   ICONOS DE MÉTRICAS
========================================================= */

.nova-search-answer-metric-icon {
    width: 33px;
    height: 33px;

    flex:
        0 0 33px;

    display: flex;

    align-items: center;
    justify-content: center;

    box-sizing: border-box;

    border:
        1px solid
        #D9E1EA;

    border-radius:
        7px;

    background:
        #FFFFFF;

    color:
        #315C97;
}


.nova-search-answer-metric-icon svg {
    width: 16px;
    height: 16px;
}


/* =========================================================
   TEXTO DE MÉTRICAS
========================================================= */

.nova-search-answer-metric-label {
    display: block;

    margin-bottom:
        3px;

    color:
        #8995A3;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .58rem;

    font-weight:
        800;

    letter-spacing:
        .75px;

    line-height:
        1.3;

    text-transform:
        uppercase;
}


.nova-search-answer-metric strong {
    display: block;

    overflow: hidden;

    color:
        #24354F;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .78rem;

    font-weight:
        700;

    line-height:
        1.35;

    white-space:
        nowrap;

    text-overflow:
        ellipsis;
}


/* =========================================================
   DISCLAIMER JURÍDICO
========================================================= */

.nova-search-answer-disclaimer {
    display: flex;

    align-items: flex-start;

    gap: 10px;

    padding:
        14px
        28px;

    border-top:
        1px solid
        rgba(201, 164, 92, .16);

    background:
        #FCFAF6;
}


.nova-search-answer-disclaimer svg {
    width: 16px;
    height: 16px;

    flex-shrink: 0;

    margin-top:
        2px;

    color:
        #9A7A42;
}


.nova-search-answer-disclaimer p {
    margin: 0;

    color:
        #786A50;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .70rem;

    line-height:
        1.65;
}


/* =========================================================
   ANIMACIÓN DE ENTRADA
========================================================= */

@keyframes novaSearchAnswerEnter {

    from {
        opacity: 0;

        transform:
            translateY(8px);
    }

    to {
        opacity: 1;

        transform:
            translateY(0);
    }

}


/* =========================================================
   TABLET
========================================================= */

@media (max-width: 850px) {

    .nova-search-answer-header {
        align-items:
            flex-start;

        flex-direction:
            column;

        padding:
            23px
            24px;
    }


    .nova-search-answer-status {
        align-self:
            flex-start;
    }


    .nova-search-answer-body {
        padding:
            24px;
    }


    .nova-search-answer-disclaimer {
        padding:
            14px
            24px;
    }


    .nova-search-answer-footer {
        flex-wrap:
            wrap;
    }


    .nova-search-answer-metric {
        flex:
            1 1 45%;

        border-bottom:
            1px solid
            #E3E8EE;
    }


    .nova-search-answer-metric:nth-last-child(-n + 2) {
        border-bottom:
            none;
    }

}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 600px) {

    .nova-search-answer {
        border-radius:
            9px;
    }


    .nova-search-answer-header {
        padding:
            21px
            18px;
    }


    .nova-search-answer-brand {
        align-items:
            flex-start;

        gap:
            12px;
    }


    .nova-search-answer-icon {
        width:
            45px;

        height:
            45px;

        flex-basis:
            45px;

        border-radius:
            7px;
    }


    .nova-search-answer-icon svg {
        width:
            21px;

        height:
            21px;
    }


    .nova-search-answer-heading h2 {
        font-size:
            1.23rem;
    }


    .nova-search-answer-heading p {
        font-size:
            .77rem;
    }


    .nova-search-answer-eyebrow {
        font-size:
            .55rem;

        letter-spacing:
            1.1px;
    }


    .nova-search-answer-body {
        padding:
            21px
            18px
            23px;
    }


    .nova-search-answer-content {
        padding-left:
            13px;
    }


    .nova-search-answer-content p {
        font-size:
            .90rem;

        line-height:
            1.82;
    }


    .nova-search-answer-footer {
        flex-direction:
            column;
    }


    .nova-search-answer-metric {
        width:
            100%;

        padding:
            14px
            18px;

        border-right:
            none;

        border-bottom:
            1px solid
            #E3E8EE;
    }


    .nova-search-answer-metric:last-child {
        border-bottom:
            none;
    }


    .nova-search-answer-disclaimer {
        padding:
            13px
            18px;
    }


    .nova-search-answer-disclaimer p {
        font-size:
            .68rem;
    }

}
 .citation-warning{margin:14px 24px 0;color:#805d2a;background:#fbf7ee;border-left:3px solid #bd9854;padding:10px 13px;font-size:.82rem}
 .nova-search-answer-content :deep(.citation-inline){border:0;background:#edf3f8;color:#173b61;border-radius:4px;padding:1px 5px;margin:0 2px;font-family:inherit;font-size:.78em;font-weight:600;line-height:1.4;cursor:pointer}
 .nova-search-answer-content :deep(.citation-inline:focus-visible){outline:2px solid #b68a3a;outline-offset:2px}
</style>
