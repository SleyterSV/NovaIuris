<template>

    <section class="court-analysis">

        <!-- =================================================
             ENCABEZADO
        ================================================== -->

        <header class="analysis-header">

            <div class="analysis-heading">

                <span class="section-eyebrow">
                    ANÁLISIS JUDICIAL
                </span>

                <h2>
                    Análisis del caso
                </h2>

                <div class="title-accent"></div>

                <p>
                    Evaluación estructurada de los hechos,
                    argumentos, riesgos y elementos jurídicos
                    relevantes para el escenario analizado.
                </p>

            </div>


            <!-- ESTADO -->

            <div
                v-if="status"
                class="analysis-status"
                :class="statusClass"
            >

                <span class="status-indicator">

                    <span class="status-dot"></span>

                </span>

                <span class="status-label">
                    {{ status }}
                </span>

            </div>

        </header>


        <!-- =================================================
             ESTADO DE CARGA
        ================================================== -->

        <div
            v-if="loading"
            class="analysis-loading"
        >

            <div class="loading-symbol">

                <div class="loading-ring"></div>

            </div>


            <div class="loading-content">

                <span class="loading-eyebrow">
                    NOVACOURT
                </span>

                <strong>
                    Analizando el escenario judicial
                </strong>

                <p>
                    NovaCourt está organizando los hechos,
                    evaluando los elementos jurídicos y
                    estructurando el análisis del caso.
                </p>

            </div>

        </div>


        <!-- =================================================
             CONTENIDO DEL ANÁLISIS
        ================================================== -->

        <div
            v-else-if="content"
            class="analysis-content"
        >

            <div class="content-rule"></div>

            <MarkdownRenderer
                :content="content"
            />

        </div>


        <!-- =================================================
             ESTADO VACÍO
        ================================================== -->

        <div
            v-else
            class="analysis-empty"
        >

            <div class="empty-mark">

                <span class="empty-line"></span>

                <span class="empty-code">
                    NC
                </span>

            </div>


            <div class="empty-content">

                <span class="empty-eyebrow">
                    RESULTADO DEL ANÁLISIS
                </span>

                <h3>
                    Análisis pendiente
                </h3>

                <p>
                    Ingresa la información del caso e inicia
                    la simulación para visualizar el análisis
                    jurídico generado por NovaCourt.
                </p>

            </div>

        </div>

    </section>

</template>


<script setup>

import {
    computed
} from "vue"

import MarkdownRenderer from "../common/MarkdownRenderer.vue"


/* =================================================
   PROPS
================================================= */

const props = defineProps({

    content: {
        type: String,
        default: ""
    },

    loading: {
        type: Boolean,
        default: false
    },

    status: {
        type: String,
        default: ""
    },

    statusType: {
        type: String,
        default: "processing"
    }

})


/* =================================================
   ESTADO VISUAL
================================================= */

const statusClass = computed(() => {

    return `status-${props.statusType}`

})

</script>


<style scoped>

/* =====================================================
   COURT ANALYSIS

   IDENTIDAD VISUAL:

   JURÍDICA
   INSTITUCIONAL
   SOBRIA
   EDITORIAL
   PREMIUM

   PALETA:

   Azul profundo  #17375E
   Azul           #315C97
   Dorado         #B08A4C
   Texto          #24364A
   Gris           #647487
   Bordes         #D9E0E8

   PRINCIPIO:

   La sección forma parte del sistema
   de NovaCourt y NO debe parecer una card.
===================================================== */


/* =====================================================
   CONTENEDOR PRINCIPAL
===================================================== */

.court-analysis {

    position: relative;

    width: 100%;

    margin: 0;

    padding:
        44px
        48px
        48px;

    background: #FFFFFF;

    box-sizing: border-box;

}


/* =====================================================
   LÍNEA SUPERIOR DE IDENTIDAD
===================================================== */

.court-analysis::before {

    content: "";

    position: absolute;

    top: 0;
    left: 0;

    width: 92px;
    height: 2px;

    background:
        linear-gradient(
            90deg,
            #17375E 0%,
            #315C97 72%,
            transparent 100%
        );

}


/* =====================================================
   ENCABEZADO
===================================================== */

.analysis-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 36px;

    padding-bottom: 30px;

    border-bottom:
        1px solid
        #D9E0E8;

}


