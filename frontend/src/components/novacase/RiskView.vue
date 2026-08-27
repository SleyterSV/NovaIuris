<template>

<section class="risk-view">

    <header class="risk-header">

        <div>

            <h2>

                Evaluación de Riesgos

            </h2>

            <p>

                Identificación de riesgos procesales y factores que pueden influir en el resultado del caso.

            </p>

        </div>

    </header>

    <div class="risk-grid">

        <AnalysisSection

            v-for="risk in risks"

            :key="risk.id"

            :title="risk.title"

            :subtitle="risk.subtitle"

            :icon="risk.icon"

            :content="risk.content"

            :confidence="risk.confidence"

            :status="risk.status"

        />

    </div>

    <section class="risk-metrics">

        <div class="metric-card">

            <span class="metric-label">

                Riesgos Detectados

            </span>

            <strong class="metric-value">

                {{ risks.length }}

            </strong>

        </div>

        <div class="metric-card">

            <span class="metric-label">

                Riesgo Promedio

            </span>

            <strong class="metric-value">

                {{ averageRisk }}%

            </strong>

        </div>

        <div class="metric-card">

            <span class="metric-label">

                Probabilidad de Éxito

            </span>

            <strong class="metric-success">

                {{ successProbability }}%

            </strong>

        </div>

        <div class="metric-card">

            <span class="metric-label">

                Nivel de Riesgo

            </span>

            <strong

                class="metric-risk"

                :class="riskLevel.class"

            >

                {{ riskLevel.label }}

            </strong>

        </div>

    </section>

    <section class="risk-summary">

        <header class="summary-header">

            <div>

                <h3>

                    Conclusión Estratégica

                </h3>

                <p>

                    Evaluación integral realizada por NovaCase sobre los principales riesgos identificados.

                </p>

            </div>

            <span

                class="summary-badge"

                :class="riskLevel.class"

            >

                {{ riskLevel.label }}

            </span>

        </header>

        <div class="summary-body">

            <MarkdownRenderer

                :content="summary"

            />

        </div>

        <footer class="summary-footer">

            <div class="summary-item">

                <span>

                    Riesgos Analizados

                </span>

                <strong>

                    {{ risks.length }}

                </strong>

            </div>

            <div class="summary-item">

                <span>

                    Probabilidad de Éxito

                </span>

                <strong>

                    {{ successProbability }}%

                </strong>

            </div>

            <div class="summary-item">

                <span>

                    Evaluación General

                </span>

                <strong

                    :class="riskLevel.class"

                >

                    {{ riskLevel.label }}

                </strong>

            </div>

        </footer>

    </section>

</section>

</template>

<script setup>

import { computed } from "vue"

import AnalysisSection from "@/components/common/AnalysisSection.vue"

import MarkdownRenderer from "@/components/common/MarkdownRenderer.vue"

const props = defineProps({

    risk: {

        type: Object,

        default: () => ({})

    }

})

const risks = computed(() => [

    {

        id: "procedural",

        title: "Riesgos Procesales",

        subtitle: "Aspectos relacionados con el proceso",

        icon: "⚖️",

        content:

            props.risk.procedural ||

            "No se identificaron riesgos procesales.",

        confidence: 82,

        status: "completed"

    },

    {

        id: "evidentiary",

        title: "Riesgos Probatorios",

        subtitle: "Valoración de la evidencia disponible",

        icon: "📄",

        content:

            props.risk.evidentiary ||

            "No se identificaron riesgos probatorios.",

        confidence: 88,

        status: "completed"

    },

    {

        id: "legal",

        title: "Riesgos Jurídicos",

        subtitle: "Interpretación normativa y jurisprudencial",

        icon: "📚",

        content:

            props.risk.legal ||

            "No se identificaron riesgos jurídicos.",

        confidence: 85,

        status: "completed"

    },

    {

        id: "strategic",

        title: "Riesgos Estratégicos",

        subtitle: "Posibles escenarios del litigio",

        icon: "🎯",

        content:

            props.risk.strategic ||

            "No se identificaron riesgos estratégicos.",

        confidence: 80,

        status: "completed"

    }

])

const summary = computed(() =>

    props.risk.summary ||

    `### Evaluación

NovaCase no encontró una evaluación general disponible.`

)

const averageRisk = computed(() => {

    if(

        risks.value.length === 0

    ){

        return 0

    }

    const total = risks.value.reduce(

        (

            sum,

            item

        ) => sum + item.confidence,

        0

    )

    return Math.round(

        total /

        risks.value.length

    )

})

const successProbability = computed(() =>

    Math.max(

        0,

        100 - averageRisk.value

    )

)

const riskLevel = computed(() => {

    if(

        averageRisk.value >= 85

    ){

        return {

            label: "ALTO",

            class: "high"

        }

    }

    if(

        averageRisk.value >= 70

    ){

        return {

            label: "MEDIO",

            class: "medium"

        }

    }

    return {

        label: "BAJO",

        class: "low"

    }

})

</script>

<style scoped>

.risk-view{

    display:flex;

    flex-direction:column;

    gap:32px;

    padding:32px;

    border-radius:24px;

    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    box-shadow: 0 8px 24px rgba(15, 39, 71, 0.06);

}

.risk-header{

    display:flex;

    justify-content:space-between;

    align-items:flex-start;

    gap:20px;

    border-bottom:1px solid #E2E8F0;

    padding-bottom:24px;

}

.risk-header h2{

    margin:0;

    color:#0F2747;

    font-size:1.8rem;

    font-weight:700;

}

.risk-header p{

    margin-top:8px;

    color:#64748B;

    line-height:1.7;

}

.risk-grid{

    display:grid;

    grid-template-columns:

        repeat(

            auto-fit,

            minmax(

                420px,

                1fr

            )

        );

    gap:24px;

}

