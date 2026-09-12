<template>

    <article class="nova-search-result-card">

        <!-- ===================================================
             CABECERA DEL RESULTADO
        ==================================================== -->

        <header class="nova-search-result-header">

            <div class="nova-search-result-heading">

                <span class="nova-search-result-type">

                    {{ result.tipo_documento || 'Documento jurídico' }}

                </span>


                <h3 class="nova-search-result-title">

                    {{ result.titulo }}

                </h3>

            </div>


            <!-- RELEVANCIA -->

            <div
                v-if="hasScore"
                class="nova-search-score"
                :aria-label="`Relevancia ${scorePercentage}%`"
            >

                <span class="nova-search-score-label">
                    RELEVANCIA
                </span>

                <strong>
                    {{ scorePercentage }}%
                </strong>

            </div>

        </header>


        <!-- ===================================================
             METADATA PRINCIPAL
        ==================================================== -->

        <div
            v-if="
                result.rama ||
                result.organo_emisor
            "
            class="nova-search-result-meta"
        >

            <div
                v-if="result.rama"
                class="nova-search-meta-item"
            >

                <span class="nova-search-meta-label">
                    Rama jurídica
                </span>

                <span class="nova-search-meta-value">
                    {{ result.rama }}
                </span>

            </div>


            <div
                v-if="result.organo_emisor"
                class="nova-search-meta-item"
            >

                <span class="nova-search-meta-label">
                    Órgano emisor
                </span>

                <span class="nova-search-meta-value">
                    {{ result.organo_emisor }}
                </span>

            </div>

        </div>


        <!-- ===================================================
             DATOS DEL DOCUMENTO
        ==================================================== -->

        <div
            v-if="
                result.expediente ||
                result.numero ||
                result.fecha_resolucion
            "
            class="nova-search-document-data"
        >

            <div
                v-if="result.expediente"
                class="nova-search-document-item"
            >

                <span class="nova-search-document-label">
                    EXPEDIENTE
                </span>

                <span class="nova-search-document-value">
                    {{ result.expediente }}
                </span>

            </div>


            <div
                v-if="result.numero"
                class="nova-search-document-item"
            >

                <span class="nova-search-document-label">
                    NÚMERO
                </span>

                <span class="nova-search-document-value">
                    {{ result.numero }}
                </span>

            </div>


            <div
                v-if="result.fecha_resolucion"
                class="nova-search-document-item"
            >

                <span class="nova-search-document-label">
                    FECHA
                </span>

                <span class="nova-search-document-value">
                    {{ result.fecha_resolucion }}
                </span>

            </div>

        </div>


        <!-- ===================================================
             MATERIA
        ==================================================== -->

        <div
            v-if="result.materia"
            class="nova-search-materia"
        >

            <span class="nova-search-materia-label">
                Materia
            </span>

            <span class="nova-search-materia-value">
                {{ result.materia }}
            </span>

        </div>


        <!-- ===================================================
             PRECEDENTE VINCULANTE
        ==================================================== -->

        <div
            v-if="result.precedente_vinculante"
            class="nova-search-precedente"
        >

            <span
                class="nova-search-precedente-icon"
                aria-hidden="true"
            >
                ◆
            </span>

            <span>
                Precedente vinculante
            </span>

        </div>


        <!-- ===================================================
             SÍNTESIS JURÍDICA
        ==================================================== -->

        <div
            v-if="result.resumen_ia"
            class="nova-search-summary"
        >

            <div class="nova-search-summary-heading">

                <span class="nova-search-summary-line"></span>

                <span class="nova-search-section-label">
                    SÍNTESIS JURÍDICA
                </span>

            </div>


            <p>
                {{ result.resumen_ia }}
            </p>

        </div>


        <!-- ===================================================
             EXTRACTO JURÍDICO
        ==================================================== -->

        <details
            v-if="result.extracto_exacto"
            class="nova-search-details"
        >

            <summary>

                <span class="nova-search-details-label">
                    Consultar extracto jurídico
                </span>


                <span
                    class="nova-search-details-symbol"
                    aria-hidden="true"
                >
                    +
                </span>

            </summary>


            <div class="nova-search-extract">

                <span class="nova-search-extract-label">
                    EXTRACTO DEL DOCUMENTO
                </span>

                <div class="nova-search-extract-content">
                    {{ result.extracto_exacto }}
                </div>

            </div>

        </details>

    </article>

