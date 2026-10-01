<template>

    <main class="novacourt-view">

        <!-- =====================================================
             CABECERA
        ====================================================== -->

        <NovaCourtHeader />
        <PipelineProgress v-if="isLoading" :progress="novaCourt.progress.value" :current="novaCourt.currentStage.value" :stages="novaCourt.stages.value" />
        <button v-if="isLoading" type="button" @click="novaCourt.cancel">Cancelar tarea</button>
        <p v-for="warning in novaCourt.warnings.value" :key="warning.stage" role="status">{{ warning.message }}</p>


        <!-- =====================================================
             ENTRADA DEL CASO
        ====================================================== -->

        <section class="novacourt-section novacourt-section-input">

            <NovaCourtInput
                v-model="caseText"
                :loading="isLoading"
                :has-documents="selectedDocumentIds.length > 0"
                @simulate="handleSimulation"
            />
            <p v-if="continuingCase && (reuseTaskId || result?.metadata?.case_reused)" role="status">Continuando el análisis existente del caso {{ activeCaseId }}.</p>
            <p v-else-if="continuingCase" role="status">Caso {{ activeCaseId }} seleccionado. El análisis se actualizará con el texto y documentos elegidos.</p>
            <p v-else role="status">Caso independiente nuevo. No se reutilizan documentos de otras sesiones.</p>
            <CaseDocumentUpload :key="activeCaseId" :case-id="activeCaseId" :initial-document-ids="requestedDocumentIds" :load-existing="continuingCase" :disabled="isLoading" @update:document-ids="selectedDocumentIds = $event" />
            <button v-if="continuingCase || result" type="button" @click="startIndependentCase">Nueva simulación independiente</button>

        </section>


        <!-- =====================================================
             ESTADO DEL PROCESAMIENTO
        ====================================================== -->

        <section
            v-if="isLoading || errorMessage"
            class="novacourt-feedback"
            aria-live="polite"
        >

            <!-- PROCESANDO -->

            <div
                v-if="isLoading"
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
                        y estructurando los posibles escenarios judiciales.
                    </p>

                </div>

            </div>


            <!-- ERROR -->

            <div
                v-if="errorMessage"
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
                        {{ errorMessage }}
                    </p>

                </div>

            </div>

        </section>


        <!-- =====================================================
             RESULTADOS
        ====================================================== -->

        <section
            v-if="hasResult"
            class="novacourt-results"
        >

            <NovaCourtTabs
                :default-tab="activeTab"
                @change="handleTabChange"
            >

                <!-- =================================================
                     RESUMEN
                ================================================== -->

                <template #overview>

                    <CourtSummary
                        :summary="summaryContent"
                        :court-status="result?.court_status"
                        :graph-status="graphData.status"
                        :simulation-status="simulationData.status"
                        :issue-count="result?.issues?.length || 0"
                        :loading="isLoading && !hasResult"
                    />

                </template>


                <!-- =================================================
                     ANÁLISIS
                ================================================== -->

                <template #arguments>

                    <CourtAnalysis
                        :content="analysisContent"
                        :loading="isLoading && !hasResult"
                        :status="analysisStatus"
                        :status-type="analysisStatusType"
                    />

                </template>


                <!-- =================================================
                     EVIDENCIA
                ================================================== -->

                <template #evidence>

                    <CourtAnalysis
                        :content="evidenceContent"
                        :loading="isLoading && !hasResult"
                        :status="evidenceStatus"
                        :status-type="evidenceStatusType"
                    />

                </template>


                <!-- =================================================
                     RIESGOS
                ================================================== -->

                <template #risks>

                    <CourtAnalysis
                        :content="riskContent"
                        :loading="isLoading && !hasResult"
                        :status="riskStatus"
                        :status-type="riskStatusType"
                    />

                </template>


                <!-- =================================================
                     SIMULACIÓN MULTIAGENTE
                ================================================== -->

                <template #strategy>

                    <CourtSimulation
                        :simulation="simulationData"
                        :case-id="result?.case_id"
                        mode="positions"
                        :loading="isLoading && !hasResult"
                        :status="simulationStatus"
                        :status-type="simulationStatusType"
                    />

                </template>

                <template #decision>
                    <CourtSimulation :simulation="simulationData" :case-id="result?.case_id" mode="decision" />
                </template>


                <!-- =================================================
                     INFORME FINAL
                ================================================== -->

                <template #report>

                    <CourtReport
                        :content="reportContent"
                        :citations="simulationData.citations"
                        :sources="simulationData.sources"
                        :case-id="result?.case_id"
                        :loading="isLoading && !hasResult"
                        :status="reportStatus"
                        :status-type="reportStatusType"
                    />

                </template>


                <!-- =================================================
                     GRAFO JURÍDICO
                ================================================== -->

                <template #graph>

                    <GraphPanel
                        :graph-data="graphData"
                        :loading="isLoading && !hasResult"
                        :sources="[...(result?.sources || []), ...(result?.sources_used || []), ...(result?.research?.sources || [])]"
                        :case-id="result?.case_id"
                    />

                </template>

            </NovaCourtTabs>

        </section>


        <!-- =====================================================
             ESTADO INICIAL
        ====================================================== -->

        <section
            v-else-if="!isLoading && !errorMessage"
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
                    para desarrollar una evaluación estructurada
                    del escenario judicial.
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
import { useRoute, useRouter } from "vue-router"
import CaseDocumentUpload from "@/components/common/CaseDocumentUpload.vue"
import CourtSimulation from '../components/novacourt/CourtSimulation.vue'
import PipelineProgress from '../components/novacourt/PipelineProgress.vue'
import { normalizeRenderableContent } from '../utils/content.js'
import { normalizeGraphState } from '../utils/graphState.js'
import { normalizeSimulationState } from '../utils/simulationState.js'