.analysis-heading {

    flex: 1;

    min-width: 0;

    max-width: 900px;

}


/* =====================================================
   EYEBROW
===================================================== */

.section-eyebrow {

    display: block;

    margin-bottom: 15px;

    color: #315C97;

    font-size: .67rem;

    font-weight: 700;

    letter-spacing: 1.55px;

    line-height: 1.2;

}


/* =====================================================
   TÍTULO
===================================================== */

.analysis-heading h2 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 2.05rem;

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
        17px
        0
        18px;

    background: #315C97;

}


/* =====================================================
   DESCRIPCIÓN
===================================================== */

.analysis-heading p {

    max-width: 830px;

    margin: 0;

    color: #647487;

    font-size: .95rem;

    font-weight: 400;

    line-height: 1.85;

    letter-spacing: .008em;

}


/* =====================================================
   ESTADO
===================================================== */

.analysis-status {

    display: inline-flex;

    align-items: center;

    gap: 9px;

    flex-shrink: 0;

    margin-top: 4px;

    min-height: 34px;

    padding:
        0
        0
        8px;

    border-bottom:
        1px solid
        #D9E0E8;

    color: #647487;

    font-size: .73rem;

    font-weight: 700;

    letter-spacing: .035em;

    white-space: nowrap;

}


/* =====================================================
   INDICADOR DEL ESTADO
===================================================== */

.status-indicator {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    width: 16px;
    height: 16px;

}


.status-dot {

    display: block;

    width: 7px;
    height: 7px;

    border-radius: 50%;

}


/* =====================================================
   PROCESANDO
===================================================== */

.status-processing {

    color: #315C97;

}


.status-processing .status-dot {

    background: #315C97;

    box-shadow:
        0 0 0 3px
        rgba(
            49,
            92,
            151,
            .10
        );

    animation:
        statusPulse
        1.7s
        ease-in-out
        infinite;

}


/* =====================================================
   COMPLETADO
===================================================== */

.status-completed {

    color: #315C97;

}


.status-completed .status-dot {

    background: #315C97;

}


/* =====================================================
   ERROR
===================================================== */

.status-error {

    color: #9B3A3A;

}


.status-error .status-dot {

    background: #B94A4A;

}


/* =====================================================
   ETIQUETA DE ESTADO
===================================================== */

.status-label {

    line-height: 1.2;

}


/* =====================================================
   CONTENIDO
===================================================== */

.analysis-content {

    width: 100%;

    padding-top: 34px;

}


/* =====================================================
   REGLA EDITORIAL DEL CONTENIDO
===================================================== */

.content-rule {

    width: 28px;

    height: 1px;

    margin-bottom: 24px;

    background: #B08A4C;

    opacity: .75;

}


/* =====================================================
   ESTADO DE CARGA
===================================================== */

.analysis-loading {

    display: flex;

    align-items: flex-start;

    gap: 21px;

    min-height: 150px;

    padding:
        34px
        0
        32px;

    border-bottom:
        1px solid
        #E1E6EC;

}


/* =====================================================
   SÍMBOLO DE CARGA
===================================================== */

.loading-symbol {

    position: relative;

    display: flex;

    align-items: center;

    justify-content: center;

    width: 46px;
    height: 46px;

    flex-shrink: 0;

    border:
        1px solid
        #D4DDE6;

}


/* Línea decorativa */

.loading-symbol::before {

    content: "";

    position: absolute;

    top: -1px;
    left: -1px;

    width: 15px;
    height: 1px;

    background: #B08A4C;

}


/* Anillo */

