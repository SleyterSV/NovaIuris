<template>

    <section class="court-simulation">

        <!-- =====================================================
             ENCABEZADO
        ====================================================== -->

        <header class="simulation-header">

            <div class="simulation-heading">

                <div class="section-eyebrow">

                    <span class="eyebrow-icon">

                        ⚖️

                    </span>

                    <span>

                        NOVACOURT · SIMULACIÓN JUDICIAL

                    </span>

                </div>


                <h2>

                    Escenarios y Proyección Judicial

                </h2>


                <div class="title-accent"></div>


                <p>

                    Evaluación de los posibles escenarios del caso,
                    sus argumentos principales y la proyección estimada
                    del desarrollo judicial.

                </p>

            </div>


            <div
                v-if="status"
                class="simulation-status"
                :class="statusClass"
            >

                <span class="status-dot"></span>

                {{ status }}

            </div>

        </header>


        <!-- =====================================================
             LOADING
        ====================================================== -->

        <div
            v-if="loading"
            class="simulation-loading"
        >

            <div class="loading-spinner"></div>


            <div>

                <strong>

                    Simulando escenarios judiciales

                </strong>


                <span>

                    NovaCourt está evaluando posibles argumentos,
                    respuestas y resultados del escenario jurídico.

                </span>

            </div>

        </div>


        <!-- =====================================================
             CONTENIDO
        ====================================================== -->

        <template v-else-if="hasSimulation">


            <!-- =================================================
                 RESUMEN GENERAL
            ================================================== -->

            <section class="simulation-overview">

                <div class="overview-main">

                    <span class="overview-label">

                        Resultado proyectado

                    </span>


                    <strong class="overview-value">

                        {{ simulation.resultado || "En evaluación" }}

                    </strong>

                </div>


                <div class="overview-metrics">

                    <div class="overview-metric">

                        <span>

                            Probabilidad estimada

                        </span>


                        <strong>

                            {{ simulation.probabilidad || "--" }}

                        </strong>

                    </div>


                    <div class="overview-metric">

                        <span>

                            Nivel de riesgo

                        </span>


                        <strong>

                            {{ simulation.riesgo || "--" }}

                        </strong>

                    </div>

                </div>

            </section>


            <!-- =================================================
                 ESCENARIOS
            ================================================== -->

            <section
                v-if="scenarios.length"
                class="scenarios-section"
            >

                <div class="section-header">

                    <div>

                        <h3>

                            Escenarios Evaluados

                        </h3>


                        <div class="section-accent"></div>


                        <p>

                            Posibles desarrollos identificados
                            durante la simulación judicial.

                        </p>

                    </div>

                </div>


                <div class="scenarios-list">

                    <article
                        v-for="(
                            scenario,
                            index
                        ) in scenarios"
                        :key="scenario.id || index"
                        class="scenario-item"
                    >

                        <div class="scenario-number">

                            {{ index + 1 }}

                        </div>


                        <div class="scenario-content">

                            <div class="scenario-top">

                                <h4>

                                    {{
                                        scenario.titulo
                                        ||
                                        scenario.title
                                        ||
                                        `Escenario ${index + 1}`
                                    }}

                                </h4>


                                <span
                                    v-if="scenario.probabilidad"
                                    class="scenario-probability"
                                >

                                    {{
                                        scenario.probabilidad
                                    }}

                                </span>

                            </div>


                            <p>

                                {{
                                    scenario.descripcion
                                    ||
                                    scenario.description
                                    ||
                                    "No se proporcionó una descripción para este escenario."
                                }}

                            </p>


                            <div
                                v-if="scenario.resultado"
                                class="scenario-result"
                            >

                                <span>

                                    Resultado estimado

                                </span>


                                <strong>

                                    {{
                                        scenario.resultado
                                    }}

                                </strong>

                            </div>

                        </div>

                    </article>

                </div>

            </section>


            <!-- =================================================
                 ARGUMENTOS PRINCIPALES
            ================================================== -->

            <section
                v-if="argumentsList.length"
                class="arguments-section"
            >

                <div class="section-header">

                    <div>

                        <h3>

                            Factores y Argumentos Relevantes

                        </h3>


                        <div class="section-accent"></div>


                        <p>

                            Elementos identificados como determinantes
                            dentro de la proyección judicial.

                        </p>

                    </div>

                </div>


                <div class="arguments-list">

                    <article
                        v-for="(
                            argument,
                            index
                        ) in argumentsList"
                        :key="argument.id || index"
                        class="argument-item"
                    >

                        <div class="argument-icon">

                            ⚖️

                        </div>


                        <div>

                            <strong>

                                {{
                                    argument.titulo
                                    ||
                                    argument.title
                                    ||
                                    `Factor ${index + 1}`
                                }}

                            </strong>


                            <p>

                                {{
                                    argument.descripcion
                                    ||
                                    argument.description
                                    ||
                                    argument
                                }}

                            </p>

                        </div>

                    </article>

                </div>

            </section>


            <!-- =================================================
                 CONCLUSIÓN
            ================================================== -->

            <section
                v-if="simulation.conclusion"
                class="simulation-conclusion"
            >

                <div class="conclusion-header">

                    <div class="conclusion-number">

                        V

                    </div>


                    <div>

                        <h3>

                            Conclusión de la Simulación

                        </h3>


                        <div class="section-accent"></div>


                        <p>

                            Síntesis final de la proyección generada
                            por NovaCourt.

                        </p>

                    </div>

                </div>


                <div class="conclusion-content">

                    <MarkdownRenderer
                        :content="simulation.conclusion"
                    />

                </div>

            </section>

        </template>


        <!-- =====================================================
             EMPTY STATE
        ====================================================== -->

        <div
            v-else
            class="simulation-empty"
        >

            <div class="empty-symbol">

                ⚖

            </div>


            <h3>

                Simulación pendiente

            </h3>


            <div class="empty-accent"></div>


            <p>

                Cuando ejecutes el análisis del caso, NovaCourt
                mostrará aquí los escenarios judiciales, factores
                relevantes y posibles resultados.

            </p>

        </div>

    </section>

