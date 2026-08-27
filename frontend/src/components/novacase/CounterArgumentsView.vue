<template>

<section class="counter-view">

    <header class="counter-header">

        <div>

            <h2>

                Contraargumentos

            </h2>

            <p>

                Posibles argumentos que podría plantear la parte contraria durante el proceso.

            </p>

        </div>

    </header>

    <div class="counter-grid">

        <AnalysisSection

            v-for="argument in counterArguments"

            :key="argument.id"

            :title="argument.title"

            :subtitle="argument.subtitle"

            :icon="argument.icon"

            :content="argument.content"

            :confidence="argument.confidence"

            :status="argument.status"

        />

    </div>

    <section class="counter-summary">

        <header class="summary-header">

            <div>

                <h3>

                    Evaluación Estratégica

                </h3>

                <p>

                    Síntesis de los principales escenarios de defensa que podrían presentarse.

                </p>

            </div>

        </header>

        <MarkdownRenderer

            :content="summary"

        />

    </section>

</section>

</template>

<script setup>

import { computed } from "vue"

import AnalysisSection from "@/components/common/AnalysisSection.vue"

import MarkdownRenderer from "@/components/common/MarkdownRenderer.vue"

const props = defineProps({

    counterArguments: {

        type: Object,

        default: () => ({})

    }

})

const counterArguments = computed(() => [

    {

        id: "procedural",

        title: "Excepciones Procesales",

        subtitle: "Posibles cuestionamientos al procedimiento",

        icon: "⚖️",

        content:

            props.counterArguments.procedural ||

            "No se identificaron excepciones procesales relevantes.",

        confidence: 89,

        status: "completed"

    },

    {

        id: "evidence",

        title: "Cuestionamiento Probatorio",

        subtitle: "Debilidades que podrían alegarse sobre la evidencia",

        icon: "📄",

        content:

            props.counterArguments.evidence ||

            "No se identificaron cuestionamientos probatorios relevantes.",

        confidence: 91,

        status: "completed"

    },

    {

        id: "legal",

        title: "Interpretación Jurídica",

        subtitle: "Normas que podrían ser interpretadas en contra",

        icon: "📚",

        content:

            props.counterArguments.legal ||

            "No se identificaron interpretaciones jurídicas adversas.",

        confidence: 87,

        status: "completed"

    },

    {

        id: "jurisprudence",

        title: "Jurisprudencia Contraria",

        subtitle: "Precedentes favorables a la contraparte",

        icon: "🏛️",

        content:

            props.counterArguments.jurisprudence ||

            "No se identificó jurisprudencia contraria relevante.",

        confidence: 85,

        status: "completed"

    }

])

const summary = computed(() =>

    props.counterArguments.summary ||

    `### Evaluación Estratégica

NovaCase no encontró una evaluación estratégica disponible para este caso.`

)

</script>

<style scoped>

.counter-view{

    display:flex;

    flex-direction:column;

    gap:32px;

    padding:32px;

    border-radius:24px;

    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    box-shadow: 0 8px 24px rgba(15, 39, 71, 0.06);

}

.counter-header{

    display:flex;

    justify-content:space-between;

    align-items:flex-start;

    gap:20px;

    border-bottom:1px solid rgba(255,255,255,.08);

    padding-bottom:24px;

}

.counter-header h2{

    margin:0;

    color:#F8FAFC;

    font-size:1.8rem;

    font-weight:700;

}

.counter-header p{

    margin-top:8px;

    color:#94A3B8;

    line-height:1.7;

}

.counter-grid{

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

.counter-summary{

    border-radius:20px;

    background:rgba(255,255,255,.03);

    border:1px solid rgba(255,255,255,.06);

    overflow:hidden;

}

.summary-header{

    display:flex;

    justify-content:space-between;

    align-items:flex-start;

    gap:20px;

    padding:24px;

    border-bottom:1px solid rgba(255,255,255,.06);

}

.summary-header h3{

    margin:0;

    color:#F8FAFC;

    font-size:1.2rem;

    font-weight:700;

}

.summary-header p{

    margin-top:8px;

    color:#94A3B8;

    line-height:1.6;

}

.counter-summary :deep(.markdown-body){

    padding:24px;

}

.counter-summary:hover{

    border-color:rgba(37,99,235,.35);

    box-shadow:

        0 12px 28px rgba(37,99,235,.12);

    transition:

        all .25s ease;

}

.counter-grid > *{

    transition:

        transform .25s ease,

        box-shadow .25s ease;

}

.counter-grid > *:hover{

    transform:translateY(-4px);

}

/* =====================================================
   RESPONSIVE
===================================================== */

@media (max-width:1200px){

    .counter-grid{

        grid-template-columns:1fr;

    }

}

@media (max-width:992px){

    .counter-view{

        padding:26px;

    }

}

@media (max-width:768px){

    .counter-view{

        padding:20px;

        gap:24px;

    }

    .counter-header{

        flex-direction:column;

        align-items:flex-start;

        gap:18px;

    }

    .summary-header{

        flex-direction:column;

        align-items:flex-start;

        gap:16px;

    }

    .counter-summary :deep(.markdown-body){

        padding:20px;

    }

}

@media (max-width:576px){

    .counter-view{

        padding:16px;

    }

    .counter-header h2{

        font-size:1.45rem;

    }

    .counter-header p{

        font-size:.9rem;

    }

    .summary-header{

        padding:18px;

    }

    .counter-summary :deep(.markdown-body){

        padding:18px;

    }

}

/* =====================================================
   ANIMACIONES
===================================================== */

.counter-view{

    animation:

        counterFadeIn

        .45s ease;

}

.counter-header{

    animation:

        headerSlideDown

        .45s ease;

}

.counter-grid > *{

    animation:

        cardAppear

        .55s ease;

}

.counter-grid > *:nth-child(2){

    animation-delay:.05s;

}

.counter-grid > *:nth-child(3){

    animation-delay:.10s;

}

.counter-grid > *:nth-child(4){

    animation-delay:.15s;

}

.counter-summary{

    animation:

        summaryAppear

        .70s ease;

}

.counter-summary:hover{

    transform:translateY(-2px);

}

@keyframes counterFadeIn{

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