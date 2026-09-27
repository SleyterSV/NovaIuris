<template>

    <div class="novacase-page">

        <!-- =====================================================
             CABECERA PRINCIPAL
        ====================================================== -->

        <header class="case-header">

            <div class="header-inner">

                <div class="header-eyebrow">

                    <span class="eyebrow-line"></span>

                    NOVA IURIS · NOVACASE

                </div>

                <div class="header-main">

                    <div class="header-copy">

                        <h1 class="title">
                            NovaCase
                        </h1>

                        <p class="subtitle">
                            Analizador Jurídico Inteligente
                        </p>

                        <p class="description">
                            Evaluación estructurada de hechos, problemas jurídicos,
                            normativa, evidencia, riesgos y estrategia del caso.
                        </p>

                    </div>

                    <div class="header-badge">

                        <span class="badge-icon">

                            <svg
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="1.7"
                                aria-hidden="true"
                            >
                                <path
                                    d="M12 3v18"
                                />

                                <path
                                    d="M5 6h14"
                                />

                                <path
                                    d="M7 6l-3 6a3 3 0 0 0 6 0L7 6Z"
                                />

                                <path
                                    d="M17 6l-3 6a3 3 0 0 0 6 0l-3-6Z"
                                />

                                <path
                                    d="M8 21h8"
                                />

                            </svg>

                        </span>

                        <span class="badge-content">

                            <strong>
                                Inteligencia jurídica
                            </strong>

                            <small>
                                Análisis estructurado
                            </small>

                        </span>

                    </div>

                </div>

            </div>

        </header>


        <!-- =====================================================
             CONTENIDO PRINCIPAL
        ====================================================== -->

        <button v-if="loading" type="button" @click="controller?.abort()">Cancelar tarea</button>
        <main class="case-container">


            <!-- =================================================
                 ENTRADA DEL CASO
            ================================================== -->

            <section class="workspace-section">

                <CaseInput
                    @analyze="handleAnalyze"
                />

            </section>


            <!-- =================================================
                 PROGRESO
            ================================================== -->

            <section
                v-if="loading || !hasResults"
                class="workspace-section progress-section"
            >

                <div class="section-label">

                    <span class="section-line"></span>

                    PROCESAMIENTO

                </div>

                <AnalysisProgress
                    :steps="steps"
                    :loading="loading"
                />

            </section>


            <!-- =================================================
                 RESULTADOS
            ================================================== -->

            <section
                v-if="hasResults"
                class="case-dashboard"
            >

                <!-- =============================================
                     ENCABEZADO DE RESULTADOS
                ============================================== -->

                <header class="results-header">

                    <div>

                        <div class="section-label">

                            <span class="section-line"></span>

                            RESULTADOS DEL ANÁLISIS

                        </div>

                        <h2>
                            Evaluación Jurídica del Caso
                        </h2>

                        <p>
                            Resultado integral generado por NovaCase a partir
                            de la información proporcionada.
                        </p>

                    </div>

                    <div class="results-status">

                        <span class="status-dot"></span>

                        <span>
                            Análisis completado
                        </span>

                    </div>

                </header>


                <!-- =============================================
                     RESUMEN EJECUTIVO
                ============================================== -->

                <ExecutiveSummary
                    :summary="analysisSummary"
                />


                <!-- =============================================
                     NAVEGACIÓN DEL CASO
                ============================================== -->

                <CaseTabs
                    defaultTab="report"
                >

                    <!-- =========================================
                         INFORME
                    ========================================== -->

                    <template #report>

                        <ReportView
                            :report="report"
                        />

                    </template>


                    <!-- =========================================
                         ANÁLISIS
                    ========================================== -->

                    <template #analysis>

                        <AnalysisView
                            :analysis="analysis"
                        />

                    </template>


                    <!-- =========================================
                         EVIDENCIA
                    ========================================== -->

                    <template #evidence>

                        <EvidenceView
                            :evidence="evidence"
                        />

                    </template>


                    <!-- =========================================
                         RIESGOS
                    ========================================== -->

                    <template #risk>

                        <RiskView
                            :risk="risk"
                        />

                    </template>


                    <!-- =========================================
                         CONTRAARGUMENTOS
                    ========================================== -->

                    <template #counter>

                        <CounterArgumentsView
                            :counter-arguments="counterArguments"
                        />

                    </template>


                    <!-- =========================================
                         ESTRATEGIA
                    ========================================== -->

                    <template #strategy>

                        <StrategyView
                            :strategy="strategy"
                        />

                    </template>

                </CaseTabs>
                <section v-for="section in supplementarySections" :key="section.title" class="workspace-section">
                  <h3>{{ section.title }}</h3><MarkdownRenderer :content="section.content" />
                </section>

            </section>


            <!-- =================================================
                 ERROR
            ================================================== -->

            <section
                v-if="error"
                class="error-card"
                role="alert"
            >

                <div class="error-icon">

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
                            d="M12 8v5"
                        />

                        <path
                            d="M12 16h.01"
                        />

                    </svg>

                </div>

                <div class="error-content">

                    <span class="error-label">
                        NOVACASE · ERROR
                    </span>

                    <h3>
                        No fue posible completar el análisis
                    </h3>

                    <p>
                        {{ error }}
                    </p>

                </div>

            </section>


        </main>


        <!-- =====================================================
             FOOTER
        ====================================================== -->

        <footer class="novacase-footer">

            <div class="footer-inner">

                <span>
                    NOVA IURIS
                </span>

                <span class="footer-separator">
                    ·
                </span>

                <span>
                    NOVACASE
                </span>

                <span class="footer-separator">
                    ·
                </span>

                <span>
                    Inteligencia jurídica
                </span>

            </div>

        </footer>

    </div>

