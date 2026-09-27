<template>

    <section class="counter-view">

        <!-- =====================================================
             CABECERA
        ====================================================== -->

        <header class="counter-header">

            <div class="counter-heading">

                <div class="counter-eyebrow">

                    <span class="eyebrow-line"></span>

                    ANÁLISIS ADVERSARIAL

                </div>

                <h2>
                    Contraargumentos
                </h2>

                <p>
                    Identificación de posibles argumentos, objeciones y
                    posiciones que podría plantear la parte contraria
                    durante el proceso.
                </p>

            </div>

            <div class="counter-status">

                <span class="status-dot"></span>

                <span>
                    Análisis completado
                </span>

            </div>

        </header>


        <!-- =====================================================
             INTRODUCCIÓN
        ====================================================== -->

        <section class="counter-intro">

            <div class="intro-icon">

                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.7"
                    aria-hidden="true"
                >

                    <path d="M12 3v18" />

                    <path d="M5 6h14" />

                    <path
                        d="M7 6l-3 6a3 3 0 0 0 6 0L7 6Z"
                    />

                    <path
                        d="M17 6l-3 6a3 3 0 0 0 6 0l-3-6Z"
                    />

                    <path d="M8 21h8" />

                </svg>

            </div>

            <div class="intro-content">

                <strong>
                    Perspectiva de la contraparte
                </strong>

                <span>
                    NovaCase analiza posibles posiciones adversas para
                    anticipar argumentos y fortalecer la estrategia jurídica.
                </span>

            </div>

        </section>


        <!-- =====================================================
             MATRIZ DE CONTRAARGUMENTOS
        ====================================================== -->

        <section class="counter-analysis">

            <header class="counter-section-header">

                <div>

                    <span class="section-kicker">
                        MATRIZ DE ANÁLISIS
                    </span>

                    <h3>
                        Principales posiciones adversariales
                    </h3>

                </div>

                <div class="analysis-count">

                    <strong>
                        {{ counterArguments.length }}
                    </strong>

                    <span>
                        áreas analizadas
                    </span>

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
                    :status="argument.status"
                />

            </div>

        </section>


        <!-- =====================================================
             RESUMEN ESTRATÉGICO
        ====================================================== -->

        <section class="counter-summary">

            <header class="summary-header">

                <div class="summary-heading">

                    <div class="summary-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >

                            <circle
                                cx="12"
                                cy="12"
                                r="8"
                            />

                            <path d="M8 12h8" />

                            <path d="M12 8v8" />

                        </svg>

                    </div>

                    <div>

                        <span class="section-kicker">
                            SÍNTESIS DEL ANÁLISIS
                        </span>

                        <h3>
                            Evaluación Estratégica
                        </h3>

                        <p>
                            Síntesis de los principales escenarios de defensa
                            que podrían presentarse frente al caso analizado.
                        </p>

                    </div>

                </div>

                <div class="summary-label">

                    <span class="summary-label-dot"></span>

                    NOVACASE

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

        <aside class="counter-disclaimer">

            <div class="disclaimer-icon">

                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.7"
                    aria-hidden="true"
                >

                    <circle
                        cx="12"
                        cy="12"
                        r="9"
                    />

                    <path d="M12 10v6" />

                    <path d="M12 7.5h.01" />

                </svg>

            </div>

            <p>
                Los contraargumentos identificados representan escenarios
                posibles y deben ser evaluados junto con las circunstancias
                específicas del caso y el criterio profesional.
            </p>

        </aside>

    </section>

</template>


<script setup>

import { computed } from "vue"


import AnalysisSection
    from "@/components/common/AnalysisSection.vue"


import MarkdownRenderer
    from "@/components/common/MarkdownRenderer.vue"


const props = defineProps({

    counterArguments: {

        type: Object,

        default: () => ({})

    }

})


/* ============================================================
   CONTRAARGUMENTOS
============================================================ */

