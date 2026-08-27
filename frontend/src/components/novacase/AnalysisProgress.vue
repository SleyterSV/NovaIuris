<template>

    <section
        class="analysis-progress"
        :class="{
            'is-loading': loading,
            'is-complete': !loading && hasCompleted
        }"
    >

        <!-- HEADER -->

        <div class="progress-header">

            <div class="header-icon">

                <span v-if="loading">
                    ⚖️
                </span>

                <span v-else-if="hasCompleted">
                    ✓
                </span>

                <span v-else>
                    ⚖️
                </span>

            </div>

            <div>

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

                    El sistema jurídico inteligente está construyendo
                    el análisis integral del caso. Este proceso puede
                    tardar algunos minutos.

                </p>

                <p v-else-if="hasCompleted">

                    El análisis ha finalizado correctamente.
                    Puedes revisar el informe y sus diferentes secciones.

                </p>

                <p v-else>

                    NovaCase está listo para analizar el caso.

                </p>

            </div>

        </div>


        <!-- PASOS -->

        <div class="steps">

            <div

                v-for="(step, index) in steps"

                :key="step.id || index"

                class="step"

                :class="statusClass(step.status)"

            >

                <!-- CONECTOR -->

                <div
                    v-if="index < steps.length - 1"
                    class="step-line"
                ></div>


                <!-- ICONO -->

                <div class="icon">

                    <span
                        v-if="step.status === 'completed'"
                        class="icon-completed"
                    >

                        ✓

                    </span>

                    <span
                        v-else-if="step.status === 'processing'"
                        class="icon-processing"
                    >

                        ⟳

                    </span>

                    <span
                        v-else
                        class="icon-pending"
                    >

                        ○

                    </span>

                </div>


                <!-- INFORMACIÓN -->

                <div class="content">

                    <div class="title">

                        {{ step.title }}

                    </div>

                    <div class="description">

                        {{ step.description }}

                    </div>

                    <div
                        v-if="step.status === 'processing'"
                        class="processing-label"
                    >

                        Procesando...

                    </div>

                    <div
                        v-else-if="step.status === 'completed'"
                        class="completed-label"
                    >

                        Completado

                    </div>

                </div>

            </div>

        </div>


        <!-- ESTADO INFERIOR -->

        <div
            v-if="loading"
            class="progress-footer"
        >

            <span class="pulse"></span>

            <span>

                NovaCase está procesando la información.
                No cierres esta ventana.

            </span>

        </div>

        <div
            v-else-if="hasCompleted"
            class="progress-footer completed"
        >

            <span class="footer-check">

                ✓

            </span>

            <span>

                Análisis finalizado correctamente.

            </span>

        </div>

    </section>

</template>


<script setup>

import { computed } from "vue"


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


const hasCompleted = computed(() => {

    return (

        props.steps.length > 0 &&

        props.steps.every(
            step => step.status === "completed"
        )

    )

})


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

.analysis-progress {
    width: 100%;
    padding: 32px;

    background: #FFFFFF;

    border: 1px solid #E2E8F0;
    border-radius: 22px;

    box-shadow:
        0 8px 24px rgba(15, 39, 71, 0.06);

    transition:
        border-color .3s ease,
        box-shadow .3s ease;
}

.analysis-progress.is-loading {
    border-color: #BFDBFE;
}

.analysis-progress.is-complete {
    border-color: #BBF7D0;
}


/* ============================================================
   HEADER
============================================================ */

.progress-header {

    display:flex;

    align-items:center;

    gap:18px;

    margin-bottom:30px;

}

.header-icon {
    width: 48px;
    height: 48px;
    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 14px;

    background: #EFF6FF;
    border: 1px solid #BFDBFE;

    font-size: 22px;
}

.is-loading .header-icon {
    animation: headerPulse 2s ease-in-out infinite;
}

.is-complete .header-icon {
    background: #F0FDF4;
    border-color: #BBF7D0;
}


