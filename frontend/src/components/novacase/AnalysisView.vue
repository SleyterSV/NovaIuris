<template>

<section class="analysis-view">

    <header class="analysis-header">

        <div>

            <h2>

                Análisis Jurídico

            </h2>

            <p>

                Evaluación estructurada del caso realizada por NovaCase.

            </p>

        </div>

    </header>

    <section class="analysis-grid">

        <article

            v-for="section in sections"

            :key="section.id"

            class="analysis-card"

        >

            <header class="card-header">

                <div class="card-title">

                    <span class="card-icon">

                        {{ section.icon }}

                    </span>

                    <div>

                        <h3>

                            {{ section.title }}

                        </h3>

                        <small>

                            Análisis generado por NovaCase

                        </small>

                    </div>

                </div>

                <span class="status-badge">

                    Completado

                </span>

            </header>

            <section class="card-body">

                <MarkdownRenderer

                    :content="section.content"

                />

            </section>

        </article>

    </section>

    <section class="analysis-process">

        <header class="process-header">

            <h3>

                Proceso de Análisis

            </h3>

            <p>

                Etapas ejecutadas por NovaCase durante la evaluación del caso.

            </p>

        </header>

        <div class="process-timeline">

            <div

                v-for="step in processSteps"

                :key="step.id"

                class="process-step"

            >

                <div class="process-icon">

                    {{ step.icon }}

                </div>

                <div class="process-content">

                    <h4>

                        {{ step.title }}

                    </h4>

                    <p>

                        {{ step.description }}

                    </p>

                </div>

                <div class="process-status">

                    ✓

                </div>

            </div>

        </div>

    </section>

</section>

</template>

<script setup>

import { computed } from "vue"

import MarkdownRenderer from "@/components/common/MarkdownRenderer.vue"

const props = defineProps({

    analysis: {

        type: Object,

        required: true

    }

})

const sections = computed(() => [

    {

        id: "summary",

        title: "Resumen Ejecutivo",

        icon: "📌",

        content: props.analysis.summary ||

            "No se generó un resumen ejecutivo."

    },

    {

        id: "facts",

        title: "Hechos Relevantes",

        icon: "⚖️",

        content: props.analysis.facts ||

            "No se identificaron hechos relevantes."

    },

    {

        id: "issues",

        title: "Problemas Jurídicos",

        icon: "📚",

        content: props.analysis.issues ||

            "No se identificaron problemas jurídicos."

    },

    {

        id: "law",

        title: "Normativa Aplicable",

        icon: "📖",

        content: props.analysis.law ||

            "No se encontró normativa aplicable."

    },

    {

        id: "jurisprudence",

        title: "Jurisprudencia",

        icon: "🏛️",

        content: props.analysis.jurisprudence ||

            "No se encontraron precedentes relevantes."

    },

    {

        id: "observations",

        title: "Observaciones",

        icon: "💡",

        content: props.analysis.observations ||

            "No existen observaciones adicionales."

    }

])

const processSteps = [

    {

        id: 1,

        icon: "📥",

        title: "Recepción del Caso",

        description:

            "Se recibió la descripción del caso para iniciar el análisis."

    },

    {

        id: 2,

        icon: "⚖️",

        title: "Identificación de Hechos",

        description:

            "Se identificaron los hechos jurídicamente relevantes."

    },

    {

        id: 3,

        icon: "📚",

        title: "Problemas Jurídicos",

        description:

            "Se determinaron las principales controversias legales."

    },

    {

        id: 4,

        icon: "📖",

        title: "Normativa Aplicable",

        description:

            "Se localizaron las normas relacionadas con el caso."

    },

    {

        id: 5,

        icon: "🏛️",

        title: "Jurisprudencia",

        description:

            "Se analizaron precedentes relevantes."

    },

    {

        id: 6,

        icon: "📄",

        title: "Informe Jurídico",

        description:

            "Se generó el informe final para el usuario."

    }

]

</script>

<style scoped>

.analysis-view{

    display:flex;

    flex-direction:column;

    gap:32px;

    padding:32px;

    border-radius:24px;

    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    box-shadow: 0 8px 24px rgba(15, 39, 71, 0.06);

}

.analysis-header{

    display:flex;

    justify-content:space-between;

    align-items:flex-start;

    gap:20px;

    border-bottom:1px solid #E2E8F0;

    padding-bottom:22px;

}

