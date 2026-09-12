<template>

    <section
        v-if="hasAnalysis"
        class="nova-search-analysis"
    >

        <!-- =========================================
             HEADER
        ========================================== -->

        <header class="analysis-header">

            <div class="analysis-heading">

                <div class="analysis-heading-top">

                    <span class="analysis-eyebrow">
                        NOVA SEARCH · INTERPRETACIÓN
                    </span>

                    <span class="analysis-index">
                        01
                    </span>

                </div>


                <h2>
                    Interpretación jurídica
                </h2>


                <p>
                    NovaSearch identifica la naturaleza, intención y
                    elementos jurídicamente relevantes de la consulta
                    para optimizar su análisis y recuperación.
                </p>

            </div>


            <!-- SELLO -->

            <div
                class="analysis-seal"
                aria-hidden="true"
            >

                <span class="analysis-seal-inner">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.6"
                    >

                        <circle
                            cx="12"
                            cy="12"
                            r="8.5"
                        />

                        <path
                            d="M12 7V12L15.5 14"
                        />

                        <path
                            d="M8.5 4.8L6.8 3.2"
                        />

                        <path
                            d="M15.5 4.8L17.2 3.2"
                        />

                    </svg>

                </span>

            </div>

        </header>


        <!-- =========================================
             CUERPO
        ========================================== -->

        <div class="analysis-body">

            <!-- LÍNEA DE CONTEXTO -->

            <div class="analysis-context">

                <span class="analysis-context-line"></span>

                <span>
                    Elementos identificados en la consulta
                </span>

            </div>


            <!-- =====================================
                 GRID
            ====================================== -->

            <div class="analysis-grid">


                <!-- RAMA JURÍDICA -->

                <article
                    v-if="analysis?.rama"
                    class="analysis-card"
                >

                    <div class="analysis-card-icon">

                        <span class="legal-symbol">
                            §
                        </span>

                    </div>


                    <div class="analysis-card-content">

                        <span class="analysis-label">
                            Rama jurídica
                        </span>

                        <strong class="analysis-value">
                            {{ analysis.rama }}
                        </strong>

                    </div>


                    <span class="analysis-card-number">
                        01
                    </span>

                </article>


                <!-- INTENCIÓN -->

                <article
                    v-if="analysis?.intent"
                    class="analysis-card"
                >

                    <div class="analysis-card-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
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


                    <div class="analysis-card-content">

                        <span class="analysis-label">
                            Intención detectada
                        </span>

                        <strong class="analysis-value">
                            {{ analysis.intent }}
                        </strong>

                    </div>


                    <span class="analysis-card-number">
                        02
                    </span>

                </article>


                <!-- CONSULTA NORMALIZADA -->

                <article
                    v-if="normalizedQuery"
                    class="
                        analysis-card
                        analysis-card-wide
                        analysis-query-card
                    "
                >

                    <div class="analysis-card-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >

                            <path d="M5 6H19" />

                            <path d="M5 11H17" />

                            <path d="M5 16H14" />

                        </svg>

                    </div>


                    <div class="analysis-card-content">

                        <span class="analysis-label">
                            Consulta interpretada
                        </span>

                        <strong
                            class="
                                analysis-value
                                analysis-value-query
                            "
                        >
                            {{ normalizedQuery }}
                        </strong>

                    </div>


                    <span class="analysis-card-number">
                        03
                    </span>

                </article>


                <!-- ENTIDADES -->

                <article
                    v-if="analysis?.entities?.length"
                    class="
                        analysis-card
                        analysis-card-wide
                        analysis-card-entities
                    "
                >

                    <div class="analysis-card-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >

                            <circle
                                cx="9"
                                cy="8"
                                r="3"
                            />

                            <circle
                                cx="17"
                                cy="10"
                                r="2.5"
                            />

                            <path
                                d="M3.5 20a5.5 5.5 0 0 1 11 0"
                            />

                            <path
                                d="M14 19a4.5 4.5 0 0 1 7 1"
                            />

                        </svg>

                    </div>


                    <div class="analysis-card-content">

                        <span class="analysis-label">
                            Conceptos y entidades detectadas
                        </span>


                        <div class="analysis-tags">

                            <span
                                v-for="entity in analysis.entities"
                                :key="entity"
                                class="analysis-tag"
                            >
                                <span class="analysis-tag-dot"></span>

                                {{ entity }}

                            </span>

                        </div>

                    </div>


                    <span class="analysis-card-number">
                        04
                    </span>

                </article>

            </div>

        </div>


        <!-- =========================================
             FOOTER
        ========================================== -->

        <footer class="analysis-footer">

            <div class="analysis-footer-brand">

                <span class="footer-mark">
                    NS
                </span>

                <span>
                    Interpretación generada automáticamente
                    para optimizar la recuperación jurídica.
                </span>

            </div>


            <span class="analysis-footer-status">

                <span class="footer-status-dot"></span>

                Procesado

            </span>

        </footer>

    </section>

