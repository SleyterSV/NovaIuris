<template>

<section class="strategy-view">

    <!-- =====================================================
         HEADER
    ====================================================== -->

    <header class="strategy-header">

        <div class="strategy-heading">

            <div class="strategy-eyebrow">

                <span class="eyebrow-line"></span>

                ANÁLISIS ESTRATÉGICO

            </div>

            <h2>
                Estrategia Jurídica
            </h2>

            <p>
                Recomendaciones estratégicas generadas por NovaCase
                para orientar la actuación jurídica y fortalecer
                la posición del caso.
            </p>

        </div>

        <div class="strategy-status">

            <span class="status-dot"></span>

            ESTRATEGIA ANALIZADA

        </div>

    </header>


    <!-- =====================================================
         INTRODUCCIÓN
    ====================================================== -->

    <div class="strategy-intro">

        <div class="intro-icon">
            <span>◆</span>
        </div>

        <div class="intro-content">

            <strong>
                Orientación estratégica del caso
            </strong>

            <span>
                NovaCase consolida los principales objetivos,
                actuaciones, riesgos y recomendaciones derivados
                del análisis jurídico.
            </span>

        </div>

    </div>


    <!-- =====================================================
         MATRIZ ESTRATÉGICA
    ====================================================== -->

    <div class="strategy-section-header">

        <div>

            <span class="section-kicker">
                MATRIZ ESTRATÉGICA
            </span>

            <h3>
                Líneas principales de actuación
            </h3>

        </div>

        <span class="strategy-count">
            {{ strategies.length }} áreas analizadas
        </span>

    </div>


    <!-- =====================================================
         ESTRATEGIAS
    ====================================================== -->

    <div class="strategy-grid">

        <AnalysisSection
            v-for="item in strategies"
            :key="item.id"
            :title="item.title"
            :subtitle="item.subtitle"
            :icon="item.icon"
            :content="item.content"
            :status="item.status"
        />

    </div>


    <!-- =====================================================
         CONCLUSIÓN ESTRATÉGICA
    ====================================================== -->

    <section class="strategy-summary">

        <header class="summary-header">

            <div class="summary-heading">

                <div class="summary-icon">
                    <span>◆</span>
                </div>

                <div>

                    <span class="section-kicker">
                        SÍNTESIS ESTRATÉGICA
                    </span>

                    <h3>
                        Conclusión Estratégica
                    </h3>

                    <p>
                        Síntesis consolidada de la estrategia
                        recomendada para el caso.
                    </p>

                </div>

            </div>

            <div class="summary-label">

                <span class="summary-label-dot"></span>

                ANÁLISIS NOVACASE

            </div>

        </header>


        <div class="summary-body">

            <MarkdownRenderer
                :content="summary"
            />

        </div>


        <footer class="summary-footer">

            <div class="summary-footer-label">

                <span class="footer-line"></span>

                LECTURA ESTRATÉGICA

            </div>

            <span class="footer-note">
                Evaluación generada a partir de la información
                disponible del caso.
            </span>

        </footer>

    </section>


    <!-- =====================================================
         AVISO PROFESIONAL
    ====================================================== -->

    <div class="strategy-disclaimer">

        <span class="disclaimer-icon">
            i
        </span>

        <p>
            Las recomendaciones estratégicas generadas por NovaCase
            constituyen una herramienta de apoyo al análisis jurídico
            y deben ser evaluadas considerando las circunstancias
            específicas del caso y el criterio profesional.
        </p>

    </div>

</section>

</template>


<script setup>

import { computed } from "vue"

import AnalysisSection
    from "@/components/common/AnalysisSection.vue"

import MarkdownRenderer
    from "@/components/common/MarkdownRenderer.vue"


const props = defineProps({

    strategy: {

        type: Object,

        default: () => ({})

    }

})


/* ============================================================
   MATRIZ ESTRATÉGICA
============================================================ */

