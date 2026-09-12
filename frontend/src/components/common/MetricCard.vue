<template>

    <article
        class="metric-card"
        :style="cardStyle"
    >

        <!-- =====================================================
             INDICADOR SUPERIOR
        ====================================================== -->

        <div class="metric-accent"></div>


        <!-- =====================================================
             ICONO
        ====================================================== -->

        <div
            class="metric-icon"
            :style="iconStyle"
            aria-hidden="true"
        >

            <span>
                {{ icon }}
            </span>

        </div>


        <!-- =====================================================
             INFORMACIÓN
        ====================================================== -->

        <div class="metric-info">

            <span class="metric-title">

                {{ title }}

            </span>


            <strong class="metric-value">

                {{ animatedValue }}

            </strong>

        </div>


        <!-- =====================================================
             DETALLE VISUAL
        ====================================================== -->

        <div class="metric-indicator">

            <span></span>
            <span></span>
            <span></span>

        </div>

    </article>

</template>


<script setup>

import {
    computed,
    ref,
    onMounted,
    onBeforeUnmount,
    watch
} from "vue"


/* ============================================================
   PROPS
============================================================ */

const props = defineProps({

    title: {

        type: String,

        required: true

    },

    value: {

        type: [
            String,
            Number
        ],

        required: true

    },

    icon: {

        type: String,

        default: "📊"

    },

    color: {

        type: String,

        default: "#2563EB"

    }

})


/* ============================================================
   ESTILOS DINÁMICOS
============================================================ */

const iconStyle = computed(() => ({

    background: `${props.color}12`,

    color: props.color,

    borderColor: `${props.color}24`

}))


const cardStyle = computed(() => ({

    "--metric-accent": props.color,

    "--metric-color": props.color,

    "--metric-soft": `${props.color}10`,

    "--metric-border": `${props.color}28`

}))


/* ============================================================
   VALOR ANIMADO
============================================================ */

const animatedValue = ref(props.value)

let animationFrame = null


function cancelAnimation() {

    if (animationFrame !== null) {

        cancelAnimationFrame(
            animationFrame
        )

        animationFrame = null

    }

}


/* ============================================================
   ANIMACIÓN NUMÉRICA
============================================================ */

function animateNumber() {

    cancelAnimation()


    if (
        typeof props.value !== "number" ||
        !Number.isFinite(props.value)
    ) {

        animatedValue.value =
            props.value

        return

    }


    const end =
        props.value


    if (end === 0) {

        animatedValue.value = 0

        return

    }


    const duration = 650

    const startTime =
        performance.now()


    function update(currentTime) {

        const elapsed =
            currentTime - startTime


        const progress =
            Math.min(
                elapsed / duration,
                1
            )


        /*
         * Curva de desaceleración
         * para una animación más natural.
         */

        const eased =
            1 -
            Math.pow(
                1 - progress,
                3
            )


        const current =
            end * eased


        animatedValue.value =
            Math.round(current)


        if (progress < 1) {

            animationFrame =
                requestAnimationFrame(
                    update
                )

        } else {

            animatedValue.value =
                end

            animationFrame = null

        }

    }


    animationFrame =
        requestAnimationFrame(
            update
        )

}


/* ============================================================
   CICLO DE VIDA
============================================================ */

onMounted(() => {

    animateNumber()

})


watch(
    () => props.value,
    () => {

        animateNumber()

    }
)


onBeforeUnmount(() => {

    cancelAnimation()

})

</script>


<style scoped>

/* ============================================================
   VARIABLES
============================================================ */

.metric-card {

    --metric-accent: #2563EB;
    --metric-color: #2563EB;
    --metric-soft: #EFF6FF;
    --metric-border: #DBEAFE;

    position: relative;

    display: flex;

    align-items: center;

    gap: 17px;

    min-width: 0;

    padding: 21px 22px;

    overflow: hidden;

    background: #FFFFFF;

    border:
        1px solid #E2E8F0;

    border-radius: 18px;

    box-shadow:
        0 6px 18px
        rgba(
            15,
            39,
            71,
            .045
        );

    transition:
        transform .28s ease,
        box-shadow .28s ease,
        border-color .28s ease;

    animation:
        metricAppear
        .45s
        ease
        both;

}


/* ============================================================
   ACENTO LATERAL
============================================================ */

.metric-accent {

    position: absolute;

    top: 0;

    left: 0;

    width: 3px;

    height: 100%;

    background:
        var(--metric-accent);

    border-radius:
        3px 0 0 3px;

    opacity: .9;

}


/* ============================================================
   EFECTO SUPERIOR SUTIL
============================================================ */

.metric-card::after {

    content: "";

    position: absolute;

    top: 0;

    right: 0;

    width: 110px;

    height: 110px;

    background:
        radial-gradient(
            circle,
            var(--metric-soft) 0%,
            transparent 70%
        );

    pointer-events: none;

}


