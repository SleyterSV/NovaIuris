<template>

    <section class="executive-summary">

        <div class="summary-header">

            <h2>

                Resumen Ejecutivo

            </h2>

            <p>

                Síntesis automática del análisis jurídico realizado por NovaCase.

            </p>

        </div>

        <div class="summary-grid">

            <div
                v-for="card in cards"
                :key="card.title"
                class="summary-card"
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

            </div>

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

.executive-summary{

    margin-top:32px;

    padding:30px;

    border-radius:22px;

    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    box-shadow: 0 8px 24px rgba(15, 39, 71, 0.06);

}

.summary-header{

    margin-bottom:28px;

}

.summary-header h2 {
    color: #0F2747;
    font-size: 1.55rem;
    font-weight: 700;
    margin-bottom: 8px;
    letter-spacing: .3px;
}

.summary-header p {
    color: #64748B;
    line-height: 1.7;
    font-size: .95rem;
}

.summary-grid{

    display:grid;

    grid-template-columns:repeat(

        auto-fit,

        minmax(220px,1fr)

    );

    gap:20px;

}

.summary-card {
    position: relative;
    overflow: hidden;

    display: flex;
    align-items: center;
    gap: 18px;

    padding: 22px;

    border-radius: 18px;

    background: #FFFFFF;

    border: 1px solid #E2E8F0;

    box-shadow:
        0 6px 20px rgba(15, 39, 71, 0.05);

    transition:
        transform .25s ease,
        box-shadow .25s ease,
        border-color .25s ease;
}

.summary-card::before {
    content: "";

    position: absolute;

    left: 0;

    top: 0;

    width: 4px;

    height: 100%;

    background: #2563EB;
}

.summary-card:hover {
    transform: translateY(-3px);

    border-color: #BFDBFE;

    box-shadow:
        0 12px 28px rgba(15, 39, 71, 0.08);
}

.card-icon {
    width: 58px;
    height: 58px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 15px;

    font-size: 1.65rem;

    background: #EFF6FF;

    color: #2563EB;

    border: 1px solid #DBEAFE;

    flex-shrink: 0;
}

.card-content{

    display:flex;

    flex-direction:column;

    justify-content:center;

}

.card-title {
    color: #64748B;

    font-size: .78rem;

    margin-bottom: 6px;

    text-transform: uppercase;

    letter-spacing: .7px;
}

.card-value {
    color: #0F2747;

    font-size: 1.1rem;

    font-weight: 700;

    line-height: 1.4;

    word-break: break-word;
}

@media(max-width:900px){

    .summary-grid{

        grid-template-columns:1fr;

    }

}

</style>
