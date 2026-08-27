<template>
    <section
        v-if="visible"
        class="nova-search-fallback"
    >

        <!-- ===================================================
             INDICADOR VISUAL
        ==================================================== -->

        <div class="nova-search-fallback-icon">

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

                <path
                    d="M12 8V12"
                />

                <circle
                    cx="12"
                    cy="16"
                    r=".8"
                    fill="currentColor"
                    stroke="none"
                />

            </svg>

        </div>


        <!-- ===================================================
             CONTENIDO
        ==================================================== -->

        <div class="nova-search-fallback-content">

            <div class="nova-search-fallback-heading">

                <div>

                    <span class="nova-search-fallback-eyebrow">
                        NOVA SEARCH · MODO ALTERNATIVO
                    </span>

                    <h3>
                        Respuesta generada con contexto complementario
                    </h3>

                </div>

                <span class="nova-search-fallback-badge">
                    INFORMACIÓN
                </span>

            </div>


            <p class="nova-search-fallback-message">

                {{ message }}

            </p>


            <p class="nova-search-fallback-note">

                Esta respuesta debe interpretarse como una orientación
                jurídica asistida por inteligencia artificial y no sustituye
                la revisión profesional de las fuentes jurídicas aplicables.

            </p>

        </div>

    </section>
</template>


<script setup>

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


const fallbackMessage = computed(() => {

    return props.message.trim() ||

        "NovaSearch utilizó un mecanismo alternativo para elaborar la respuesta debido a que el contexto jurídico recuperado no fue suficiente para completar el análisis habitual."

})

</script>


<style scoped>

/* =======================================================
   NOVA SEARCH — FALLBACK STATE
======================================================= */

.nova-search-fallback{

    width:100%;

    display:flex;

    align-items:flex-start;

    gap:18px;

    padding:24px 26px;

    margin-bottom:22px;

    background:

        linear-gradient(
            135deg,
            #FFFCF7 0%,
            #FFF9EF 100%
        );

    border:
        1px solid
        #E9DCC5;

    border-left:
        3px solid
        #B08A4C;

    border-radius:12px;

    box-shadow:

        0 10px 26px
        rgba(
            92,
            68,
            30,
            .045
        );

    animation:

        novaSearchFallbackEnter
        .35s
        ease-out;

}


/* =======================================================
   ICONO
======================================================= */

.nova-search-fallback-icon{

    width:46px;

    height:46px;

    flex:
        0 0 46px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#FFF7E8;

    border:
        1px solid
        #E8D4B2;

    color:#9A753B;

}


.nova-search-fallback-icon svg{

    width:23px;

    height:23px;

}


/* =======================================================
   CONTENIDO
======================================================= */

.nova-search-fallback-content{

    flex:1;

    min-width:0;

}


.nova-search-fallback-heading{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:18px;

    margin-bottom:9px;

}


.nova-search-fallback-eyebrow{

    display:block;

    margin-bottom:5px;

    color:#8A6A37;

    font-size:.66rem;

    font-weight:800;

    letter-spacing:1.3px;

}


.nova-search-fallback h3{

    margin:0;

    color:#17375E;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1.08rem;

    font-weight:600;

    line-height:1.4;

}


.nova-search-fallback-message{

    margin:0;

    color:#625847;

    font-size:.9rem;

    line-height:1.7;

}


.nova-search-fallback-note{

    margin:12px 0 0;

    padding-top:12px;

    border-top:

        1px solid
        rgba(
            176,
            138,
            76,
            .18
        );

    color:#857A68;

    font-size:.78rem;

    line-height:1.65;

}


/* =======================================================
   BADGE
======================================================= */

.nova-search-fallback-badge{

    flex-shrink:0;

    display:inline-flex;

    align-items:center;

    justify-content:center;

    min-height:26px;

    padding:
        0
        10px;

    border:
        1px solid
        #DFC89E;

    border-radius:999px;

    background:
        rgba(
            255,
            255,
            255,
            .6
        );

    color:#8A6A37;

    font-size:.62rem;

    font-weight:800;

    letter-spacing:.7px;

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

        padding:22px;

    }


    .nova-search-fallback-icon{

        width:42px;

        height:42px;

        flex-basis:42px;

    }


    .nova-search-fallback-heading{

        flex-direction:column;

        gap:10px;

    }


    .nova-search-fallback-badge{

        align-self:flex-start;

    }

}
</style>