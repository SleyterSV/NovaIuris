<template>

    <section class="court-summary">

        <!-- =========================================
             CABECERA
        ========================================== -->

        <header class="summary-header">

            <div class="summary-header-accent"></div>

            <div class="summary-header-content">

                <span class="section-eyebrow">

                    RESUMEN JUDICIAL

                </span>

                <h2>

                    Panorama del caso

                </h2>

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

                <div class="summary-item-number">

                    0{{ index + 1 }}

                </div>


                <div class="summary-item-content">

                    <span class="summary-label">

                        {{ item.label }}

                    </span>

                    <strong class="summary-value">

                        {{ item.value }}

                    </strong>

                </div>


                <div class="summary-item-icon">

                    {{ item.icon }}

                </div>

            </div>

        </div>

    </section>

</template>


<script setup>

import {

    computed

} from "vue"


const props = defineProps({

    summary: {

        type: Object,

        default: () => ({})

    }

})


const summaryItems = computed(() => [

    {

        label: "Tipo de Proceso",

        value:

            props.summary.proceso
            ||
            "No identificado",

        icon: "⚖️"

    },


    {

        label: "Escenario Judicial",

        value:

            props.summary.escenario
            ||
            "En evaluación",

        icon: "🏛️"

    },


    {

        label: "Probabilidad Estimada",

        value:

            props.summary.probabilidad
            ||
            "--",

        icon: "◉"

    },


    {

        label: "Nivel de Riesgo",

        value:

            props.summary.riesgo
            ||
            "--",

        icon: "△"

    }

])

</script>


<style scoped>

/* =========================================
   COURT SUMMARY
   ESTILO JURÍDICO · EDITORIAL · INSTITUCIONAL

   REFERENCIA VISUAL:
   NOVA IURIS
   AZUL MARINO + DORADO SOBRIO
========================================= */

.court-summary {

    width: 100%;

    background: #FFFFFF;

}


/* =========================================
   CABECERA
========================================= */

.summary-header {

    display: flex;

    align-items: stretch;

    gap: 24px;

    padding-bottom: 28px;

    border-bottom:
        1px solid
        #D8DEE6;

}


.summary-header-accent {

    width: 3px;

    flex-shrink: 0;

    min-height: 112px;

    background:

        linear-gradient(
            180deg,
            #B08A4C 0%,
            #D5BD8C 100%
        );

}


.summary-header-content {

    flex: 1;

    min-width: 0;

}


/* =========================================
   EYEBROW
========================================= */

.section-eyebrow {

    display: block;

    margin-bottom: 10px;

    color: #8B7047;

    font-size: .68rem;

    font-weight: 800;

    letter-spacing: 1.6px;

}


/* =========================================
   TÍTULO
========================================= */

.summary-header h2 {

    margin: 0 0 11px;

    color: #102238;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.7rem;

    font-weight: 500;

    line-height: 1.3;

    letter-spacing: -.2px;

}


/* =========================================
   DESCRIPCIÓN
========================================= */

.summary-header p {

    max-width: 760px;

    margin: 0;

    color: #5E6D7E;

    font-size: .95rem;

    font-weight: 400;

    line-height: 1.8;

}


/* =========================================
   INFORMACIÓN
========================================= */

.summary-information {

    width: 100%;

}


/* =========================================
   FILA DE INFORMACIÓN

   IMPORTANTE:
   NO USAMOS CARDS INDIVIDUALES.
   EL RESULTADO SE PRESENTA COMO
   INFORMACIÓN ESTRUCTURADA DE UN INFORME.
========================================= */

.summary-item {

    display: grid;

    grid-template-columns:
        58px
        minmax(0, 1fr)
        42px;

    align-items: center;

    gap: 20px;

    min-height: 104px;

    padding: 22px 4px;

    border-bottom:
        1px solid
        #E1E6EC;

    transition:
        padding-left .25s ease,
        background .25s ease;

}


.summary-item:last-child {

    border-bottom: none;

}


/* =========================================
   INTERACCIÓN SUTIL
========================================= */

.summary-item:hover {

    padding-left: 10px;

    background:

        linear-gradient(
            90deg,
            rgba(23, 55, 94, .035) 0%,
            rgba(23, 55, 94, 0) 72%
        );

}


/* =========================================
   NUMERACIÓN
========================================= */

.summary-item-number {

    color: #B08A4C;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: .88rem;

    font-weight: 600;

    letter-spacing: .08em;

}


/* =========================================
   CONTENIDO
========================================= */

.summary-item-content {

    display: flex;

    flex-direction: column;

    gap: 7px;

    min-width: 0;

}


.summary-label {

    color: #7A8694;

    font-size: .68rem;

    font-weight: 800;

    letter-spacing: 1.25px;

    text-transform: uppercase;

}


.summary-value {

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.08rem;

    font-weight: 500;

    line-height: 1.45;

    word-break: break-word;

}


/* =========================================
   ICONO
========================================= */

.summary-item-icon {

    width: 38px;

    height: 38px;

    display: flex;

    align-items: center;

    justify-content: center;

    justify-self: end;

    color: #B08A4C;

    border-left:
        1px solid
        #E1E6EC;

    font-size: 1rem;

    line-height: 1;

    opacity: .9;

}


/* =========================================
   RESPONSIVE - TABLET
========================================= */

@media (max-width: 768px) {

    .summary-header {

        gap: 20px;

        padding-bottom: 24px;

    }


    .summary-header h2 {

        font-size: 1.5rem;

    }


    .summary-item {

        grid-template-columns:
            48px
            minmax(0, 1fr)
            36px;

        gap: 16px;

    }

}


/* =========================================
   RESPONSIVE - MOBILE
========================================= */

@media (max-width: 576px) {

    .summary-header {

        gap: 16px;

    }


    .summary-header-accent {

        width: 3px;

        min-height: 130px;

    }


    .section-eyebrow {

        font-size: .63rem;

        letter-spacing: 1.3px;

    }


    .summary-header h2 {

        font-size: 1.35rem;

    }


    .summary-header p {

        font-size: .88rem;

        line-height: 1.7;

    }


    .summary-item {

        grid-template-columns:
            36px
            minmax(0, 1fr);

        gap: 13px;

        min-height: 90px;

        padding:
            18px
            0;

    }


    .summary-item-icon {

        display: none;

    }


    .summary-label {

        font-size: .62rem;

    }


    .summary-value {

        font-size: 1rem;

    }

}

</style>