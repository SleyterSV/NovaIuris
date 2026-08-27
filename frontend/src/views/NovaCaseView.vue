<template>

<div class="novacase-page">

    <!-- Header -->

    <header class="case-header">

        <div class="header-content">

            <h1 class="title">

                NovaCase

            </h1>

            <p class="subtitle">

                Analizador Jurídico Inteligente para evaluación integral de casos.

            </p>

        </div>

    </header>

    <!-- Contenido -->

    <main class="case-container">

        <CaseInput
            @analyze="handleAnalyze"
        />

        <AnalysisProgress
            :steps="steps"
            :loading="loading"
        />

    <section

        v-if="hasResults"

        class="case-dashboard"

    >

        <ExecutiveSummary

            :summary="analysisSummary"

        />

        <CaseTabs

            defaultTab="report"

        >

            <!-- ===========================
                INFORME
            ============================ -->

            <template #report>

                <ReportView

                    :report="report"

                />

            </template>

            <!-- ===========================
                ANÁLISIS
            ============================ -->

            <template #analysis>

                <AnalysisView

                    :analysis="analysis"

                />

            </template>

            <!-- ===========================
                EVIDENCIA
            ============================ -->

            <template #evidence>

                <EvidenceView

                    :evidence="evidence"

                />

            </template>

            <!-- ===========================
                RIESGOS
            ============================ -->

            <template #risk>

                <RiskView

                    :risk="risk"

                />

            </template>

            <!-- ===========================
                CONTRAARGUMENTOS
            ============================ -->

            <template #counter>

                <CounterArgumentsView

                    :counter-arguments="counterArguments"

                />

            </template>

            <!-- ===========================
                ESTRATEGIA
            ============================ -->

            <template #strategy>

                <StrategyView

                    :strategy="strategy"

                />

            </template>

        </CaseTabs>

    </section>


    <!-- ===========================
        ERROR
    =========================== -->

    <section

        v-if="error"

        class="error-card"

    >

        <h3>

            Error durante el análisis

        </h3>

        <p>

            {{ error }}

        </p>

    </section>

    </main>

</div>

</template>

<script setup>

import { ref, computed } from "vue"

import { analyzeCase } from "@/services/caseService"

import CaseInput from "@/components/novacase/CaseInput.vue"

import AnalysisProgress from "@/components/novacase/AnalysisProgress.vue"

import ExecutiveSummary from "@/components/common/ExecutiveSummary.vue"

import CaseTabs from "@/components/novacase/CaseTabs.vue"

import ReportView from "@/components/novacase/ReportView.vue"

import AnalysisView from "@/components/novacase/AnalysisView.vue"

import EvidenceView from "@/components/novacase/EvidenceView.vue"

import RiskView from "@/components/novacase/RiskView.vue"

import CounterArgumentsView from "@/components/novacase/CounterArgumentsView.vue"

import StrategyView from "@/components/novacase/StrategyView.vue"

/* =====================================================
   ESTADO GLOBAL
===================================================== */

const loading = ref(false)

const error = ref(null)

const currentStep = ref(0)

let progressTimer = null

/* =====================================================
   RESULTADOS DEL CASO
===================================================== */

const report = ref("")

const summary = ref({})

const analysis = ref({})

const evidence = ref({})

const risk = ref({})

const counterArguments = ref({})

const strategy = ref({})

/* =====================================================
   PROGRESO DEL ANÁLISIS
===================================================== */

const steps = ref([
    {
        id: 1,
        title: "Recepción del caso",
        description: "Recibiendo y preparando la información proporcionada.",
        status: "pending"
    },
    {
        id: 2,
        title: "Análisis jurídico",
        description: "Identificando hechos, problemas jurídicos, normas y criterios relevantes.",
        status: "pending"
    },
    {
        id: 3,
        title: "Evaluación probatoria",
        description: "Analizando las evidencias, fortalezas y aspectos que requieren atención.",
        status: "pending"
    },
    {
        id: 4,
        title: "Evaluación de riesgos",
        description: "Identificando riesgos jurídicos y procesales del caso.",
        status: "pending"
    },
    {
        id: 5,
        title: "Generación del informe",
        description: "Integrando el análisis y preparando el informe jurídico final.",
        status: "pending"
    }
])

