<template>

    <section
        v-if="answer"
        class="nova-search-answer"
    >

        <!-- =============================================
             CABECERA
        ============================================== -->

        <header class="nova-search-answer-header">

            <div class="nova-search-answer-brand">

                <div class="nova-search-answer-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.6"
                        aria-hidden="true"
                    >
                        <path
                            d="M12 3L19 6V11C19 15.5 16.2 19.4 12 21C7.8 19.4 5 15.5 5 11V6L12 3Z"
                        />

                        <path
                            d="M8.5 11.5H15.5"
                        />

                        <path
                            d="M12 8.5V14.5"
                        />

                    </svg>

                </div>


                <div class="nova-search-answer-heading">

                    <span class="nova-search-answer-eyebrow">
                        NOVA SEARCH · ANÁLISIS JURÍDICO
                    </span>

                    <h2>
                        Respuesta jurídica
                    </h2>

                    <p>
                        Síntesis estructurada a partir de la información
                        jurídica recuperada y analizada.
                    </p>

                </div>

            </div>


            <div class="nova-search-answer-status">

                <span class="nova-search-answer-status-dot"></span>

                <span>
                    Análisis completado
                </span>

            </div>

        </header>


        <!-- =============================================
             CONTENIDO DE LA RESPUESTA
        ============================================== -->

        <div class="nova-search-answer-body">

            <div class="nova-search-answer-content">

                <p>
                    {{ answer }}
                </p>

            </div>

        </div>


        <!-- =============================================
             MÉTRICAS
        ============================================== -->

        <footer
            v-if="hasMetrics"
            class="nova-search-answer-footer"
        >

            <!-- Tiempo -->

            <div
                v-if="searchTime !== null"
                class="nova-search-answer-metric"
            >

                <div class="nova-search-answer-metric-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        aria-hidden="true"
                    >
                        <circle
                            cx="12"
                            cy="12"
                            r="8"
                        />

                        <path
                            d="M12 8V12L15 14"
                        />

                    </svg>

                </div>


                <div>

                    <span class="nova-search-answer-metric-label">
                        Tiempo de análisis
                    </span>

                    <strong>
                        {{ formattedSearchTime }}
                    </strong>

                </div>

            </div>


            <!-- Fuentes -->

            <div
                v-if="hasTotalResults"
                class="nova-search-answer-metric"
            >

                <div class="nova-search-answer-metric-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        aria-hidden="true"
                    >
                        <path
                            d="M5 4H19V20H5Z"
                        />

                        <path
                            d="M8 8H16"
                        />

                        <path
                            d="M8 12H16"
                        />

                        <path
                            d="M8 16H13"
                        />

                    </svg>

                </div>


                <div>

                    <span class="nova-search-answer-metric-label">
                        Fuentes recuperadas
                    </span>

                    <strong>
                        {{ totalResults }}
                    </strong>

                </div>

            </div>


            <!-- Rama jurídica -->

            <div
                v-if="rama"
                class="nova-search-answer-metric"
            >

                <div class="nova-search-answer-metric-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        aria-hidden="true"
                    >
                        <path
                            d="M12 3V21"
                        />

                        <path
                            d="M7 6H17"
                        />

                        <path
                            d="M8 6L5 11H11L8 6Z"
                        />

                        <path
                            d="M16 6L13 11H19L16 6Z"
                        />

                    </svg>

                </div>


                <div>

                    <span class="nova-search-answer-metric-label">
                        Rama jurídica
                    </span>

                    <strong>
                        {{ rama }}
                    </strong>

                </div>

            </div>

        </footer>


        <!-- =============================================
             NOTA INFORMATIVA
        ============================================== -->

        <div class="nova-search-answer-disclaimer">

            <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                aria-hidden="true"
            >
                <circle
                    cx="12"
                    cy="12"
                    r="9"
                />

                <path
                    d="M12 10V16"
                />

                <path
                    d="M12 7H12.01"
                />

            </svg>

            <p>
                La respuesta es una síntesis generada a partir de las fuentes
                recuperadas por NovaSearch y debe ser contrastada con la
                normativa y jurisprudencia aplicable al caso concreto.
            </p>

        </div>

    </section>