import {
    computed,
    ref,
    watch
} from "vue"


/* =========================================================
   COMPOSABLE
========================================================= */

import {
    useNovaCourt
} from "../composables/useNovaCourt"


/* =========================================================
   COMPONENTES
========================================================= */

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

import CourtReport
    from "../components/novacourt/CourtReport.vue"

import GraphPanel
    from "../components/novacourt/GraphPanel.vue"


/* =========================================================
   NOVACOURT
========================================================= */

const novaCourt = useNovaCourt()
const route = useRoute()
const router = useRouter()
const requestedCaseId = typeof route.query.case_id === "string" && /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(route.query.case_id) && !route.query.case_id.includes("..") ? route.query.case_id : null
const reuseTaskId = ref(requestedCaseId && typeof globalThis.history?.state?.reuseTaskId === 'string'
    ? globalThis.history.state.reuseTaskId : null)
const continuingCase = ref(Boolean(requestedCaseId))
const activeCaseId = ref(requestedCaseId || crypto.randomUUID())
const requestedDocumentIds = requestedCaseId && typeof route.query.document_ids === "string"
    ? [...new Set(route.query.document_ids.split(",").filter(id => id.length > 0 && id.length <= 128))].slice(0, 20)
    : []
const originalCaseText = requestedCaseId && globalThis.history?.state?.caseText
    ? String(globalThis.history.state.caseText) : ''
const selectedDocumentIds = ref([])
if (requestedCaseId && globalThis.history?.state?.caseText) novaCourt.caseText.value = String(globalThis.history.state.caseText)


/*
    Utilizamos directamente las referencias
    proporcionadas por el composable.
*/

const caseText =
    novaCourt.caseText

const isLoading =
    novaCourt.isAnalyzing

const error =
    novaCourt.error

const result =
    novaCourt.result

const analyzeCase =
    novaCourt.analyzeCase


/* =========================================================
   ESTADO LOCAL DE LA VISTA
========================================================= */

const activeTab =
    ref("overview")


/* =========================================================
   MENSAJE DE ERROR
========================================================= */