const counterArguments = computed(() => [

    {

        id: "procedural",

        title: "Excepciones Procesales",

        subtitle:
            "Posibles cuestionamientos al procedimiento",

        icon: "⚖️",

        content:

            props.counterArguments.procedural ||

            "No identificado con la información disponible.",

        status: "completed"

    },


    {

        id: "evidence",

        title: "Cuestionamiento Probatorio",

        subtitle:
            "Debilidades que podrían alegarse sobre la evidencia",

        icon: "📄",

        content:

            props.counterArguments.evidence ||

            "No identificado con la información disponible.",

        status: "completed"

    },


    {

        id: "legal",

        title: "Interpretación Jurídica",

        subtitle:
            "Normas que podrían ser interpretadas en contra",

        icon: "📚",

        content:

            props.counterArguments.legal ||

            "No identificado con la información disponible.",

        status: "completed"

    },


    {

        id: "jurisprudence",

        title: "Jurisprudencia Contraria",

        subtitle:
            "Precedentes favorables a la contraparte",

        icon: "🏛️",

        content:

            props.counterArguments.jurisprudence ||

            "No identificado con la información disponible.",

        status: "completed"

    }

])


/* ============================================================
   RESUMEN
============================================================ */

const summary = computed(() =>

    props.counterArguments.summary ||

    `### Evaluación Estratégica

NovaCase no encontró una evaluación estratégica disponible para este caso.`

)

</script>


<style scoped>

/* =========================================================
   NOVACASE — CONTRAARGUMENTOS
========================================================= */

.counter-view {

    display: flex;

    flex-direction: column;

    gap: 28px;

    padding: 32px;

    box-sizing: border-box;

    background: #FFFFFF;

    border: 1px solid #DCE5EE;

    border-radius: 18px;

    box-shadow:
        0 8px 24px
        rgba(23, 55, 94, .055);

    color: #17375E;

    animation:
        counterAppear
        .45s
        ease-out;

}


/* =========================================================
   HEADER
========================================================= */

.counter-header {

    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 24px;

    padding-bottom: 22px;

    border-bottom:
        1px solid #DCE5EE;

}


.counter-heading {

    min-width: 0;

}


.counter-eyebrow {

    display: flex;

    align-items: center;

    gap: 8px;

    margin-bottom: 9px;

    color: #8A6A36;

    font-size: .58rem;

    font-weight: 800;

    letter-spacing: 1.35px;

}


.eyebrow-line {

    width: 22px;

    height: 1px;

    flex-shrink: 0;

    background: #B08A4C;

}


.counter-header h2 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.55rem;

    font-weight: 600;

    line-height: 1.3;

    letter-spacing: -.25px;

}


.counter-header p {

    max-width: 780px;

    margin: 8px 0 0;

    color: #718090;

    font-size: .81rem;

    line-height: 1.7;

}


/* =========================================================
   STATUS
========================================================= */

.counter-status {

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
        1px solid #D8E7DD;

    border-radius: 999px;

    color: #587161;

    font-size: .61rem;

    font-weight: 800;

    letter-spacing: .05em;

}


.status-dot {

    width: 6px;

    height: 6px;

    flex-shrink: 0;

    border-radius: 50%;

    background: #668B70;

    box-shadow:
        0 0 0 3px
        rgba(102, 139, 112, .10);

}


/* =========================================================
   INTRODUCCIÓN
========================================================= */

.counter-intro {

    display: flex;

    align-items: center;

    gap: 14px;

    padding:
        16px
        18px;

    background:
        linear-gradient(
            135deg,
            #FCFDFE 0%,
            #F6F9FC 100%
        );

    border:
        1px solid #DCE5EE;

    border-left:
        3px solid #B08A4C;

    border-radius: 11px;

}


.intro-icon {

    width: 38px;

    height: 38px;

    display: flex;

    align-items: center;

    justify-content: center;

    flex-shrink: 0;

    background: #FCF9F4;

    border:
        1px solid
        rgba(176, 138, 76, .30);

    border-radius: 9px;

    color: #8A6A36;

}


.intro-icon svg {

    width: 19px;

    height: 19px;

}