.analysis-header h2{

    margin:0;

    color:#0F2747;

    font-size:1.8rem;

    font-weight:700;

}

.analysis-header p{

    margin-top:8px;

    color:#64748B;

    line-height:1.7;

}

.analysis-grid{

    display:grid;

    grid-template-columns:

        repeat(

            auto-fit,

            minmax(

                380px,

                1fr

            )

        );

    gap:24px;

}

.analysis-card{
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:20px;
    overflow:hidden;
    transition:
        transform .25s ease,
        border-color .25s ease,
        box-shadow .25s ease;
}

.analysis-card:hover{

    transform:translateY(-4px);

    border-color:#BFDBFE;

    box-shadow:

        0 12px 30px rgba(37,99,235,.12);

}

.card-header{

    display:flex;

    justify-content:space-between;

    align-items:center;

    padding:20px 24px;

    border-bottom:1px solid #E2E8F0;

}

.card-title{

    display:flex;

    align-items:center;

    gap:14px;

}

.card-icon{
    width:48px;
    height:48px;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:14px;
    background:#EFF6FF;
    border:1px solid #DBEAFE;
    font-size:1.35rem;
}

.card-title h3{

    margin:0;

    color:#0F2747;

    font-size:1.05rem;

}

.card-title small{

    color:#64748B;

}

.status-badge{

    padding:6px 12px;

    border-radius:999px;

    background:#F0FDF4;

    color:#15803D;

    border:1px solid #BBF7D0;

    font-size:.75rem;

    font-weight:700;

}

.card-body{

    padding:24px;

}

.analysis-process{

    margin-top:12px;

}

.process-header h3{

    margin:0;

    color:#0F2747;

}

.process-header p{

    margin-top:8px;

    color:#64748B;

}

.process-timeline{

    margin-top:24px;

    display:flex;

    flex-direction:column;

    gap:18px;

}

.process-step{

    display:grid;

    grid-template-columns:

        60px

        1fr

        40px;

    gap:18px;

    align-items:center;

    padding:18px;

    border-radius:18px;

    background:#FFFFFF;

    border:1px solid #E2E8F0;

    transition:

        all .25s ease;

}

.process-step:hover{

    transform:translateX(6px);

    border-color:#BFDBFE;

}

.process-icon{

    width:52px;

    height:52px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:14px;

    background:#EFF6FF;

    border:1px solid #DBEAFE;

    color:#2563EB;

    font-size:1.35rem;

}

.process-content h4{

    margin:0;

    color:#0F2747;

}

.process-content p{

    margin-top:6px;

    color:#64748B;

    line-height:1.6;

}

.process-status{

    width:34px;

    height:34px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#15803D;
    
    color:#FFFFFF;

    font-weight:700;

}

/* ===========================
   ANIMACIONES
=========================== */

.analysis-view{

    animation:

        analysisFadeIn

        .45s ease;

}

.analysis-card{

    animation:

        cardAppear

        .5s ease;

}

.analysis-card:nth-child(2){

    animation-delay:.05s;

}

.analysis-card:nth-child(3){

    animation-delay:.10s;

}

.analysis-card:nth-child(4){

    animation-delay:.15s;

}

.analysis-card:nth-child(5){

    animation-delay:.20s;

}

.analysis-card:nth-child(6){

    animation-delay:.25s;

}

@keyframes analysisFadeIn{

    from{

        opacity:0;

        transform:translateY(18px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

@keyframes cardAppear{

    from{

        opacity:0;

        transform:translateY(15px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

/* ===========================
   RESPONSIVE
=========================== */

@media (max-width:1100px){

    .analysis-grid{

        grid-template-columns:1fr;

    }

}

@media (max-width:768px){

    .analysis-view{

        padding:22px;

        gap:24px;

    }

    .analysis-header{

        flex-direction:column;

        align-items:flex-start;

    }

    .card-header{

        flex-direction:column;

        align-items:flex-start;

        gap:14px;

    }

    .process-step{

        grid-template-columns:1fr;

        text-align:center;

    }

    .process-icon{

        margin:auto;

    }

    .process-status{

        margin:auto;

    }

}

@media (max-width:480px){

    .analysis-view{

        padding:16px;

    }

    .analysis-header h2{

        font-size:1.45rem;

    }

    .card-body{

        padding:18px;

    }

}

</style>