</template>


<script setup>
import { normalizeCaseResult } from "@/utils/caseContract.js"
import MarkdownRenderer from "@/components/common/MarkdownRenderer.vue"
import { normalizeRenderableContent } from "@/utils/content.js"

import {
    ref,
    computed,
    onBeforeUnmount
} from "vue"

import {
    analyzeCase
} from "@/services/caseService"


/* =========================================================
   COMPONENTES
========================================================= */

import CaseInput
    from "@/components/novacase/CaseInput.vue"

import AnalysisProgress
    from "@/components/novacase/AnalysisProgress.vue"

import ExecutiveSummary
    from "@/components/common/ExecutiveSummary.vue"

import CaseTabs
    from "@/components/novacase/CaseTabs.vue"

import ReportView
    from "@/components/novacase/ReportView.vue"

import AnalysisView
    from "@/components/novacase/AnalysisView.vue"

import EvidenceView
    from "@/components/novacase/EvidenceView.vue"

import RiskView
    from "@/components/novacase/RiskView.vue"

import CounterArgumentsView
    from "@/components/novacase/CounterArgumentsView.vue"

import StrategyView
    from "@/components/novacase/StrategyView.vue"


/* =========================================================
   ESTADO GLOBAL
========================================================= */

const canonicalResult = ref(null)
const supplementarySections = computed(() => [
  { title: 'Investigación jurídica', content: canonicalResult.value?.research?.documents },
  { title: 'Argumentos jurídicos', content: canonicalResult.value?.arguments },
  { title: 'Cronología', content: canonicalResult.value?.timeline },
  { title: 'Citas', content: canonicalResult.value?.citations },
  { title: 'Elementos complementarios de estrategia', content: canonicalResult.value && Object.fromEntries(['defense_strategy','strengths','weaknesses','recommended_evidence','recommended_documents','missing_information'].map(key => [key, canonicalResult.value.strategy[key]])) }
])
const loading = ref(false)

const error = ref(null)

const currentStep = ref(0)

let progressTimer = null
let controller = null
onBeforeUnmount(() => controller?.abort())


/* =========================================================
   RESULTADOS
========================================================= */

const report = ref("")

const summary = ref({})

const analysis = ref({})

const evidence = ref({})

const risk = ref({})

const counterArguments = ref({})

const strategy = ref({})


/* =========================================================
   PROGRESO DEL ANÁLISIS
========================================================= */

const steps = ref([

    {
        id: 1,
        title: "Recepción del caso",
        description:
            "Recibiendo y preparando la información proporcionada.",
        status: "pending"
    },

    {
        id: 2,
        title: "Análisis jurídico",
        description:
            "Identificando hechos, problemas jurídicos, normas y criterios relevantes.",
        status: "pending"
    },

    {
        id: 3,
        title: "Evaluación probatoria",
        description:
            "Analizando las evidencias, fortalezas y aspectos que requieren atención.",
        status: "pending"
    },

    {
        id: 4,
        title: "Evaluación de riesgos",
        description:
            "Identificando riesgos jurídicos y procesales del caso.",
        status: "pending"
    },

    {
        id: 5,
        title: "Generación del informe",
        description:
            "Integrando el análisis y preparando el informe jurídico final.",
        status: "pending"
    }

])