</template>


<script setup>

import {

    computed

} from "vue"

import MarkdownRenderer from "../common/MarkdownRenderer.vue"


/* =====================================================
   PROPS
===================================================== */

const props = defineProps({

    simulation: {

        type: Object,

        default: () => ({})

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


/* =====================================================
   ESTADO COMPUTADO
===================================================== */

const hasSimulation = computed(() => {

    return Object.keys(

        props.simulation

    ).length > 0

})


const scenarios = computed(() => {

    return props.simulation.escenarios

        ||

        props.simulation.scenarios

        ||

        []

})


const argumentsList = computed(() => {

    return props.simulation.argumentos

        ||

        props.simulation.arguments

        ||

        []

})


const statusClass = computed(() =>

    `status-${props.statusType}`

)

</script>


<style scoped>

/* =====================================================
   NOVACOURT SIMULATION
   ESTILO JURÍDICO · EDITORIAL · INSTITUCIONAL
   AZUL SOBRIO · JERARQUÍA · SIN EFECTO DASHBOARD
===================================================== */


/* =====================================================
   CONTENEDOR PRINCIPAL
===================================================== */

.court-simulation {

    width: 100%;

    box-sizing: border-box;

    padding: 42px 48px 48px;

    background: transparent;

    border: none;

    box-shadow: none;

}


/* =====================================================
   HEADER
===================================================== */

.simulation-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 32px;

    padding-bottom: 30px;

    border-bottom: 1px solid #D7DEE6;

}


.simulation-heading {

    min-width: 0;

}


/* =====================================================
   EYEBROW
===================================================== */

.section-eyebrow {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    margin-bottom: 18px;

    color: #315C97;

    font-size: .69rem;

    font-weight: 700;

    letter-spacing: 1.2px;

}


.eyebrow-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    color: #315C97;

    font-size: .9rem;

    line-height: 1;

}


/* =====================================================
   TÍTULO
===================================================== */

.simulation-heading h2 {

    margin: 0;

    color: #102238;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size: 2rem;

    font-weight: 500;

    line-height: 1.25;

    letter-spacing: -.3px;

}


/* =====================================================
   ACENTO EDITORIAL
===================================================== */

.title-accent {

    width: 44px;

    height: 2px;

    margin: 19px 0 17px;

    background: #315C97;

}


/* =====================================================
   DESCRIPCIÓN
===================================================== */

.simulation-heading p {

    max-width: 800px;

    margin: 0;

    color: #596575;

    font-size: .97rem;

    font-weight: 400;

    line-height: 1.85;

    letter-spacing: .01em;

}


/* =====================================================
   STATUS
===================================================== */

.simulation-status {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    flex-shrink: 0;

    margin-top: 4px;

    padding-bottom: 7px;

    border-bottom: 1px solid currentColor;

    font-size: .75rem;

    font-weight: 700;

    letter-spacing: .02em;

}


.status-dot {

    width: 7px;

    height: 7px;

    border-radius: 50%;

}


/* Procesando */

.status-processing {

    color: #315C97;

}


.status-processing .status-dot {

    background: #315C97;

    animation: pulse 1.5s infinite;

}


/* Completado */

.status-completed {

    color: #2E6B52;

}


.status-completed .status-dot {

    background: #2E6B52;

}


/* Error */

.status-error {

    color: #9B3D3D;

}


.status-error .status-dot {

    background: #B94A48;

}


/* =====================================================
   LOADING
===================================================== */

.simulation-loading {

    display: flex;

    align-items: center;

    gap: 20px;

    min-height: 180px;

    padding: 34px 0;

    border-bottom: 1px solid #D7DEE6;

}


.loading-spinner {

    width: 30px;

    height: 30px;

    flex-shrink: 0;

    border: 2px solid #D7DEE6;

    border-top-color: #315C97;

    border-radius: 50%;

    animation: spin .9s linear infinite;

}


.simulation-loading strong {

    display: block;

    margin-bottom: 7px;

    color: #102238;

    font-size: .98rem;

    font-weight: 700;

}


.simulation-loading span {

    display: block;

    max-width: 600px;

    color: #647080;

    font-size: .91rem;

    line-height: 1.7;

}


/* =====================================================
   RESUMEN GENERAL
===================================================== */

.simulation-overview {

    display: grid;

    grid-template-columns:

        minmax(0, 1.5fr)
        minmax(260px, .8fr);

    gap: 42px;

    margin-top: 36px;

    padding-bottom: 36px;

    border-bottom: 1px solid #D7DEE6;

}


/* Resultado principal */

.overview-main {

    position: relative;

    padding-left: 22px;

}


.overview-main::before {

    content: "";

    position: absolute;

    top: 3px;

    left: 0;

    bottom: 3px;

    width: 2px;

    background: #315C97;

}


.overview-label {

    display: block;

    margin-bottom: 11px;

    color: #6B7888;

    font-size: .71rem;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 1.1px;

}


.overview-value {

    display: block;

    color: #102238;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.55rem;

    font-weight: 500;

    line-height: 1.5;

}


/* Métricas */

.overview-metrics {

    display: grid;

    grid-template-columns: 1fr 1fr;

    border-left: 1px solid #D7DEE6;

}


.overview-metric {

    padding: 0 22px;

}


.overview-metric + .overview-metric {

    border-left: 1px solid #D7DEE6;

}


.overview-metric span {

    display: block;

    margin-bottom: 9px;

    color: #7A8594;

    font-size: .71rem;

    font-weight: 600;

    line-height: 1.5;

}


.overview-metric strong {

    color: #17375E;

    font-size: 1.08rem;

    font-weight: 700;

}


/* =====================================================
   SECCIONES
===================================================== */

.scenarios-section,

.arguments-section,

.simulation-conclusion {

    margin-top: 40px;

}


.section-header {

    margin-bottom: 24px;

}


.section-header h3,

.conclusion-header h3 {

    margin: 0;

    color: #102238;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.45rem;

    font-weight: 500;

    line-height: 1.35;

}


.section-accent {

    width: 34px;

    height: 2px;

    margin: 14px 0;

    background: #315C97;

}


.section-header p,

.conclusion-header p {

    margin: 0;

    color: #647080;

    font-size: .92rem;

    line-height: 1.75;

}


/* =====================================================
   ESCENARIOS
   LISTADO EDITORIAL, NO CARDS
===================================================== */

.scenarios-list {

    border-top: 1px solid #D7DEE6;

}


.scenario-item {

    display: grid;

    grid-template-columns: 58px minmax(0, 1fr);

    gap: 20px;

    padding: 28px 0;

    border-bottom: 1px solid #D7DEE6;

}


.scenario-number {

    width: 38px;

    height: 38px;

    display: flex;

    align-items: center;

    justify-content: center;

    color: #315C97;

    border: 1px solid #AEBFD0;

    font-size: .82rem;

    font-weight: 700;

}


.scenario-content {

    min-width: 0;

}


.scenario-top {

    display: flex;

    align-items: baseline;

    justify-content: space-between;

    gap: 20px;

}


.scenario-top h4 {

    margin: 0;

    color: #102238;

    font-size: 1.03rem;

    font-weight: 700;

    line-height: 1.5;

}


.scenario-probability {

    flex-shrink: 0;

    color: #315C97;

    font-size: .76rem;

    font-weight: 700;

    white-space: nowrap;

}


.scenario-content > p {

    max-width: 850px;

    margin: 11px 0 0;

    color: #596575;

    font-size: .92rem;

    line-height: 1.8;

}


.scenario-result {

    display: flex;

    align-items: baseline;

    gap: 12px;

    margin-top: 16px;

}


.scenario-result span {

    color: #7A8594;

    font-size: .69rem;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: .8px;

}


.scenario-result strong {

    color: #17375E;

    font-size: .9rem;

}


/* =====================================================
   ARGUMENTOS
   LISTADO JURÍDICO
===================================================== */

.arguments-list {

    border-top: 1px solid #D7DEE6;

}


.argument-item {

    display: grid;

    grid-template-columns: 42px minmax(0, 1fr);

    gap: 17px;

    padding: 22px 0;

    border-bottom: 1px solid #D7DEE6;

}


.argument-icon {

    width: 30px;

    height: 30px;

    display: flex;

    align-items: center;

    justify-content: center;

    color: #315C97;

    font-size: 1rem;

}


.argument-item strong {

    display: block;

    margin-bottom: 7px;

    color: #102238;

    font-size: .96rem;

    font-weight: 700;

}


.argument-item p {

    max-width: 850px;

    margin: 0;

    color: #647080;

    font-size: .9rem;

    line-height: 1.75;

}


/* =====================================================
   CONCLUSIÓN
===================================================== */

.simulation-conclusion {

    padding-top: 4px;

}


.conclusion-header {

    display: grid;

    grid-template-columns: 54px minmax(0, 1fr);

    gap: 18px;

    padding-bottom: 26px;

    border-bottom: 1px solid #D7DEE6;

}


.conclusion-number {

    width: 40px;

    height: 40px;

    display: flex;

    align-items: center;

    justify-content: center;

    color: #315C97;

    border: 1px solid #AEBFD0;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size: .95rem;

}


.conclusion-content {

    padding-top: 26px;

}


.simulation-conclusion :deep(.markdown-container) {

    padding: 0;

}


/* =====================================================
   EMPTY STATE
===================================================== */

.simulation-empty {

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    min-height: 320px;

    padding: 50px 30px;

    text-align: center;

    border-top: 1px solid #D7DEE6;

    border-bottom: 1px solid #D7DEE6;

}


.empty-symbol {

    margin-bottom: 20px;

    color: #315C97;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size: 2.1rem;

    line-height: 1;

}


.simulation-empty h3 {

    margin: 0;

    color: #102238;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.45rem;

    font-weight: 500;

}


.empty-accent {

    width: 34px;

    height: 2px;

    margin: 16px 0;

    background: #315C97;

}


.simulation-empty p {

    max-width: 540px;

    margin: 0;

    color: #647080;

    font-size: .93rem;

    line-height: 1.8;

}


/* =====================================================
   ANIMACIONES
===================================================== */

@keyframes spin {

    to {

        transform: rotate(360deg);

    }

}


@keyframes pulse {

    0% {

        transform: scale(1);

        opacity: 1;

    }

    50% {

        transform: scale(1.25);

        opacity: .55;

    }

    100% {

        transform: scale(1);

        opacity: 1;

    }

}


/* =====================================================
   RESPONSIVE
===================================================== */

@media (max-width: 900px) {

    .court-simulation {

        padding: 36px 28px 40px;

    }


    .simulation-header {

        flex-direction: column;

        gap: 18px;

    }


    .simulation-overview {

        grid-template-columns: 1fr;

        gap: 30px;

    }


    .overview-metrics {

        border-top: 1px solid #D7DEE6;

        border-left: none;

        padding-top: 24px;

    }


    .overview-metric:first-child {

        padding-left: 0;

    }

}


@media (max-width: 600px) {

    .court-simulation {

        padding: 30px 20px 34px;

    }


    .simulation-heading h2 {

        font-size: 1.6rem;

    }


    .simulation-heading p {

        font-size: .91rem;

        line-height: 1.75;

    }


    .simulation-overview {

        margin-top: 30px;

    }


    .overview-value {

        font-size: 1.3rem;

    }


    .overview-metrics {

        grid-template-columns: 1fr;

        gap: 20px;

    }


    .overview-metric {

        padding: 0;

    }


    .overview-metric + .overview-metric {

        padding-top: 20px;

        border-top: 1px solid #D7DEE6;

        border-left: none;

    }


    .scenario-item {

        grid-template-columns: 42px minmax(0, 1fr);

        gap: 14px;

        padding: 24px 0;

    }


    .scenario-top {

        flex-direction: column;

        gap: 7px;

    }


    .section-header h3,

    .conclusion-header h3 {

        font-size: 1.28rem;

    }


    .simulation-loading {

        align-items: flex-start;

        min-height: 150px;

        padding: 28px 0;

    }


    .simulation-empty {

        min-height: 260px;

        padding: 40px 20px;

    }

}

</style>