function resetProgress() {
    steps.value.forEach(step => {
        step.status = "pending"
    })

    currentStep.value = 0
}


function startVisualProgress() {

    resetProgress()

    steps.value[0].status = "processing"

    /*
     * Este progreso es únicamente visual.
     *
     * El frontend NO afirma que una etapa terminó realmente.
     * Solo mueve el indicador para mostrar actividad mientras
     * el backend continúa procesando el caso.
     */

    const progression = [
        8000,    // Recepción
        90000,   // Análisis jurídico
        90000,   // Evaluación probatoria
        90000    // Riesgos
    ]

    let index = 0

    function advance() {

        if (!loading.value) {
            return
        }

        if (index >= progression.length) {
            return
        }

        steps.value[index].status = "processing"

        currentStep.value = index

        const delay = progression[index]

        index++

        progressTimer = setTimeout(() => {

            if (!loading.value) {
                return
            }

            /*
             * Importante:
             * No marcamos como "completed".
             *
             * Solo avanzamos visualmente a la siguiente etapa.
             */

            if (index < steps.value.length) {

                steps.value[index].status = "processing"

                currentStep.value = index

                advance()
            }

        }, delay)
    }

    advance()
}


function finishProgress() {

    if (progressTimer) {

        clearTimeout(progressTimer)

        progressTimer = null
    }

    steps.value.forEach(step => {
        step.status = "completed"
    })

    currentStep.value = steps.value.length - 1
}

/* =====================================================
   ANALIZAR CASO
===================================================== */

async function handleAnalyze(caseText) {

    loading.value = true
    error.value = null

    /*
     * Limpiar resultados anteriores
     */

    report.value = ""
    summary.value = {}
    analysis.value = {}
    evidence.value = {}
    risk.value = {}
    counterArguments.value = {}
    strategy.value = {}

    /*
     * Iniciar progreso visual
     */

    startVisualProgress()

    try {

        /*
         * NovaCase ejecuta todo el análisis en backend.
         */

        const response = await analyzeCase(
            caseText
        )

        /*
         * Validar respuesta
         */

        if (!response) {

            throw new Error(
                "NovaCase no recibió una respuesta válida del servidor."
            )
        }

        /*
         * =====================================================
         * RESULTADO PRINCIPAL
         * =====================================================
         */

        report.value =
            response.report || ""

        /*
         * =====================================================
         * ANÁLISIS JURÍDICO
         * =====================================================
         */

        analysis.value = {

            ...(
                response.analysis || {}
            ),

            analysis_statistics:
                response.analysis_statistics,

            analysis_summary:
                response.analysis_summary
        }

        /*
         * =====================================================
         * EVIDENCIA
         * =====================================================
         */

        evidence.value =
            response.evidence_analysis || {}

        /*
         * =====================================================
         * RIESGOS
         * =====================================================
         */

        risk.value = {

            risks:
                response.analysis?.riesgos || [],

            score:
                response.evidence_analysis?.evidence_score,

            strength:
                response.evidence_analysis?.evidence_strength,

            evidentiaryRisks:
                response.evidence_analysis?.evidentiary_risks || []
        }

        /*
         * =====================================================
         * INFORMACIÓN INTERNA
         * =====================================================
         *
         * Los contraargumentos pueden utilizarse internamente
         * para fortalecer el análisis, pero no se muestran como
         * una etapa independiente en la interfaz.
         */

        counterArguments.value =
            response.counter_arguments || {}

        /*
         * =====================================================
         * ESTRATEGIA
         * =====================================================
         */

        strategy.value = {

            legalArguments:
                response.legal_arguments,

            recommendations:
                response.evidence_analysis?.recommendations || [],

            report:
                response.report
        }

        /*
         * =====================================================
         * RESUMEN EJECUTIVO
         * =====================================================
         */

        summary.value = {

            ...(
                response.analysis_summary || {}
            ),

            statistics:
                response.analysis_statistics
        }

        /*
         * =====================================================
         * FINALIZAR PROGRESO
         * =====================================================
         *
         * Solo aquí marcamos las etapas como completadas,
         * porque aquí sabemos que el backend terminó.
         */

        finishProgress()

    }
    catch (err) {

        console.error(
            "NovaCase error:",
            err
        )

        /*
         * Detener progreso visual
         */

        if (progressTimer) {

            clearTimeout(
                progressTimer
            )

            progressTimer = null
        }

        /*
         * Marcar como pendiente la etapa que estaba procesándose.
         */

        if (
            currentStep.value >= 0 &&
            currentStep.value < steps.value.length
        ) {

            steps.value[
                currentStep.value
            ].status = "pending"
        }

        error.value =

            err.response?.data?.error ||

            err.response?.data?.message ||

            err.message ||

            "Ocurrió un error al analizar el caso."

    }
    finally {

        loading.value = false
    }
}

