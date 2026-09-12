<template>

<section class="executive-summary">

    <!-- =====================================================
         CABECERA
    ====================================================== -->

    <header class="summary-header">

        <div class="summary-heading">

            <div class="summary-eyebrow">

                <span class="eyebrow-line"></span>

                SÍNTESIS DEL CASO

            </div>

            <h2>
                Resumen Ejecutivo
            </h2>

            <p>
                Síntesis automática del análisis jurídico
                realizado por NovaCase.
            </p>

        </div>

        <div class="summary-badge">

            <span class="badge-dot"></span>

            ANÁLISIS NOVACASE

        </div>

    </header>


    <!-- =====================================================
         MÉTRICAS
    ====================================================== -->

    <div class="summary-grid">

        <article
            v-for="(card, index) in cards"
            :key="card.title"
            class="summary-card"
            :style="{
                '--card-delay': `${index * 45}ms`
            }"
        >

            <div class="card-icon">

                {{ card.icon }}

            </div>


            <div class="card-content">

                <span class="card-title">

                    {{ card.title }}

                </span>

                <strong class="card-value">

                    {{ card.value }}

                </strong>

            </div>


            <span class="card-index">

                {{ String(index + 1).padStart(2, "0") }}

            </span>

        </article>

    </div>

</section>

</template>


<script setup>

import { computed } from "vue"


const props = defineProps({

    summary: {

        type: Object,

        default: () => ({})

    }

})


const cards = computed(() => [

    {

        title: "Rama del Derecho",

        value:
            props.summary.rama
            || "No identificada",

        icon: "⚖️"

    },

    {

        title: "Tipo de Proceso",

        value:
            props.summary.proceso
            || "No identificado",

        icon: "📂"

    },

    {

        title: "Probabilidad de Éxito",

        value:
            props.summary.probabilidad
            || "--",

        icon: "🎯"

    },

    {

        title: "Nivel de Riesgo",

        value:
            props.summary.riesgo
            || "--",

        icon: "⚠️"

    },

    {

        title: "Nivel de Evidencia",

        value:
            props.summary.evidencia
            || "--",

        icon: "📑"

    },

    {

        title: "Documentos Analizados",

        value:
            props.summary.documentos
            || 0,

        icon: "📚"

    }

])

</script>


<style scoped>

/* ============================================================
   SISTEMA VISUAL
============================================================ */

.executive-summary {

    --nova-navy: #0F2747;

    --nova-blue: #2563EB;

    --nova-blue-dark: #1D4ED8;

    --nova-blue-light: #EFF6FF;

    --nova-blue-border: #BFDBFE;

    --nova-text: #334155;

    --nova-muted: #64748B;

    --nova-subtle: #94A3B8;

    --nova-border: #E2E8F0;

    --nova-soft: #F8FAFC;

    --nova-white: #FFFFFF;

    position: relative;

    display: flex;

    flex-direction: column;

    gap: 26px;

    margin-top: 28px;

    padding: 28px;

    overflow: hidden;

    background: var(--nova-white);

    border:
        1px solid var(--nova-border);

    border-radius: 22px;

    box-shadow:
        0 6px 20px rgba(15, 39, 71, .05);

    animation:
        summaryAppear
        .45s
        ease
        both;

}


/* ============================================================
   DETALLE SUPERIOR
============================================================ */

.executive-summary::before {

    content: "";

    position: absolute;

    top: 0;

    left: 0;

    width: 100%;

    height: 3px;

    background:
        linear-gradient(
            90deg,
            var(--nova-blue),
            #3B82F6,
            #60A5FA
        );

}


/* ============================================================
   CABECERA
============================================================ */

.summary-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 24px;

    padding-bottom: 22px;

    border-bottom:
        1px solid var(--nova-border);

}


.summary-heading {

    display: flex;

    flex-direction: column;

    gap: 7px;

}


/* ============================================================
   EYEBROW
============================================================ */

.summary-eyebrow {

    display: flex;

    align-items: center;

    gap: 8px;

    margin-bottom: 2px;

    color: var(--nova-blue);

    font-size: .67rem;

    font-weight: 800;

    letter-spacing: .12em;

}


.eyebrow-line {

    width: 24px;

    height: 2px;

    flex-shrink: 0;

    border-radius: 999px;

    background: var(--nova-blue);

}


/* ============================================================
   TÍTULO
============================================================ */

.summary-header h2 {

    margin: 0;

    color: var(--nova-navy);

    font-size: 1.55rem;

    line-height: 1.25;

    font-weight: 750;

    letter-spacing: -.025em;

}


.summary-header p {

    max-width: 720px;

    margin: 0;

    color: var(--nova-muted);

    font-size: .88rem;

    line-height: 1.65;

}


/* ============================================================
   BADGE
============================================================ */

.summary-badge {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    flex-shrink: 0;

    padding: 7px 11px;

    border:
        1px solid var(--nova-blue-border);

    border-radius: 999px;

    background: var(--nova-blue-light);

    color: var(--nova-blue-dark);

    font-size: .62rem;

    font-weight: 800;

    letter-spacing: .065em;

}