.intro-content {

    display: flex;

    flex-direction: column;

    gap: 3px;

}


.intro-content strong {

    color: #304C6C;

    font-size: .78rem;

    font-weight: 800;

}


.intro-content span {

    color: #718090;

    font-size: .75rem;

    line-height: 1.6;

}


/* =========================================================
   SECCIÓN DE ANÁLISIS
========================================================= */

.counter-analysis {

    display: flex;

    flex-direction: column;

    gap: 17px;

}


.counter-section-header {

    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 20px;

}


.section-kicker {

    display: block;

    margin-bottom: 5px;

    color: #8A6A36;

    font-size: .56rem;

    font-weight: 800;

    letter-spacing: 1.25px;

}


.counter-section-header h3 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.05rem;

    font-weight: 600;

    line-height: 1.35;

}


/* =========================================================
   CONTADOR
========================================================= */

.analysis-count {

    display: inline-flex;

    align-items: baseline;

    gap: 5px;

    padding:
        7px
        10px;

    background: #F7F9FB;

    border:
        1px solid #DCE5EE;

    border-radius: 8px;

    color: #8A97A5;

    font-size: .62rem;

    white-space: nowrap;

}


.analysis-count strong {

    color: #315C97;

    font-size: .76rem;

    font-weight: 800;

}


/* =========================================================
   GRID
========================================================= */

.counter-grid {

    display: grid;

    grid-template-columns:
        repeat(
            2,
            minmax(0, 1fr)
        );

    gap: 18px;

}


.counter-grid > * {

    min-width: 0;

    transition:
        transform .25s ease,
        box-shadow .25s ease;

    animation:
        cardAppear
        .5s
        ease-out
        both;

}


.counter-grid > *:nth-child(2) {

    animation-delay: .06s;

}


.counter-grid > *:nth-child(3) {

    animation-delay: .12s;

}


.counter-grid > *:nth-child(4) {

    animation-delay: .18s;

}


.counter-grid > *:hover {

    transform:
        translateY(-2px);

}


/* =========================================================
   RESUMEN ESTRATÉGICO
========================================================= */

.counter-summary {

    overflow: hidden;

    background: #FFFFFF;

    border:
        1px solid #DCE5EE;

    border-radius: 14px;

    box-shadow:
        0 5px 16px
        rgba(23, 55, 94, .035);

    animation:
        summaryAppear
        .55s
        ease-out
        both;

}


.summary-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    padding:
        18px
        20px;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #FBFCFD 100%
        );

    border-bottom:
        1px solid #DCE5EE;

}


.summary-heading {

    display: flex;

    align-items: center;

    gap: 12px;

    min-width: 0;

}


.summary-icon {

    width: 36px;

    height: 36px;

    display: flex;

    align-items: center;

    justify-content: center;

    flex-shrink: 0;

    background: #FCF9F4;

    border:
        1px solid
        rgba(176, 138, 76, .30);

    border-radius: 9px;

    color: #8A6A36;

}


