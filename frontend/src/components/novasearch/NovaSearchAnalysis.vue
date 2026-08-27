<template>
    <section
        v-if="hasAnalysis"
        class="nova-search-analysis"
    >
        <!-- =========================================
             HEADER
        ========================================== -->

        <header class="analysis-header">

            <div class="analysis-heading">

                <span class="analysis-eyebrow">
                    ANÁLISIS DE LA CONSULTA
                </span>

                <h2>
                    Interpretación jurídica
                </h2>

                <p>
                    NovaSearch identifica automáticamente la naturaleza,
                    intención y elementos jurídicamente relevantes de la consulta.
                </p>

            </div>


            <div class="analysis-seal">

                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.7"
                    aria-hidden="true"
                >
                    <path
                        d="M12 3a9 9 0 1 0 9 9"
                    />

                    <path
                        d="M12 3v9l6.5 4"
                    />

                    <path
                        d="M9.5 9.5c.7-1.2 2-2 3.5-2
                           2.2 0 4 1.5 4 3.5
                           0 1.3-.8 2.2-1.8 2.8
                           -.9.5-1.7 1-1.7 2.2"
                    />
                </svg>

            </div>

        </header>


        <!-- =========================================
             GRID DE INFORMACIÓN
        ========================================== -->

        <div class="analysis-grid">


            <!-- RAMA JURÍDICA -->

            <article
                v-if="analysis?.rama"
                class="analysis-card"
            >

                <div class="analysis-card-icon">

                    <span>§</span>

                </div>


                <div class="analysis-card-content">

                    <span class="analysis-label">
                        Rama jurídica
                    </span>

                    <strong class="analysis-value">
                        {{ analysis.rama }}
                    </strong>

                </div>

            </article>


            <!-- INTENCIÓN -->

            <article
                v-if="analysis?.intent"
                class="analysis-card"
            >

                <div class="analysis-card-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                    >
                        <circle
                            cx="12"
                            cy="12"
                            r="8"
                        />

                        <path
                            d="M12 8v4l3 2"
                        />
                    </svg>

                </div>


                <div class="analysis-card-content">

                    <span class="analysis-label">
                        Intención detectada
                    </span>

                    <strong class="analysis-value">
                        {{ analysis.intent }}
                    </strong>

                </div>

            </article>


            <!-- CONSULTA NORMALIZADA -->

            <article
                v-if="normalizedQuery"
                class="analysis-card analysis-card-wide"
            >

                <div class="analysis-card-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                    >
                        <path
                            d="M4 6h16"
                        />

                        <path
                            d="M4 12h11"
                        />

                        <path
                            d="M4 18h8"
                        />
                    </svg>

                </div>


                <div class="analysis-card-content">

                    <span class="analysis-label">
                        Consulta interpretada
                    </span>

                    <strong class="analysis-value analysis-value-query">
                        {{ normalizedQuery }}
                    </strong>

                </div>

            </article>


            <!-- ENTIDADES -->

            <article
                v-if="analysis?.entities?.length"
                class="analysis-card analysis-card-entities"
            >

                <div class="analysis-card-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                    >
                        <path
                            d="M8 7a4 4 0 1 0 0-8
                               4 4 0 0 0 0 8Z"
                        />

                        <path
                            d="M16 11a3 3 0 1 0 0-6
                               3 3 0 0 0 0 6Z"
                        />

                        <path
                            d="M2 21v-2a6 6 0 0 1 12 0v2"
                        />

                        <path
                            d="M14 15a5 5 0 0 1 8 4v2"
                        />
                    </svg>

                </div>


                <div class="analysis-card-content">

                    <span class="analysis-label">
                        Conceptos y entidades detectadas
                    </span>


                    <div class="analysis-tags">

                        <span
                            v-for="entity in analysis.entities"
                            :key="entity"
                            class="analysis-tag"
                        >
                            {{ entity }}
                        </span>

                    </div>

                </div>

            </article>


        </div>


        <!-- =========================================
             FOOTER
        ========================================== -->

        <footer class="analysis-footer">

            <div class="analysis-footer-line"></div>

            <span>
                Interpretación generada para optimizar la recuperación
                y clasificación del contexto jurídico.
            </span>

        </footer>

    </section>
</template>


<script setup>

import { computed } from "vue"


const props = defineProps({

    analysis: {

        type: Object,

        default: () => ({})

    },

    normalizedQuery: {

        type: String,

        default: ""

    }

})


/* =========================================
   VERIFICAR SI EXISTE INFORMACIÓN
========================================= */

const hasAnalysis = computed(() => {

    return (

        props.analysis?.rama ||

        props.analysis?.intent ||

        props.normalizedQuery ||

        props.analysis?.entities?.length

    )

})

</script>


<style scoped>

/* =========================================
   NOVA SEARCH — ANALYSIS
========================================= */

.nova-search-analysis{

    width:100%;

    padding:30px 32px;

    background:

        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FCFDFE 60%,
            #F7F9FC 100%
        );

    border:
        1px solid
        #D6DFEA;

    border-radius:12px;

    box-shadow:

        0 12px 30px
        rgba(
            23,
            55,
            94,
            .055
        );

}