</template>


<script setup>

import { computed } from "vue"


/* =========================================
   PROPS
========================================= */

const props = defineProps({

    analysis: {

        type: Object,

        default: () => ({})

    },

    normalizedQuery: {

        type: String,

        default: ""

    }

})


/* =========================================
   VERIFICAR SI EXISTE INFORMACIÓN
========================================= */

const hasAnalysis = computed(() => {

    return (

        props.analysis?.rama ||

        props.analysis?.intent ||

        props.normalizedQuery ||

        props.analysis?.entities?.length

    )

})

</script>


<style scoped>

/* =========================================================
   NOVA SEARCH — ANALYSIS
   LÍNEA VISUAL INSTITUCIONAL NOVA IURIS
========================================================= */


/* =========================================================
   CONTENEDOR PRINCIPAL
========================================================= */

.nova-search-analysis {

    width: 100%;

    box-sizing: border-box;

    overflow: hidden;

    background:

        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FCFDFE 58%,
            #F7F9FC 100%
        );

    border:
        1px solid
        #D6DFEA;

    border-radius: 12px;

    box-shadow:

        0 14px 34px
        rgba(
            23,
            55,
            94,
            .055
        );

    animation:

        novaAnalysisEnter
        .35s
        ease-out;

}


/* =========================================================
   HEADER
========================================================= */

.analysis-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 28px;

    padding:
        28px
        30px
        25px;

    border-bottom:
        1px solid
        #E2E8EF;

    background:

        linear-gradient(
            90deg,
            #FFFFFF 0%,
            #FBFCFE 100%
        );

}


.analysis-heading {

    min-width: 0;

    flex: 1;

}


.analysis-heading-top {

    display: flex;

    align-items: center;

    gap: 10px;

    margin-bottom: 7px;

}


.analysis-eyebrow {

    display: block;

    color:
        #7A6440;

    font-size:
        .65rem;

    font-weight:
        800;

    letter-spacing:
        1.45px;

}


.analysis-index {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    min-width: 27px;

    height: 19px;

    padding: 0 6px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .28
        );

    border-radius: 4px;

    background:
        rgba(
            176,
            138,
            76,
            .045
        );

    color:
        #9A7A42;

    font-size:
        .59rem;

    font-weight:
        800;

    letter-spacing:
        .6px;

}


.analysis-heading h2 {

    margin: 0;

    color:
        #17375E;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:
        1.5rem;

    font-weight:
        600;

    line-height:
        1.3;

}


.analysis-heading p {

    max-width:
        780px;

    margin:
        8px
        0
        0;

    color:
        #627183;

    font-size:
        .88rem;

    line-height:
        1.7;

}


/* =========================================================
   SELLO
========================================================= */

.analysis-seal {

    position:
        relative;

    width:
        66px;

    height:
        66px;

    flex:
        0 0 66px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .50
        );

    border-radius:
        50%;

    background:

        radial-gradient(
            circle,
            rgba(
                176,
                138,
                76,
                .065
            ) 0%,
            transparent 70%
        );

    color:
        #7A6440;

}


