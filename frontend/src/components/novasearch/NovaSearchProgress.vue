<template>
    <section
        class="nova-search-progress"
        aria-live="polite"
    >

        <!-- ENCABEZADO -->

        <div class="progress-header">

            <div class="progress-identity">

                <div class="progress-emblem">

                    <svg
                        class="progress-emblem-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.6"
                        aria-hidden="true"
                    >
                        <path
                            d="M12 3v18"
                        />

                        <path
                            d="M5 7h14"
                        />

                        <path
                            d="M7 7l-3 7h6l-3-7Z"
                        />

                        <path
                            d="M17 7l-3 7h6l-3-7Z"
                        />

                        <path
                            d="M8 21h8"
                        />
                    </svg>

                    <span class="progress-emblem-ring"></span>

                </div>


                <div class="progress-heading">

                    <span class="progress-eyebrow">
                        NOVA SEARCH · PROCESAMIENTO ACTIVO
                    </span>

                    <h2>
                        Analizando información jurídica
                    </h2>

                    <p>
                        NovaSearch está interpretando tu consulta y recuperando
                        información relevante para estructurar una respuesta.
                    </p>

                </div>

            </div>


            <!-- ESTADO -->

            <div class="progress-status">

                <span class="progress-status-dot"></span>

                <span>
                    En proceso
                </span>

            </div>

        </div>


        <!-- CUERPO -->

        <div class="progress-body">

            <!-- ETAPA ACTUAL -->

            <div class="progress-stage-row">

                <span class="progress-stage-label">
                    Etapa actual
                </span>

                <strong class="progress-stage-value">
                    {{ currentStage }}
                </strong>

            </div>


            <!-- BARRA -->

            <div
                class="progress-track"
                role="progressbar"
                aria-valuemin="0"
                aria-valuemax="100"
                :aria-valuenow="normalizedProgress"
            >

                <div
                    class="progress-fill"
                    :style="{
                        width: `${normalizedProgress}%`
                    }"
                >

                    <span class="progress-fill-glow"></span>

                </div>

            </div>


            <!-- META -->

            <div class="progress-meta">

                <span>
                    Procesamiento jurídico inteligente
                </span>

                <strong>
                    {{ normalizedProgress }}%
                </strong>

            </div>

        </div>


        <!-- ETAPAS -->

        <div class="progress-steps">

            <div
                class="progress-step"
                :class="{
                    active: normalizedProgress >= 15,
                    completed: normalizedProgress >= 25
                }"
            >

                <span class="step-indicator">
                    01
                </span>

                <div>

                    <strong>
                        Interpretación
                    </strong>

                    <small>
                        Comprensión de la consulta
                    </small>

                </div>

            </div>


            <div
                class="progress-step"
                :class="{
                    active: normalizedProgress >= 30,
                    completed: normalizedProgress >= 55
                }"
            >

                <span class="step-indicator">
                    02
                </span>

                <div>

                    <strong>
                        Recuperación
                    </strong>

                    <small>
                        Búsqueda de fuentes relevantes
                    </small>

                </div>

            </div>


            <div
                class="progress-step"
                :class="{
                    active: normalizedProgress >= 60,
                    completed: normalizedProgress >= 85
                }"
            >

                <span class="step-indicator">
                    03
                </span>

                <div>

                    <strong>
                        Análisis
                    </strong>

                    <small>
                        Evaluación del contexto jurídico
                    </small>

                </div>

            </div>


            <div
                class="progress-step"
                :class="{
                    active: normalizedProgress >= 90,
                    completed: normalizedProgress >= 100
                }"
            >

                <span class="step-indicator">
                    04
                </span>

                <div>

                    <strong>
                        Síntesis
                    </strong>

                    <small>
                        Construcción de la respuesta
                    </small>

                </div>

            </div>

        </div>

    </section>
</template>


<script setup>

import { computed } from "vue"


const props = defineProps({

    stage: {

        type: String,

        default: ""

    },

    progress: {

        type: Number,

        default: 0

    }

})


/* =========================================
   PROGRESO NORMALIZADO
========================================= */

const normalizedProgress = computed(() => {

    const value = Number(props.progress) || 0

    return Math.min(
        100,
        Math.max(
            0,
            Math.round(value)
        )
    )

})


