<template>

    <section
        class="nova-analysis-progress"
        :class="{
            'is-loading': loading,
            'is-complete': !loading && hasCompleted
        }"
        aria-live="polite"
    >

        <!-- =====================================================
             CABECERA
        ====================================================== -->

        <header class="progress-header">

            <div class="progress-header-main">

                <div
                    class="progress-emblem"
                    :class="{
                        'is-processing': loading,
                        'is-completed': !loading && hasCompleted
                    }"
                >

                    <!-- PROCESANDO -->

                    <svg
                        v-if="loading"
                        class="emblem-icon emblem-spinner"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.6"
                        aria-hidden="true"
                    >

                        <circle
                            cx="12"
                            cy="12"
                            r="8.5"
                            opacity=".22"
                        />

                        <path
                            d="M12 3.5a8.5 8.5 0 0 1 8.5 8.5"
                        />

                    </svg>


                    <!-- COMPLETADO -->

                    <svg
                        v-else-if="hasCompleted"
                        class="emblem-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        aria-hidden="true"
                    >

                        <path
                            d="M5 12.5l4.2 4.2L19 7"
                        />

                    </svg>


                    <!-- PENDIENTE -->

                    <svg
                        v-else
                        class="emblem-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        aria-hidden="true"
                    >

                        <path
                            d="M12 4v16"
                        />

                        <path
                            d="M8 8h8"
                        />

                        <path
                            d="M8 16h8"
                        />

                    </svg>

                </div>


                <div class="progress-heading">

                    <span class="progress-eyebrow">
                        NOVACASE · ANÁLISIS JURÍDICO
                    </span>


                    <h2 v-if="loading">
                        NovaCase está analizando el caso
                    </h2>

                    <h2 v-else-if="hasCompleted">
                        Análisis jurídico completado
                    </h2>

                    <h2 v-else>
                        Preparando análisis jurídico
                    </h2>


                    <p v-if="loading">
                        El sistema está procesando la información del caso
                        y construyendo el análisis jurídico integral.
                    </p>

                    <p v-else-if="hasCompleted">
                        El análisis ha finalizado correctamente.
                        Puedes revisar las diferentes secciones del informe.
                    </p>

                    <p v-else>
                        NovaCase está listo para iniciar el análisis jurídico
                        del caso.
                    </p>

                </div>

            </div>


            <!-- INDICADOR GENERAL -->

            <div
                v-if="steps.length"
                class="progress-summary"
            >

                <span class="progress-summary-label">
                    PROGRESO
                </span>

                <strong>
                    {{ completedSteps }}/{{ steps.length }}
                </strong>

            </div>

        </header>


        <!-- =====================================================
             BARRA DE PROGRESO
        ====================================================== -->

        <div
            v-if="steps.length"
            class="progress-track-wrapper"
        >

            <div class="progress-track">

                <div
                    class="progress-track-fill"
                    :style="{ width: progressPercentage + '%' }"
                ></div>

            </div>

            <span class="progress-percentage">
                {{ progressPercentage }}%
            </span>

        </div>


        <!-- =====================================================
             ETAPAS
        ====================================================== -->

        <div
            v-if="steps.length"
            class="steps"
        >

            <article
                v-for="(step, index) in steps"
                :key="step.id || index"
                class="step"
                :class="statusClass(step.status)"
            >

                <!-- CONECTOR -->

                <div
                    v-if="index < steps.length - 1"
                    class="step-connector"
                    :class="{
                        'is-completed':
                            step.status === 'completed'
                    }"
                    aria-hidden="true"
                ></div>


                <!-- INDICADOR -->

                <div class="step-indicator">

                    <!-- COMPLETADO -->

                    <svg
                        v-if="step.status === 'completed'"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        aria-hidden="true"
                    >

                        <path
                            d="M5 12.5l4.2 4.2L19 7"
                        />

                    </svg>


                    <!-- PROCESANDO -->

                    <span
                        v-else-if="step.status === 'processing'"
                        class="processing-ring"
                        aria-hidden="true"
                    ></span>


                    <!-- PENDIENTE -->

                    <span
                        v-else
                        class="pending-dot"
                        aria-hidden="true"
                    ></span>

                </div>


                <!-- INFORMACIÓN -->

                <div class="step-content">

                    <div class="step-topline">

                        <span class="step-number">
                            ETAPA {{ String(index + 1).padStart(2, "0") }}
                        </span>


                        <span
                            v-if="step.status === 'completed'"
                            class="step-status completed"
                        >
                            Completado
                        </span>


                        <span
                            v-else-if="step.status === 'processing'"
                            class="step-status processing"
                        >
                            En proceso
                        </span>


                        <span
                            v-else
                            class="step-status pending"
                        >
                            Pendiente
                        </span>

                    </div>


                    <h3>
                        {{ step.title }}
                    </h3>


                    <p>
                        {{ step.description }}
                    </p>

                </div>

            </article>

        </div>


        <!-- =====================================================
             SIN PASOS
        ====================================================== -->

        <div
            v-else
            class="empty-steps"
        >

            <span class="empty-steps-label">
                NOVACASE
            </span>

            <p>
                Las etapas del análisis aparecerán aquí cuando
                el proceso haya sido iniciado.
            </p>

        </div>


        <!-- =====================================================
             FOOTER / ESTADO
        ====================================================== -->

        <footer
            v-if="loading"
            class="progress-footer"
        >

            <span class="footer-indicator"></span>

            <div>

                <strong>
                    Análisis en curso
                </strong>

                <span>
                    NovaCase está procesando la información.
                    No cierres esta ventana.
                </span>

            </div>

        </footer>


        <footer
            v-else-if="hasCompleted"
            class="progress-footer completed"
        >

            <span class="footer-check">

                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    aria-hidden="true"
                >

                    <path
                        d="M5 12.5l4.2 4.2L19 7"
                    />

                </svg>

            </span>


            <div>

                <strong>
                    Análisis finalizado
                </strong>

                <span>
                    El informe jurídico está listo para su revisión.
                </span>

            </div>

        </footer>

    </section>

