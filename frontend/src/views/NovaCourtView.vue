<template>

    <main class="novacourt-view">

        <!-- =========================================
             CABECERA PRINCIPAL
        ========================================== -->

        <NovaCourtHeader />


        <!-- =========================================
             ENTRADA DEL CASO
        ========================================== -->

        <section class="novacourt-section novacourt-section-input">

            <NovaCourtInput
                v-model="caseText"
                :loading="loading"
                @simulate="handleSimulation"
            />

        </section>


        <!-- =========================================
             ESTADO GENERAL DEL PROCESO
        ========================================== -->

        <section
            v-if="loading || error"
            class="novacourt-feedback"
            aria-live="polite"
        >

            <!-- PROCESAMIENTO -->

            <div
                v-if="loading"
                class="feedback-card feedback-processing"
            >

                <div class="feedback-indicator">

                    <span class="feedback-dot"></span>

                </div>


                <div class="feedback-content">

                    <span class="feedback-label">

                        PROCESAMIENTO JUDICIAL

                    </span>


                    <strong>

                        NovaCourt está analizando el caso

                    </strong>


                    <p>

                        El sistema está organizando los hechos,
                        identificando los elementos jurídicos relevantes
                        y estructurando la evaluación del escenario.

                    </p>

                </div>

            </div>


            <!-- ERROR -->

            <div
                v-if="error"
                class="feedback-card feedback-error"
            >

                <div class="feedback-error-icon">

                    !

                </div>


                <div class="feedback-content">

                    <span class="feedback-label">

                        ERROR DE PROCESAMIENTO

                    </span>


                    <strong>

                        No fue posible completar el análisis

                    </strong>


                    <p>

                        {{ error }}

                    </p>

                </div>

            </div>

        </section>


        <!-- =========================================
             RESULTADOS
        ========================================== -->

        <section
            v-if="hasResult"
            class="novacourt-results"
        >

            <NovaCourtTabs
                :default-tab="activeTab"
                @change="activeTab = $event"
            >

                <!-- =====================================
                     RESUMEN
                ====================================== -->

                <template #overview>

                    <CourtSummary
                        :content="summaryContent"
                        :loading="loading"
                    />

                </template>


                <!-- =====================================
                     ANÁLISIS
                ====================================== -->

                <template #arguments>

                    <CourtAnalysis
                        :content="analysisContent"
                        :loading="loading"
                        :status="analysisStatus"
                        :status-type="analysisStatusType"
                    />

                </template>


                <!-- =====================================
                     EVIDENCIA
                ====================================== -->

                <template #evidence>

                    <CourtAnalysis
                        :content="evidenceContent"
                        :loading="loading"
                        :status="evidenceStatus"
                        :status-type="evidenceStatusType"
                    />

                </template>


                <!-- =====================================
                     RIESGOS
                ====================================== -->

                <template #risks>

                    <CourtAnalysis
                        :content="riskContent"
                        :loading="loading"
                        :status="riskStatus"
                        :status-type="riskStatusType"
                    />

                </template>


                <!-- =====================================
                     SIMULACIÓN / ESTRATEGIA
                ====================================== -->

                <template #strategy>

                    <CourtSimulation
                        :simulation="simulationData"
                        :loading="loading"
                        :status="simulationStatus"
                        :status-type="simulationStatusType"
                    />

                </template>


                <!-- =====================================
                     PROYECCIÓN / INFORME
                ====================================== -->

                <template #prediction>

                    <CourtReport
                        :content="reportContent"
                        :loading="loading"
                        :status="reportStatus"
                        :status-type="reportStatusType"
                    />

                </template>


                <!-- =====================================
                     GRAFO JURÍDICO
                ====================================== -->

                <template #graph>

                    <GraphPanel
                        :data="graphData"
                        :loading="loading"
                    />

                </template>

            </NovaCourtTabs>

        </section>


        <!-- =========================================
             ESTADO INICIAL
        ========================================== -->

        <section
            v-else-if="!loading && !error"
            class="novacourt-initial-state"
        >

            <div class="initial-state-line"></div>


            <div class="initial-state-content">

                <span class="initial-state-eyebrow">

                    SISTEMA DE ANÁLISIS JUDICIAL

                </span>


                <h2>

                    Preparado para evaluar un nuevo caso

                </h2>


                <p>

                    Describe los hechos relevantes, las partes
                    involucradas, las pretensiones y los argumentos
                    principales. NovaCourt organizará la información
                    para desarrollar una evaluación estructurada del
                    escenario judicial.

                </p>

            </div>


            <div
                class="initial-state-seal"
                aria-hidden="true"
            >

                <span>

                    NC

                </span>

            </div>

        </section>

    </main>