.progress-header h2 {
    margin: 0;
    color: #0F2747;
    font-size: 1.25rem;
    font-weight: 700;
}

.progress-header p {
    margin: 7px 0 0;
    color: #64748B;
    font-size: .92rem;
    line-height: 1.6;
}


/* ============================================================
   STEPS
============================================================ */

.steps {

    display:flex;

    flex-direction:column;

}


.step {

    position:relative;

    display:flex;

    gap:18px;

    min-height:88px;

}


.icon {
    position: relative;
    z-index: 2;

    width: 40px;
    height: 40px;
    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 50%;

    background: #FFFFFF;
    border: 2px solid #CBD5E1;
    color: #64748B;

    font-size: 17px;

    transition: all .3s ease;
}


.step-processing .icon {
    border-color: #2563EB;
    background: #EFF6FF;
    color: #2563EB;

    box-shadow:
        0 0 0 6px rgba(37, 99, 235, 0.06);
}


.icon-processing {

    display:inline-block;

    animation:

        spin 1.2s linear infinite;

}


.step-completed .icon {
    border-color: #15803D;
    background: #F0FDF4;
    color: #15803D;
}


.step-pending .icon {
    border-color: #CBD5E1;
    background: #FFFFFF;
    color: #94A3B8;
}


/* ============================================================
   LINEA
============================================================ */

.step-line {
    position: absolute;
    top: 40px;
    left: 19px;
    width: 2px;
    height: 48px;

    background: #E2E8F0;

    z-index: 1;
}

.step-completed .step-line {
    background: #BBF7D0;
}


/* ============================================================
   CONTENT
============================================================ */

.content {

    padding-top:2px;

    padding-bottom:22px;

}


.title {
    color: #0F2747;
    font-size: .98rem;
    font-weight: 650;
    line-height: 1.4;
}

.step-processing .title {
    color: #0F2747;
}

.step-pending .title {
    color: #64748B;
}

.description {
    margin-top: 5px;
    color: #64748B;
    font-size: .84rem;
    line-height: 1.55;
}

.step-processing .description {
    color: #64748B;
}

.processing-label {
    margin-top: 8px;
    color: #2563EB;
    font-size: .78rem;
    font-weight: 600;
}

.completed-label {
    margin-top: 8px;
    color: #15803D;
    font-size: .78rem;
    font-weight: 600;
}


/* ============================================================
   FOOTER
============================================================ */

.progress-footer {
    display: flex;
    align-items: center;
    gap: 10px;

    margin-top: 12px;
    padding: 14px 16px;

    border-radius: 12px;

    background: #EFF6FF;
    color: #64748B;

    font-size: .82rem;
}

.progress-footer.completed {
    background: #F0FDF4;
    color: #15803D;
}


.pulse {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #2563EB;

    animation:
        pulse 1.5s ease-in-out infinite;
}

.footer-check {
    display: flex;
    align-items: center;
    justify-content: center;

    width: 18px;
    height: 18px;

    border-radius: 50%;

    background: #DCFCE7;
    color: #15803D;

    font-size: 11px;
}


/* ============================================================
   ANIMACIONES
============================================================ */

@keyframes spin {

    from {

        transform:rotate(0deg);

    }

    to {

        transform:rotate(360deg);

    }

}


@keyframes pulse {

    0%,
    100% {

        opacity:.35;

        transform:scale(.85);

    }

    50% {

        opacity:1;

        transform:scale(1.15);

    }

}


@keyframes headerPulse {

    0%,
    100% {

        transform:scale(1);

    }

    50% {

        transform:scale(1.04);

    }

}


/* ============================================================
   RESPONSIVE
============================================================ */

@media(max-width:700px) {

    .analysis-progress {

        padding:24px 20px;

    }

    .progress-header {

        align-items:flex-start;

    }

    .header-icon {

        width:42px;

        height:42px;

    }

    .progress-header h2 {

        font-size:1.05rem;

    }

    .progress-header p {

        font-size:.85rem;

    }

}

</style>