</template>


<script setup>

import { computed } from "vue"


/* =====================================================
   PROPS
===================================================== */

const props = defineProps({

    steps: {

        type: Array,

        default: () => []

    },

    loading: {

        type: Boolean,

        default: false

    }

})


/* =====================================================
   ESTADO DEL ANÁLISIS
===================================================== */

const hasCompleted = computed(() => {

    return (

        props.steps.length > 0 &&

        props.steps.every(

            step => step.status === "completed"

        )

    )

})


/* =====================================================
   ETAPAS COMPLETADAS
===================================================== */

const completedSteps = computed(() => {

    return props.steps.filter(

        step => step.status === "completed"

    ).length

})


/* =====================================================
   PORCENTAJE
===================================================== */

const progressPercentage = computed(() => {

    if (!props.steps.length) {

        return 0

    }

    return Math.round(

        (

            completedSteps.value /

            props.steps.length

        ) * 100

    )

})


/* =====================================================
   CLASE DE ESTADO
===================================================== */

function statusClass(status) {

    return {

        "step-completed":
            status === "completed",

        "step-processing":
            status === "processing",

        "step-pending":
            status === "pending"

    }

}

</script>


<style scoped>

/* =======================================================
   NOVACASE — ANALYSIS PROGRESS
======================================================= */

.nova-analysis-progress{

    width:100%;

    padding:30px 30px 24px;

    background:#FFFFFF;

    border:
        1px solid
        #DCE5EE;

    border-radius:14px;

    box-shadow:
        0 10px 28px
        rgba(
            23,
            55,
            94,
            .045
        );

    transition:
        border-color .25s ease,
        box-shadow .25s ease;

}


.nova-analysis-progress.is-loading{

    border-color:#C9D9EA;

}


.nova-analysis-progress.is-complete{

    border-color:#D5E1D9;

}