/* =========================================================
   RESET PROGRESO
========================================================= */

function resetProgress() {

    steps.value.forEach(step => {

        step.status = "pending"

    })

    currentStep.value = 0

}


/* =========================================================
   PROGRESO VISUAL
========================================================= */

function startVisualProgress() { resetProgress() }
function updateTask(task) {
  steps.value = task.stages.map(stage => ({ ...stage, title: stage.label, description: '',
    status: stage.status === 'running' ? 'processing' : stage.status }))
  if (task.partial_result?.analysis) canonicalResult.value = normalizeCaseResult(task.partial_result)
}

function finishProgress() {

    if (progressTimer) {

        clearTimeout(
            progressTimer
        )

        progressTimer = null

    }


    steps.value.forEach(step => {

        step.status =
            "completed"

    })


    currentStep.value =
        steps.value.length - 1

}


/* =========================================================
   ANALIZAR CASO
========================================================= */

async function handleAnalyze(caseText) {
    if (loading.value) return
    controller = new AbortController()

    loading.value = true
    canonicalResult.value = null

    error.value = null


    /* -----------------------------------------------------
       LIMPIAR RESULTADOS ANTERIORES
    ----------------------------------------------------- */

    report.value = ""

    summary.value = {}

    analysis.value = {}

    evidence.value = {}

    risk.value = {}

    counterArguments.value = {}

    strategy.value = {}


    /* -----------------------------------------------------
       INICIAR PROGRESO
    ----------------------------------------------------- */

    startVisualProgress()


    try {


        /* =================================================
           EJECUTAR ANÁLISIS
        ================================================== */

        const response = normalizeCaseResult(await analyzeCase(caseText, { onProgress: updateTask, signal: controller.signal }))
        canonicalResult.value = response

        if (!response) {

            throw new Error(
                "NovaCase no recibió una respuesta válida del servidor."
            )

        }


        /* =================================================
           INFORME
        ================================================== */

        report.value = normalizeRenderableContent(response.report)
        analysis.value = response.analysis
        evidence.value = response.evidence
        risk.value = response.risks
        counterArguments.value = response.counter_arguments
        strategy.value = response.strategy
        summary.value = response.summary
        finishProgress()


    }

    catch (err) {

        console.error(
            "NovaCase error:",
            err
        )


        /* -------------------------------------------------
           DETENER PROGRESO
        ------------------------------------------------- */

        if (progressTimer) {

            clearTimeout(
                progressTimer
            )

            progressTimer = null

        }


        /* -------------------------------------------------
           RESTAURAR ESTADO DE LA ETAPA
        ------------------------------------------------- */

        if (
            currentStep.value >= 0 &&
            currentStep.value < steps.value.length
        ) {

            steps.value[
                currentStep.value
            ].status = "pending"

        }


        /* -------------------------------------------------
           MENSAJE
        ------------------------------------------------- */

        error.value =

            err.response?.data?.error?.message ||

            err.response?.data?.message ||

            err.message ||

            "Ocurrió un error al analizar el caso."

    }

    finally {

        loading.value = false

    }

}


/* =========================================================
   COMPUTED
========================================================= */

const hasResults = computed(() => {

    return Boolean(

        report.value ||

        Object.keys(
            analysis.value
        ).length

    )

})


const analysisStatistics = computed(() => {

    return (

        canonicalResult.value?.metadata
            .analysis_statistics ||

        {}

    )

})


const analysisSummary = computed(() => summary.value)

const documentsDetected = computed(() => {

    return (

        analysis.value
            .documentos_detectados ||

        []

    )

})


const evidenceCount = computed(() => {

    return (

        analysisStatistics.value.evidence ||

        0

    )

})


const missingInformationCount = computed(() => {

    return (

        analysisStatistics.value.missing_information ||

        0

    )

})


const keywordCount = computed(() => {

    return (

        analysisStatistics.value.keywords ||

        0

    )

})

</script>


<style scoped>

/* =========================================================
   NOVACASE — MAIN VIEW
========================================================= */

.novacase-page {

    width: 100%;

    min-height: 100vh;

    box-sizing: border-box;

    background:
        linear-gradient(
            180deg,
            #F8FAFC 0%,
            #F5F8FB 100%
        );

    color: #17375E;

}


/* =========================================================
   HEADER
========================================================= */

.case-header {

    width: 100%;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #FBFCFD 100%
        );

    border-bottom:
        1px solid
        #DCE5EE;

}