</template>


<script setup>

import {
    computed
} from 'vue'


/* =========================================================
   PROPS
========================================================= */

const props = defineProps({

    answer: {

        type: String,

        default: ''

    },

    searchTime: {

        type: [
            Number,
            String
        ],

        default: null

    },

    totalResults: {

        type: [
            Number,
            String
        ],

        default: 0

    },

    rama: {

        type: String,

        default: ''

    }

})


/* =========================================================
   COMPUTED
========================================================= */

const hasTotalResults = computed(() => {

    return Number(props.totalResults) > 0

})


const hasMetrics = computed(() => {

    return (
        props.searchTime !== null ||
        hasTotalResults.value ||
        Boolean(props.rama)
    )

})


const formattedSearchTime = computed(() => {

    if (
        props.searchTime === null ||
        props.searchTime === undefined ||
        props.searchTime === ''
    ) {

        return '—'

    }


    const time = Number(props.searchTime)


    if (Number.isNaN(time)) {

        return props.searchTime

    }


    if (time < 1000) {

        return `${Math.round(time)} ms`

    }


    return `${(time / 1000).toFixed(2)} s`

})

</script>


<style scoped>

/* =========================================================
   NOVA SEARCH — ANSWER
   Diseño institucional Nova Iuris / NovaCourt
========================================================= */

.nova-search-answer{

    width:100%;

    overflow:hidden;

    background:

        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FCFDFE 65%,
            #F8FAFC 100%
        );

    border:
        1px solid
        #D6DFEA;

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

        novaSearchAnswerEnter
        .4s
        ease-out;

}


/* =========================================================
   CABECERA
========================================================= */

.nova-search-answer-header{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:28px;

    padding:26px 30px;

    border-bottom:

        1px solid
        #E2E8F0;

    background:

        linear-gradient(
            90deg,
            #FFFFFF 0%,
            #FBFCFE 100%
        );

}


.nova-search-answer-brand{

    display:flex;

    align-items:center;

    gap:16px;

    min-width:0;

}


.nova-search-answer-icon{

    width:52px;

    height:52px;

    flex:
        0 0 52px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:12px;

    background:
        #17375E;

    color:
        #FFFFFF;

    box-shadow:

        0 8px 20px
        rgba(
            23,
            55,
            94,
            .14
        );

}


.nova-search-answer-icon svg{

    width:25px;

    height:25px;

}


.nova-search-answer-heading{

    min-width:0;

}


.nova-search-answer-eyebrow{

    display:block;

    margin-bottom:5px;

    color:
        #7A6440;

    font-size:.67rem;

    font-weight:800;

    letter-spacing:1.35px;

}


.nova-search-answer-heading h2{

    margin:0;

    color:
        #17375E;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1.45rem;

    font-weight:600;

    line-height:1.3;

}


.nova-search-answer-heading p{

    margin:

        5px
        0
        0;

    color:
        #6B7A8B;

    font-size:.83rem;

    line-height:1.55;

}


/* =========================================================
   ESTADO
========================================================= */

.nova-search-answer-status{

    display:inline-flex;

    align-items:center;

    gap:8px;

    flex-shrink:0;

    padding:

        8px
        12px;

    border:

        1px solid
        #D9E8DF;

    border-radius:999px;

    background:
        #F5FAF7;

    color:
        #35624B;

    font-size:.72rem;

    font-weight:700;

}


.nova-search-answer-status-dot{

    width:7px;

    height:7px;

    border-radius:50%;

    background:
        #4E8A68;

    box-shadow:

        0 0 0 4px
        rgba(
            78,
            138,
            104,
            .10
        );

}


/* =========================================================
   CUERPO
========================================================= */

.nova-search-answer-body{

    padding:30px;

}


.nova-search-answer-content{

    max-width:1000px;

}


.nova-search-answer-content p{

    margin:0;

    color:
        #344457;

    font-size:.96rem;

    line-height:1.9;

    white-space:
        pre-wrap;

}