</template>


<script setup>

import { computed } from "vue"


/* =========================================================
   PROPS
========================================================= */

const props = defineProps({

    result: {

        type: Object,

        required: true

    }

})


/* =========================================================
   RELEVANCIA
========================================================= */

const hasScore = computed(() => {

    return typeof props.result.score === "number"

})


const scorePercentage = computed(() => {

    if (!hasScore.value) {

        return 0

    }


    return Math.min(

        100,

        Math.max(

            0,

            Math.round(
                props.result.score * 100
            )

        )

    )

})

</script>


<style scoped>

/* =========================================================
   NOVA SEARCH — RESULT CARD
   Estilo institucional / jurídico / premium
========================================================= */

.nova-search-result-card {

    position: relative;

    width: 100%;

    box-sizing: border-box;

    padding: 26px 28px;

    margin-bottom: 16px;

    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FFFFFF 70%,
            #FBFCFE 100%
        );

    border:
        1px solid
        #D9E2EC;

    border-radius: 12px;

    box-shadow:
        0 8px 24px
        rgba(
            23,
            55,
            94,
            .045
        );

    transition:
        transform .22s ease,
        border-color .22s ease,
        box-shadow .22s ease;

}


/* Línea institucional superior */

.nova-search-result-card::before {

    content: "";

    position: absolute;

    top: 0;

    left: 28px;

    width: 42px;

    height: 2px;

    background:
        #B08A4C;

    opacity: .75;

}


.nova-search-result-card:hover {

    transform:
        translateY(-2px);

    border-color:
        #C4D1DF;

    box-shadow:
        0 14px 34px
        rgba(
            23,
            55,
            94,
            .075
        );

}


/* =========================================================
   CABECERA
========================================================= */

.nova-search-result-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 24px;

}


.nova-search-result-heading {

    flex: 1;

    min-width: 0;

}


/* =========================================================
   TIPO DE DOCUMENTO
========================================================= */

.nova-search-result-type {

    display: inline-flex;

    align-items: center;

    min-height: 24px;

    box-sizing: border-box;

    padding:
        0
        10px;

    margin-bottom: 9px;

    border:
        1px solid
        #D6E0EA;

    border-radius: 999px;

    background:
        #F6F8FB;

    color:
        #315C97;

    font-size: .62rem;

    font-weight: 800;

    letter-spacing: .8px;

    line-height: 1;

    text-transform: uppercase;

}


/* =========================================================
   TÍTULO
========================================================= */

.nova-search-result-title {

    margin: 0;

    color:
        #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:
        1.18rem;

    font-weight:
        600;

    line-height:
        1.48;

    letter-spacing:
        -.1px;

}


/* =========================================================
   SCORE
========================================================= */

.nova-search-score {

    position: relative;

    min-width: 76px;

    flex:
        0 0 76px;

    box-sizing: border-box;

    padding:
        9px
        10px;

    text-align: center;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .34
        );

    border-radius: 9px;

    background:
        linear-gradient(
            135deg,
            #FFFCF7 0%,
            #FFF9EF 100%
        );

}


.nova-search-score::before {

    content: "";

    position: absolute;

    top: 0;

    left: 12px;

    right: 12px;

    height: 1px;

    background:
        rgba(
            176,
            138,
            76,
            .45
        );

}


.nova-search-score-label {

    display: block;

    margin-bottom: 3px;

    color:
        #8A6A37;

    font-size:
        .54rem;

    font-weight:
        800;

    letter-spacing:
        .8px;

}


.nova-search-score strong {

    display: block;

    color:
        #17375E;

    font-size:
        .95rem;

    font-weight:
        800;

    line-height:
        1.2;

}


/* =========================================================
   METADATA PRINCIPAL
========================================================= */