.header-inner {

    width: min(
        1500px,
        calc(100% - 80px)
    );

    margin: 0 auto;

    padding:
        42px
        0
        34px;

}


.header-eyebrow {

    display: flex;

    align-items: center;

    gap: 9px;

    margin-bottom: 17px;

    color: #7A6440;

    font-size: .61rem;

    font-weight: 800;

    letter-spacing: 1.6px;

}


.eyebrow-line {

    width: 25px;

    height: 1px;

    background: #B08A4C;

}


.header-main {

    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 30px;

}


.header-copy {

    min-width: 0;

}


.title {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 2.65rem;

    font-weight: 600;

    line-height: 1.15;

    letter-spacing: -.5px;

}


.subtitle {

    margin: 8px 0 0;

    color: #315C97;

    font-size: .95rem;

    font-weight: 700;

}


.description {

    max-width: 760px;

    margin: 9px 0 0;

    color: #718090;

    font-size: .84rem;

    line-height: 1.7;

}


/* =========================================================
   BADGE HEADER
========================================================= */

.header-badge {

    display: flex;

    align-items: center;

    gap: 11px;

    flex-shrink: 0;

    padding:
        10px
        13px;

    background: #FFFFFF;

    border:
        1px solid
        #D9E2EC;

    border-radius: 10px;

    box-shadow:
        0 4px 14px
        rgba(
            23,
            55,
            94,
            .035
        );

}


.badge-icon {

    width: 34px;

    height: 34px;

    display: flex;

    align-items: center;

    justify-content: center;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .35
        );

    border-radius: 8px;

    background: #FCF9F4;

    color: #8A6A36;

}


.badge-icon svg {

    width: 19px;

    height: 19px;

}


.badge-content {

    display: flex;

    flex-direction: column;

    gap: 2px;

}


.badge-content strong {

    color: #304C6C;

    font-size: .67rem;

    font-weight: 800;

}


.badge-content small {

    color: #8C98A5;

    font-size: .58rem;

}


/* =========================================================
   CONTENEDOR
========================================================= */

.case-container {

    width: min(
        1500px,
        calc(100% - 80px)
    );

    margin: 0 auto;

    padding:
        38px
        0
        50px;

}


/* =========================================================
   SECCIONES DE WORKSPACE
========================================================= */

.workspace-section {

    display: flex;

    flex-direction: column;

    gap: 13px;

}


/* =====================================================
   SECCIÓN DE PROCESAMIENTO
===================================================== */

.progress-section{

    position:relative;

    margin-top:8px;

    padding-top:26px;

}

.progress-section::before{

    content:"";

    position:absolute;

    top:0;
    left:0;
    right:0;

    height:1px;

    background:linear-gradient(
        90deg,
        transparent 0%,
        #DCE5EE 12%,
        #DCE5EE 88%,
        transparent 100%
    );

}


.section-label {

    display: flex;

    align-items: center;

    gap: 8px;

    color: #8A6A36;

    font-size: .58rem;

    font-weight: 800;

    letter-spacing: 1.35px;

}


.section-line {

    width: 20px;

    height: 1px;

    background: #B08A4C;

}


/* =========================================================
   DASHBOARD
========================================================= */

.case-dashboard {

    display: flex;

    flex-direction: column;

    gap: 28px;

    animation:
        dashboardAppear
        .45s
        ease-out;

}


/* =========================================================
   RESULTADOS HEADER
========================================================= */

.results-header {

    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 24px;

    padding:
        3px
        3px
        20px;

    border-bottom:
        1px solid
        #DCE5EE;

}


.results-header h2 {

    margin:
        9px
        0
        6px;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.45rem;

    font-weight: 600;

    line-height: 1.35;

}


.results-header p {

    margin: 0;

    color: #718090;

    font-size: .81rem;

    line-height: 1.65;

}


/* =========================================================
   ESTADO
========================================================= */

.results-status {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    flex-shrink: 0;

    min-height: 31px;

    padding:
        0
        12px;

    background: #F7FAF8;

    border:
        1px solid
        #D8E7DD;

    border-radius: 999px;

    color: #587161;

    font-size: .63rem;

    font-weight: 750;

}


.status-dot {

    width: 6px;

    height: 6px;

    border-radius: 50%;

    background: #668B70;

    box-shadow:
        0 0 0 3px
        rgba(
            102,
            139,
            112,
            .10
        );

}


/* =========================================================
   ERROR
========================================================= */