/* =======================================================
   HEADER
======================================================= */

.progress-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:24px;

    padding:
        0
        0
        22px;

    border-bottom:
        1px solid
        #E4EAF0;

}


.progress-header-main{

    display:flex;

    align-items:flex-start;

    gap:16px;

    min-width:0;

}


/* =======================================================
   EMBLEMA
======================================================= */

.progress-emblem{

    width:50px;

    height:50px;

    flex:
        0 0
        50px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#F5F8FB;

    border:
        1px solid
        #D9E3ED;

    color:#315C97;

}


.progress-emblem.is-processing{

    background:#F2F6FB;

    border-color:#C8D9EA;

    color:#315C97;

}


.progress-emblem.is-completed{

    background:#F5F9F6;

    border-color:#D2E2D7;

    color:#46745A;

}


.emblem-icon{

    width:24px;

    height:24px;

}


.emblem-spinner{

    animation:
        emblemSpin
        1.25s
        linear
        infinite;

}


/* =======================================================
   TEXTO HEADER
======================================================= */

.progress-heading{

    min-width:0;

}


.progress-eyebrow{

    display:block;

    margin-bottom:6px;

    color:#7A6440;

    font-size:.62rem;

    font-weight:800;

    letter-spacing:1.35px;

}


.progress-heading h2{

    margin:0;

    color:#17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:1.38rem;

    font-weight:600;

    line-height:1.35;

}


.progress-heading p{

    max-width:700px;

    margin:7px 0 0;

    color:#6B7A8A;

    font-size:.86rem;

    line-height:1.7;

}


/* =======================================================
   RESUMEN
======================================================= */

.progress-summary{

    min-width:70px;

    display:flex;

    flex-direction:column;

    align-items:center;

    justify-content:center;

    padding:
        9px
        12px;

    background:#FBFCFD;

    border:
        1px solid
        #DCE4EC;

    border-radius:9px;

}


.progress-summary-label{

    color:#8B97A5;

    font-size:.55rem;

    font-weight:800;

    letter-spacing:1px;

}


.progress-summary strong{

    margin-top:2px;

    color:#17375E;

    font-size:1rem;

    font-weight:800;

}


/* =======================================================
   BARRA DE PROGRESO
======================================================= */

.progress-track-wrapper{

    display:flex;

    align-items:center;

    gap:12px;

    margin:
        22px
        0
        25px;

}


.progress-track{

    position:relative;

    flex:1;

    height:4px;

    overflow:hidden;

    background:#E8EDF2;

    border-radius:999px;

}


.progress-track-fill{

    height:100%;

    background:#315C97;

    border-radius:999px;

    transition:
        width .45s
        ease;

}


.is-complete
.progress-track-fill{

    background:#5C806A;

}


.progress-percentage{

    min-width:34px;

    color:#748294;

    font-size:.65rem;

    font-weight:800;

    text-align:right;

}


/* =======================================================
   ETAPAS
======================================================= */

.steps{

    display:flex;

    flex-direction:column;

}


/* =======================================================
   STEP
======================================================= */

.step{

    position:relative;

    display:flex;

    align-items:flex-start;

    gap:16px;

    min-height:91px;

}


.step:last-child{

    min-height:auto;

}


/* =======================================================
   CONECTOR
======================================================= */

.step-connector{

    position:absolute;

    top:39px;

    left:19px;

    width:1px;

    height:52px;

    background:#DDE5EC;

    z-index:1;

}


.step-connector.is-completed{

    background:
        linear-gradient(
            to bottom,
            #B8CCBE,
            #DDE5EC
        );

}


/* =======================================================
   INDICADOR
======================================================= */

.step-indicator{

    position:relative;

    z-index:2;

    width:40px;

    height:40px;

    flex:
        0 0
        40px;

    display:flex;

    align-items:center;

    justify-content:center;

    margin-top:1px;

    background:#FFFFFF;

    border:
        1.5px solid
        #CBD6E0;

    border-radius:50%;

    color:#FFFFFF;

    transition:
        background .25s ease,
        border-color .25s ease,
        box-shadow .25s ease;

}