</template>


<script setup>

import {
    computed,
    ref
} from "vue"

import {
    useNovaCourt
} from "../composables/useNovaCourt"

import NovaCourtHeader
    from "../components/novacourt/NovaCourtHeader.vue"

import NovaCourtInput
    from "../components/novacourt/NovaCourtInput.vue"

import NovaCourtTabs
    from "../components/novacourt/NovaCourtTabs.vue"

import CourtSummary
    from "../components/novacourt/CourtSummary.vue"

import CourtAnalysis
    from "../components/novacourt/CourtAnalysis.vue"

import CourtSimulation
    from "../components/novacourt/CourtSimulation.vue"

import CourtReport
    from "../components/novacourt/CourtReport.vue"

import GraphPanel
    from "../components/novacourt/GraphPanel.vue"


/* =========================================
   NOVACOURT COMPOSABLE
========================================= */

const {
    loading,
    error,
    result,
    analyzeCase
} = useNovaCourt()


/* =========================================
   ESTADO LOCAL
========================================= */

const caseText = ref("")

const activeTab = ref(
    "overview"
)


/* =========================================
   EJECUTAR SIMULACIÓN
========================================= */

async function handleSimulation(){

    const normalizedText =
        caseText.value.trim()


    if(
        !normalizedText ||
        loading.value
    ){
        return
    }


    activeTab.value =
        "overview"


    await analyzeCase(
        normalizedText
    )

}


/* =========================================
   RESULTADO DISPONIBLE
========================================= */

const hasResult = computed(() => {

    return Boolean(
        result.value
    )

})


/* =========================================
   RESUMEN
========================================= */

const summaryContent = computed(() => {

    return (
        result.value?.summary ||
        result.value?.overview ||
        ""
    )

})


/* =========================================
   ANÁLISIS JURÍDICO
========================================= */

const analysisContent = computed(() => {

    return (
        result.value?.analysis ||
        result.value?.arguments ||
        ""
    )

})


/* =========================================
   EVIDENCIA
========================================= */

const evidenceContent = computed(() => {

    return (
        result.value?.evidence ||
        result.value?.probative_analysis ||
        ""
    )

})


/* =========================================
   RIESGOS
========================================= */

const riskContent = computed(() => {

    return (
        result.value?.risks ||
        result.value?.risk_analysis ||
        ""
    )

})


/* =========================================
   SIMULACIÓN
========================================= */

/*
   CourtSimulation recibe un OBJETO.

   Se evita enviar strategyContent como String,
   porque el componente trabaja con propiedades como:

   - resultado
   - probabilidad
   - riesgo
   - escenarios
   - argumentos
   - conclusion
*/

const simulationData = computed(() => {

    const simulation =
        result.value?.simulation ||
        result.value?.strategy ||
        result.value?.court_simulation ||
        {}


    if(
        simulation &&
        typeof simulation === "object" &&
        !Array.isArray(simulation)
    ){
        return simulation
    }


    return {}

})


/* =========================================
   INFORME / PROYECCIÓN
========================================= */

const reportContent = computed(() => {

    return (
        result.value?.report ||
        result.value?.final_report ||
        result.value?.conclusion ||
        ""
    )

})


/* =========================================
   GRAFO JURÍDICO
========================================= */

const graphData = computed(() => {

    return (
        result.value?.graph ||
        result.value?.graph_data ||
        null
    )

})


/* =========================================
   ESTADOS DE ANÁLISIS
========================================= */

const analysisStatus = computed(() => {

    if(loading.value){
        return "Procesando análisis"
    }


    if(analysisContent.value){
        return "Análisis disponible"
    }


    return ""

})


const analysisStatusType = computed(() => {

    if(loading.value){
        return "processing"
    }


    if(analysisContent.value){
        return "completed"
    }


    return "processing"

})


/* =========================================
   ESTADOS DE EVIDENCIA
========================================= */

const evidenceStatus = computed(() => {

    if(loading.value){
        return "Evaluando elementos probatorios"
    }


    if(evidenceContent.value){
        return "Evaluación disponible"
    }


    return ""

})


const evidenceStatusType = computed(() => {

    if(loading.value){
        return "processing"
    }


    if(evidenceContent.value){
        return "completed"
    }


    return "processing"

})


/* =========================================
   ESTADOS DE RIESGO
========================================= */

const riskStatus = computed(() => {

    if(loading.value){
        return "Evaluando riesgos jurídicos"
    }


    if(riskContent.value){
        return "Evaluación disponible"
    }


    return ""

})


