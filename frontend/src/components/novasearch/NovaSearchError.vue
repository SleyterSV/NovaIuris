<template>

    <section
        v-if="message"
        class="nova-search-error"
        role="alert"
        aria-live="polite"
    >

        <!-- ===================================================
             INDICADOR
        ==================================================== -->

        <div class="error-indicator">

            <div class="error-indicator-inner">

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
                        d="M12 8v5"
                    />

                    <circle
                        cx="12"
                        cy="16.4"
                        r=".7"
                        fill="currentColor"
                        stroke="none"
                    />

                </svg>

            </div>

        </div>


        <!-- ===================================================
             CONTENIDO
        ==================================================== -->

        <div class="error-content">

            <div class="error-header">

                <div class="error-heading">

                    <span class="error-eyebrow">
                        NOVA SEARCH · SISTEMA DE BÚSQUEDA
                    </span>

                    <h3>
                        No fue posible completar la búsqueda
                    </h3>

                </div>


                <span class="error-badge">
                    ERROR
                </span>

            </div>


            <!-- MENSAJE -->

            <p class="error-message">
                {{ message }}
            </p>


            <!-- AYUDA -->

            <div class="error-help">

                <span class="error-help-mark"></span>

                <span>
                    Verifica tu conexión o reformula la consulta
                    e inténtalo nuevamente.
                </span>

            </div>

        </div>


        <!-- ===================================================
             ACCIÓN
        ==================================================== -->

        <button
            v-if="showRetry"
            type="button"
            class="error-retry-button"
            @click="$emit('retry')"
        >

            <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                aria-hidden="true"
            >

                <path
                    d="M20 11a8 8 0 1 0 1 4"
                />

                <path
                    d="M20 5v6h-6"
                />

            </svg>

            <span>
                Intentar nuevamente
            </span>

        </button>

    </section>

</template>


<script setup>

/* =========================================================
   PROPS
========================================================= */

defineProps({

    message: {

        type: String,

        default: ""

    },

    showRetry: {

        type: Boolean,

        default: true

    }

})


/* =========================================================
   EVENTOS
========================================================= */

defineEmits([

    "retry"

])

</script>


<style scoped>

/* =======================================================
   NOVA SEARCH — ERROR STATE
   Estado de error institucional
======================================================= */

.nova-search-error{

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
        #A34B4B;

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

        novaSearchErrorEnter
        .32s
        ease-out;

}


/* =======================================================
   INDICADOR
======================================================= */

.error-indicator{

    width:44px;

    height:44px;

    flex:

        0 0
        44px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#FBF7F7;

    border:

        1px solid
        #E9DADA;

}


.error-indicator-inner{

    width:34px;

    height:34px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#F9EEEE;

    color:#A34B4B;

}


.error-indicator svg{

    width:19px;

    height:19px;

}


/* =======================================================
   CONTENIDO
======================================================= */

.error-content{

    flex:1;

    min-width:0;

}


/* =======================================================
   CABECERA
======================================================= */

.error-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:20px;

    margin-bottom:9px;

}


.error-heading{

    min-width:0;

}


.error-eyebrow{

    display:block;

    margin-bottom:5px;

    color:#7A6440;

    font-size:.61rem;

    font-weight:800;

    letter-spacing:1.2px;

}


.error-heading h3{

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

.error-badge{

    flex-shrink:0;

    display:inline-flex;

    align-items:center;

    justify-content:center;

    min-height:25px;

    padding:

        0
        10px;

    background:#FBF7F7;

    border:

        1px solid
        #E5CFCF;

    border-radius:999px;

    color:#9A5555;

    font-size:.57rem;

    font-weight:800;

    letter-spacing:.8px;

}


/* =======================================================
   MENSAJE
======================================================= */

.error-message{

    max-width:900px;

    margin:0;

    color:#536273;

    font-size:.86rem;

    line-height:1.75;

}


/* =======================================================
   AYUDA
======================================================= */

.error-help{

    display:flex;

    align-items:flex-start;

    gap:9px;

    margin-top:14px;

    padding-top:12px;

    border-top:

        1px solid
        #E8EDF2;

    color:#84909D;

    font-size:.72rem;

    line-height:1.65;

}


.error-help-mark{

    width:5px;

    height:5px;

    flex:

        0 0
        5px;

    margin-top:7px;

    border-radius:50%;

    background:#B08A4C;

}


/* =======================================================
   BOTÓN
======================================================= */

.error-retry-button{

    flex-shrink:0;

    min-height:40px;

    display:inline-flex;

    align-items:center;

    justify-content:center;

    gap:8px;

    padding:

        0
        15px;

    background:#FFFFFF;

    border:

        1px solid
        #D3DDE7;

    border-radius:8px;

    color:#315C97;

    font-family:inherit;

    font-size:.76rem;

    font-weight:750;

    cursor:pointer;

    transition:

        background
        .2s
        ease,

        border-color
        .2s
        ease,

        color
        .2s
        ease,

        transform
        .2s
        ease,

        box-shadow
        .2s
        ease;

}


.error-retry-button svg{

    width:16px;

    height:16px;

}


.error-retry-button:hover{

    background:#F6F8FB;

    border-color:#B9C8D8;

    color:#17375E;

    transform:

        translateY(
            -1px
        );

    box-shadow:

        0 6px 14px
        rgba(
            23,
            55,
            94,
            .07
        );

}


.error-retry-button:active{

    transform:

        translateY(
            0
        );

    box-shadow:none;

}


.error-retry-button:focus-visible{

    outline:

        2px solid
        #315C97;

    outline-offset:3px;

}


/* =======================================================
   ANIMACIÓN
======================================================= */

@keyframes novaSearchErrorEnter{

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

@media(max-width:700px){

    .nova-search-error{

        flex-direction:column;

        gap:14px;

        padding:21px;

    }


    .error-header{

        flex-direction:column;

        gap:9px;

    }


    .error-badge{

        align-self:flex-start;

    }


    .error-retry-button{

        width:100%;

    }

}


@media(max-width:576px){

    .nova-search-error{

        padding:19px;

        border-radius:10px;

    }


    .error-indicator{

        width:42px;

        height:42px;

        flex-basis:42px;

    }


    .error-indicator-inner{

        width:32px;

        height:32px;

    }


    .error-heading h3{

        font-size:.98rem;

    }


    .error-message{

        font-size:.84rem;

    }


    .error-help{

        font-size:.7rem;

    }

}

</style>