const errorMessage = computed(() => {

    const value =
        error.value

    if (!value) {
        return ""
    }

    if (typeof value === "string") {
        return value
    }

    if (value?.message) {
        return value.message
    }

    return "Se produjo un error durante el procesamiento del caso."

})


/* =========================================================
   EJECUTAR SIMULACIÓN
========================================================= */

async function handleSimulation(text) {

    /*
        El NovaCourtInput emite el texto
        directamente mediante @simulate.
    */

    const normalizedText =
        String(text ?? "").trim()


    /*
        Validación básica.
    */

    if (!normalizedText && selectedDocumentIds.value.length === 0) {

        error.value =
            "Ingresa la descripción del caso antes de iniciar el análisis."

        return
    }


    /*
        Evitar doble ejecución.
    */

    if (isLoading.value) {
        return
    }


    /*
        Mantener sincronizado el texto
        con el composable.
    */

    const effectiveText = normalizedText || "Analiza los documentos jurídicos aportados para este caso."
    caseText.value = effectiveText


    /*
        Reiniciar pestaña.
    */

    activeTab.value =
        "overview"


    /*
        Ejecutar análisis.
    */

    try {

        const sameDocuments = selectedDocumentIds.value.length === requestedDocumentIds.length &&
            selectedDocumentIds.value.every(id => requestedDocumentIds.includes(id))
        await analyzeCase(effectiveText, { caseId:activeCaseId.value, documentIds:selectedDocumentIds.value,
            reuseTaskId: effectiveText === originalCaseText && sameDocuments ? reuseTaskId.value : null })
        reuseTaskId.value = null

    }
    catch (err) {

        console.error(
            "[NovaCourt] Error durante el análisis:",
            err
        )

        /*
            El composable normalmente
            ya gestiona este error.
            Este bloque funciona como
            protección adicional.
        */

        if (!error.value) {

            error.value =
                err?.message ||
                "No fue posible completar el análisis judicial."

        }

    }

}


/* =========================================================
   CAMBIO DE PESTAÑA
========================================================= */

function startIndependentCase() {
    novaCourt.resetAnalysis()
    selectedDocumentIds.value = []
    activeCaseId.value = crypto.randomUUID()
    continuingCase.value = false
    reuseTaskId.value = null
    router.replace({ path:"/novacourt" })
}

function handleTabChange(tab) {

    if (!tab) {
        return
    }

    activeTab.value =
        tab

}


/* =========================================================
   RESULTADO DISPONIBLE
========================================================= */

const hasResult = computed(() => {

    return Boolean(
        result.value
    )

})


/* =========================================================
   RESUMEN
========================================================= */

const summaryContent = computed(() => {

    const data =
        result.value || {}

    return (
        data.summary ||
        data.overview ||
        data.case_summary ||
        ""
    )

})


/* =========================================================
   ANÁLISIS JURÍDICO
========================================================= */

const analysisContent = computed(() => {

    const data =
        result.value || {}

    return normalizeRenderableContent(
        data.analysis ||
        data.arguments ||
        data.legal_analysis ||
        ""
    )

})


/* =========================================================
   EVIDENCIA
========================================================= */

const evidenceContent = computed(() => {

    const data =
        result.value || {}

    return normalizeRenderableContent(
        data.evidence ||
        data.probative_analysis ||
        data.evidence_analysis ||
        ""
    )

})


/* =========================================================
   RIESGOS
========================================================= */

const riskContent = computed(() => {

    const data =
        result.value || {}

    return normalizeRenderableContent(
        data.risks ||
        data.risk_analysis ||
        data.legal_risks ||
        ""
    )

})


/* =========================================================
   SIMULACIÓN MULTIAGENTE
========================================================= */

const simulationData = computed(() => normalizeSimulationState(result.value?.simulation))

const reportContent = computed(() => (result.value?.court_report_document?.sections || [])
    .map(section => `## ${section.title}\n\n${section.content}`).join('\n\n'))

/* =========================================================
   GRAFO JURÍDICO
========================================================= */

