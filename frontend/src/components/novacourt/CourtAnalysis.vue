<template>

    <section class="court-analysis">

        <!-- =========================================
             ENCABEZADO
        ========================================== -->

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


            <div
                v-if="status"
                class="analysis-status"
                :class="statusClass"
            >

                <span class="status-dot"></span>

                <span>
                    {{ status }}
                </span>

            </div>

        </header>


        <!-- =========================================
             LOADING
        ========================================== -->

        <div
            v-if="loading"
            class="analysis-loading"
        >

            <div class="loading-indicator">

                <div class="loading-spinner"></div>

            </div>


            <div class="loading-content">

                <strong>
                    Analizando el escenario judicial
                </strong>

                <span>
                    NovaCourt está organizando los hechos,
                    evaluando los elementos jurídicos y
                    estructurando el análisis del caso.
                </span>

            </div>

        </div>


        <!-- =========================================
             CONTENIDO
        ========================================== -->

        <div
            v-else-if="content"
            class="analysis-content"
        >

            <MarkdownRenderer
                :content="content"
            />

        </div>


        <!-- =========================================
             ESTADO VACÍO
        ========================================== -->

        <div
            v-else
            class="analysis-empty"
        >

            <div class="empty-mark">
                ANALYSIS
            </div>


            <div class="empty-content">

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


/* =========================================
   PROPS
========================================= */

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


/* =========================================
   ESTADO
========================================= */

const statusClass = computed(() =>

    `status-${props.statusType}`

)

</script>


<style scoped>

/* =====================================================
   COURT ANALYSIS

   IDENTIDAD:
   JURÍDICA · INSTITUCIONAL · SOBRIA · EDITORIAL

   PRINCIPIO:
   EL CONTENEDOR NO ES UNA CARD.
   ES UNA SECCIÓN INTEGRADA DENTRO DEL SISTEMA.
===================================================== */


/* =====================================================
   CONTENEDOR PRINCIPAL
===================================================== */

.court-analysis {

    width: 100%;

    margin: 0;

    padding: 42px 48px 44px;

    background: #FFFFFF;

}


/* =====================================================
   ENCABEZADO
===================================================== */

.analysis-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 32px;

    padding-bottom: 28px;

    border-bottom:
        1px solid
        #D9E0E8;

}


.analysis-heading {

    flex: 1;

    min-width: 0;

    max-width: 880px;

}


/* =====================================================
   ETIQUETA SUPERIOR
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
   TÍTULO
===================================================== */

.analysis-heading h2 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 2rem;

    font-weight: 500;

    line-height: 1.25;

    letter-spacing: -.2px;

}


/* =====================================================
   LÍNEA DE IDENTIDAD
===================================================== */

.title-accent {

    width: 46px;

    height: 2px;

    margin: 18px 0;

    background: #315C97;

}


/* =====================================================
   DESCRIPCIÓN
===================================================== */

.analysis-heading p {

    max-width: 820px;

    margin: 0;

    color: #5E6D7E;

    font-size: .97rem;

    font-weight: 400;

    line-height: 1.85;

    letter-spacing: .01em;

}


/* =====================================================
   ESTADO DEL ANÁLISIS

   Se mantiene compacto para informar sin convertirlo
   en una tarjeta independiente.
===================================================== */

.analysis-status {

    display: inline-flex;

    align-items: center;

    gap: 9px;

    flex-shrink: 0;

    margin-top: 3px;

    padding: 9px 0;

    color: #647487;

    border-bottom:
        1px solid
        #D9E0E8;

    font-size: .76rem;

    font-weight: 700;

    letter-spacing: .01em;

    white-space: nowrap;

}


.status-dot {

    width: 7px;

    height: 7px;

    flex-shrink: 0;

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

    animation:
        pulse
        1.5s
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
   CONTENIDO
===================================================== */

.analysis-content {

    width: 100%;

    padding-top: 34px;

}


/* =====================================================
   LOADING

   Estado integrado a la sección.
   Sin apariencia de card.
===================================================== */

.analysis-loading {

    display: flex;

    align-items: flex-start;

    gap: 20px;

    min-height: 150px;

    padding: 30px 0;

    border-bottom:
        1px solid
        #E1E6EC;

}


.loading-indicator {

    width: 44px;

    height: 44px;

    display: flex;

    align-items: center;

    justify-content: center;

    flex-shrink: 0;

    border:
        1px solid
        #D4DDE6;

}


.loading-spinner {

    width: 21px;

    height: 21px;

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

    gap: 7px;

    padding-top: 2px;

}


.loading-content strong {

    color: #17375E;

    font-size: .96rem;

    font-weight: 700;

    line-height: 1.5;

}


.loading-content span {

    max-width: 620px;

    color: #647487;

    font-size: .91rem;

    line-height: 1.75;

}


/* =====================================================
   ESTADO VACÍO

   Diseño editorial y sobrio.
===================================================== */

.analysis-empty {

    display: flex;

    align-items: flex-start;

    gap: 28px;

    min-height: 220px;

    padding: 38px 0;

    border-bottom:
        1px solid
        #E1E6EC;

}


.empty-mark {

    flex-shrink: 0;

    padding-top: 3px;

    color: #315C97;

    font-size: .62rem;

    font-weight: 700;

    letter-spacing: 1.6px;

    writing-mode: vertical-rl;

    transform: rotate(180deg);

}


.empty-content {

    max-width: 570px;

}


.empty-content h3 {

    margin: 0 0 11px;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.25rem;

    font-weight: 500;

    line-height: 1.35;

}


.empty-content p {

    margin: 0;

    color: #647487;

    font-size: .94rem;

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
   RESPONSIVE - TABLET
===================================================== */

@media (max-width: 768px) {

    .court-analysis {

        padding:
            34px
            30px
            36px;

    }


    .analysis-header {

        flex-direction: column;

        gap: 20px;

    }


    .analysis-status {

        align-self: flex-start;

        margin-top: 0;

    }


    .analysis-heading h2 {

        font-size: 1.8rem;

    }


    .analysis-content {

        padding-top: 28px;

    }

}


/* =====================================================
   RESPONSIVE - MOBILE
===================================================== */

@media (max-width: 576px) {

    .court-analysis {

        padding:
            28px
            20px
            30px;

    }


    .analysis-header {

        padding-bottom: 24px;

    }


    .section-eyebrow {

        margin-bottom: 13px;

        font-size: .64rem;

    }


    .analysis-heading h2 {

        font-size: 1.55rem;

    }


    .title-accent {

        width: 38px;

        margin:
            16px
            0;

    }


    .analysis-heading p {

        font-size: .9rem;

        line-height: 1.75;

    }


    .analysis-content {

        padding-top: 24px;

    }


    .analysis-loading {

        gap: 15px;

        min-height: 130px;

        padding: 24px 0;

    }


    .loading-indicator {

        width: 40px;

        height: 40px;

    }


    .loading-spinner {

        width: 19px;

        height: 19px;

    }


    .loading-content strong {

        font-size: .92rem;

    }


    .loading-content span {

        font-size: .88rem;

        line-height: 1.7;

    }


    .analysis-empty {

        gap: 20px;

        min-height: 190px;

        padding: 30px 0;

    }


    .empty-content h3 {

        font-size: 1.15rem;

    }


    .empty-content p {

        font-size: .89rem;

        line-height: 1.75;

    }

}

</style>