/* ============================================================
   HOVER
============================================================ */

.metric-card:hover {

    transform:
        translateY(-3px);

    border-color:
        var(--metric-border);

    box-shadow:
        0 12px 28px
        rgba(
            15,
            39,
            71,
            .075
        );

}


/* ============================================================
   ICONO
============================================================ */

.metric-icon {

    position: relative;

    z-index: 1;

    display: flex;

    align-items: center;

    justify-content: center;

    width: 56px;

    height: 56px;

    flex-shrink: 0;

    border:
        1px solid
        var(--metric-border);

    border-radius: 15px;

    font-size: 1.5rem;

    line-height: 1;

    box-shadow:
        0 4px 10px
        rgba(
            15,
            39,
            71,
            .035
        );

    transition:
        transform .28s ease,
        box-shadow .28s ease;

}


.metric-icon span {

    display: block;

    line-height: 1;

}


.metric-card:hover
.metric-icon {

    transform:
        scale(1.06);

    box-shadow:
        0 7px 16px
        rgba(
            37,
            99,
            235,
            .12
        );

}


/* ============================================================
   INFORMACIÓN
============================================================ */

.metric-info {

    position: relative;

    z-index: 1;

    display: flex;

    flex-direction: column;

    justify-content: center;

    gap: 5px;

    min-width: 0;

    flex: 1;

}


/* ============================================================
   TÍTULO
============================================================ */

.metric-title {

    display: block;

    overflow: hidden;

    color: #64748B;

    font-size: .69rem;

    font-weight: 750;

    line-height: 1.35;

    text-transform: uppercase;

    letter-spacing: .085em;

    text-overflow: ellipsis;

    white-space: nowrap;

}


/* ============================================================
   VALOR
============================================================ */

.metric-value {

    display: block;

    overflow-wrap: anywhere;

    color: #0F2747;

    font-size: 1.24rem;

    font-weight: 750;

    line-height: 1.3;

    letter-spacing: -.018em;

    transition:
        color .25s ease;

}


.metric-card:hover
.metric-value {

    color:
        var(--metric-color);

}


/* ============================================================
   INDICADOR VISUAL
============================================================ */

.metric-indicator {

    position: relative;

    z-index: 1;

    display: flex;

    align-items: flex-end;

    gap: 3px;

    align-self: flex-end;

    height: 20px;

    padding-bottom: 1px;

    opacity: .55;

    transition:
        opacity .25s ease,
        transform .25s ease;

}


.metric-indicator span {

    display: block;

    width: 3px;

    border-radius:
        999px;

    background:
        var(--metric-color);

}


.metric-indicator span:nth-child(1) {

    height: 7px;

}


.metric-indicator span:nth-child(2) {

    height: 12px;

}


.metric-indicator span:nth-child(3) {

    height: 17px;

}


.metric-card:hover
.metric-indicator {

    opacity: .85;

    transform:
        translateX(-2px);

}


/* ============================================================
   ANIMACIÓN
============================================================ */

@keyframes metricAppear {

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


/* ============================================================
   ACCESIBILIDAD
============================================================ */

@media (
    prefers-reduced-motion: reduce
) {

    .metric-card,
    .metric-icon,
    .metric-value,
    .metric-indicator {

        animation: none;

        transition: none;

    }

}


/* ============================================================
   RESPONSIVE — TABLET
============================================================ */

@media (max-width: 768px) {

    .metric-card {

        gap: 14px;

        padding: 18px;

        border-radius: 17px;

    }


    .metric-icon {

        width: 52px;

        height: 52px;

        border-radius: 14px;

        font-size: 1.38rem;

    }


    .metric-title {

        font-size: .66rem;

    }


    .metric-value {

        font-size: 1.12rem;

    }


    .metric-indicator {

        display: none;

    }

}


/* ============================================================
   RESPONSIVE — MOBILE
============================================================ */

@media (max-width: 576px) {

    .metric-card {

        gap: 13px;

        padding: 17px;

        border-radius: 16px;

    }


    .metric-icon {

        width: 48px;

        height: 48px;

        border-radius: 13px;

        font-size: 1.25rem;

    }


    .metric-title {

        font-size: .63rem;

        letter-spacing: .065em;

    }


    .metric-value {

        font-size: 1.04rem;

        line-height: 1.35;

    }

}


/* ============================================================
   MOBILE MUY PEQUEÑO
============================================================ */

@media (max-width: 380px) {

    .metric-card {

        gap: 11px;

        padding: 15px;

    }


    .metric-icon {

        width: 44px;

        height: 44px;

        font-size: 1.15rem;

    }


    .metric-value {

        font-size: .98rem;

    }

}

</style>