/* =========================================================
   FOOTER — MÉTRICAS
========================================================= */

.nova-search-answer-footer{

    display:flex;

    align-items:stretch;

    border-top:

        1px solid
        #E2E8F0;

    background:
        #F8FAFC;

}


.nova-search-answer-metric{

    display:flex;

    align-items:center;

    gap:11px;

    flex:1;

    min-width:0;

    padding:

        16px
        22px;

    border-right:

        1px solid
        #E2E8F0;

}


.nova-search-answer-metric:last-child{

    border-right:none;

}


.nova-search-answer-metric-icon{

    width:34px;

    height:34px;

    flex:
        0 0 34px;

    display:flex;

    align-items:center;

    justify-content:center;

    border:

        1px solid
        #D6DFEA;

    border-radius:9px;

    background:
        #FFFFFF;

    color:
        #315C97;

}


.nova-search-answer-metric-icon svg{

    width:16px;

    height:16px;

}


.nova-search-answer-metric-label{

    display:block;

    margin-bottom:3px;

    color:
        #8794A3;

    font-size:.62rem;

    font-weight:800;

    letter-spacing:.7px;

    text-transform:uppercase;

}


.nova-search-answer-metric strong{

    display:block;

    overflow:hidden;

    color:
        #17375E;

    font-size:.82rem;

    font-weight:700;

    white-space:nowrap;

    text-overflow:ellipsis;

}


/* =========================================================
   DISCLAIMER
========================================================= */

.nova-search-answer-disclaimer{

    display:flex;

    align-items:flex-start;

    gap:10px;

    padding:

        15px
        30px;

    border-top:

        1px solid
        rgba(
            176,
            138,
            76,
            .16
        );

    background:
        #FCFAF6;

}


.nova-search-answer-disclaimer svg{

    width:17px;

    height:17px;

    flex-shrink:0;

    margin-top:2px;

    color:
        #9A7A42;

}


.nova-search-answer-disclaimer p{

    margin:0;

    color:
        #7A6A4C;

    font-size:.73rem;

    line-height:1.65;

}


/* =========================================================
   ANIMACIÓN
========================================================= */

@keyframes novaSearchAnswerEnter{

    from{

        opacity:0;

        transform:
            translateY(10px);

    }

    to{

        opacity:1;

        transform:
            translateY(0);

    }

}


/* =========================================================
   RESPONSIVE
========================================================= */

@media(max-width:850px){

    .nova-search-answer-header{

        align-items:flex-start;

        flex-direction:column;

        padding:24px;

    }


    .nova-search-answer-status{

        align-self:flex-start;

    }


    .nova-search-answer-body{

        padding:24px;

    }


    .nova-search-answer-disclaimer{

        padding:15px 24px;

    }


    .nova-search-answer-footer{

        flex-wrap:wrap;

    }


    .nova-search-answer-metric{

        flex:

            1 1 45%;

        border-bottom:

            1px solid
            #E2E8F0;

    }

}


@media(max-width:600px){

    .nova-search-answer{

        border-radius:10px;

    }


    .nova-search-answer-header{

        padding:22px 18px;

    }


    .nova-search-answer-brand{

        align-items:flex-start;

    }


    .nova-search-answer-icon{

        width:46px;

        height:46px;

        flex-basis:46px;

        border-radius:10px;

    }


    .nova-search-answer-icon svg{

        width:22px;

        height:22px;

    }


    .nova-search-answer-heading h2{

        font-size:1.25rem;

    }


    .nova-search-answer-heading p{

        font-size:.78rem;

    }


    .nova-search-answer-body{

        padding:22px 18px;

    }


    .nova-search-answer-content p{

        font-size:.91rem;

        line-height:1.82;

    }


    .nova-search-answer-footer{

        flex-direction:column;

    }


    .nova-search-answer-metric{

        width:100%;

        padding:15px 18px;

        border-right:none;

    }


    .nova-search-answer-disclaimer{

        padding:14px 18px;

    }

}
</style>