.analysis-seal::before {

    content:
        "";

    position:
        absolute;

    inset:
        6px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .24
        );

    border-radius:
        50%;

}


.analysis-seal-inner {

    position:
        relative;

    z-index:
        1;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

}


.analysis-seal svg {

    width:
        28px;

    height:
        28px;

}


/* =========================================================
   BODY
========================================================= */

.analysis-body {

    padding:
        24px
        30px
        27px;

}


.analysis-context {

    display:
        flex;

    align-items:
        center;

    gap:
        9px;

    margin-bottom:
        14px;

    color:
        #8A96A3;

    font-size:
        .67rem;

    font-weight:
        800;

    letter-spacing:
        .8px;

    text-transform:
        uppercase;

}


.analysis-context-line {

    width:
        22px;

    height:
        1px;

    flex:
        0 0 22px;

    background:
        #B08A4C;

}


/* =========================================================
   GRID
========================================================= */

.analysis-grid {

    display:
        grid;

    grid-template-columns:
        repeat(
            2,
            minmax(
                0,
                1fr
            )
        );

    gap:
        12px;

}


/* =========================================================
   CARDS
========================================================= */

.analysis-card {

    position:
        relative;

    display:
        flex;

    align-items:
        flex-start;

    gap:
        13px;

    min-width:
        0;

    box-sizing:
        border-box;

    padding:
        17px;

    background:
        #FFFFFF;

    border:
        1px solid
        #E0E7EF;

    border-radius:
        9px;

    transition:

        border-color
        .2s
        ease,

        box-shadow
        .2s
        ease,

        transform
        .2s
        ease;

}


.analysis-card:hover {

    transform:
        translateY(
            -1px
        );

    border-color:
        #C9D6E4;

    box-shadow:

        0 7px 18px
        rgba(
            23,
            55,
            94,
            .055
        );

}


.analysis-card-wide {

    grid-column:
        span 2;

}


.analysis-card-entities {

    grid-column:
        span 2;

}


/* =========================================================
   ICONOS
========================================================= */

.analysis-card-icon {

    width:
        38px;

    height:
        38px;

    flex:
        0 0 38px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    box-sizing:
        border-box;

    border:
        1px solid
        #DCE5EE;

    border-radius:
        9px;

    background:
        #F7F9FC;

    color:
        #315C97;

}


.analysis-card-icon svg {

    width:
        18px;

    height:
        18px;

}


.legal-symbol {

    color:
        #315C97;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:
        1.15rem;

    font-weight:
        600;

}


/* =========================================================
   CONTENIDO
========================================================= */

.analysis-card-content {

    flex:
        1;

    min-width:
        0;

}


.analysis-label {

    display:
        block;

    margin-bottom:
        5px;

    color:
        #8995A2;

    font-size:
        .61rem;

    font-weight:
        800;

    letter-spacing:
        .9px;

    text-transform:
        uppercase;

}


.analysis-value {

    display:
        block;

    color:
        #17375E;

    font-size:
        .88rem;

    font-weight:
        700;

    line-height:
        1.5;

}


.analysis-value-query {

    color:
        #3D5269;

    font-weight:
        600;

    line-height:
        1.65;

    word-break:
        break-word;

}


/* =========================================================
   NUMERACIÓN
========================================================= */

.analysis-card-number {

    position:
        absolute;

    top:
        13px;

    right:
        14px;

    color:
        #B0BAC5;

    font-size:
        .57rem;

    font-weight:
        800;

    letter-spacing:
        .6px;

}


/* =========================================================
   ENTIDADES
========================================================= */

.analysis-tags {

    display:
        flex;

    flex-wrap:
        wrap;

    gap:
        7px;

    margin-top:
        2px;

}