.badge-dot {

    width: 6px;

    height: 6px;

    border-radius: 50%;

    background: var(--nova-blue);

    box-shadow:
        0 0 0 3px rgba(37, 99, 235, .08);

}


/* ============================================================
   GRID
============================================================ */

.summary-grid {

    display: grid;

    grid-template-columns:
        repeat(
            3,
            minmax(0, 1fr)
        );

    gap: 16px;

}


/* ============================================================
   TARJETAS
============================================================ */

.summary-card {

    --card-delay: 0ms;

    position: relative;

    display: flex;

    align-items: center;

    min-width: 0;

    gap: 14px;

    padding: 18px;

    overflow: hidden;

    background: var(--nova-white);

    border:
        1px solid var(--nova-border);

    border-radius: 16px;

    box-shadow:
        0 3px 12px rgba(15, 39, 71, .035);

    animation:
        cardAppear
        .45s
        ease
        var(--card-delay)
        both;

    transition:
        transform .25s ease,
        border-color .25s ease,
        box-shadow .25s ease;

}


.summary-card:hover {

    transform:
        translateY(-3px);

    border-color:
        var(--nova-blue-border);

    box-shadow:
        0 9px 22px rgba(15, 39, 71, .07);

}


/* ============================================================
   INDICADOR LATERAL
============================================================ */

.summary-card::before {

    content: "";

    position: absolute;

    top: 0;

    bottom: 0;

    left: 0;

    width: 3px;

    background:
        var(--nova-blue);

    opacity: .8;

}


/* ============================================================
   ICONO
============================================================ */

.card-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 46px;

    height: 46px;

    flex-shrink: 0;

    border:
        1px solid #DBEAFE;

    border-radius: 12px;

    background:
        var(--nova-blue-light);

    color: var(--nova-blue);

    font-size: 1.15rem;

    box-shadow:
        0 3px 8px rgba(37, 99, 235, .06);

    transition:
        transform .25s ease,
        box-shadow .25s ease;

}


.summary-card:hover .card-icon {

    transform:
        translateY(-1px)
        scale(1.04);

    box-shadow:
        0 5px 12px rgba(37, 99, 235, .10);

}


/* ============================================================
   CONTENIDO
============================================================ */

.card-content {

    display: flex;

    flex-direction: column;

    min-width: 0;

    gap: 5px;

}


.card-title {

    overflow: hidden;

    color: var(--nova-muted);

    font-size: .65rem;

    font-weight: 800;

    line-height: 1.3;

    letter-spacing: .075em;

    text-overflow: ellipsis;

    text-transform: uppercase;

    white-space: nowrap;

}


.card-value {

    overflow: hidden;

    color: var(--nova-navy);

    font-size: 1rem;

    font-weight: 750;

    line-height: 1.4;

    text-overflow: ellipsis;

    white-space: nowrap;

}


/* ============================================================
   ÍNDICE
============================================================ */

.card-index {

    position: absolute;

    top: 10px;

    right: 12px;

    color: #CBD5E1;

    font-size: .58rem;

    font-weight: 800;

    letter-spacing: .05em;

}


/* ============================================================
   RESPONSIVE — 1100PX
============================================================ */

@media (max-width: 1100px) {

    .summary-grid {

        grid-template-columns:
            repeat(
                2,
                minmax(0, 1fr)
            );

    }

}


/* ============================================================
   RESPONSIVE — 768PX
============================================================ */

@media (max-width: 768px) {

    .executive-summary {

        gap: 22px;

        margin-top: 24px;

        padding: 22px;

        border-radius: 20px;

    }


    .summary-header {

        flex-direction: column;

        gap: 15px;

    }


    .summary-badge {

        align-self: flex-start;

    }


    .summary-grid {

        grid-template-columns: 1fr;

        gap: 14px;

    }

}


/* ============================================================
   RESPONSIVE — 576PX
============================================================ */

@media (max-width: 576px) {

    .executive-summary {

        gap: 20px;

        margin-top: 20px;

        padding: 18px;

        border-radius: 17px;

    }


    .summary-header {

        padding-bottom: 18px;

    }


    .summary-header h2 {

        font-size: 1.3rem;

    }


    .summary-header p {

        font-size: .82rem;

    }


    .summary-card {

        padding: 16px;

        border-radius: 14px;

    }


    .card-icon {

        width: 42px;

        height: 42px;

        border-radius: 11px;

        font-size: 1.05rem;

    }


    .card-title {

        font-size: .61rem;

    }


    .card-value {

        font-size: .92rem;

    }

}


/* ============================================================
   ANIMACIONES
============================================================ */

@keyframes summaryAppear {

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


@keyframes cardAppear {

    from {

        opacity: 0;

        transform:
            translateY(10px);

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

    .executive-summary,
    .summary-card {

        animation: none;

        transition: none;

    }

}

</style>