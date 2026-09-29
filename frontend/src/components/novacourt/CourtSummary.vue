<template>

    <section class="court-summary">

        <!-- =========================================
             CABECERA
        ========================================== -->

        <header class="summary-header">

            <div class="summary-header-line"></div>

            <div class="summary-header-content">

                <span class="section-eyebrow">
                    RESUMEN JUDICIAL
                </span>

                <h2>
                    Panorama del caso
                </h2>

                <div class="title-accent"></div>

                <p>
                    Síntesis estructurada del escenario judicial
                    y de los principales factores identificados
                    durante la simulación.
                </p>

            </div>

        </header>


        <!-- =========================================
             INFORMACIÓN DEL CASO
        ========================================== -->

        <div class="summary-information">

            <div
                v-for="(item, index) in summaryItems"
                :key="item.label"
                class="summary-item"
            >

                <!-- NUMERACIÓN -->

                <div class="summary-item-number">

                    {{ String(index + 1).padStart(2, "0") }}

                </div>


                <!-- CONTENIDO -->

                <div class="summary-item-content">

                    <span class="summary-label">

                        {{ item.label }}

                    </span>

                    <strong
                        class="summary-value"
                        :class="{
                            'value-positive':
                                item.type === 'positive',

                            'value-warning':
                                item.type === 'warning',

                            'value-neutral':
                                item.type === 'neutral'
                        }"
                    >

                        {{ item.value }}

                    </strong>

                </div>


                <!-- INDICADOR -->

                <div
                    class="summary-item-indicator"
                    :class="{
                        'indicator-positive':
                            item.type === 'positive',

                        'indicator-warning':
                            item.type === 'warning',

                        'indicator-neutral':
                            item.type === 'neutral'
                    }"
                    aria-hidden="true"
                ></div>

            </div>

        </div>

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

        value:
            props.summary.proceso
            ||
            "No identificado con la información disponible.",

        type: "neutral"

    },


    {

        label: "Problemas jurídicos identificados",

        value:
            String(props.issueCount),

        type: "neutral"

    },


    {

        label: "Simulación jurídica",

        value:
            props.simulationStatus === 'ready' ? 'Disponible' : 'No disponible',

        type: "warning"

    },
    { label: 'Grafo jurídico', value: props.graphStatus === 'ready' ? 'Disponible' : 'No disponible', type: 'neutral' }

])

</script>


<style scoped>

/* =====================================================
   COURT SUMMARY

   IDENTIDAD:
   JURÍDICA · INSTITUCIONAL · EDITORIAL · SOBRIA

   SISTEMA VISUAL:
   AZUL MARINO  → #17375E
   AZUL         → #315C97
   DORADO       → #B08A4C
   FONDO        → #FFFFFF

   PRINCIPIO:
   NO CARD.
   NO SOMBRAS.
   NO EXCESOS DECORATIVOS.

   DEBE SENTIRSE COMO UNA SECCIÓN
   DE UN INFORME JURÍDICO PROFESIONAL.
===================================================== */


/* =====================================================
   CONTENEDOR PRINCIPAL
===================================================== */

.court-summary {

    width: 100%;

    margin: 0;

    padding: 0;

    background: #FFFFFF;

}


/* =====================================================
   CABECERA
===================================================== */

.summary-header {

    position: relative;

    display: flex;

    align-items: stretch;

    width: 100%;

    padding:

        0

        0

        30px;

    border-bottom:
        1px solid
        #D9E0E8;

}


/* =====================================================
   LÍNEA DE IDENTIDAD

   Azul principal.
   El dorado queda reservado para
   pequeños detalles del sistema.
===================================================== */

.summary-header-line {

    width: 3px;

    min-height: 116px;

    flex-shrink: 0;

    margin-right: 24px;

    background:

        linear-gradient(
            180deg,
            #17375E 0%,
            #315C97 100%
        );

}


/* =====================================================
   CONTENIDO CABECERA
===================================================== */

.summary-header-content {

    flex: 1;

    min-width: 0;

    max-width: 880px;

}


/* =====================================================
   EYEBROW
===================================================== */

.section-eyebrow {

    display: block;

    margin-bottom: 13px;

    color: #315C97;

    font-size: .67rem;

    font-weight: 800;

    letter-spacing: 1.55px;

    line-height: 1.2;

}


/* =====================================================
   TÍTULO
===================================================== */

.summary-header h2 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.85rem;

    font-weight: 500;

    line-height: 1.28;

    letter-spacing: -.25px;

}


/* =====================================================
   ACENTO DEL TÍTULO
===================================================== */

.title-accent {

    width: 44px;

    height: 2px;

    margin:
        17px
        0
        17px;

    background: #315C97;

}


/* =====================================================
   DESCRIPCIÓN
===================================================== */

.summary-header p {

    max-width: 790px;

    margin: 0;

    color: #5E6D7E;

    font-size: .94rem;

    font-weight: 400;

    line-height: 1.82;

    letter-spacing: .005em;

}


/* =====================================================
   INFORMACIÓN
===================================================== */