.nova-search-result-meta {

    display: flex;

    flex-wrap: wrap;

    gap:
        10px
        22px;

    margin-top:
        17px;

}


.nova-search-meta-item {

    display: flex;

    align-items: baseline;

    gap: 7px;

    min-width: 0;

}


.nova-search-meta-label {

    color:
        #8A98A8;

    font-size:
        .59rem;

    font-weight:
        800;

    letter-spacing:
        .7px;

    text-transform:
        uppercase;

}


.nova-search-meta-value {

    color:
        #536579;

    font-size:
        .77rem;

    font-weight:
        600;

}


/* =========================================================
   DATOS DEL DOCUMENTO
========================================================= */

.nova-search-document-data {

    display: flex;

    flex-wrap: wrap;

    gap:
        0;

    margin-top:
        17px;

    padding-top:
        17px;

    border-top:
        1px solid
        #E7ECF1;

}


.nova-search-document-item {

    min-width: 150px;

    padding:
        0
        20px;

    border-right:
        1px solid
        #E3E9EF;

}


.nova-search-document-item:first-child {

    padding-left: 0;

}


.nova-search-document-item:last-child {

    border-right:
        none;

}


.nova-search-document-label {

    display: block;

    margin-bottom: 4px;

    color:
        #98A4B0;

    font-size:
        .57rem;

    font-weight:
        800;

    letter-spacing:
        .75px;

}


.nova-search-document-value {

    display: block;

    color:
        #42566C;

    font-size:
        .79rem;

    font-weight:
        600;

    line-height:
        1.45;

}


/* =========================================================
   MATERIA
========================================================= */

.nova-search-materia {

    display: flex;

    align-items: center;

    flex-wrap: wrap;

    gap: 8px;

    margin-top:
        18px;

}


.nova-search-materia-label {

    color:
        #8A98A8;

    font-size:
        .61rem;

    font-weight:
        800;

    letter-spacing:
        .75px;

    text-transform:
        uppercase;

}


.nova-search-materia-value {

    display: inline-flex;

    align-items: center;

    min-height: 26px;

    padding:
        4px
        10px;

    box-sizing: border-box;

    border:
        1px solid
        #DCE5EE;

    border-radius:
        6px;

    background:
        #F5F7FA;

    color:
        #315C97;

    font-size:
        .71rem;

    font-weight:
        700;

}


/* =========================================================
   PRECEDENTE VINCULANTE
========================================================= */

.nova-search-precedente {

    display: inline-flex;

    align-items: center;

    gap:
        8px;

    margin-top:
        14px;

    padding:
        7px
        11px;

    box-sizing: border-box;

    border:
        1px solid
        #E7D8B9;

    border-radius:
        7px;

    background:
        #FFFBF4;

    color:
        #7A6440;

    font-size:
        .71rem;

    font-weight:
        750;

}


.nova-search-precedente-icon {

    color:
        #B08A4C;

    font-size:
        .58rem;

}


/* =========================================================
   SÍNTESIS JURÍDICA
========================================================= */

.nova-search-summary {

    margin-top:
        21px;

}


.nova-search-summary-heading {

    display: flex;

    align-items: center;

    gap:
        8px;

    margin-bottom:
        8px;

}


.nova-search-summary-line {

    width:
        16px;

    height:
        1px;

    flex:
        0 0 16px;

    background:
        #B08A4C;

}


.nova-search-section-label {

    display: block;

    color:
        #7A6440;

    font-size:
        .61rem;

    font-weight:
        800;

    letter-spacing:
        1.05px;

}


.nova-search-summary p {

    margin:
        0;

    color:
        #4B5B6C;

    font-size:
        .89rem;

    line-height:
        1.82;

}


/* =========================================================
   EXTRACTO
========================================================= */

.nova-search-details {

    margin-top:
        20px;

    padding-top:
        17px;

    border-top:
        1px solid
        #E7ECF1;

}


.nova-search-details summary {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap:
        12px;

    cursor:
        pointer;

    list-style:
        none;

    color:
        #315C97;

    font-size:
        .78rem;

    font-weight:
        750;

    outline:
        none;

}