.analysis-tag {

    display:
        inline-flex;

    align-items:
        center;

    gap:
        6px;

    min-height:
        27px;

    box-sizing:
        border-box;

    padding:
        4px
        9px;

    border:
        1px solid
        #DCE5EE;

    border-radius:
        6px;

    background:
        #F7F9FC;

    color:
        #315C97;

    font-size:
        .7rem;

    font-weight:
        650;

    line-height:
        1.35;

    transition:

        background
        .2s
        ease,

        border-color
        .2s
        ease;

}


.analysis-tag:hover {

    background:
        #F1F5F9;

    border-color:
        #C8D6E5;

}


.analysis-tag-dot {

    width:
        5px;

    height:
        5px;

    flex:
        0 0 5px;

    border-radius:
        50%;

    background:
        #B08A4C;

}


/* =========================================================
   FOOTER
========================================================= */

.analysis-footer {

    display:
        flex;

    align-items:
        center;

    justify-content:
        space-between;

    gap:
        18px;

    padding:
        13px
        30px;

    border-top:
        1px solid
        #E3E8EE;

    background:
        #FBFCFE;

}


.analysis-footer-brand {

    display:
        flex;

    align-items:
        center;

    gap:
        9px;

    min-width:
        0;

    color:
        #8995A2;

    font-size:
        .68rem;

    line-height:
        1.5;

}


.footer-mark {

    display:
        inline-flex;

    align-items:
        center;

    justify-content:
        center;

    width:
        24px;

    height:
        24px;

    flex:
        0 0 24px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .28
        );

    border-radius:
        50%;

    color:
        #8B7044;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:
        .57rem;

    font-weight:
        700;

    letter-spacing:
        .5px;

}


.analysis-footer-status {

    display:
        inline-flex;

    align-items:
        center;

    gap:
        6px;

    flex-shrink:
        0;

    color:
        #64798C;

    font-size:
        .65rem;

    font-weight:
        700;

}


.footer-status-dot {

    width:
        6px;

    height:
        6px;

    border-radius:
        50%;

    background:
        #4E8A68;

    box-shadow:

        0 0 0 3px
        rgba(
            78,
            138,
            104,
            .09
        );

}


/* =========================================================
   ANIMACIÓN
========================================================= */

@keyframes novaAnalysisEnter {

    from {

        opacity:
            0;

        transform:
            translateY(
                8px
            );

    }

    to {

        opacity:
            1;

        transform:
            translateY(
                0
            );

    }

}


/* =========================================================
   RESPONSIVE
========================================================= */

@media(max-width:800px) {

    .analysis-header {

        padding:
            25px
            24px
            22px;

    }


    .analysis-body {

        padding:
            22px
            24px
            24px;

    }


    .analysis-footer {

        padding:
            13px
            24px;

    }

}


@media(max-width:700px) {

    .analysis-grid {

        grid-template-columns:
            1fr;

    }


    .analysis-card-wide,
    .analysis-card-entities {

        grid-column:
            span 1;

    }

}


@media(max-width:600px) {

    .nova-search-analysis {

        border-radius:
            10px;

    }


    .analysis-header {

        flex-direction:
            column;

        gap:
            20px;

        padding:
            22px
            18px;

    }


    .analysis-heading h2 {

        font-size:
            1.28rem;

    }


    .analysis-heading p {

        font-size:
            .82rem;

        line-height:
            1.65;

    }


    .analysis-seal {

        width:
            54px;

        height:
            54px;

        flex-basis:
            54px;

    }


    .analysis-seal svg {

        width:
            23px;

        height:
            23px;

    }


    .analysis-body {

        padding:
            20px
            18px
            22px;

    }


    .analysis-card {

        padding:
            15px;

    }


    .analysis-card-number {

        display:
            none;

    }


    .analysis-value {

        font-size:
            .84rem;

    }


    .analysis-footer {

        align-items:
            flex-start;

        flex-direction:
            column;

        gap:
            10px;

        padding:
            13px
            18px;

    }

}
</style>