.loading-ring {

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


/* =====================================================
   CONTENIDO DE CARGA
===================================================== */

.loading-content {

    display: flex;

    flex-direction: column;

    gap: 6px;

    padding-top: 1px;

}


.loading-eyebrow {

    color: #315C97;

    font-size: .61rem;

    font-weight: 700;

    letter-spacing: 1.35px;

    line-height: 1.3;

}


.loading-content strong {

    color: #17375E;

    font-size: .96rem;

    font-weight: 700;

    line-height: 1.5;

}


.loading-content p {

    max-width: 650px;

    margin: 2px 0 0;

    color: #647487;

    font-size: .9rem;

    line-height: 1.75;

}


/* =====================================================
   ESTADO VACÍO
===================================================== */

.analysis-empty {

    display: flex;

    align-items: flex-start;

    gap: 27px;

    min-height: 215px;

    padding:
        40px
        0
        34px;

    border-bottom:
        1px solid
        #E1E6EC;

}


/* =====================================================
   MARCA DEL ESTADO VACÍO
===================================================== */

.empty-mark {

    display: flex;

    flex-direction: column;

    align-items: center;

    gap: 9px;

    width: 28px;

    flex-shrink: 0;

    padding-top: 3px;

}


.empty-line {

    width: 1px;

    height: 32px;

    background:
        linear-gradient(
            180deg,
            #315C97,
            #B08A4C
        );

}


.empty-code {

    color: #315C97;

    font-size: .58rem;

    font-weight: 700;

    letter-spacing: 1.2px;

    line-height: 1;

}


/* =====================================================
   CONTENIDO VACÍO
===================================================== */

.empty-content {

    max-width: 600px;

}


.empty-eyebrow {

    display: block;

    margin-bottom: 10px;

    color: #7A8795;

    font-size: .62rem;

    font-weight: 700;

    letter-spacing: 1.3px;

    line-height: 1.3;

}


.empty-content h3 {

    margin: 0 0 11px;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.3rem;

    font-weight: 500;

    line-height: 1.35;

}


.empty-content p {

    margin: 0;

    color: #647487;

    font-size: .93rem;

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


@keyframes statusPulse {

    0%,
    100% {

        transform:
            scale(1);

        opacity: 1;

    }

    50% {

        transform:
            scale(1.3);

        opacity: .55;

    }

}


/* =====================================================
   TABLET
===================================================== */

@media (max-width: 900px) {

    .court-analysis {

        padding:
            38px
            32px
            42px;

    }


    .court-analysis::before {

        width: 78px;

    }


    .analysis-header {

        gap: 26px;

    }


    .analysis-heading h2 {

        font-size: 1.9rem;

    }


    .analysis-heading p {

        font-size: .93rem;

    }


    .analysis-content {

        padding-top: 30px;

    }

}


/* =====================================================
   TABLET PEQUEÑA
===================================================== */

@media (max-width: 768px) {

    .court-analysis {

        padding:
            34px
            30px
            38px;

    }


    .analysis-header {

        flex-direction: column;

        gap: 20px;

        padding-bottom: 26px;

    }


    .analysis-status {

        align-self: flex-start;

        margin-top: 0;

    }


    .analysis-heading h2 {

        font-size: 1.8rem;

    }


    .analysis-loading {

        min-height: 140px;

    }

}


/* =====================================================
   MOBILE
===================================================== */

@media (max-width: 576px) {

    .court-analysis {

        padding:
            29px
            20px
            32px;

    }


    .court-analysis::before {

        width: 58px;

    }


    .analysis-header {

        padding-bottom: 24px;

    }


    .section-eyebrow {

        margin-bottom: 13px;

        font-size: .63rem;

        letter-spacing: 1.35px;

    }


    .analysis-heading h2 {

        font-size: 1.55rem;

        letter-spacing: -.15px;

    }


    .title-accent {

        width: 38px;

        margin:
            15px
            0
            16px;

    }


    .analysis-heading p {

        font-size: .89rem;

        line-height: 1.75;

    }


    .analysis-status {

        font-size: .69rem;

    }


    .analysis-content {

        padding-top: 25px;

    }


    .content-rule {

        margin-bottom: 20px;

    }


    .analysis-loading {

        gap: 15px;

        min-height: 130px;

        padding:
            27px
            0
            25px;

    }


    .loading-symbol {

        width: 40px;
        height: 40px;

    }


    .loading-ring {

        width: 18px;
        height: 18px;

    }


    .loading-content strong {

        font-size: .9rem;

    }


    .loading-content p {

        font-size: .86rem;

        line-height: 1.7;

    }


    .analysis-empty {

        gap: 19px;

        min-height: 185px;

        padding:
            31px
            0
            28px;

    }


    .empty-mark {

        width: 23px;

    }


    .empty-line {

        height: 27px;

    }


    .empty-content h3 {

        font-size: 1.16rem;

    }


    .empty-content p {

        font-size: .87rem;

        line-height: 1.75;

    }

}

</style>