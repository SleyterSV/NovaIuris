<template>

    <div class="novacase-page">

        <!-- =====================================================
             CABECERA PRINCIPAL
        ====================================================== -->

        <header v-if="!embedded" class="case-header">

            <div class="header-inner">

                <div class="header-eyebrow">

                    <span class="eyebrow-line"></span>

                    MYKE · NOVACASE

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

        <main class="case-container">


            <!-- =================================================
                 ENTRADA DEL CASO
            ================================================== -->

            <section v-if="!embedded" ref="caseInputSection" class="workspace-section">

                <CaseInput
                    :case-id="inputCaseId" :loading="loading"
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
                <button v-if="loading" type="button" class="cancel-analysis" @click="controller?.abort('user')">Cancelar análisis</button>

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

                        <span>{{ canonicalResult?.status === "partial" ? "Análisis disponible parcialmente" : "Análisis completado" }}</span>

                    </div>

                </header>
                <div v-if="privateDocumentCount === 0" class="case-documents-notice">
                    <span>Sin documentos aportados: los hechos del relato permanecen como alegaciones.</span>
                    <button type="button" @click="addDocuments">Agregar documentos al caso</button>
                </div>


                <!-- =============================================
                     RESUMEN EJECUTIVO
                ============================================== -->

                <!-- =============================================
                     NAVEGACIÓN DEL CASO
                ============================================== -->

                <CaseTabs
                    defaultTab="summary"
                    :available-tabs="availableTabs"
                >

                    <template #summary>
                        <ExecutiveSummary :summary="analysisSummary" :analysis="analysis"
                            :facts="canonicalResult?.facts || []"
                            :report-document="canonicalResult?.report_document || {}"
                            :sources="[...(canonicalResult?.research?.sources || []), ...(canonicalResult?.sources || []), ...(canonicalResult?.sources_used || [])]"
                            :case-id="canonicalResult?.case_id" :partial="canonicalResult?.status === 'partial'" />
                        <button v-if="hasResults && caseTaskCompleted && canonicalResult?.case_id"
                            type="button" class="summary-court-cta" @click="continueInNovaCourt">
                            Simular en NovaCourt <span aria-hidden="true">→</span>
                        </button>
                    </template>

                    <!-- =========================================
                         INFORME
                    ========================================== -->

                    <template #report>

                        <ReportView
                            :report="report"
                            :report-document="canonicalResult?.report_document"
                            :citations="canonicalResult?.citations || []"
                            :sources="canonicalResult?.sources || []"
                            :case-id="canonicalResult?.case_id"
                            :task-id="completedTaskId"
                            :report-status="canonicalResult?.report_status || 'not_requested'"
                            :report-error="canonicalResult?.report_error"
                            :document-count="privateDocumentCount"
                            :public-source-count="publicSourceCount"
                        />

                    </template>


                    <!-- =========================================
                         ANÁLISIS
                    ========================================== -->

                    <template #analysis>

                        <AnalysisView
                            :analysis="analysis"
                            :summary="summary"
                            :facts="canonicalResult?.facts || []"
                            :timeline-data="canonicalResult?.timeline || []"
                            :sources="[...(canonicalResult?.research?.sources || []), ...(canonicalResult?.sources || []), ...(canonicalResult?.sources_used || [])]"
                            :citations="canonicalResult?.citations || []"
                            :case-id="canonicalResult?.case_id"
                            :document-count="privateDocumentCount"
                            :public-source-count="publicSourceCount"
                            :completed="canonicalResult?.status === 'completed'"
                            @select-source="selectedSource = $event"
                        />

                    </template>

                    <template #arguments>
                        <ArgumentsView :arguments="canonicalResult?.arguments || {}"
                            :facts="canonicalResult?.facts || []"
                            :sources="[...(canonicalResult?.research?.sources || []), ...(canonicalResult?.sources || []), ...(canonicalResult?.sources_used || [])]"
                            :citations="canonicalResult?.citations || []"
                            :case-id="canonicalResult?.case_id" @select-source="selectedSource = $event" />
                    </template>


                    <!-- =========================================
                         EVIDENCIA
                    ========================================== -->

                    <template #evidence>

                        <EvidenceView
                            :evidence="evidence"
                            :analysis="analysis"
                            :fact-groups="factGroups"
                            :facts="canonicalResult?.facts || []"
                            :issues="canonicalResult?.issues || []"
                            :evidence-links="canonicalResult?.evidence?.evidence_links || []"
                            :document-count="privateDocumentCount"
                            :sources="[...(canonicalResult?.research?.sources || []), ...(canonicalResult?.sources || []), ...(canonicalResult?.sources_used || [])]"
                            :citations="canonicalResult?.citations || []"
                            :case-id="canonicalResult?.case_id"
                            @select-source="selectedSource = $event"
                            @add-documents="addDocuments"
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
                            :responses="canonicalResult?.arguments?.counterargument_responses || []"
                            :sources="[...(canonicalResult?.research?.sources || []), ...(canonicalResult?.sources || []), ...(canonicalResult?.sources_used || [])]"
                            :citations="canonicalResult?.citations || []"
                            :case-id="canonicalResult?.case_id"
                            @select-source="selectedSource = $event"
                        />

                    </template>


                    <!-- =========================================
                         ESTRATEGIA
                    ========================================== -->

                    <template #strategy>
                        <StrategyView
                            :strategy="strategy"
                            :final-strategy="canonicalResult?.final_strategy || {}"
                            :arguments="canonicalResult?.arguments || {}"
                            :facts="canonicalResult?.facts || []"
                            :issues="canonicalResult?.issues || []"
                            :evidence="canonicalResult?.evidence || {}"
                            :risks="canonicalResult?.risks || {}"
                            :counter-arguments="canonicalResult?.counter_arguments || {}"
                            :sources="[...(canonicalResult?.research?.sources || []), ...(canonicalResult?.sources || []), ...(canonicalResult?.sources_used || [])]"
                            :citations="canonicalResult?.citations || []"
                            :case-id="canonicalResult?.case_id"
                            :analyzed="Boolean(canonicalResult?.final_strategy)"
                            @select-source="selectedSource = $event"
                        />

                    </template>

                    <template #sources>
                        <CaseSourcesView
                            :sources="[...(canonicalResult?.research?.sources || []), ...(canonicalResult?.sources_used || [])]"
                            :citations="canonicalResult?.citations || []"
                            :case-id="canonicalResult?.case_id"
                            @select-source="selectedSource = $event"
                        />
                    </template>

                </CaseTabs>
                <SourceModal :source="selectedSource" :case-id="canonicalResult?.case_id" @close="selectedSource = null" />

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
                    MYKE
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
import '@/styles/novacaseEditorial.css'
import { useRouter } from "vue-router"
import { normalizeCaseResult } from "@/utils/caseContract.js"
import { factAllegationOrigin } from "@/utils/novacasePresentation.js"
import { caseReuseContext } from "@/utils/mikeWorkspace.js"
import { normalizeRenderableContent } from "@/utils/content.js"