.summary-information {

    width: 100%;

    margin-top: 4px;

}


/* =====================================================
   FILA DE INFORMACIÓN

   Se mantiene como estructura editorial,
   no como colección de cards.
===================================================== */

.summary-item {

    position: relative;

    display: grid;

    grid-template-columns:

        58px

        minmax(0, 1fr)

        20px;

    align-items: center;

    gap: 20px;

    width: 100%;

    min-height: 104px;

    padding:

        22px

        4px;

    border-bottom:
        1px solid
        #E1E6EC;

    transition:
        background .22s ease,
        padding-left .22s ease;

}


/* =====================================================
   ÚLTIMO ELEMENTO
===================================================== */

.summary-item:last-child {

    border-bottom: none;

}


/* =====================================================
   HOVER

   Muy discreto para mantener
   apariencia institucional.
===================================================== */

.summary-item:hover {

    padding-left: 10px;

    background:

        linear-gradient(
            90deg,
            rgba(23, 55, 94, .035) 0%,
            rgba(23, 55, 94, 0) 75%
        );

}


/* =====================================================
   NUMERACIÓN
===================================================== */

.summary-item-number {

    align-self: start;

    padding-top: 2px;

    color: #B08A4C;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: .79rem;

    font-weight: 600;

    letter-spacing: .12em;

    line-height: 1.4;

}


/* =====================================================
   CONTENIDO
===================================================== */

.summary-item-content {

    display: flex;

    flex-direction: column;

    gap: 7px;

    min-width: 0;

}


/* =====================================================
   ETIQUETA
===================================================== */

.summary-label {

    display: block;

    color: #7A8795;

    font-size: .65rem;

    font-weight: 800;

    letter-spacing: 1.35px;

    line-height: 1.3;

    text-transform: uppercase;

}


/* =====================================================
   VALOR
===================================================== */

.summary-value {

    display: block;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.06rem;

    font-weight: 500;

    line-height: 1.45;

    word-break: break-word;

}


/* =====================================================
   VALORES ESPECIALES
===================================================== */

.value-positive {

    color: #315C97;

}


.value-warning {

    color: #8B7047;

}


.value-neutral {

    color: #17375E;

}


/* =====================================================
   INDICADOR LATERAL
===================================================== */

.summary-item-indicator {

    width: 7px;

    height: 7px;

    justify-self: end;

    border-radius: 50%;

    opacity: .9;

}


/* =====================================================
   INDICADORES
===================================================== */

.indicator-positive {

    background: #315C97;

}


.indicator-warning {

    background: #B08A4C;

}


.indicator-neutral {

    background: #9BA8B5;

}


/* =====================================================
   FOCUS / ACCESIBILIDAD
===================================================== */

.summary-item:focus-within {

    outline:
        1px solid
        rgba(
            49,
            92,
            151,
            .18
        );

    outline-offset: -1px;

}


/* =====================================================
   RESPONSIVE - TABLET
===================================================== */

@media (max-width: 768px) {

    .summary-header {

        padding-bottom: 26px;

    }


    .summary-header-line {

        width: 3px;

        min-height: 108px;

        margin-right: 20px;

    }


    .summary-header h2 {

        font-size: 1.65rem;

    }


    .summary-header p {

        font-size: .92rem;

        line-height: 1.78;

    }


    .summary-item {

        grid-template-columns:

            48px

            minmax(0, 1fr)

            16px;

        gap: 16px;

        min-height: 96px;

        padding:

            20px

            3px;

    }


    .summary-item-number {

        font-size: .76rem;

    }


    .summary-value {

        font-size: 1rem;

    }

}


/* =====================================================
   RESPONSIVE - MOBILE
===================================================== */

@media (max-width: 576px) {

    .summary-header {

        padding-bottom: 24px;

    }


    .summary-header-line {

        width: 2px;

        min-height: 126px;

        margin-right: 16px;

    }


    .section-eyebrow {

        margin-bottom: 11px;

        font-size: .62rem;

        letter-spacing: 1.25px;

    }


    .summary-header h2 {

        font-size: 1.42rem;

        line-height: 1.3;

    }


    .title-accent {

        width: 38px;

        height: 2px;

        margin:
            15px
            0;

    }


    .summary-header p {

        font-size: .88rem;

        line-height: 1.72;

    }


    .summary-information {

        margin-top: 2px;

    }


    .summary-item {

        grid-template-columns:

            34px

            minmax(0, 1fr)

            8px;

        gap: 13px;

        min-height: 88px;

        padding:

            18px

            0;

    }


    .summary-item:hover {

        padding-left: 5px;

    }


    .summary-item-number {

        padding-top: 1px;

        font-size: .69rem;

        letter-spacing: .08em;

    }


    .summary-item-content {

        gap: 6px;

    }


    .summary-label {

        font-size: .59rem;

        letter-spacing: 1.1px;

    }


    .summary-value {

        font-size: .96rem;

        line-height: 1.42;

    }


    .summary-item-indicator {

        width: 6px;

        height: 6px;

    }

}

</style>