/* =====================================================
   COMPUTED
===================================================== */

const hasResults = computed(()=>{

    return Boolean(

        report.value ||

        Object.keys(

            analysis.value

        ).length

    )

})

const analysisStatistics = computed(()=>{

    return (

        analysis.value.analysis_statistics ||

        {}

    )

})

const analysisSummary = computed(()=>{

    return (

        analysis.value.analysis_summary ||

        {}

    )

})

const documentsDetected = computed(()=>{

    return (

        analysis.value.documentos_detectados ||

        []

    )

})

const evidenceCount = computed(()=>{

    return (

        analysisStatistics.value.evidence ||

        0

    )

})

const missingInformationCount = computed(()=>{

    return (

        analysisStatistics.value.missing_information ||

        0

    )

})

const keywordCount = computed(()=>{

    return (

        analysisStatistics.value.keywords ||

        0

    )

})

</script>

<style scoped>

/* =====================================================
   LAYOUT
===================================================== */

.novacase-page{
    min-height:100vh;
    padding:48px;
    background:#F8FAFC;
}

/* =====================================================
   HEADER
===================================================== */

.case-header{

    margin-bottom:42px;

    text-align:center;

}

.header-content{

    max-width:900px;

    margin:auto;

}

.title{

    margin:0;

    font-size:3rem;

    font-weight:800;

    letter-spacing:-1px;

    color:#0F2747;

}

.subtitle{

    margin-top:18px;

    color:#64748B;

    font-size:1.1rem;

    line-height:1.8;

}

/* =====================================================
   CONTENEDOR
===================================================== */

.case-container{

    display:flex;

    flex-direction:column;

    gap:34px;

    max-width:1500px;

    margin:auto;

}

/* =====================================================
   DASHBOARD
===================================================== */

.case-dashboard{

    display:flex;

    flex-direction:column;

    gap:34px;

    animation:

        dashboardFade

        .45s ease;

}

/* =====================================================
   ERROR
===================================================== */

.error-card{

    padding:28px;

    border-radius:18px;

    background:#FEF2F2;

    border:1px solid #FECACA;

    color:#B91C1C;

}

.error-card h3{
    color:#B91C1C;
}

.error-card p{

    margin:0;

    line-height:1.8;

}

/* =====================================================
   SCROLL
===================================================== */

::-webkit-scrollbar{

    width:10px;

}

::-webkit-scrollbar-track{
    background:#F8FAFC;
}

::-webkit-scrollbar-thumb{
    background:#CBD5E1;
}

::-webkit-scrollbar-thumb:hover{
    background:#94A3B8;
}

/* =====================================================
   RESPONSIVE
===================================================== */

@media (max-width:1200px){

    .case-container{

        max-width:100%;

    }

}

@media (max-width:992px){

    .novacase-page{

        padding:30px;

    }

    .title{

        font-size:2.4rem;

    }

}

@media (max-width:768px){

    .novacase-page{

        padding:22px;

    }

    .case-container{

        gap:26px;

    }

    .title{

        font-size:2rem;

    }

    .subtitle{

        font-size:1rem;

    }

}

@media (max-width:576px){

    .novacase-page{

        padding:16px;

    }

    .title{

        font-size:1.7rem;

    }

}

/* =====================================================
   ANIMACIONES
===================================================== */

.case-header{

    animation:

        headerAppear

        .45s ease;

}

.case-container{

    animation:

        containerAppear

        .55s ease;

}

@keyframes headerAppear{

    from{

        opacity:0;

        transform:translateY(-20px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

@keyframes containerAppear{

    from{

        opacity:0;

        transform:translateY(20px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

@keyframes dashboardFade{

    from{

        opacity:0;

        transform:translateY(24px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

</style>