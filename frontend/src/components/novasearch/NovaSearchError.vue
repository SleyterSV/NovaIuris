<template>
    <section
        v-if="message"
        class="nova-search-error"
        role="alert"
    >

        <!-- ICONO -->
        <div class="nova-search-error-icon">

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
                    d="M12 7.5V12.5"
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


        <!-- CONTENIDO -->
        <div class="nova-search-error-content">

            <span class="nova-search-error-eyebrow">
                NOVA SEARCH
            </span>

            <h3>
                No fue posible completar la búsqueda
            </h3>

            <p>
                {{ message }}
            </p>

            <span class="nova-search-error-help">
                Verifica tu conexión e intenta realizar nuevamente la consulta.
            </span>

        </div>


        <!-- ACCIÓN OPCIONAL -->
        <button
            v-if="showRetry"
            type="button"
            class="nova-search-error-button"
            @click="$emit('retry')"
        >
            Intentar nuevamente
        </button>

    </section>
</template>


<script setup>

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


defineEmits([

    "retry"

])

</script>


<style scoped>

/* =======================================================
   NOVA SEARCH — ERROR STATE
======================================================= */

.nova-search-error{

    width:100%;

    display:flex;

    align-items:flex-start;

    gap:18px;

    padding:24px 26px;

    background:

        linear-gradient(
            135deg,
            #FFFDFD 0%,
            #FFF8F8 100%
        );

    border:
        1px solid
        #F0D6D6;

    border-left:
        3px solid
        #A34B4B;

    border-radius:12px;

    box-shadow:

        0 10px 26px
        rgba(
            74,
            35,
            35,
            .045
        );

    animation:

        novaSearchErrorEnter
        .35s
        ease-out;

}


/* =======================================================
   ICONO
======================================================= */

.nova-search-error-icon{

    width:46px;

    height:46px;

    flex:
        0 0 46px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#FFF1F1;

    border:
        1px solid
        #F2D3D3;

    color:#A34B4B;

}


.nova-search-error-icon svg{

    width:23px;

    height:23px;

}


/* =======================================================
   CONTENIDO
======================================================= */

.nova-search-error-content{

    flex:1;

    min-width:0;

}


.nova-search-error-eyebrow{

    display:block;

    margin-bottom:5px;

    color:#8B5A5A;

    font-size:.66rem;

    font-weight:800;

    letter-spacing:1.35px;

}


.nova-search-error h3{

    margin:0 0 7px;

    color:#17375E;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1.1rem;

    font-weight:600;

    line-height:1.35;

}


.nova-search-error p{

    margin:0;

    color:#5E4B4B;

    font-size:.9rem;

    line-height:1.7;

}


.nova-search-error-help{

    display:block;

    margin-top:10px;

    color:#8A7777;

    font-size:.78rem;

    line-height:1.5;

}


/* =======================================================
   BOTÓN
======================================================= */

.nova-search-error-button{

    flex-shrink:0;

    min-height:40px;

    padding:
        0
        16px;

    border:
        1px solid
        #D8B7B7;

    border-radius:8px;

    background:#FFFFFF;

    color:#17375E;

    font-size:.78rem;

    font-weight:700;

    cursor:pointer;

    transition:

        background
        .2s
        ease,

        border-color
        .2s
        ease,

        transform
        .2s
        ease,

        box-shadow
        .2s
        ease;

}


.nova-search-error-button:hover{

    background:#FFF8F8;

    border-color:#A34B4B;

    transform:

        translateY(
            -1px
        );

    box-shadow:

        0 6px 14px
        rgba(
            74,
            35,
            35,
            .08
        );

}


.nova-search-error-button:active{

    transform:

        translateY(
            0
        );

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

@media(max-width:640px){

    .nova-search-error{

        flex-direction:column;

        padding:22px;

        gap:14px;

    }


    .nova-search-error-icon{

        width:42px;

        height:42px;

        flex-basis:42px;

    }


    .nova-search-error-button{

        width:100%;

    }

}
</style>