.summary-icon svg {

    width: 18px;

    height: 18px;

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


.summary-header p {

    max-width: 700px;

    margin: 4px 0 0;

    color: #718090;

    font-size: .75rem;

    line-height: 1.55;

}


.summary-label {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    flex-shrink: 0;

    color: #8A97A5;

    font-size: .57rem;

    font-weight: 800;

    letter-spacing: 1px;

}


.summary-label-dot {

    width: 5px;

    height: 5px;

    border-radius: 50%;

    background: #B08A4C;

}


/* =========================================================
   CUERPO DEL RESUMEN
========================================================= */

.summary-body {

    padding:
        23px
        24px;

}


.counter-summary :deep(.markdown-body) {

    color: #334C66;

}


.counter-summary :deep(.markdown-body h1),
.counter-summary :deep(.markdown-body h2),
.counter-summary :deep(.markdown-body h3) {

    color: #17375E;

}


.counter-summary :deep(.markdown-body strong) {

    color: #304C6C;

}


/* =========================================================
   FOOTER DEL RESUMEN
========================================================= */

.summary-footer {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    padding:
        12px
        20px;

    background: #F7F9FB;

    border-top:
        1px solid #DCE5EE;

}


.summary-footer-label {

    display: flex;

    align-items: center;

    gap: 7px;

    color: #304C6C;

    font-size: .57rem;

    font-weight: 800;

    letter-spacing: 1px;

}


.footer-line {

    width: 17px;

    height: 1px;

    background: #B08A4C;

}


.footer-note {

    color: #8A97A5;

    font-size: .62rem;

}


/* =========================================================
   DISCLAIMER
========================================================= */

.counter-disclaimer {

    display: flex;

    align-items: flex-start;

    gap: 10px;

    padding:
        12px
        14px;

    background: #FAFBFC;

    border:
        1px solid #E1E7ED;

    border-radius: 9px;

}


.disclaimer-icon {

    width: 20px;

    height: 20px;

    display: flex;

    align-items: center;

    justify-content: center;

    flex-shrink: 0;

    color: #8A97A5;

}


.disclaimer-icon svg {

    width: 17px;

    height: 17px;

}


.counter-disclaimer p {

    margin: 0;

    color: #7A8794;

    font-size: .65rem;

    line-height: 1.6;

}


/* =========================================================
   RESPONSIVE — 1100 PX
========================================================= */

@media (max-width: 1100px) {

    .counter-grid {

        grid-template-columns: 1fr;

    }

}


/* =========================================================
   RESPONSIVE — 900 PX
========================================================= */

@media (max-width: 900px) {

    .counter-view {

        padding: 26px;

    }


    .counter-header {

        align-items: flex-start;

        flex-direction: column;

    }


    .counter-status {

        align-self: flex-start;

    }

}


/* =========================================================
   RESPONSIVE — 700 PX
========================================================= */

@media (max-width: 700px) {

    .counter-view {

        gap: 24px;

        padding: 21px;

        border-radius: 15px;

    }


    .counter-header h2 {

        font-size: 1.4rem;

    }


    .counter-header p {

        font-size: .77rem;

    }


    .counter-intro {

        align-items: flex-start;

    }


    .counter-section-header {

        align-items: flex-start;

        flex-direction: column;

        gap: 10px;

    }


    .summary-header {

        align-items: flex-start;

        flex-direction: column;

        padding: 18px;

    }


    .summary-label {

        margin-left: 48px;

    }


    .summary-body {

        padding: 20px;

    }


    .summary-footer {

        align-items: flex-start;

        flex-direction: column;

        gap: 8px;

        padding:
            13px
            18px;

    }

}


/* =========================================================
   RESPONSIVE — 480 PX
========================================================= */

@media (max-width: 480px) {

    .counter-view {

        padding: 17px;

        gap: 20px;

    }


    .counter-header {

        padding-bottom: 19px;

    }


    .counter-header h2 {

        font-size: 1.3rem;

    }


    .counter-header p {

        font-size: .74rem;

    }


    .counter-intro {

        padding:
            14px;

    }


    .intro-icon {

        width: 35px;

        height: 35px;

    }


    .intro-content strong {

        font-size: .74rem;

    }


    .intro-content span {

        font-size: .71rem;

    }


    .counter-grid {

        gap: 14px;

    }


    .summary-heading {

        align-items: flex-start;

    }


    .summary-header h3 {

        font-size: .98rem;

    }


    .summary-label {

        margin-left: 0;

    }


    .summary-body {

        padding: 17px;

    }


    .counter-disclaimer {

        padding:
            11px
            12px;

    }

}


/* =========================================================
   ANIMACIONES
========================================================= */

@keyframes counterAppear {

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


@keyframes cardAppear {

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


@keyframes summaryAppear {

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


/* =========================================================
   REDUCIR MOVIMIENTO
========================================================= */

@media (prefers-reduced-motion: reduce) {

    .counter-view,
    .counter-grid > *,
    .counter-summary {

        animation: none;

        transition: none;

    }

}

</style>