const strategies = computed(() => [

    {

        id: "objective",

        title: "Objetivo Principal",

        subtitle:
            "Resultado jurídico esperado",

        icon: "🎯",

        content:

            props.strategy.objective ||

            "No identificado con la información disponible.",

        status: "completed"

    },

    {

        id: "strategy",

        title: "Estrategia Recomendada",

        subtitle:
            "Línea principal de actuación",

        icon: "⚖️",

        content:

            props.strategy.strategy ||

            "No identificado con la información disponible.",

        status: "completed"

    },

    {

        id: "actions",

        title: "Actuaciones Sugeridas",

        subtitle:
            "Acciones prioritarias",

        icon: "📋",

        content:

            props.strategy.actions ||

            "No identificado con la información disponible.",

        status: "completed"

    },

    {

        id: "execution",

        title: "Riesgos procesales",

        subtitle:
            "Aspectos que requieren seguimiento",

        icon: "⚠️",

        content:

            props.strategy.execution ||

            "No identificado con la información disponible.",

        status: "completed"

    },

    {

        id: "recommendations",

        title: "Recomendaciones Finales",

        subtitle:
            "Buenas prácticas para fortalecer el caso",

        icon: "💡",

        content:

            props.strategy.recommendations ||

            "No identificado con la información disponible.",

        status: "completed"

    }

])


/* ============================================================
   RESUMEN
============================================================ */

const summary = computed(() =>

    props.strategy.summary ||

`# Conclusión Estratégica

NovaCase no generó una estrategia final para este caso.

Cuando el backend esté conectado, aquí aparecerá la estrategia jurídica consolidada elaborada por el sistema.`

)

</script>


<style scoped>

/* ============================================================
   VARIABLES
============================================================ */

.strategy-view {

    --nova-navy: #0F2747;

    --nova-blue: #2563EB;

    --nova-blue-hover: #1D4ED8;

    --nova-blue-light: #EFF6FF;

    --nova-blue-border: #BFDBFE;

    --nova-text: #334155;

    --nova-muted: #64748B;

    --nova-soft: #F8FAFC;

    --nova-border: #E2E8F0;

    --nova-white: #FFFFFF;

    display: flex;

    flex-direction: column;

    gap: 28px;

    padding: 32px;

    background: var(--nova-white);

    border: 1px solid var(--nova-border);

    border-radius: 24px;

    box-shadow:
        0 8px 24px rgba(15, 39, 71, .06);

    animation:
        strategyFadeIn
        .45s
        ease
        both;

}


/* ============================================================
   HEADER
============================================================ */

.strategy-header {

    display: flex;

    justify-content: space-between;

    align-items: flex-start;

    gap: 24px;

    padding-bottom: 24px;

    border-bottom:
        1px solid var(--nova-border);

}


.strategy-heading {

    display: flex;

    flex-direction: column;

    gap: 8px;

}


.strategy-eyebrow {

    display: flex;

    align-items: center;

    gap: 9px;

    margin-bottom: 2px;

    color: var(--nova-blue);

    font-size: .72rem;

    font-weight: 800;

    letter-spacing: .12em;

}


.eyebrow-line {

    width: 28px;

    height: 2px;

    flex-shrink: 0;

    border-radius: 999px;

    background:
        var(--nova-blue);

}


.strategy-header h2 {

    margin: 0;

    color: var(--nova-navy);

    font-size: 1.8rem;

    line-height: 1.2;

    font-weight: 750;

    letter-spacing: -.025em;

}


.strategy-header p {

    max-width: 820px;

    margin: 0;

    color: var(--nova-muted);

    font-size: .95rem;

    line-height: 1.7;

}


/* ============================================================
   STATUS
============================================================ */

.strategy-status {

    display: inline-flex;

    align-items: center;

    gap: 8px;

    flex-shrink: 0;

    padding: 8px 12px;

    border:
        1px solid #D1FAE5;

    border-radius: 999px;

    background: #F0FDF4;

    color: #15803D;

    font-size: .68rem;

    font-weight: 800;

    letter-spacing: .06em;

}


.status-dot {

    width: 7px;

    height: 7px;

    flex-shrink: 0;

    border-radius: 50%;

    background: #16A34A;

    box-shadow:
        0 0 0 3px rgba(22, 163, 74, .10);

}


/* ============================================================
   INTRODUCCIÓN
============================================================ */

.strategy-intro {

    display: flex;

    align-items: center;

    gap: 16px;

    padding: 18px 20px;

    border:
        1px solid var(--nova-blue-border);

    border-radius: 16px;

    background:
        linear-gradient(
            135deg,
            #F8FBFF 0%,
            #EFF6FF 100%
        );

}


.intro-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 42px;

    height: 42px;

    flex-shrink: 0;

    border:
        1px solid var(--nova-blue-border);

    border-radius: 12px;

    background:
        var(--nova-white);

    color:
        var(--nova-blue);

    font-size: .85rem;

    box-shadow:
        0 4px 10px rgba(37, 99, 235, .08);

}