import {
    ref,
    computed,
    watch,
    nextTick,
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
import CaseSourcesView from "@/components/novacase/CaseSourcesView.vue"
import SourceModal from "@/components/common/SourceModal.vue"

import CaseTabs
    from "@/components/novacase/CaseTabs.vue"

import ReportView
    from "@/components/novacase/ReportView.vue"

import AnalysisView
    from "@/components/novacase/AnalysisView.vue"

import EvidenceView
    from "@/components/novacase/EvidenceView.vue"
import ArgumentsView from "@/components/novacase/ArgumentsView.vue"

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
const lastCaseText = ref('')
const props = defineProps({ embedded: Boolean, request: { type:Object, default:null } })
const emit = defineEmits(['case-completed', 'reuse-case', 'task-state', 'add-documents'])
const completedTaskId = ref(null)
const caseTaskCompleted = ref(false)
const inputCaseId = ref(crypto.randomUUID())
const router = useRouter()
const selectedSource = ref(null)
const caseInputSection = ref(null)
const loading = ref(false)

const error = ref(null)

const currentStep = ref(0)

let controller = null
onBeforeUnmount(() => controller?.abort('detach'))


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

const steps = ref([])


/* =========================================================
   RESET PROGRESO
========================================================= */

function resetProgress() {
    steps.value = []
    currentStep.value = 0
}


/* =========================================================
   PROGRESO VISUAL
========================================================= */

function startVisualProgress() { resetProgress() }
function updateTask(task) {
  steps.value = (Array.isArray(task.stages) ? task.stages : []).map(stage => ({ ...stage, title: stage.label, description: '',
    status: stage.status === 'running' ? 'processing' : stage.status }))
  if (task.partial_result?.analysis) canonicalResult.value = normalizeCaseResult(task.partial_result)
}

function finishProgress(result) {
    if (result?.status !== "partial") {
        steps.value = steps.value.map(step => ({
            ...step,
            status: step.status === "processing" ? "completed" : step.status
        }))
    }
    currentStep.value = steps.value.reduce((last, step, index) => step.status === "completed" ? index : last, 0)
}


/* =========================================================
   ANALIZAR CASO
========================================================= */

async function handleAnalyze(payload) {
    if (loading.value) return
    const historical = payload.historicalResult
    emit('task-state', { tool:'case', running:!historical })
    const caseText = payload.caseText
    lastCaseText.value = caseText
    const caseId = payload.caseId
    const documentIds = payload.documentIds || []
    controller = new AbortController()

    loading.value = true
    canonicalResult.value = null
    completedTaskId.value = null
    caseTaskCompleted.value = false
    selectedSource.value = null

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

        const response = normalizeCaseResult(historical ? historical.result : await analyzeCase(caseText, { caseId, documentIds,
            existingTaskId:payload.existingTaskId,
            onTask: task => {
                completedTaskId.value = task.task_id
                emit('task-state', { tool:'case', running:true, taskId:task.task_id })
            },
            onProgress: updateTask, signal: controller.signal }))
        canonicalResult.value = response

        if (!response) {

            throw new Error(
                "NovaCase no recibió una respuesta válida del servidor."
            )

        }
        completedTaskId.value = historical?.run?.task_id || completedTaskId.value
        caseTaskCompleted.value = true
        emit('case-completed', { result:response, taskId:completedTaskId.value, caseText })
        if (historical) emit('task-state', { tool:'case', running:false, taskId:completedTaskId.value, status:'completed' })


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
        finishProgress(response)
        inputCaseId.value = crypto.randomUUID()


    }

    catch (err) {

        console.error("NovaCase request failed")


        /* -------------------------------------------------
           DETENER PROGRESO
        ------------------------------------------------- */

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
        emit('task-state', { tool:'case', running:false })

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
const privateDocumentCount = computed(() => canonicalResult.value?.document_ids?.length || 0)
const publicSourceCount = computed(() => canonicalResult.value?.research?.public_source_count ??
    (canonicalResult.value?.research?.sources || []).filter(source => source.source_scope === 'public_legal').length)

async function addDocuments() {
    const caseId = canonicalResult.value?.case_id
    if (!caseId) return
    if (props.embedded) {
        emit('add-documents', { caseId })
        return
    }
    inputCaseId.value = caseId
    await nextTick()
    const uploader = caseInputSection.value?.querySelector('.document-upload')
    uploader?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    uploader?.querySelector('input[type="file"]')?.click()
}

const availableTabs = computed(() => {
    const result = canonicalResult.value
    if (!result) return []
    const tabs = []
    if (normalizeRenderableContent(result.summary)) tabs.push("summary")
    tabs.push("analysis")
    if (normalizeRenderableContent(result.arguments)) tabs.push("arguments")
    if (normalizeRenderableContent(result.evidence)) tabs.push("evidence")
    if (normalizeRenderableContent(result.risks)) tabs.push("risk")
    if (normalizeRenderableContent(result.counter_arguments)) tabs.push("counter")
    if (normalizeRenderableContent(result.final_strategy || result.strategy)) tabs.push("strategy")
    if (result.research?.sources?.length || result.sources_used?.length || result.citations?.length) tabs.push("sources")
    if (result.report || result.report_status === "failed") tabs.push("report")
    return tabs
})

/* Keep provenance controls compact so they remain usable with long case files. */

function factStatusLabel(status) {
    return ({ alleged: "Alegación", supported: "Con respaldo documental identificado", disputed: "Controvertido", unclear: "No determinado" })[status] || "No determinado"
}

const factGroups = computed(() => {
    const facts = canonicalResult.value?.facts || []
    return [
        { key: 'supported', title: 'Hechos con respaldo documental', facts: facts.filter(fact => fact.status === 'supported' && factSources(fact).length) },
        { key: 'alleged', title: 'Hechos alegados', facts: facts.filter(fact => ['alleged', 'disputed'].includes(fact.status) || (fact.status === 'supported' && !factSources(fact).length)) },
        { key: 'pending', title: 'Hechos pendientes de corroboración', facts: facts.filter(fact => !['supported', 'alleged', 'disputed'].includes(fact.status)) }
    ]
})

function sourceMap() {
    const result = canonicalResult.value || {}
    return new Map([...(result.research?.sources || []), ...(result.sources || []),
        ...(result.sources_used || [])].map(source => [source.source_id, source]))
}

function factSources(fact) {
    const sources = sourceMap()
    return (fact.source_ids || []).map(id => sources.get(id)).filter(source =>
        source && ["case", "private_case"].includes(source.source_scope) && source.case_id === canonicalResult.value?.case_id)
}

function continueInNovaCourt() {
  const result = canonicalResult.value
  if (!result?.case_id) return
  if (props.embedded) {
    emit('reuse-case', caseReuseContext(result, completedTaskId.value, lastCaseText.value))
    return
  }
  router.push({ path:"/mike", query:{ tool:'court', case_id:result.case_id, document_ids:(result.document_ids || []).join(",") },
    state:{ caseText:result.case, reuseTaskId:completedTaskId.value } })
}

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

watch(() => props.request, request => {
    if (request) handleAnalyze({ caseText:request.text, caseId:request.caseId,
        documentIds:request.documentIds, existingTaskId:request.existingTaskId,
        historicalResult:request.historicalResult })
}, { immediate:true })
</script>


<style scoped>
.research-notice,.case-documents-notice{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;border-radius:9px;padding:13px 16px;margin:14px 0;color:#27415d;font-size:.86rem;line-height:1.45}.research-notice{border:1px solid #cddce9;background:#f4f8fc}.research-notice.verified{border-color:#b6d9c9;background:#f1f9f5}.research-notice.error{border-color:#e4bdb9;background:#fff5f3}.research-notice.unavailable{border-color:#e1d4b5;background:#fcfaf3}.case-documents-notice{justify-content:space-between;border:1px solid #e1d4b5;background:#fcfaf3}.case-documents-notice button{border:1px solid #173a5f;border-radius:6px;padding:9px 13px;background:#173a5f;color:#fff;font-weight:650;cursor:pointer}@media(max-width:640px){.case-documents-notice button{width:100%}}

.case-facts { margin: 18px 0; padding: 18px; background: #fff; border: 1px solid #dce5ee; border-radius: 10px; }
.case-facts h3 { margin: 0 0 12px; color: #17375e; font: 600 1rem Georgia, serif; }
.case-facts ul { display: grid; gap: 12px; margin: 0; padding-left: 20px; }
.case-facts li { padding: 10px 0; border-bottom: 1px solid #e8edf2; }
.fact-status { display: inline-block; margin: 6px 8px 0 0; color: #65768a; font-size: .75rem; }
.fact-reference { display: block; margin: 6px 0; color: #65768a; font-size: .82rem; }

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
