<template>

    <section
        v-if="visible"
        class="nova-search-fallback"
    >

        <!-- ===================================================
             INDICADOR
        ==================================================== -->

        <div class="fallback-indicator">

            <div class="fallback-indicator-inner">

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
                        r="8.5"
                    />

                    <path
                        d="M12 10.5v5"
                    />

                    <circle
                        cx="12"
                        cy="7.2"
                        r=".75"
                        fill="currentColor"
                        stroke="none"
                    />

                </svg>

            </div>

        </div>


        <!-- ===================================================
             CONTENIDO
        ==================================================== -->

        <div class="fallback-content">

            <div class="fallback-header">

                <div class="fallback-heading">

                    <span class="fallback-eyebrow">
                        NOVA SEARCH · CONTEXTO COMPLEMENTARIO
                    </span>

                    <h3>
                        Respuesta generada con contexto adicional
                    </h3>

                </div>


                <span class="fallback-badge">
                    INFORMACIÓN
                </span>

            </div>


            <p class="fallback-message">
                {{ fallbackMessage }}
            </p>


            <div class="fallback-disclaimer">

                <span class="fallback-disclaimer-mark"></span>

                <p>
                    Esta respuesta constituye una orientación jurídica
                    asistida por inteligencia artificial y debe contrastarse
                    con las fuentes jurídicas aplicables y la revisión
                    profesional correspondiente.
                </p>

            </div>

        </div>

    </section>

</template>


<script setup>

/* =========================================================
   PROPS
========================================================= */

import { computed } from "vue"


const props = defineProps({

    message: {

        type: String,

        default: ""

    },

    visible: {

        type: Boolean,

        default: true

    }

})


/* =========================================================
   MENSAJE
========================================================= */

const fallbackMessage = computed(() => {

    const message = props.message?.trim()

    if (message) {

        return message

    }

    return (
        "NovaSearch utilizó un mecanismo alternativo para elaborar "
        + "esta respuesta debido a que el contexto jurídico recuperado "
        + "no fue suficiente para completar el análisis habitual."
    )

})

</script>


<style scoped>

/* =======================================================
   NOVA SEARCH — FALLBACK
   Línea visual institucional
======================================================= */

.nova-search-fallback{

    position:relative;

    width:100%;

    display:flex;

    align-items:flex-start;

    gap:18px;

    padding:22px 24px;

    margin-bottom:22px;

    background:

        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FCFDFE 100%
        );

    border:

        1px solid
        #DCE4EC;

    border-left:

        3px solid
        #B08A4C;

    border-radius:11px;

    box-shadow:

        0 8px 24px
        rgba(
            23,
            55,
            94,
            .045
        );

    animation:

        novaSearchFallbackEnter
        .32s
        ease-out;

}


/* =======================================================
   INDICADOR
======================================================= */

.fallback-indicator{

    width:44px;

    height:44px;

    flex:

        0 0
        44px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#F7F9FC;

    border:

        1px solid
        #DCE5EE;

}


.fallback-indicator-inner{

    width:34px;

    height:34px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#F1F5F9;

    color:#315C97;

}


.fallback-indicator svg{

    width:19px;

    height:19px;

}


/* =======================================================
   CONTENIDO
======================================================= */

.fallback-content{

    flex:1;

    min-width:0;

}


/* =======================================================
   CABECERA
======================================================= */

.fallback-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:20px;

    margin-bottom:9px;

}


.fallback-heading{

    min-width:0;

}


.fallback-eyebrow{

    display:block;

    margin-bottom:5px;

    color:#7A6440;

    font-size:.61rem;

    font-weight:800;

    letter-spacing:1.25px;

}


.fallback-heading h3{

    margin:0;

    color:#17375E;

    font-family:

        Georgia,

        "Times New Roman",

        serif;

    font-size:1.03rem;

    font-weight:600;

    line-height:1.45;

}


/* =======================================================
   BADGE
======================================================= */

.fallback-badge{

    flex-shrink:0;

    display:inline-flex;

    align-items:center;

    justify-content:center;

    min-height:25px;

    padding:

        0
        10px;

    background:#F7F9FC;

    border:

        1px solid
        #D8E2EC;

    border-radius:999px;

    color:#315C97;

    font-size:.57rem;

    font-weight:800;

    letter-spacing:.8px;

}


/* =======================================================
   MENSAJE
======================================================= */

.fallback-message{

    max-width:900px;

    margin:0;

    color:#536273;

    font-size:.86rem;

    line-height:1.75;

}


/* =======================================================
   AVISO / DISCLAIMER
======================================================= */

.fallback-disclaimer{

    display:flex;

    align-items:flex-start;

    gap:9px;

    margin-top:14px;

    padding-top:12px;

    border-top:

        1px solid
        #E8EDF2;

}


.fallback-disclaimer-mark{

    width:5px;

    height:5px;

    flex:

        0 0
        5px;

    margin-top:7px;

    border-radius:50%;

    background:#B08A4C;

}


.fallback-disclaimer p{

    margin:0;

    color:#84909D;

    font-size:.72rem;

    line-height:1.65;

}


/* =======================================================
   ANIMACIÓN
======================================================= */

@keyframes novaSearchFallbackEnter{

    from{

        opacity:0;

        transform:

            translateY(
                8px
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


/* =======================================================
   RESPONSIVE
======================================================= */

@media(max-width:640px){

    .nova-search-fallback{

        flex-direction:column;

        gap:14px;

        padding:20px;

    }


    .fallback-indicator{

        width:42px;

        height:42px;

        flex-basis:42px;

    }


    .fallback-indicator-inner{

        width:32px;

        height:32px;

    }


    .fallback-header{

        flex-direction:column;

        gap:9px;

    }


    .fallback-badge{

        align-self:flex-start;

    }


    .fallback-heading h3{

        font-size:.98rem;

    }


    .fallback-message{

        font-size:.84rem;

    }

}


@media(max-width:420px){

    .nova-search-fallback{

        padding:18px;

        border-radius:10px;

    }


    .fallback-eyebrow{

        font-size:.57rem;

        letter-spacing:1px;

    }


    .fallback-disclaimer{

        gap:8px;

    }

}

</style>