const riskStatusType = computed(() => {

    if(loading.value){
        return "processing"
    }


    if(riskContent.value){
        return "completed"
    }


    return "processing"

})


/* =========================================
   ESTADOS DE SIMULACIÓN
========================================= */

const simulationStatus = computed(() => {

    if(loading.value){
        return "Simulando escenarios"
    }


    if(
        Object.keys(
            simulationData.value
        ).length
    ){
        return "Simulación disponible"
    }


    return ""

})


const simulationStatusType = computed(() => {

    if(loading.value){
        return "processing"
    }


    if(
        Object.keys(
            simulationData.value
        ).length
    ){
        return "completed"
    }


    return "processing"

})


/* =========================================
   ESTADOS DEL INFORME
========================================= */

const reportStatus = computed(() => {

    if(loading.value){
        return "Generando proyección"
    }


    if(reportContent.value){
        return "Informe disponible"
    }


    return ""

})


const reportStatusType = computed(() => {

    if(loading.value){
        return "processing"
    }


    if(reportContent.value){
        return "completed"
    }


    return "processing"

})

</script>


<style scoped>

/* =========================================
   NOVACOURT VIEW
   CONTENEDOR PRINCIPAL
========================================= */

.novacourt-view{

    width:100%;
    max-width:1440px;

    margin:0 auto;

    padding:
        32px
        28px
        56px;

    color:#17375E;

}


/* =========================================
   SECCIONES
========================================= */

.novacourt-section{

    width:100%;

}


.novacourt-section-input{

    margin-top:24px;

}


/* =========================================
   RESULTADOS
========================================= */

.novacourt-results{

    width:100%;

    margin-top:28px;

    animation:
        sectionAppear
        .4s
        ease;

}


/* =========================================
   FEEDBACK
========================================= */

.novacourt-feedback{

    width:100%;

    margin-top:20px;

}


.feedback-card{

    display:flex;

    align-items:flex-start;

    gap:16px;

    padding:20px 22px;

    border-radius:10px;

}


.feedback-processing{

    background:
        linear-gradient(
            135deg,
            #F8FAFC 0%,
            #F3F6FA 100%
        );

    border:
        1px solid
        #D6DFEA;

}


.feedback-error{

    background:
        linear-gradient(
            135deg,
            #FFF9F8 0%,
            #FCF4F3 100%
        );

    border:
        1px solid
        #E8C9C4;

}


/* =========================================
   INDICADOR DE PROCESAMIENTO
========================================= */

.feedback-indicator{

    width:40px;
    height:40px;

    display:flex;

    align-items:center;
    justify-content:center;

    flex-shrink:0;

    background:#FFFFFF;

    border:
        1px solid
        #D6DFEA;

    border-radius:6px;

}


.feedback-dot{

    width:8px;
    height:8px;

    border-radius:50%;

    background:#315C97;

    animation:
        statusPulse
        1.5s
        ease-in-out
        infinite;

}


/* =========================================
   INDICADOR DE ERROR
========================================= */

.feedback-error-icon{

    width:40px;
    height:40px;

    display:flex;

    align-items:center;
    justify-content:center;

    flex-shrink:0;

    color:#9A3D32;

    background:#FFFFFF;

    border:
        1px solid
        #E8C9C4;

    border-radius:6px;

    font-size:1rem;
    font-weight:700;

}


/* =========================================
   CONTENIDO FEEDBACK
========================================= */

.feedback-content{

    display:flex;

    flex-direction:column;

    gap:5px;

}


.feedback-label{

    color:#315C97;

    font-size:.66rem;
    font-weight:800;

    letter-spacing:1.2px;

}


.feedback-error
.feedback-label{

    color:#9A3D32;

}


.feedback-content strong{

    color:#102238;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:1rem;
    font-weight:600;

    line-height:1.4;

}


.feedback-content p{

    max-width:820px;

    margin:0;

    color:#5E6D7E;

    font-size:.9rem;

    line-height:1.7;

}


/* =========================================
   ESTADO INICIAL
========================================= */

.novacourt-initial-state{

    position:relative;

    display:flex;

    align-items:center;

    gap:28px;

    width:100%;

    min-height:196px;

    margin-top:28px;

    padding:
        32px
        38px;

    overflow:hidden;

    background:
        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FBFCFE 58%,
            #F6F8FB 100%
        );

    border:
        1px solid
        #D6DFEA;

    border-radius:10px;

    box-shadow:
        0 14px 34px
        rgba(
            15,
            27,
            45,
            .045
        );

}


