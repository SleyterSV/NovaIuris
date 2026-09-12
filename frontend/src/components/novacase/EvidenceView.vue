<template>

    <section class="evidence-view">

        <!-- =====================================================
             CABECERA
        ====================================================== -->

        <header class="evidence-header">

            <div class="evidence-heading">

                <div class="section-eyebrow">

                    <span class="eyebrow-line"></span>

                    NOVACASE · EVIDENCIA

                </div>

                <h2>
                    Análisis Probatorio
                </h2>

                <p>
                    Evaluación de las pruebas identificadas durante
                    el análisis jurídico del caso.
                </p>

            </div>

        </header>


        <!-- =====================================================
             EVIDENCIAS
        ====================================================== -->

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


        <!-- =====================================================
             ESTADÍSTICAS
        ====================================================== -->

        <section class="evidence-stats">

            <div class="stat-card">

                <div class="stat-icon">

                    <span>01</span>

                </div>

                <div class="stat-content">

                    <span class="stat-label">
                        Evidencias analizadas
                    </span>

                    <strong class="stat-value">
                        {{ evidences.length }}
                    </strong>

                </div>

            </div>


            <div class="stat-card">

                <div class="stat-icon">

                    <span>02</span>

                </div>

                <div class="stat-content">

                    <span class="stat-label">
                        Nivel promedio
                    </span>

                    <strong class="stat-value">
                        {{ averageConfidence }}%
                    </strong>

                </div>

            </div>


            <div class="stat-card">

                <div class="stat-icon success-icon">

                    <span>✓</span>

                </div>

                <div class="stat-content">

                    <span class="stat-label">
                        Estado general
                    </span>

                    <strong class="stat-success">
                        Validado
                    </strong>

                </div>

            </div>

        </section>


        <!-- =====================================================
             CONCLUSIÓN PROBATORIA
        ====================================================== -->

        <section class="evidence-summary">

            <div class="summary-header">

                <div>

                    <div class="summary-eyebrow">

                        <span class="summary-line"></span>

                        CONCLUSIÓN PROBATORIA

                    </div>

                    <h3>
                        Evaluación general de la evidencia
                    </h3>

                </div>

                <div class="summary-badge">

                    <span class="summary-dot"></span>

                    Análisis completado

                </div>

            </div>


            <div class="summary-content">

                <MarkdownRenderer
                    :content="summary"
                />

            </div>

        </section>

    </section>

</template>


<script setup>

import { computed } from "vue"

import AnalysisSection
    from "@/components/common/AnalysisSection.vue"

import MarkdownRenderer
    from "@/components/common/MarkdownRenderer.vue"


/* =========================================================
   PROPS
========================================================= */

const props = defineProps({

    evidence: {

        type: Object,

        default: () => ({})

    }

})


/* =========================================================
   EVIDENCIAS
========================================================= */

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

        title: "Evidencia digital",

        subtitle: "Mensajes, correos y archivos",

        icon: "💻",

        content:
            props.evidence.digitalEvidence ||

            "No se encontró evidencia digital.",

        confidence: 90,

        status: "completed"

    }

])


/* =========================================================
   RESUMEN
========================================================= */

const summary = computed(() =>

    props.evidence.summary ||

    `### Conclusión

NovaCase no encontró una conclusión probatoria disponible.`

)


/* =========================================================
   PROMEDIO
========================================================= */

const averageConfidence = computed(() => {

    if (
        evidences.value.length === 0
    ) {

        return 0

    }


    const total =
        evidences.value.reduce(

            (
                sum,
                item
            ) =>

                sum +
                item.confidence,

            0

        )


    return Math.round(

        total /
        evidences.value.length

    )

})

</script>


<style scoped>

/* =========================================================
   EVIDENCE VIEW
========================================================= */

.evidence-view {

    display: flex;

    flex-direction: column;

    gap: 28px;

    padding: 30px;

    background: #FFFFFF;

    border:
        1px solid
        #DCE5EE;

    border-radius: 14px;

    box-shadow:
        0 8px 24px
        rgba(
            23,
            55,
            94,
            .055
        );

    animation:
        evidenceAppear
        .45s
        ease-out;

}


/* =========================================================
   CABECERA
========================================================= */

.evidence-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    padding-bottom: 22px;

    border-bottom:
        1px solid
        #E2E8F0;

}


.evidence-heading {

    min-width: 0;

}


.section-eyebrow {

    display: flex;

    align-items: center;

    gap: 8px;

    margin-bottom: 10px;

    color: #8A6A36;

    font-size: .57rem;

    font-weight: 800;

    letter-spacing: 1.4px;

}


.eyebrow-line {

    width: 20px;

    height: 1px;

    background: #B08A4C;

}


.evidence-header h2 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.55rem;

    font-weight: 600;

    line-height: 1.3;

}


.evidence-header p {

    max-width: 720px;

    margin:
        7px
        0
        0;

    color: #718090;

    font-size: .79rem;

    line-height: 1.7;

}


/* =========================================================
   GRID DE EVIDENCIAS
========================================================= */

.evidence-grid {

    display: grid;

    grid-template-columns:
        repeat(
            2,
            minmax(
                0,
                1fr
            )
        );

    gap: 18px;

}


/* =========================================================
   ESTADÍSTICAS
========================================================= */

.evidence-stats {

    display: grid;

    grid-template-columns:
        repeat(
            3,
            minmax(
                0,
                1fr
            )
        );

    gap: 14px;

}


.stat-card {

    display: flex;

    align-items: center;

    gap: 13px;

    min-width: 0;

    padding: 17px;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #FBFCFD 100%
        );

    border:
        1px solid
        #E1E7ED;

    border-radius: 11px;

    box-shadow:
        0 4px 14px
        rgba(
            23,
            55,
            94,
            .035
        );

    transition:
        transform .22s ease,
        border-color .22s ease,
        box-shadow .22s ease;

}