/* =========================================
   ETAPA ACTUAL
========================================= */

const currentStage = computed(() => {

    if (
        props.stage &&
        props.stage.trim()
    ) {

        return props.stage

    }


    const progress = normalizedProgress.value


    if (progress < 25) {

        return "Interpretando la consulta jurídica"

    }


    if (progress < 55) {

        return "Recuperando información relevante"

    }


    if (progress < 85) {

        return "Analizando el contexto jurídico"

    }


    if (progress < 100) {

        return "Estructurando la respuesta jurídica"

    }


    return "Análisis completado"

})

</script>


<style scoped>

/* =========================================
   NOVA SEARCH PROGRESS
========================================= */

.nova-search-progress{

    width:100%;

    overflow:hidden;

    background:
        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FBFCFE 100%
        );

    border:
        1px solid
        #DCE3EB;

    border-radius:12px;

    box-shadow:

        0 14px 34px
        rgba(
            23,
            55,
            94,
            .06
        );

    animation:

        progressEnter
        .35s
        ease-out;

}


/* =========================================
   HEADER
========================================= */

.progress-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:28px;

    padding:
        28px
        30px
        24px;

    border-bottom:
        1px solid
        #E3E8EE;

}


.progress-identity{

    display:flex;

    align-items:flex-start;

    gap:16px;

    min-width:0;

}


/* =========================================
   EMBLEMA
========================================= */

.progress-emblem{

    position:relative;

    width:56px;

    height:56px;

    flex:0 0 56px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#17375E;

    color:#FFFFFF;

    box-shadow:

        0 8px 20px
        rgba(
            23,
            55,
            94,
            .14
        );

}


.progress-emblem-ring{

    position:absolute;

    inset:5px;

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .65
        );

    border-radius:50%;

}


.progress-emblem-icon{

    position:relative;

    z-index:1;

    width:26px;

    height:26px;

}


/* =========================================
   TÍTULOS
========================================= */

.progress-heading{

    min-width:0;

}


.progress-eyebrow{

    display:block;

    margin-bottom:6px;

    color:#7A6440;

    font-size:.64rem;

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

    font-size:1.45rem;

    font-weight:600;

    line-height:1.3;

}


.progress-heading p{

    max-width:700px;

    margin:

        8px
        0
        0;

    color:#6A7989;

    font-size:.88rem;

    line-height:1.65;

}


/* =========================================
   ESTADO
========================================= */

.progress-status{

    display:inline-flex;

    align-items:center;

    gap:8px;

    flex-shrink:0;

    padding:

        8px
        12px;

    border:
        1px solid
        #D7E3F0;

    border-radius:999px;

    background:#F7FAFD;

    color:#315C97;

    font-size:.72rem;

    font-weight:700;

}


.progress-status-dot{

    width:7px;

    height:7px;

    border-radius:50%;

    background:#315C97;

    animation:

        statusPulse
        1.5s
        ease-in-out
        infinite;

}


/* =========================================
   CUERPO
========================================= */

.progress-body{

    padding:
        24px
        30px
        28px;

}


.progress-stage-row{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:20px;

    margin-bottom:12px;

}


.progress-stage-label{

    color:#8794A2;

    font-size:.72rem;

    font-weight:700;

}


.progress-stage-value{

    color:#29415D;

    font-size:.78rem;

    font-weight:700;

    text-align:right;

}


/* =========================================
   BARRA
========================================= */

.progress-track{

    width:100%;

    height:7px;

    overflow:hidden;

    border-radius:999px;

    background:#E8EDF2;

}


.progress-fill{

    position:relative;

    height:100%;

    min-width:4px;

    overflow:hidden;

    border-radius:inherit;

    background:

        linear-gradient(
            90deg,
            #17375E,
            #315C97
        );

    transition:

        width
        .45s
        ease;

}


.progress-fill-glow{

    position:absolute;

    top:0;

    left:-40%;

    width:35%;

    height:100%;

    background:

        linear-gradient(
            90deg,
            transparent,
            rgba(
                255,
                255,
                255,
                .45
            ),
            transparent
        );

    animation:

        progressGlow
        1.8s
        linear
        infinite;

}


/* =========================================
   META
========================================= */