/* =========================================
   DETALLE DECORATIVO
========================================= */

.novacourt-initial-state::before{

    content:"";

    position:absolute;

    top:0;
    left:0;

    width:100%;
    height:2px;

    background:
        linear-gradient(
            90deg,
            #17375E 0%,
            #315C97 42%,
            rgba(
                49,
                92,
                151,
                .22
            ) 72%,
            transparent 100%
        );

}


.novacourt-initial-state::after{

    content:"";

    position:absolute;

    width:260px;
    height:260px;

    right:-145px;
    bottom:-185px;

    border:
        1px solid
        rgba(
            49,
            92,
            151,
            .08
        );

    border-radius:50%;

    pointer-events:none;

}


/* =========================================
   LÍNEA INSTITUCIONAL
========================================= */

.initial-state-line{

    position:relative;

    z-index:2;

    width:3px;

    align-self:stretch;

    min-height:118px;

    flex-shrink:0;

    background:
        linear-gradient(
            180deg,
            #B08A4C 0%,
            #D0AA63 100%
        );

    border-radius:2px;

}


/* =========================================
   CONTENIDO
========================================= */

.initial-state-content{

    position:relative;

    z-index:2;

    flex:1;

    min-width:0;

}


.initial-state-eyebrow{

    display:block;

    margin-bottom:10px;

    color:#7A6440;

    font-size:.67rem;
    font-weight:800;

    letter-spacing:1.45px;

}


.initial-state-content h2{

    margin:0 0 10px;

    color:#17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:1.55rem;
    font-weight:600;

    line-height:1.3;

}


.initial-state-content p{

    max-width:850px;

    margin:0;

    color:#5E6D7E;

    font-size:.95rem;

    line-height:1.8;

}


/* =========================================
   SELLO NOVACOURT
========================================= */

.initial-state-seal{

    position:relative;

    z-index:2;

    width:82px;
    height:82px;

    display:flex;

    align-items:center;
    justify-content:center;

    flex-shrink:0;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .55
        );

    border-radius:50%;

}


.initial-state-seal::before{

    content:"";

    position:absolute;

    inset:7px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .32
        );

    border-radius:50%;

}


.initial-state-seal span{

    position:relative;

    z-index:2;

    color:#7A6440;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:1rem;
    font-weight:600;

    letter-spacing:2px;

}


/* =========================================
   ANIMACIONES
========================================= */

@keyframes sectionAppear{

    from{

        opacity:0;

        transform:
            translateY(10px);

    }


    to{

        opacity:1;

        transform:
            translateY(0);

    }

}


@keyframes statusPulse{

    0%,
    100%{

        transform:
            scale(1);

        opacity:1;

    }


    50%{

        transform:
            scale(1.4);

        opacity:.5;

    }

}


/* =========================================
   RESPONSIVE - TABLET
========================================= */

@media(max-width:900px){

    .novacourt-view{

        padding:
            24px
            20px
            44px;

    }


    .novacourt-initial-state{

        padding:
            28px
            30px;

    }

}


/* =========================================
   RESPONSIVE - MOBILE GRANDE
========================================= */

@media(max-width:700px){

    .novacourt-initial-state{

        align-items:flex-start;

        gap:20px;

        min-height:auto;

    }


    .initial-state-line{

        min-height:128px;

    }


    .initial-state-seal{

        width:64px;
        height:64px;

    }


    .initial-state-content h2{

        font-size:1.3rem;

    }

}


/* =========================================
   RESPONSIVE - MOBILE
========================================= */

@media(max-width:576px){

    .novacourt-view{

        padding:
            16px
            14px
            36px;

    }


    .novacourt-section-input{

        margin-top:16px;

    }


    .novacourt-feedback{

        margin-top:16px;

    }


    .novacourt-results{

        margin-top:20px;

    }


    .feedback-card{

        gap:13px;

        padding:17px;

        border-radius:8px;

    }


    .feedback-indicator,
    .feedback-error-icon{

        width:36px;
        height:36px;

    }


    .feedback-content strong{

        font-size:.95rem;

    }


    .feedback-content p{

        font-size:.86rem;

    }


    .novacourt-initial-state{

        flex-direction:column;

        gap:18px;

        margin-top:20px;

        padding:
            26px
            22px;

        border-radius:8px;

    }


    .initial-state-line{

        width:42px;
        height:3px;

        min-height:3px;

        align-self:auto;

    }


    .initial-state-seal{

        display:none;

    }


    .initial-state-content h2{

        font-size:1.2rem;

    }


    .initial-state-content p{

        font-size:.88rem;

        line-height:1.7;

    }

}

</style>