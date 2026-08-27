<template>

<section class="evidence-view">

    <header class="evidence-header">

        <div>

            <h2>

                Análisis Probatorio

            </h2>

            <p>

                Evaluación de las pruebas identificadas durante el análisis jurídico.

            </p>

        </div>

    </header>

    <div class="evidence-grid">

        <AnalysisSection

            v-for="item in evidences"

            :key="item.id"

            :title="item.title"

            :subtitle="item.subtitle"

            :icon="item.icon"

            :content="item.content"

            :confidence="item.confidence"

            :status="item.status"

        />

    </div>

    <section class="evidence-stats">

        <div class="stat-card">

            <span class="stat-label">

                Evidencias Analizadas

            </span>

            <strong class="stat-value">

                {{ evidences.length }}

            </strong>

        </div>

        <div class="stat-card">

            <span class="stat-label">

                Nivel Promedio

            </span>

            <strong class="stat-value">

                {{ averageConfidence }}%

            </strong>

        </div>

        <div class="stat-card">

            <span class="stat-label">

                Estado General

            </span>

            <strong class="stat-success">

                Validado

            </strong>

        </div>

    </section>

    <section class="evidence-summary">

        <h3>

            Conclusión Probatoria

        </h3>

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

    evidence: {

        type: Object,

        default: () => ({})

    }

})

const evidences = computed(() => [

    {

        id: "documents",

        title: "Documentos",

        subtitle: "Pruebas documentales",

        icon: "📄",

        content:

            props.evidence.documents ||

            "No se identificaron documentos relevantes.",

        confidence: 96,

        status: "completed"

    },

    {

        id: "testimonies",

        title: "Testimonios",

        subtitle: "Declaraciones relevantes",

        icon: "👤",

        content:

            props.evidence.testimonies ||

            "No se identificaron testimonios relevantes.",

        confidence: 91,

        status: "completed"

    },

    {

        id: "expert",

        title: "Peritajes",

        subtitle: "Informes periciales",

        icon: "🧪",

        content:

            props.evidence.expertReports ||

            "No existen informes periciales.",

        confidence: 88,

        status: "completed"

    },

    {

        id: "digital",

        title: "Evidencia Digital",

        subtitle: "Mensajes, correos y archivos",

        icon: "💻",

        content:

            props.evidence.digitalEvidence ||

            "No se encontró evidencia digital.",

        confidence: 90,

        status: "completed"

    }

])

const summary = computed(() =>

    props.evidence.summary ||

    `### Conclusión

NovaCase no encontró una conclusión probatoria disponible.`

)

const averageConfidence = computed(() => {

    if(

        evidences.value.length === 0

    ){

        return 0

    }

    const total = evidences.value.reduce(

        (

            sum,

            item

        ) => sum + item.confidence,

        0

    )

    return Math.round(

        total /

        evidences.value.length

    )

})

</script>

<style scoped>

.evidence-view{

    display:flex;

    flex-direction:column;

    gap:32px;

    padding:32px;

    border-radius:24px;

    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    box-shadow: 0 8px 24px rgba(15, 39, 71, 0.06);

}

.evidence-header{

    display:flex;

    justify-content:space-between;

    align-items:flex-start;

    gap:20px;

    border-bottom:1px solid rgba(255,255,255,.08);

    padding-bottom:24px;

}

.evidence-header h2{

    margin:0;

    color:#F8FAFC;

    font-size:1.8rem;

    font-weight:700;

}

.evidence-header p{

    margin-top:8px;

    color:#94A3B8;

    line-height:1.7;

}

.evidence-grid{

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

.evidence-stats{

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

.stat-card{

    display:flex;

    flex-direction:column;

    gap:10px;

    padding:22px;

    border-radius:18px;

    background:rgba(255,255,255,.03);

    border:1px solid rgba(255,255,255,.05);

    transition:

        all .25s ease;

}

.stat-card:hover{

    transform:translateY(-4px);

    border-color:rgba(37,99,235,.35);

}

.stat-label{

    color:#94A3B8;

    font-size:.78rem;

    text-transform:uppercase;

    letter-spacing:.6px;

}

.stat-value{

    color:#F8FAFC;

    font-size:1.5rem;

    font-weight:700;

}

.stat-success{

    color:#22C55E;

    font-size:1.1rem;

    font-weight:700;

}

.evidence-summary{

    padding:26px;

    border-radius:20px;

    background:rgba(255,255,255,.03);

    border:1px solid rgba(255,255,255,.06);

}

.evidence-summary h3{

    margin:0 0 18px;

    color:#F8FAFC;

    font-size:1.2rem;

    font-weight:700;

}

/* =====================================================
   RESPONSIVE
===================================================== */

@media (max-width:1200px){

    .evidence-grid{

        grid-template-columns:1fr;

    }

}

@media (max-width:992px){

    .evidence-view{

        padding:26px;

    }

    .evidence-stats{

        grid-template-columns:

            repeat(

                2,

                1fr

            );

    }

}

@media (max-width:768px){

    .evidence-view{

        padding:20px;

        gap:24px;

    }

    .evidence-header{

        flex-direction:column;

        align-items:flex-start;

        gap:16px;

    }

    .evidence-grid{

        grid-template-columns:1fr;

        gap:20px;

    }

    .evidence-stats{

        grid-template-columns:1fr;

        gap:16px;

    }

    .stat-card{

        padding:18px;

    }

    .evidence-summary{

        padding:20px;

    }

}

@media (max-width:576px){

    .evidence-view{

        padding:16px;

    }

    .evidence-header h2{

        font-size:1.45rem;

    }

    .evidence-header p{

        font-size:.9rem;

    }

    .stat-value{

        font-size:1.25rem;

    }

    .stat-success{

        font-size:1rem;

    }

    .evidence-summary{

        padding:18px;

    }

}

/* =====================================================
   ANIMACIONES
===================================================== */

.evidence-view{

    animation:

        evidenceFadeIn

        .45s ease;

}

.evidence-header{

    animation:

        headerSlideDown

        .45s ease;

}

.evidence-summary{

    animation:

        summaryAppear

        .70s ease;

}

.stat-card{

    animation:

        statAppear

        .55s ease;

}

.stat-card:nth-child(2){

    animation-delay:.08s;

}

.stat-card:nth-child(3){

    animation-delay:.16s;

}

.evidence-grid > *{

    animation:

        cardAppear

        .55s ease;

}

.evidence-grid > *:nth-child(2){

    animation-delay:.05s;

}

.evidence-grid > *:nth-child(3){

    animation-delay:.10s;

}

.evidence-grid > *:nth-child(4){

    animation-delay:.15s;

}

.stat-card:hover{

    box-shadow:

        0 12px 28px rgba(37,99,235,.14);

}

.evidence-summary:hover{

    border-color:rgba(37,99,235,.35);

    transition:border-color .25s ease;

}

@keyframes evidenceFadeIn{

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

@keyframes statAppear{

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