.intro-content {

    display: flex;

    flex-direction: column;

    gap: 4px;

}


.intro-content strong {

    color:
        var(--nova-navy);

    font-size: .94rem;

    font-weight: 700;

}


.intro-content span {

    color:
        var(--nova-muted);

    font-size: .85rem;

    line-height: 1.5;

}


/* ============================================================
   SECTION HEADER
============================================================ */

.strategy-section-header {

    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 20px;

}


.section-kicker {

    display: block;

    margin-bottom: 6px;

    color:
        var(--nova-blue);

    font-size: .68rem;

    font-weight: 800;

    letter-spacing: .12em;

}


.strategy-section-header h3 {

    margin: 0;

    color:
        var(--nova-navy);

    font-size: 1.15rem;

    line-height: 1.3;

    font-weight: 700;

    letter-spacing: -.01em;

}


.strategy-count {

    padding: 7px 11px;

    border:
        1px solid var(--nova-border);

    border-radius: 8px;

    background:
        var(--nova-soft);

    color:
        var(--nova-muted);

    font-size: .72rem;

    font-weight: 700;

    white-space: nowrap;

}


/* ============================================================
   GRID
============================================================ */

.strategy-grid {

    display: grid;

    grid-template-columns:
        repeat(
            2,
            minmax(0, 1fr)
        );

    gap: 20px;

}


.strategy-grid > * {

    min-width: 0;

    transition:
        transform .25s ease,
        box-shadow .25s ease;

    animation:
        cardAppear
        .55s
        ease
        both;

}


.strategy-grid > *:nth-child(2) {

    animation-delay:
        .06s;

}


.strategy-grid > *:nth-child(3) {

    animation-delay:
        .12s;

}


.strategy-grid > *:nth-child(4) {

    animation-delay:
        .18s;

}


.strategy-grid > *:nth-child(5) {

    animation-delay:
        .24s;

}


.strategy-grid > *:hover {

    transform:
        translateY(-3px);

}


/* ============================================================
   SUMMARY
============================================================ */

.strategy-summary {

    position: relative;

    overflow: hidden;

    border:
        1px solid var(--nova-border);

    border-radius: 20px;

    background:
        var(--nova-white);

    box-shadow:
        0 4px 14px rgba(15, 39, 71, .035);

    animation:
        summaryAppear
        .65s
        ease
        both;

    transition:
        border-color .25s ease,
        box-shadow .25s ease,
        transform .25s ease;

}


.strategy-summary::before {

    content: "";

    position: absolute;

    top: 0;

    left: 0;

    width: 100%;

    height: 3px;

    background:
        linear-gradient(
            90deg,
            #2563EB,
            #3B82F6,
            #60A5FA
        );

}


.strategy-summary:hover {

    border-color:
        #D6E4F8;

    box-shadow:
        0 12px 28px rgba(15, 39, 71, .07);

    transform:
        translateY(-2px);

}


/* ============================================================
   SUMMARY HEADER
============================================================ */

.summary-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    padding: 22px 24px;

    border-bottom:
        1px solid var(--nova-border);

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #FBFDFF 100%
        );

}


.summary-heading {

    display: flex;

    align-items: center;

    gap: 14px;

}


.summary-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 40px;

    height: 40px;

    flex-shrink: 0;

    border:
        1px solid var(--nova-blue-border);

    border-radius: 11px;

    background:
        var(--nova-blue-light);

    color:
        var(--nova-blue);

    font-size: .75rem;

}


.summary-header h3 {

    margin: 0;

    color:
        var(--nova-navy);

    font-size: 1.15rem;

    line-height: 1.3;

    font-weight: 750;

}


.summary-header p {

    max-width: 720px;

    margin: 5px 0 0;

    color:
        var(--nova-muted);

    font-size: .82rem;

    line-height: 1.55;

}


.summary-label {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    flex-shrink: 0;

    color:
        var(--nova-muted);

    font-size: .66rem;

    font-weight: 800;

    letter-spacing: .08em;

}


.summary-label-dot {

    width: 6px;

    height: 6px;

    border-radius: 50%;

    background:
        var(--nova-blue);

}


/* ============================================================
   SUMMARY BODY
============================================================ */

.summary-body {

    padding: 26px;

}


.strategy-summary :deep(.markdown-body) {

    color:
        var(--nova-text);

}


/* ============================================================
   SUMMARY FOOTER
============================================================ */