.step-indicator svg{

    width:18px;

    height:18px;

}


/* =======================================================
   COMPLETADO
======================================================= */

.step-completed
.step-indicator{

    background:#F5F9F6;

    border-color:#6F927C;

    color:#46745A;

}


.step-completed
.step-indicator::after{

    content:"";

    position:absolute;

    inset:-5px;

    border:
        1px solid
        rgba(
            92,
            128,
            106,
            .12
        );

    border-radius:50%;

}


/* =======================================================
   PROCESANDO
======================================================= */

.step-processing
.step-indicator{

    background:#F3F7FC;

    border-color:#315C97;

    color:#315C97;

    box-shadow:
        0 0 0 5px
        rgba(
            49,
            92,
            151,
            .07
        );

}


.processing-ring{

    width:13px;

    height:13px;

    border:
        1.7px solid
        rgba(
            49,
            92,
            151,
            .22
        );

    border-top-color:#315C97;

    border-radius:50%;

    animation:
        stepSpin
        .9s
        linear
        infinite;

}


/* =======================================================
   PENDIENTE
======================================================= */

.step-pending
.step-indicator{

    background:#FFFFFF;

    border-color:#D1DAE3;

}


.pending-dot{

    width:7px;

    height:7px;

    border-radius:50%;

    background:#B3BFCA;

}


/* =======================================================
   CONTENIDO STEP
======================================================= */

.step-content{

    min-width:0;

    flex:1;

    padding:
        1px
        0
        25px;

}


.step-topline{

    display:flex;

    align-items:center;

    flex-wrap:wrap;

    gap:8px;

    margin-bottom:5px;

}


.step-number{

    color:#96A1AC;

    font-size:.57rem;

    font-weight:800;

    letter-spacing:1px;

}


.step-status{

    display:inline-flex;

    align-items:center;

    min-height:20px;

    padding:
        2px
        7px;

    border-radius:999px;

    font-size:.58rem;

    font-weight:800;

    letter-spacing:.35px;

}


.step-status.completed{

    background:#F2F7F3;

    border:
        1px solid
        #D5E3D9;

    color:#52725E;

}


.step-status.processing{

    background:#F2F6FB;

    border:
        1px solid
        #D3E0ED;

    color:#315C97;

}


.step-status.pending{

    background:#F7F9FA;

    border:
        1px solid
        #E1E6EB;

    color:#8A96A2;

}


.step-content h3{

    margin:0;

    color:#263E59;

    font-size:.91rem;

    font-weight:700;

    line-height:1.45;

}


.step-processing
.step-content h3{

    color:#17375E;

}


.step-pending
.step-content h3{

    color:#687889;

}


.step-content p{

    max-width:760px;

    margin:5px 0 0;

    color:#748294;

    font-size:.78rem;

    line-height:1.65;

}


/* =======================================================
   EMPTY STATE
======================================================= */

.empty-steps{

    padding:
        30px
        20px;

    text-align:center;

    background:#FAFBFC;

    border:
        1px dashed
        #D9E1E9;

    border-radius:10px;

}


.empty-steps-label{

    display:block;

    margin-bottom:6px;

    color:#7A6440;

    font-size:.59rem;

    font-weight:800;

    letter-spacing:1.2px;

}


.empty-steps p{

    max-width:520px;

    margin:0 auto;

    color:#7B8997;

    font-size:.8rem;

    line-height:1.6;

}


/* =======================================================
   FOOTER
======================================================= */

.progress-footer{

    display:flex;

    align-items:center;

    gap:11px;

    margin-top:4px;

    padding:
        13px
        15px;

    background:#F6F8FB;

    border:
        1px solid
        #E0E7EE;

    border-radius:9px;

    color:#687789;

}


.progress-footer.completed{

    background:#F5F9F6;

    border-color:#D9E5DC;

    color:#587261;

}