.error-card {

    display: flex;

    align-items: flex-start;

    gap: 14px;

    padding:
        18px
        20px;

    background: #FFF9F9;

    border:
        1px solid
        #F0CACA;

    border-radius: 11px;

    color: #7F1D1D;

    animation:
        errorAppear
        .3s
        ease-out;

}


.error-icon {

    width: 34px;

    height: 34px;

    flex:
        0 0
        34px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 8px;

    background: #FEF2F2;

    color: #B91C1C;

}


.error-icon svg {

    width: 18px;

    height: 18px;

}


.error-content {

    min-width: 0;

}


.error-label {

    display: block;

    margin-bottom: 4px;

    color: #A44A4A;

    font-size: .55rem;

    font-weight: 800;

    letter-spacing: 1px;

}


.error-card h3 {

    margin: 0 0 5px;

    color: #991B1B;

    font-size: .92rem;

    font-weight: 750;

}


.error-card p {

    margin: 0;

    color: #8B4A4A;

    font-size: .78rem;

    line-height: 1.65;

}


/* =========================================================
   FOOTER
========================================================= */

.novacase-footer {

    border-top:
        1px solid
        #E1E7ED;

    background: #FFFFFF;

}


.footer-inner {

    width: min(
        1500px,
        calc(100% - 80px)
    );

    min-height: 48px;

    margin: 0 auto;

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 8px;

    color: #9AA5B0;

    font-size: .55rem;

    font-weight: 750;

    letter-spacing: .65px;

}


.footer-inner span:first-child {

    color: #315C97;

}


.footer-separator {

    color: #C2CBD4;

}


/* =========================================================
   SCROLLBAR
========================================================= */

:deep(::-webkit-scrollbar) {

    width: 9px;

}


:deep(::-webkit-scrollbar-track) {

    background: #F5F7FA;

}


:deep(::-webkit-scrollbar-thumb) {

    background: #CBD5E1;

    border-radius: 999px;

}


:deep(::-webkit-scrollbar-thumb:hover) {

    background: #94A3B8;

}


/* =========================================================
   ANIMACIONES
========================================================= */

@keyframes dashboardAppear {

    from {

        opacity: 0;

        transform:
            translateY(12px);

    }

    to {

        opacity: 1;

        transform:
            translateY(0);

    }

}


@keyframes errorAppear {

    from {

        opacity: 0;

        transform:
            translateY(6px);

    }

    to {

        opacity: 1;

        transform:
            translateY(0);

    }

}


/* =========================================================
   REDUCIR MOVIMIENTO
========================================================= */

@media (
    prefers-reduced-motion: reduce
) {

    .case-dashboard,
    .error-card {

        animation: none;

    }

}


/* =========================================================
   1200 PX
========================================================= */

@media (max-width: 1200px) {

    .header-inner,
    .case-container,
    .footer-inner {

        width:
            calc(
                100% - 56px
            );

    }

}


/* =========================================================
   900 PX
========================================================= */

@media (max-width: 900px) {

    .header-main {

        align-items: flex-start;

        flex-direction: column;

        gap: 20px;

    }


    .header-badge {

        align-self: flex-start;

    }


    .results-header {

        align-items: flex-start;

        flex-direction: column;

        gap: 14px;

    }


    .results-status {

        align-self: flex-start;

    }

}


/* =========================================================
   700 PX
========================================================= */

@media (max-width: 700px) {

    .header-inner,
    .case-container,
    .footer-inner {

        width:
            calc(
                100% - 36px
            );

    }


    .header-inner {

        padding:
            30px
            0
            25px;

    }


    .case-container {

        padding:
            28px
            0
            38px;

    }


    .title {

        font-size: 2.2rem;

    }


    .subtitle {

        font-size: .9rem;

    }


    .description {

        font-size: .79rem;

    }


    .results-header h2 {

        font-size: 1.28rem;

    }


    .error-card {

        padding:
            16px;

    }

}


/* =========================================================
   480 PX
========================================================= */

@media (max-width: 480px) {

    .header-inner,
    .case-container,
    .footer-inner {

        width:
            calc(
                100% - 28px
            );

    }


    .header-inner {

        padding:
            25px
            0
            22px;

    }


    .case-container {

        padding:
            23px
            0
            30px;

    }


    .title {

        font-size: 1.9rem;

    }


    .header-badge {

        width: 100%;

        box-sizing: border-box;

    }


    .badge-content {

        flex: 1;

    }


    .section-label {

        font-size: .55rem;

    }


    .footer-inner {

        min-height: 44px;

        font-size: .49rem;

    }

}

</style>