/* =========================================
   HEADER
========================================= */

.analysis-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:28px;

    padding-bottom:24px;

    border-bottom:
        1px solid
        #E5EBF1;

}


.analysis-heading{

    min-width:0;

}


.analysis-eyebrow{

    display:block;

    margin-bottom:8px;

    color:#7A6440;

    font-size:.68rem;

    font-weight:800;

    letter-spacing:1.45px;

}


.analysis-heading h2{

    margin:0 0 10px;

    color:#17375E;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1.55rem;

    font-weight:600;

    line-height:1.3;

}


.analysis-heading p{

    max-width:760px;

    margin:0;

    color:#5E6D7E;

    font-size:.94rem;

    line-height:1.75;

}


/* =========================================
   SELLO
========================================= */

.analysis-seal{

    width:64px;

    height:64px;

    flex-shrink:0;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .50
        );

    color:#7A6440;

    background:

        radial-gradient(
            circle,
            rgba(
                176,
                138,
                76,
                .06
            ) 0%,
            transparent 70%
        );

}


.analysis-seal svg{

    width:27px;

    height:27px;

}


/* =========================================
   GRID
========================================= */

.analysis-grid{

    display:grid;

    grid-template-columns:

        repeat(
            2,
            minmax(
                0,
                1fr
            )
        );

    gap:14px;

    margin-top:24px;

}


/* =========================================
   CARD
========================================= */

.analysis-card{

    display:flex;

    align-items:flex-start;

    gap:14px;

    min-width:0;

    padding:18px;

    background:#FFFFFF;

    border:
        1px solid
        #E0E7EF;

    border-radius:10px;

    transition:

        transform
        .2s
        ease,

        border-color
        .2s
        ease,

        box-shadow
        .2s
        ease;

}


.analysis-card:hover{

    transform:

        translateY(
            -2px
        );

    border-color:
        #C8D5E4;

    box-shadow:

        0 8px 20px
        rgba(
            23,
            55,
            94,
            .06
        );

}


.analysis-card-wide{

    grid-column:
        span 2;

}


.analysis-card-entities{

    grid-column:
        span 2;

}


/* =========================================
   ICONOS
========================================= */

.analysis-card-icon{

    width:38px;

    height:38px;

    flex:

        0 0
        38px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:9px;

    background:

        #F6F8FB;

    border:

        1px solid
        #E1E8F0;

    color:#315C97;

}


.analysis-card-icon span{

    color:#315C97;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1.1rem;

    font-weight:600;

}


.analysis-card-icon svg{

    width:19px;

    height:19px;

}


/* =========================================
   CONTENIDO
========================================= */

.analysis-card-content{

    flex:1;

    min-width:0;

}


.analysis-label{

    display:block;

    margin-bottom:6px;

    color:#7A8795;

    font-size:.68rem;

    font-weight:800;

    text-transform:uppercase;

    letter-spacing:1px;

}


.analysis-value{

    display:block;

    color:#17375E;

    font-size:.96rem;

    font-weight:700;

    line-height:1.55;

}


.analysis-value-query{

    color:#30465F;

    font-weight:600;

    white-space:normal;

    word-break:break-word;

}


/* =========================================
   ENTIDADES
========================================= */

.analysis-tags{

    display:flex;

    flex-wrap:wrap;

    gap:8px;

    margin-top:3px;

}


.analysis-tag{

    display:inline-flex;

    align-items:center;

    min-height:28px;

    padding:

        5px
        10px;

    border-radius:999px;

    background:

        #F5F7FA;

    border:

        1px solid
        #DCE5EE;

    color:#315C97;

    font-size:.78rem;

    font-weight:600;

    line-height:1.3;

}


/* =========================================
   FOOTER
========================================= */

.analysis-footer{

    display:flex;

    align-items:center;

    gap:10px;

    margin-top:22px;

    padding-top:18px;

    color:#8491A0;

    font-size:.75rem;

    line-height:1.5;

}


.analysis-footer-line{

    width:18px;

    height:1px;

    flex-shrink:0;

    background:#B08A4C;

}


/* =========================================
   RESPONSIVE
========================================= */

@media(max-width:760px){

    .nova-search-analysis{

        padding:26px 24px;

    }


    .analysis-header{

        gap:20px;

    }


    .analysis-grid{

        grid-template-columns:
            1fr;

    }


    .analysis-card-wide,

    .analysis-card-entities{

        grid-column:
            span 1;

    }

}


@media(max-width:576px){

    .nova-search-analysis{

        padding:22px 18px;

        border-radius:10px;

    }


    .analysis-header{

        flex-direction:column;

    }


    .analysis-seal{

        width:54px;

        height:54px;

    }


    .analysis-heading h2{

        font-size:1.25rem;

    }


    .analysis-heading p{

        font-size:.88rem;

    }


    .analysis-card{

        padding:16px;

    }


    .analysis-footer{

        align-items:flex-start;

    }

}

</style>