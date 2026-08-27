<template>

<section class="strategy-view">

    <header class="strategy-header">

        <div>

            <h2>

                Estrategia Jurídica

            </h2>

            <p>

                Recomendaciones estratégicas generadas por NovaCase para maximizar las probabilidades de éxito.

            </p>

        </div>

    </header>

    <div class="strategy-grid">

        <AnalysisSection

            v-for="item in strategies"

            :key="item.id"

            :title="item.title"

            :subtitle="item.subtitle"

            :icon="item.icon"

            :content="item.content"

            :confidence="item.confidence"

            :status="item.status"

        />

    </div>

    <section class="strategy-summary">

        <header class="summary-header">

            <div>

                <h3>

                    Conclusión Estratégica

                </h3>

                <p>

                    Síntesis de la estrategia recomendada para el caso.

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

    strategy: {

        type: Object,

        default: () => ({})

    }

})

const strategies = computed(() => [

    {

        id: "objective",

        title: "Objetivo Principal",

        subtitle: "Resultado jurídico esperado",

        icon: "🎯",

        content:

            props.strategy.objective ||

            "No se definió un objetivo estratégico.",

        confidence: 96,

        status: "completed"

    },

    {

        id: "strategy",

        title: "Estrategia Recomendada",

        subtitle: "Línea principal de actuación",

        icon: "⚖️",

        content:

            props.strategy.strategy ||

            "No se generó una estrategia principal.",

        confidence: 94,

        status: "completed"

    },

    {

        id: "actions",

        title: "Actuaciones Sugeridas",

        subtitle: "Acciones prioritarias",

        icon: "📋",

        content:

            props.strategy.actions ||

            "No se recomendaron actuaciones específicas.",

        confidence: 92,

        status: "completed"

    },

    {

        id: "execution",

        title: "Riesgos de Ejecución",

        subtitle: "Aspectos que requieren seguimiento",

        icon: "⚠️",

        content:

            props.strategy.execution ||

            "No se identificaron riesgos de ejecución.",

        confidence: 89,

        status: "completed"

    },

    {

        id: "recommendations",

        title: "Recomendaciones Finales",

        subtitle: "Buenas prácticas para fortalecer el caso",

        icon: "💡",

        content:

            props.strategy.recommendations ||

            "No se generaron recomendaciones adicionales.",

        confidence: 95,

        status: "completed"

    }

])

const summary = computed(() =>

    props.strategy.summary ||

`# Conclusión Estratégica

NovaCase no generó una estrategia final para este caso.

Cuando el backend esté conectado, aquí aparecerá la estrategia jurídica consolidada elaborada por el sistema.`

)

</script>

<style scoped>

.strategy-view{

    display:flex;

    flex-direction:column;

    gap:32px;

    padding:32px;

    border-radius:24px;

    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    box-shadow: 0 8px 24px rgba(15, 39, 71, 0.06);

}

.strategy-header{

    display:flex;

    justify-content:space-between;

    align-items:flex-start;

    gap:20px;

    border-bottom:1px solid rgba(255,255,255,.08);

    padding-bottom:24px;

}

.strategy-header h2{

    margin:0;

    color:#F8FAFC;

    font-size:1.8rem;

    font-weight:700;

}

.strategy-header p{

    margin-top:8px;

    color:#94A3B8;

    line-height:1.7;

}

.strategy-grid{

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

.strategy-summary{

    border-radius:20px;

    overflow:hidden;

    background:rgba(255,255,255,.03);

    border:1px solid rgba(255,255,255,.06);

    transition:

        all .30s ease;

}

.strategy-summary:hover{

    border-color:rgba(37,99,235,.35);

    box-shadow:

        0 16px 36px rgba(37,99,235,.14);

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

    line-height:1.7;

}

.strategy-summary :deep(.markdown-body){

    padding:26px;

}

.strategy-grid > *{

    transition:

        transform .28s ease,

        box-shadow .28s ease;

}

.strategy-grid > *:hover{

    transform:translateY(-4px);

}

.strategy-summary{

    position:relative;

}

.strategy-summary::before{

    content:"";

    position:absolute;

    top:0;

    left:0;

    width:100%;

    height:4px;

    background:linear-gradient(

        90deg,

        #2563EB,

        #3B82F6,

        #60A5FA

    );

}

/* =====================================================
   RESPONSIVE
===================================================== */

@media (max-width:1200px){

    .strategy-grid{

        grid-template-columns:1fr;

    }

}

@media (max-width:992px){

    .strategy-view{

        padding:26px;

    }

}

@media (max-width:768px){

    .strategy-view{

        padding:20px;

        gap:24px;

    }

    .strategy-header{

        flex-direction:column;

        align-items:flex-start;

        gap:18px;

    }

    .summary-header{

        flex-direction:column;

        align-items:flex-start;

        gap:16px;

    }

    .strategy-summary :deep(.markdown-body){

        padding:20px;

    }

}

@media (max-width:576px){

    .strategy-view{

        padding:16px;

    }

    .strategy-header h2{

        font-size:1.45rem;

    }

    .strategy-header p{

        font-size:.9rem;

    }

    .summary-header{

        padding:18px;

    }

    .strategy-summary :deep(.markdown-body){

        padding:18px;

    }

}

/* =====================================================
   ANIMACIONES
===================================================== */

.strategy-view{

    animation:

        strategyFadeIn

        .45s ease;

}

.strategy-header{

    animation:

        headerSlideDown

        .45s ease;

}

.strategy-grid > *{

    animation:

        cardAppear

        .55s ease;

}

.strategy-grid > *:nth-child(2){

    animation-delay:.05s;

}

.strategy-grid > *:nth-child(3){

    animation-delay:.10s;

}

.strategy-grid > *:nth-child(4){

    animation-delay:.15s;

}

.strategy-grid > *:nth-child(5){

    animation-delay:.20s;

}

.strategy-summary{

    animation:

        summaryAppear

        .70s ease;

}

.strategy-summary:hover{

    transform:translateY(-2px);

}

@keyframes strategyFadeIn{

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