const graphData = ref(normalizeGraphState(null))
watch(() => result.value?.graph, graph => {
    if (graph && graph.version > 0 && graph.graph_id &&
        graph.case_id === graphData.value?.case_id &&
        graph.graph_id === graphData.value?.graph_id &&
        graph.version === graphData.value?.version &&
        graph.status === graphData.value?.status) return
    graphData.value = graph
        ? normalizeGraphState(graph, graphData.value)
        : normalizeGraphState(null)
}, { immediate: true })

const analysisStatus = computed(() => {

    if (isLoading.value) {
        return "Procesando análisis"
    }

    if (analysisContent.value) {
        return "Análisis disponible"
    }

    return ""

})


const analysisStatusType = computed(() => {

    if (isLoading.value) {
        return "processing"
    }

    if (analysisContent.value) {
        return "completed"
    }

    return "processing"

})


/* =========================================================
   ESTADO — EVIDENCIA
========================================================= */

const evidenceStatus = computed(() => {

    if (isLoading.value) {
        return "Evaluando elementos probatorios"
    }

    if (evidenceContent.value) {
        return "Evaluación disponible"
    }

    return ""

})


const evidenceStatusType = computed(() => {

    if (isLoading.value) {
        return "processing"
    }

    if (evidenceContent.value) {
        return "completed"
    }

    return "processing"

})


/* =========================================================
   ESTADO — RIESGOS
========================================================= */

const riskStatus = computed(() => {

    if (isLoading.value) {
        return "Evaluando riesgos jurídicos"
    }

    if (riskContent.value) {
        return "Evaluación disponible"
    }

    return ""

})


const riskStatusType = computed(() => {

    if (isLoading.value) {
        return "processing"
    }

    if (riskContent.value) {
        return "completed"
    }

    return "processing"

})


/* =========================================================
   ESTADO — SIMULACIÓN
========================================================= */

const simulationStatus = computed(() => simulationData.value.status === 'ready'
    ? 'Simulación disponible' : simulationData.value.message || 'Simulación no disponible')
const simulationStatusType = computed(() => simulationData.value.status === 'ready' ? 'completed' : 'processing')

const reportStatus = computed(() => {

    if (isLoading.value) {
        return "Preparando documento de simulación"
    }

    if (reportContent.value) {
        return "Informe disponible"
    }

    return ""

})


const reportStatusType = computed(() => {

    if (isLoading.value) {
        return "processing"
    }

    if (reportContent.value) {
        return "completed"
    }

    return "processing"

})

</script>


<style scoped>

/* =========================================================
   CONTENEDOR PRINCIPAL
========================================================= */

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


/* =========================================================
   SECCIONES
========================================================= */

.novacourt-section{

    width:100%;

}


.novacourt-section-input{

    margin-top:24px;

}


/* =========================================================
   RESULTADOS
========================================================= */

.novacourt-results{

    width:100%;

    margin-top:28px;

    animation:
        sectionAppear
        .4s
        ease;

}


/* =========================================================
   FEEDBACK
========================================================= */

.novacourt-feedback{

    width:100%;

    margin-top:20px;

}


.feedback-card{

    display:flex;

    align-items:flex-start;

    gap:16px;

    padding:
        20px
        22px;

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


/* =========================================================
   INDICADOR
========================================================= */

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


/* =========================================================
   ERROR ICON
========================================================= */

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


/* =========================================================
   FEEDBACK CONTENT
========================================================= */

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


/* =========================================================
   ESTADO INICIAL
========================================================= */

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


/* =========================================================
   DETALLE SUPERIOR
========================================================= */

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


/* =========================================================
   LÍNEA INSTITUCIONAL
========================================================= */

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


/* =========================================================
   CONTENIDO
========================================================= */

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

    margin:
        0
        0
        10px;

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


/* =========================================================
   SELLO
========================================================= */

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


/* =========================================================
   ANIMACIONES
========================================================= */

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


/* =========================================================
   TABLET
========================================================= */

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


/* =========================================================
   MOBILE GRANDE
========================================================= */

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


/* =========================================================
   MOBILE
========================================================= */

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
