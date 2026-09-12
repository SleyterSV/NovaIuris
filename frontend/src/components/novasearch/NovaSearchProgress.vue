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

/* =========================================================
   NOVA SEARCH — PROGRESS
   ESTILO INSTITUCIONAL / JURÍDICO
========================================================= */

.nova-search-progress {
    width: 100%;
    overflow: hidden;
    box-sizing: border-box;

    background:
        linear-gradient(
            145deg,
            #FFFFFF 0%,
            #FCFDFE 58%,
            #F7F9FC 100%
        );

    border: 1px solid #D9E1EA;
    border-radius: 10px;

    box-shadow:
        0 10px 28px rgba(11, 22, 40, .055);

    animation:
        progressEnter
        .35s
        ease-out;
}


/* =========================================================
   HEADER
========================================================= */

.progress-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;

    gap: 28px;

    padding:
        26px
        28px
        23px;

    border-bottom:
        1px solid
        #E3E8EE;
}


.progress-identity {
    display: flex;
    align-items: flex-start;

    gap: 15px;

    min-width: 0;
}


/* =========================================================
   EMBLEMA
========================================================= */

.progress-emblem {
    position: relative;

    width: 52px;
    height: 52px;

    flex: 0 0 52px;

    display: flex;
    align-items: center;
    justify-content: center;

    background:
        #0B1628;

    color: #FFFFFF;

    border:
        1px solid
        rgba(201, 164, 92, .42);

    box-shadow:
        0 7px 18px
        rgba(11, 22, 40, .12);
}


.progress-emblem-ring {
    position: absolute;

    inset: 5px;

    border:
        1px solid
        rgba(201, 164, 92, .55);

    border-radius: 50%;

    pointer-events: none;
}


.progress-emblem-icon {
    position: relative;

    z-index: 1;

    width: 25px;
    height: 25px;
}


/* =========================================================
   CABECERA DE TEXTO
========================================================= */

.progress-heading {
    min-width: 0;
}


.progress-eyebrow {
    display: block;

    margin-bottom: 6px;

    color:
        #9A7A42;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: .60rem;

    font-weight: 800;

    letter-spacing: 1.45px;

    line-height: 1.3;

    text-transform: uppercase;
}


.progress-heading h2 {
    margin: 0;

    color:
        #0B1628;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.42rem;

    font-weight: 500;

    line-height: 1.25;

    letter-spacing: -.15px;
}


.progress-heading p {
    max-width: 700px;

    margin:
        8px
        0
        0;

    color:
        #687386;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: .84rem;

    line-height: 1.65;
}


/* =========================================================
   ESTADO
========================================================= */

.progress-status {
    display: inline-flex;

    align-items: center;
    gap: 8px;

    flex-shrink: 0;

    padding:
        7px
        11px;

    border:
        1px solid
        rgba(201, 164, 92, .30);

    border-radius: 6px;

    background:
        rgba(201, 164, 92, .055);

    color:
        #8A6D3B;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: .64rem;

    font-weight: 800;

    letter-spacing: .65px;

    text-transform: uppercase;
}


.progress-status-dot {
    width: 6px;
    height: 6px;

    flex: 0 0 6px;

    border-radius: 50%;

    background:
        #C9A45C;

    animation:
        statusPulse
        1.5s
        ease-in-out
        infinite;
}


/* =========================================================
   CUERPO
========================================================= */

.progress-body {
    padding:
        23px
        28px
        26px;
}


/* =========================================================
   ETAPA ACTUAL
========================================================= */

.progress-stage-row {
    display: flex;

    align-items: center;
    justify-content: space-between;

    gap: 20px;

    margin-bottom: 11px;
}


.progress-stage-label {
    color:
        #8A97A5;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: .68rem;

    font-weight: 700;

    letter-spacing: .25px;
}


.progress-stage-value {
    color:
        #24354F;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: .76rem;

    font-weight: 700;

    text-align: right;
}


/* =========================================================
   BARRA DE PROGRESO
========================================================= */

.progress-track {
    width: 100%;
    height: 6px;

    overflow: hidden;

    border-radius: 999px;

    background:
        #E8EDF2;
}


.progress-fill {
    position: relative;

    height: 100%;

    min-width: 4px;

    overflow: hidden;

    border-radius: inherit;

    background:
        linear-gradient(
            90deg,
            #0B1628 0%,
            #315C97 72%,
            #C9A45C 100%
        );

    transition:
        width
        .45s
        ease;
}


.progress-fill-glow {
    position: absolute;

    top: 0;
    left: -40%;

    width: 35%;
    height: 100%;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, .42),
            transparent
        );

    animation:
        progressGlow
        1.8s
        linear
        infinite;
}


/* =========================================================
   META
========================================================= */

.progress-meta {
    display: flex;

    align-items: center;
    justify-content: space-between;

    gap: 16px;

    margin-top: 9px;

    color:
        #8A97A5;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: .68rem;

    line-height: 1.4;
}