.stat-card:hover {

    transform:
        translateY(-2px);

    border-color:
        #C8D6E4;

    box-shadow:
        0 8px 20px
        rgba(
            23,
            55,
            94,
            .07
        );

}


/* =========================================================
   ICONOS DE ESTADÍSTICAS
========================================================= */

.stat-icon {

    width: 35px;

    height: 35px;

    flex:
        0 0
        35px;

    display: flex;

    align-items: center;

    justify-content: center;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .32
        );

    border-radius: 8px;

    background:
        #FCF9F4;

    color: #8A6A36;

    font-size: .58rem;

    font-weight: 800;

}


.stat-icon span {

    display: block;

}


.success-icon {

    border-color:
        #D8E7DD;

    background:
        #F7FAF8;

    color: #668B70;

    font-size: .9rem;

}


/* =========================================================
   CONTENIDO DE ESTADÍSTICAS
========================================================= */

.stat-content {

    display: flex;

    flex-direction: column;

    gap: 4px;

    min-width: 0;

}


.stat-label {

    color: #7C8997;

    font-size: .57rem;

    font-weight: 750;

    letter-spacing: .65px;

    text-transform: uppercase;

}


.stat-value {

    color: #17375E;

    font-size: 1.18rem;

    font-weight: 750;

    line-height: 1.2;

}


.stat-success {

    color: #587161;

    font-size: .9rem;

    font-weight: 750;

    line-height: 1.3;

}


/* =========================================================
   RESUMEN
========================================================= */

.evidence-summary {

    overflow: hidden;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #FBFCFD 100%
        );

    border:
        1px solid
        #DCE5EE;

    border-radius: 12px;

    box-shadow:
        0 5px 18px
        rgba(
            23,
            55,
            94,
            .035
        );

    transition:
        border-color .25s ease,
        box-shadow .25s ease;

}


.evidence-summary:hover {

    border-color:
        #C8D6E4;

    box-shadow:
        0 8px 22px
        rgba(
            23,
            55,
            94,
            .06
        );

}


/* =========================================================
   CABECERA DEL RESUMEN
========================================================= */

.summary-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    padding:
        20px
        22px;

    border-bottom:
        1px solid
        #E5EAF0;

}


.summary-eyebrow {

    display: flex;

    align-items: center;

    gap: 7px;

    margin-bottom: 6px;

    color: #8A6A36;

    font-size: .54rem;

    font-weight: 800;

    letter-spacing: 1.25px;

}


.summary-line {

    width: 17px;

    height: 1px;

    background:
        #B08A4C;

}


.summary-header h3 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.05rem;

    font-weight: 600;

}


/* =========================================================
   BADGE DEL RESUMEN
========================================================= */

.summary-badge {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    flex-shrink: 0;

    min-height: 27px;

    padding:
        0
        10px;

    border:
        1px solid
        #D8E7DD;

    border-radius: 999px;

    background:
        #F7FAF8;

    color: #587161;

    font-size: .57rem;

    font-weight: 750;

}


.summary-dot {

    width: 5px;

    height: 5px;

    border-radius: 50%;

    background:
        #668B70;

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
   CONTENIDO DEL RESUMEN
========================================================= */

.summary-content {

    padding:
        20px
        22px;

    color: #526477;

    font-size: .79rem;

    line-height: 1.75;

}


:deep(.summary-content) {

    color: #526477;

}


:deep(.markdown-container) {

    margin: 0;

}


:deep(.markdown-container h1),
:deep(.markdown-container h2),
:deep(.markdown-container h3) {

    color: #17375E;

}


:deep(.markdown-container p) {

    color: #526477;

}


/* =========================================================
   RESPONSIVE — 1100 PX
========================================================= */

@media (max-width: 1100px) {

    .evidence-grid {

        grid-template-columns:
            1fr;

    }

}


/* =========================================================
   RESPONSIVE — 900 PX
========================================================= */

@media (max-width: 900px) {

    .evidence-view {

        padding: 24px;

    }


    .evidence-stats {

        grid-template-columns:
            repeat(
                2,
                minmax(
                    0,
                    1fr
                )
            );

    }

}


/* =========================================================
   RESPONSIVE — 700 PX
========================================================= */

@media (max-width: 700px) {

    .evidence-view {

        gap: 22px;

        padding: 20px;

    }


    .evidence-header {

        padding-bottom: 18px;

    }


    .evidence-header h2 {

        font-size: 1.35rem;

    }


    .evidence-header p {

        font-size: .76rem;

    }


    .evidence-stats {

        grid-template-columns:
            1fr;

    }


    .summary-header {

        align-items: flex-start;

        flex-direction: column;

    }


    .summary-badge {

        align-self: flex-start;

    }

}


/* =========================================================
   RESPONSIVE — 480 PX
========================================================= */

@media (max-width: 480px) {

    .evidence-view {

        padding: 16px;

        border-radius: 11px;

    }


    .evidence-header h2 {

        font-size: 1.22rem;

    }


    .evidence-header p {

        font-size: .73rem;

    }


    .stat-card {

        padding: 15px;

    }


    .summary-header {

        padding:
            17px
            18px;

    }


    .summary-content {

        padding:
            17px
            18px;

    }


    .summary-header h3 {

        font-size: .96rem;

    }

}


/* =========================================================
   ANIMACIONES
========================================================= */

@keyframes evidenceAppear {

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


/* =========================================================
   REDUCIR MOVIMIENTO
========================================================= */

@media (
    prefers-reduced-motion: reduce
) {

    .evidence-view,
    .stat-card {

        animation: none;

        transition: none;

    }

}

</style>