.summary-footer {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    padding: 15px 24px;

    border-top:
        1px solid var(--nova-border);

    background:
        var(--nova-soft);

}


.summary-footer-label {

    display: flex;

    align-items: center;

    gap: 8px;

    color:
        var(--nova-navy);

    font-size: .67rem;

    font-weight: 800;

    letter-spacing: .08em;

}


.footer-line {

    width: 18px;

    height: 2px;

    border-radius: 999px;

    background:
        var(--nova-blue);

}


.footer-note {

    color:
        var(--nova-muted);

    font-size: .72rem;

    line-height: 1.4;

}


/* ============================================================
   DISCLAIMER
============================================================ */

.strategy-disclaimer {

    display: flex;

    align-items: flex-start;

    gap: 11px;

    padding: 14px 16px;

    border:
        1px solid var(--nova-border);

    border-radius: 12px;

    background:
        #FAFBFC;

}


.disclaimer-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 20px;

    height: 20px;

    flex-shrink: 0;

    border:
        1px solid #CBD5E1;

    border-radius: 50%;

    color:
        var(--nova-muted);

    font-size: .7rem;

    font-weight: 700;

}


.strategy-disclaimer p {

    margin: 0;

    color:
        var(--nova-muted);

    font-size: .72rem;

    line-height: 1.55;

}


/* ============================================================
   RESPONSIVE
============================================================ */

@media (max-width: 1100px) {

    .strategy-grid {

        grid-template-columns:
            1fr;

    }

}


@media (max-width: 992px) {

    .strategy-view {

        padding: 26px;

    }

    .strategy-header {

        flex-direction: column;

        align-items: flex-start;

    }

    .strategy-status {

        align-self: flex-start;

    }

}


@media (max-width: 768px) {

    .strategy-view {

        gap: 24px;

        padding: 20px;

        border-radius: 20px;

    }


    .strategy-header {

        padding-bottom: 20px;

    }


    .strategy-header h2 {

        font-size: 1.5rem;

    }


    .strategy-header p {

        font-size: .9rem;

    }


    .strategy-intro {

        align-items: flex-start;

        padding: 16px;

    }


    .strategy-section-header {

        align-items: flex-start;

        flex-direction: column;

        gap: 12px;

    }


    .summary-header {

        align-items: flex-start;

        flex-direction: column;

        padding: 20px;

    }


    .summary-label {

        margin-left: 54px;

    }


    .summary-body {

        padding: 20px;

    }


    .summary-footer {

        align-items: flex-start;

        flex-direction: column;

        padding: 16px 20px;

    }

}


@media (max-width: 576px) {

    .strategy-view {

        gap: 20px;

        padding: 16px;

    }


    .strategy-header h2 {

        font-size: 1.4rem;

    }


    .strategy-header p {

        font-size: .88rem;

    }


    .strategy-intro {

        padding: 14px;

    }


    .intro-icon {

        width: 38px;

        height: 38px;

    }


    .intro-content strong {

        font-size: .88rem;

    }


    .intro-content span {

        font-size: .79rem;

    }


    .strategy-grid {

        gap: 16px;

    }


    .strategy-count {

        font-size: .68rem;

    }


    .summary-heading {

        align-items: flex-start;

    }


    .summary-header h3 {

        font-size: 1.05rem;

    }


    .summary-header p {

        font-size: .78rem;

    }


    .summary-label {

        margin-left: 0;

    }


    .summary-body {

        padding: 17px;

    }


    .strategy-disclaimer {

        padding: 12px;

    }

}


/* ============================================================
   ANIMATIONS
============================================================ */

@keyframes strategyFadeIn {

    from {

        opacity: 0;

        transform:
            translateY(16px);

    }

    to {

        opacity: 1;

        transform:
            translateY(0);

    }

}


@keyframes cardAppear {

    from {

        opacity: 0;

        transform:
            translateY(14px);

    }

    to {

        opacity: 1;

        transform:
            translateY(0);

    }

}


@keyframes summaryAppear {

    from {

        opacity: 0;

        transform:
            translateY(18px);

    }

    to {

        opacity: 1;

        transform:
            translateY(0);

    }

}


/* ============================================================
   REDUCED MOTION
============================================================ */

@media (prefers-reduced-motion: reduce) {

    .strategy-view,
    .strategy-grid > *,
    .strategy-summary {

        animation: none;

        transition: none;

    }

}

</style>