.progress-meta{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:16px;

    margin-top:10px;

    color:#8A97A5;

    font-size:.72rem;

}


.progress-meta strong{

    color:#17375E;

    font-size:.8rem;

    font-weight:800;

}


/* =========================================
   ETAPAS
========================================= */

.progress-steps{

    display:grid;

    grid-template-columns:

        repeat(
            4,
            minmax(0,1fr)
        );

    border-top:
        1px solid
        #E3E8EE;

    background:#FBFCFE;

}


.progress-step{

    display:flex;

    align-items:center;

    gap:10px;

    min-width:0;

    padding:

        18px
        20px;

    border-right:
        1px solid
        #E3E8EE;

    opacity:.58;

    transition:

        opacity
        .25s
        ease,

        background
        .25s
        ease;

}


.progress-step:last-child{

    border-right:none;

}


.progress-step.active{

    opacity:1;

    background:#FFFFFF;

}


.step-indicator{

    width:30px;

    height:30px;

    flex:0 0 30px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#EDF2F7;

    border:
        1px solid
        #D8E0E8;

    color:#718096;

    font-size:.65rem;

    font-weight:800;

    transition:

        background
        .25s
        ease,

        border-color
        .25s
        ease,

        color
        .25s
        ease;

}


.progress-step.active .step-indicator{

    background:#EFF4FA;

    border-color:#B7C8DB;

    color:#315C97;

}


.progress-step.completed .step-indicator{

    background:#17375E;

    border-color:#17375E;

    color:#FFFFFF;

}


.progress-step strong{

    display:block;

    margin-bottom:3px;

    color:#465A70;

    font-size:.72rem;

    font-weight:750;

}


.progress-step.active strong{

    color:#17375E;

}


.progress-step small{

    display:block;

    color:#8A97A5;

    font-size:.64rem;

    line-height:1.4;

}


/* =========================================
   ANIMACIONES
========================================= */

@keyframes progressEnter{

    from{

        opacity:0;

        transform:
            translateY(
                10px
            );

    }

    to{

        opacity:1;

        transform:
            translateY(
                0
            );

    }

}


@keyframes progressGlow{

    from{

        transform:
            translateX(
                0
            );

    }

    to{

        transform:
            translateX(
                420%
            );

    }

}


@keyframes statusPulse{

    0%,
    100%{

        opacity:1;

        box-shadow:

            0 0 0 0
            rgba(
                49,
                92,
                151,
                .25
            );

    }

    50%{

        opacity:.65;

        box-shadow:

            0 0 0 5px
            rgba(
                49,
                92,
                151,
                0
            );

    }

}


/* =========================================
   RESPONSIVE
========================================= */

@media(max-width:900px){

    .progress-header{

        padding:
            24px;

    }


    .progress-body{

        padding:
            22px
            24px
            24px;

    }


    .progress-steps{

        grid-template-columns:

            repeat(
                2,
                minmax(0,1fr)
            );

    }


    .progress-step:nth-child(2){

        border-right:none;

    }


    .progress-step:nth-child(-n+2){

        border-bottom:
            1px solid
            #E3E8EE;

    }

}


@media(max-width:640px){

    .progress-header{

        flex-direction:column;

        gap:20px;

    }


    .progress-status{

        align-self:flex-start;

    }


    .progress-stage-row{

        flex-direction:column;

        align-items:flex-start;

        gap:5px;

    }


    .progress-stage-value{

        text-align:left;

    }

}


@media(max-width:520px){

    .progress-header{

        padding:
            22px
            18px;

    }


    .progress-body{

        padding:
            20px
            18px
            22px;

    }


    .progress-identity{

        gap:13px;

    }


    .progress-emblem{

        width:48px;

        height:48px;

        flex-basis:48px;

    }


    .progress-emblem-icon{

        width:22px;

        height:22px;

    }


    .progress-heading h2{

        font-size:1.2rem;

    }


    .progress-heading p{

        font-size:.82rem;

    }


    .progress-steps{

        grid-template-columns:1fr;

    }


    .progress-step{

        border-right:none;

        border-bottom:
            1px solid
            #E3E8EE;

    }


    .progress-step:last-child{

        border-bottom:none;

    }

}
</style>