.nova-search-details summary::-webkit-details-marker {

    display:
        none;

}


.nova-search-details-label {

    transition:
        color .2s ease;

}


.nova-search-details summary:hover
.nova-search-details-label {

    color:
        #17375E;

}


.nova-search-details-symbol {

    width:
        26px;

    height:
        26px;

    flex:
        0 0 26px;

    display: flex;

    align-items: center;

    justify-content: center;

    box-sizing: border-box;

    border:
        1px solid
        #D5DFEA;

    border-radius:
        50%;

    background:
        #FFFFFF;

    color:
        #7A6440;

    font-size:
        .95rem;

    font-weight:
        400;

    line-height:
        1;

    transition:
        transform .2s ease,
        border-color .2s ease,
        background .2s ease;

}


.nova-search-details summary:hover
.nova-search-details-symbol {

    border-color:
        #C2CFDD;

    background:
        #F8FAFC;

}


.nova-search-details[open]
.nova-search-details-symbol {

    transform:
        rotate(45deg);

}


.nova-search-extract {

    margin-top:
        14px;

    padding:
        16px
        18px;

    border-left:
        2px solid
        #B08A4C;

    border-radius:
        0
        7px
        7px
        0;

    background:
        #F8FAFC;

}


.nova-search-extract-label {

    display:
        block;

    margin-bottom:
        8px;

    color:
        #8996A4;

    font-size:
        .58rem;

    font-weight:
        800;

    letter-spacing:
        .85px;

}


.nova-search-extract-content {

    color:
        #536273;

    font-size:
        .85rem;

    line-height:
        1.8;

    white-space:
        pre-wrap;

}


/* =========================================================
   FOCUS ACCESIBLE
========================================================= */

.nova-search-details summary:focus-visible {

    outline:
        2px solid
        rgba(
            49,
            92,
            151,
            .28
        );

    outline-offset:
        4px;

    border-radius:
        4px;

}


/* =========================================================
   RESPONSIVE — TABLET
========================================================= */

@media (max-width: 760px) {

    .nova-search-result-card {

        padding:
            24px;

    }


    .nova-search-result-card::before {

        left:
            24px;

    }


    .nova-search-result-header {

        gap:
            18px;

    }


    .nova-search-result-title {

        font-size:
            1.1rem;

    }


    .nova-search-document-item {

        min-width:
            135px;

    }

}


/* =========================================================
   RESPONSIVE — MOBILE
========================================================= */

@media (max-width: 640px) {

    .nova-search-result-card {

        padding:
            21px
            18px;

        margin-bottom:
            13px;

        border-radius:
            10px;

    }


    .nova-search-result-card::before {

        left:
            18px;

        width:
            34px;

    }


    .nova-search-result-header {

        flex-direction:
            column;

        gap:
            14px;

    }


    .nova-search-score {

        align-self:
            flex-start;

        min-width:
            74px;

        flex-basis:
            74px;

    }


    .nova-search-result-title {

        font-size:
            1.05rem;

        line-height:
            1.45;

    }


    .nova-search-result-meta {

        flex-direction:
            column;

        gap:
            8px;

    }


    .nova-search-document-data {

        flex-direction:
            column;

        gap:
            13px;

    }


    .nova-search-document-item {

        min-width:
            0;

        padding:
            0 0 13px;

        border-right:
            none;

        border-bottom:
            1px solid
            #E7ECF1;

    }


    .nova-search-document-item:last-child {

        padding-bottom:
            0;

        border-bottom:
            none;

    }


    .nova-search-summary p {

        font-size:
            .87rem;

        line-height:
            1.78;

    }


    .nova-search-extract {

        padding:
            14px;

    }

}


/* =========================================================
   REDUCCIÓN DE MOVIMIENTO
========================================================= */

@media (prefers-reduced-motion: reduce) {

    .nova-search-result-card,
    .nova-search-details-symbol,
    .nova-search-details-label {

        transition:
            none;

    }

    .nova-search-result-card:hover {

        transform:
            none;

    }

}

</style>