.progress-meta strong {
    color:
        #24354F;

    font-size: .76rem;

    font-weight: 800;
}


/* =========================================================
   ETAPAS
========================================================= */

.progress-steps {
    display: grid;

    grid-template-columns:
        repeat(
            4,
            minmax(0, 1fr)
        );

    border-top:
        1px solid
        #E3E8EE;

    background:
        #FAFBFC;
}


.progress-step {
    display: flex;

    align-items: center;

    gap: 10px;

    min-width: 0;

    padding:
        16px
        18px;

    border-right:
        1px solid
        #E3E8EE;

    opacity: .52;

    transition:
        opacity
        .25s
        ease,

        background
        .25s
        ease;
}


.progress-step:last-child {
    border-right: none;
}


.progress-step.active {
    opacity: 1;

    background:
        #FFFFFF;
}


/* =========================================================
   INDICADOR DE ETAPA
========================================================= */

.step-indicator {
    width: 29px;
    height: 29px;

    flex: 0 0 29px;

    display: flex;

    align-items: center;
    justify-content: center;

    box-sizing: border-box;

    border:
        1px solid
        #D6DEE7;

    border-radius: 50%;

    background:
        #F3F6F9;

    color:
        #7B8998;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: .60rem;

    font-weight: 800;

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


.progress-step.active .step-indicator {
    border-color:
        rgba(49, 92, 151, .38);

    background:
        #F2F6FA;

    color:
        #315C97;
}


.progress-step.completed .step-indicator {
    border-color:
        #0B1628;

    background:
        #0B1628;

    color:
        #FFFFFF;
}


/* =========================================================
   TEXTO DE ETAPAS
========================================================= */

.progress-step strong {
    display: block;

    margin-bottom: 3px;

    color:
        #52657A;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: .68rem;

    font-weight: 700;

    line-height: 1.3;
}


.progress-step.active strong {
    color:
        #24354F;
}


.progress-step small {
    display: block;

    color:
        #8A97A5;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: .61rem;

    line-height: 1.4;
}


/* =========================================================
   ANIMACIÓN DE ENTRADA
========================================================= */

@keyframes progressEnter {

    from {
        opacity: 0;

        transform:
            translateY(8px);
    }

    to {
        opacity: 1;

        transform:
            translateY(0);
    }

}


/* =========================================================
   BRILLO DE LA BARRA
========================================================= */

@keyframes progressGlow {

    from {
        transform:
            translateX(0);
    }

    to {
        transform:
            translateX(420%);
    }

}


/* =========================================================
   PULSO DE ESTADO
========================================================= */

@keyframes statusPulse {

    0%,
    100% {
        opacity: 1;

        box-shadow:
            0 0 0 0
            rgba(
                201,
                164,
                92,
                .20
            );
    }

    50% {
        opacity: .65;

        box-shadow:
            0 0 0 5px
            rgba(
                201,
                164,
                92,
                0
            );
    }

}


/* =========================================================
   TABLET
========================================================= */

@media (max-width: 900px) {

    .progress-header {
        padding:
            24px;
    }


    .progress-body {
        padding:
            21px
            24px
            24px;
    }


    .progress-steps {
        grid-template-columns:
            repeat(
                2,
                minmax(0, 1fr)
            );
    }


    .progress-step:nth-child(2) {
        border-right: none;
    }


    .progress-step:nth-child(-n + 2) {
        border-bottom:
            1px solid
            #E3E8EE;
    }

}


/* =========================================================
   TABLET PEQUEÑO
========================================================= */

@media (max-width: 640px) {

    .progress-header {
        flex-direction: column;

        gap: 18px;
    }


    .progress-status {
        align-self: flex-start;
    }


    .progress-stage-row {
        flex-direction: column;

        align-items: flex-start;

        gap: 5px;
    }


    .progress-stage-value {
        text-align: left;
    }

}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 520px) {

    .progress-header {
        padding:
            21px
            18px;
    }


    .progress-body {
        padding:
            19px
            18px
            21px;
    }


    .progress-identity {
        gap: 12px;
    }


    .progress-emblem {
        width: 46px;
        height: 46px;

        flex-basis: 46px;
    }


    .progress-emblem-icon {
        width: 21px;
        height: 21px;
    }


    .progress-heading h2 {
        font-size: 1.18rem;
    }


    .progress-heading p {
        font-size: .79rem;

        line-height: 1.65;
    }


    .progress-eyebrow {
        font-size: .56rem;

        letter-spacing: 1.15px;
    }


    .progress-steps {
        grid-template-columns: 1fr;
    }


    .progress-step {
        padding:
            15px
            18px;

        border-right: none;

        border-bottom:
            1px solid
            #E3E8EE;
    }


    .progress-step:last-child {
        border-bottom: none;
    }

}
</style>