.progress-footer > div{

    display:flex;

    flex-direction:column;

    gap:2px;

    min-width:0;

}


.progress-footer strong{

    color:#40566D;

    font-size:.72rem;

    font-weight:800;

}


.progress-footer.completed strong{

    color:#4D6E59;

}


.progress-footer span:not(.footer-indicator):not(.footer-check){

    font-size:.7rem;

    line-height:1.5;

}


/* =======================================================
   FOOTER INDICADOR
======================================================= */

.footer-indicator{

    width:8px;

    height:8px;

    flex:
        0 0
        8px;

    border-radius:50%;

    background:#315C97;

    box-shadow:
        0 0 0 4px
        rgba(
            49,
            92,
            151,
            .08
        );

    animation:
        footerPulse
        1.6s
        ease-in-out
        infinite;

}


/* =======================================================
   FOOTER CHECK
======================================================= */

.footer-check{

    width:25px;

    height:25px;

    flex:
        0 0
        25px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#E8F1EA;

    color:#52725E;

}


.footer-check svg{

    width:14px;

    height:14px;

}


/* =======================================================
   ANIMACIONES
======================================================= */

@keyframes emblemSpin{

    from{

        transform:rotate(0deg);

    }

    to{

        transform:rotate(360deg);

    }

}


@keyframes stepSpin{

    from{

        transform:rotate(0deg);

    }

    to{

        transform:rotate(360deg);

    }

}


@keyframes footerPulse{

    0%,
    100%{

        opacity:.4;

        transform:scale(.85);

    }

    50%{

        opacity:1;

        transform:scale(1);

    }

}


/* =======================================================
   ACCESIBILIDAD
======================================================= */

@media(
    prefers-reduced-motion:reduce
){

    .emblem-spinner,
    .processing-ring,
    .footer-indicator{

        animation:none;

    }

    .progress-track-fill{

        transition:none;

    }

}


/* =======================================================
   RESPONSIVE — TABLET
======================================================= */

@media(max-width:760px){

    .nova-analysis-progress{

        padding:
            24px
            22px
            20px;

    }


    .progress-header{

        flex-direction:column;

        gap:18px;

    }


    .progress-summary{

        flex-direction:row;

        gap:8px;

        width:auto;

        align-self:flex-start;

    }


    .progress-summary strong{

        margin-top:0;

    }


    .progress-heading h2{

        font-size:1.22rem;

    }


    .progress-heading p{

        font-size:.82rem;

    }

}


/* =======================================================
   RESPONSIVE — MOBILE
======================================================= */

@media(max-width:520px){

    .nova-analysis-progress{

        padding:
            21px
            17px
            18px;

        border-radius:12px;

    }


    .progress-header-main{

        gap:12px;

    }


    .progress-emblem{

        width:42px;

        height:42px;

        flex-basis:42px;

    }


    .emblem-icon{

        width:20px;

        height:20px;

    }


    .progress-eyebrow{

        font-size:.56rem;

        letter-spacing:1.05px;

    }


    .progress-heading h2{

        font-size:1.08rem;

    }


    .progress-heading p{

        font-size:.77rem;

        line-height:1.6;

    }


    .progress-track-wrapper{

        margin:
            18px
            0
            21px;

    }


    .step{

        gap:12px;

        min-height:86px;

    }


    .step-indicator{

        width:34px;

        height:34px;

        flex-basis:34px;

    }


    .step-connector{

        top:34px;

        left:16px;

        height:52px;

    }


    .step-indicator svg{

        width:15px;

        height:15px;

    }


    .processing-ring{

        width:11px;

        height:11px;

    }


    .step-content{

        padding-bottom:22px;

    }


    .step-content h3{

        font-size:.84rem;

    }


    .step-content p{

        font-size:.73rem;

        line-height:1.55;

    }


    .step-number{

        font-size:.52rem;

    }


    .step-status{

        font-size:.54rem;

    }


    .progress-footer{

        align-items:flex-start;

    }

}

</style>