.risk-metrics{

    display:grid;

    grid-template-columns:

        repeat(

            auto-fit,

            minmax(

                220px,

                1fr

            )

        );

    gap:18px;

}

.metric-card{

    display:flex;

    flex-direction:column;

    gap:10px;

    padding:22px;

    border-radius:18px;

    background:#FFFFFF;

    border:1px solid #E2E8F0;

    transition:

        all .25s ease;

}

.metric-card:hover{

    transform:translateY(-4px);

    border-color:#BFDBFE;

    box-shadow:

        0 12px 30px rgba(37,99,235,.12);

}

.metric-label{

    color:#64748B;

    font-size:.78rem;

    text-transform:uppercase;

    letter-spacing:.5px;

}

.metric-value{

    color:#0F2747;

    font-size:1.5rem;

    font-weight:700;

}

.metric-success{

    color:#15803D;

    font-size:1.2rem;

    font-weight:700;

}

.metric-risk{

    font-size:1.2rem;

    font-weight:700;

}

.metric-risk.high{
    color:#B91C1C;
}

.metric-risk.medium{
    color:#B45309;
}

.metric-risk.low{
    color:#15803D;
}

.risk-summary{

    border-radius:20px;

    background:#FFFFFF;

    border:1px solid #E2E8F0;

    overflow:hidden;

}

.summary-header{

    display:flex;

    justify-content:space-between;

    align-items:center;

    padding:24px;

    border-bottom:1px solid #E2E8F0;

}

.summary-header h3{
    color:#0F2747;
}

.summary-header p{
    color:#64748B;
}

.summary-badge{

    padding:8px 16px;

    border-radius:999px;

    font-size:.75rem;

    font-weight:700;

    text-transform:uppercase;

}

.summary-badge.high{
    background:#FEF2F2;
    color:#B91C1C;
    border:1px solid #FECACA;
}

.summary-badge.medium{
    background:#FFFBEB;
    color:#B45309;
    border:1px solid #FDE68A;
}

.summary-badge.low{
    background:#F0FDF4;
    color:#15803D;
    border:1px solid #BBF7D0;
}

.summary-body{

    padding:26px;

}

.summary-footer{

    display:flex;

    justify-content:space-between;

    gap:24px;

    padding:20px 24px;

    border-top:1px solid #E2E8F0;

    background:#F8FAFC;

}

.summary-item{

    display:flex;

    flex-direction:column;

    gap:6px;

}

.summary-item span{
    color:#64748B;
}

.summary-item strong{
    color:#0F2747;
}

.summary-item strong.high{
    color:#B91C1C;
}

.summary-item strong.medium{
    color:#B45309;
}

.summary-item strong.low{
    color:#15803D;
}

/* =====================================================
   RESPONSIVE
===================================================== */

@media (max-width:1200px){

    .risk-grid{

        grid-template-columns:1fr;

    }

}

@media (max-width:992px){

    .risk-view{

        padding:26px;

    }

    .risk-metrics{

        grid-template-columns:

            repeat(

                2,

                1fr

            );

    }

}

@media (max-width:768px){

    .risk-view{

        padding:20px;

        gap:24px;

    }

    .risk-header{

        flex-direction:column;

        align-items:flex-start;

        gap:18px;

    }

    .risk-grid{

        grid-template-columns:1fr;

    }

    .risk-metrics{

        grid-template-columns:1fr;

        gap:16px;

    }

    .summary-header{

        flex-direction:column;

        align-items:flex-start;

        gap:16px;

    }

    .summary-footer{

        flex-direction:column;

        gap:18px;

    }

}

@media (max-width:576px){

    .risk-view{

        padding:16px;

    }

    .risk-header h2{

        font-size:1.45rem;

    }

    .metric-value,

    .metric-success,

    .metric-risk{

        font-size:1.1rem;

    }

    .summary-body{

        padding:18px;

    }

    .summary-header{

        padding:18px;

    }

    .summary-footer{

        padding:18px;

    }

}

/* =====================================================
   ANIMACIONES
===================================================== */

.risk-view{

    animation:

        riskFadeIn

        .45s ease;

}

.risk-header{

    animation:

        headerSlideDown

        .45s ease;

}

.risk-grid > *{

    animation:

        cardAppear

        .55s ease;

}

.risk-grid > *:nth-child(2){

    animation-delay:.05s;

}

.risk-grid > *:nth-child(3){

    animation-delay:.10s;

}

.risk-grid > *:nth-child(4){

    animation-delay:.15s;

}

.metric-card{

    animation:

        metricAppear

        .60s ease;

}

.metric-card:nth-child(2){

    animation-delay:.05s;

}

.metric-card:nth-child(3){

    animation-delay:.10s;

}

.metric-card:nth-child(4){

    animation-delay:.15s;

}

.risk-summary{

    animation:

        summaryAppear

        .70s ease;

}

.metric-card:hover{

    box-shadow:

        0 12px 30px rgba(37,99,235,.14);

}

.summary-badge{

    transition:

        transform .25s ease;

}

.summary-header:hover .summary-badge{

    transform:scale(1.06);

}

@keyframes riskFadeIn{

    from{

        opacity:0;

        transform:translateY(18px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

@keyframes headerSlideDown{

    from{

        opacity:0;

        transform:translateY(-12px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

@keyframes cardAppear{

    from{

        opacity:0;

        transform:translateY(16px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

@keyframes metricAppear{

    from{

        opacity:0;

        transform:scale(.96);

    }

    to{

        opacity:1;

        transform:scale(1);

    }

}

@keyframes summaryAppear{

    from{

        opacity:0;

        transform:translateY(20px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

</style>

