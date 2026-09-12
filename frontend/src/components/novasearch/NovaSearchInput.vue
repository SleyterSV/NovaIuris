<template>

    <section class="nova-search-input">

        <!-- =========================================
             CABECERA
        ========================================== -->

        <div class="nova-search-input-header">

            <div class="nova-search-input-heading">

                <span class="nova-search-eyebrow">
                    MOTOR DE BÚSQUEDA JURÍDICA
                </span>

                <h2>
                    Consulta jurídica inteligente
                </h2>

                <p>
                    Formula una consulta, describe un problema jurídico
                    o ingresa términos relevantes para recuperar información
                    y desarrollar un análisis jurídico estructurado.
                </p>

            </div>


            <!-- SELLO NOVA SEARCH -->

            <div
                class="nova-search-seal"
                aria-hidden="true"
            >

                <div class="nova-search-seal-inner">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >

                        <circle
                            cx="10.5"
                            cy="10.5"
                            r="6"
                        />

                        <path
                            d="M15 15L20 20"
                        />

                    </svg>

                </div>

                <span>
                    NS
                </span>

            </div>

        </div>


        <!-- =========================================
             FORMULARIO DE BÚSQUEDA
        ========================================== -->

        <form
            class="nova-search-form"
            @submit.prevent="handleSubmit"
        >

            <div class="nova-search-field">

                <!-- ICONO -->

                <div
                    class="nova-search-icon-wrapper"
                    aria-hidden="true"
                >

                    <svg
                        class="nova-search-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                    >

                        <circle
                            cx="11"
                            cy="11"
                            r="6.5"
                        />

                        <path
                            d="M16 16L21 21"
                        />

                    </svg>

                </div>


                <!-- INPUT -->

                <input
                    :value="modelValue"
                    type="text"
                    class="nova-search-control"
                    placeholder="Ejemplo: Nulidad de acto jurídico por falta de manifestación de voluntad..."
                    :disabled="loading"
                    autocomplete="off"
                    @input="updateValue"
                />


                <!-- BOTÓN -->

                <button
                    type="submit"
                    class="nova-search-button"
                    :disabled="loading || !modelValue.trim()"
                >

                    <span
                        v-if="loading"
                        class="nova-search-spinner"
                    ></span>

                    <span v-if="loading">
                        Analizando
                    </span>

                    <span v-else>
                        Buscar
                    </span>

                </button>

            </div>


            <!-- =========================================
                 INFORMACIÓN COMPLEMENTARIA
            ========================================== -->

            <div class="nova-search-footer">

                <div class="nova-search-help">

                    <span class="help-dot"></span>

                    <span>
                        Busca jurisprudencia, legislación y contenido
                        jurídico relevante.
                    </span>

                </div>


                <span class="nova-search-shortcut">
                    Enter para buscar
                </span>

            </div>

        </form>

    </section>

</template>


<script setup>

/* =========================================
   PROPS
========================================= */

const props = defineProps({

    modelValue: {

        type: String,

        default: ""

    },

    loading: {

        type: Boolean,

        default: false

    }

})


/* =========================================
   EVENTOS
========================================= */

const emit = defineEmits([

    "update:modelValue",

    "search"

])


/* =========================================
   ACTUALIZAR CONSULTA
========================================= */

function updateValue(event){

    emit(
        "update:modelValue",
        event.target.value
    )

}


/* =========================================
   EJECUTAR BÚSQUEDA
========================================= */

function handleSubmit(){

    const normalizedQuery =
        props.modelValue.trim()


    if(
        props.loading ||
        !normalizedQuery
    ){

        return

    }


    emit("search")

}

</script>


<style scoped>

/* =========================================================
   NOVA SEARCH INPUT
   IDENTIDAD VISUAL NOVA IURIS
========================================================= */

.nova-search-input{

    position:relative;

    width:100%;

    padding:36px;

    overflow:hidden;

    background:
        linear-gradient(
            145deg,
            #FFFFFF 0%,
            #FFFFFF 55%,
            #F5F8FC 100%
        );

    border:
        1px solid
        #D7E0EA;

    border-radius:16px;

    box-shadow:
        0 18px 45px
        rgba(
            11,
            22,
            40,
            .055
        );

}


/* =========================================================
   LÍNEA SUPERIOR INSTITUCIONAL
========================================================= */

.nova-search-input::before{

    content:"";

    position:absolute;

    top:0;

    left:0;

    right:0;

    height:3px;

    background:
        linear-gradient(
            90deg,
            #17375E 0%,
            #315C97 60%,
            #C9A45C 100%
        );

}


/* =========================================================
   DECORACIÓN SUTIL
========================================================= */

.nova-search-input::after{

    content:"";

    position:absolute;

    width:220px;

    height:220px;

    top:-150px;

    right:-100px;

    border-radius:50%;

    border:
        1px solid
        rgba(
            49,
            92,
            151,
            .055
        );

    pointer-events:none;

}


/* =========================================================
   CABECERA
========================================================= */

.nova-search-input-header{

    position:relative;

    z-index:1;

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:32px;

    margin-bottom:28px;

}


.nova-search-input-heading{

    min-width:0;

    flex:1;

}


/* =========================================================
   EYEBROW
========================================================= */

.nova-search-eyebrow{

    display:inline-flex;

    align-items:center;

    gap:9px;

    margin-bottom:10px;

    color:#9A7A42;

    font-size:.66rem;

    font-weight:800;

    letter-spacing:1.65px;

    line-height:1.2;

    text-transform:uppercase;

}


.nova-search-eyebrow::before{

    content:"";

    width:22px;

    height:1px;

    background:#C9A45C;

}


/* =========================================================
   TÍTULO
========================================================= */

.nova-search-input-heading h2{

    margin:
        0
        0
        10px;

    color:#17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:1.65rem;

    font-weight:600;

    line-height:1.25;

    letter-spacing:-.35px;

}


/* =========================================================
   DESCRIPCIÓN
========================================================= */

.nova-search-input-heading p{

    max-width:790px;

    margin:0;

    color:#64748B;

    font-size:.91rem;

    line-height:1.72;

}


/* =========================================================
   SELLO NOVA SEARCH
========================================================= */

.nova-search-seal{

    position:relative;

    width:76px;

    height:76px;

    flex:0 0 76px;

    display:flex;

    align-items:center;

    justify-content:center;

    border:
        1px solid
        rgba(
            23,
            55,
            94,
            .20
        );

    border-radius:50%;

    background:
        linear-gradient(
            145deg,
            #FFFFFF,
            #F4F7FB
        );

    box-shadow:
        0 8px 22px
        rgba(
            23,
            55,
            94,
            .07
        );

}


/* ANILLO INTERIOR */

.nova-search-seal::before{

    content:"";

    position:absolute;

    inset:6px;

    border:
        1px solid
        rgba(
            201,
            164,
            92,
            .55
        );

    border-radius:50%;

}


/* DETALLE CENTRAL */

.nova-search-seal-inner{

    position:absolute;

    top:18px;

    left:50%;

    transform:
        translateX(-50%);

    display:flex;

    align-items:center;

    justify-content:center;

}


.nova-search-seal-inner svg{

    width:22px;

    height:22px;

    color:#315C97;

    stroke:currentColor;

}


/* NS */

.nova-search-seal span{

    position:absolute;

    bottom:12px;

    left:50%;

    transform:
        translateX(-50%);

    color:#17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:.64rem;

    font-weight:700;

    letter-spacing:1.5px;

}


/* =========================================================
   FORMULARIO
========================================================= */

.nova-search-form{

    position:relative;

    z-index:2;

    width:100%;

}


/* =========================================================
   CAMPO PRINCIPAL
========================================================= */

.nova-search-field{

    display:flex;

    align-items:center;

    width:100%;

    min-height:68px;

    padding:7px;

    background:#FFFFFF;

    border:
        1px solid
        #C8D4E2;

    border-radius:11px;

    transition:
        border-color .2s ease,
        box-shadow .2s ease,
        transform .2s ease;

}


.nova-search-field:hover{

    border-color:#AEBFD2;

}


.nova-search-field:focus-within{

    border-color:#315C97;

    box-shadow:
        0 0 0 4px
        rgba(
            49,
            92,
            151,
            .085
        );

}


/* =========================================================
   CONTENEDOR DEL ICONO
========================================================= */

.nova-search-icon-wrapper{

    width:44px;

    height:44px;

    flex:0 0 44px;

    display:flex;

    align-items:center;

    justify-content:center;

    margin-left:4px;

    border-radius:8px;

    background:
        #F2F6FA;

    color:#315C97;

}


.nova-search-icon{

    width:21px;

    height:21px;

}


/* =========================================================
   INPUT
========================================================= */

.nova-search-control{

    flex:1;

    width:100%;

    min-width:0;

    padding:
        17px
        15px;

    border:none;

    outline:none;

    background:transparent;

    color:#17375E;

    font-family:inherit;

    font-size:.94rem;

    line-height:1.5;

}


.nova-search-control::placeholder{

    color:#98A5B4;

}


.nova-search-control:disabled{

    cursor:not-allowed;

    opacity:.68;

}


/* =========================================================
   BOTÓN BUSCAR
========================================================= */

.nova-search-button{

    min-width:128px;

    min-height:52px;

    display:inline-flex;

    align-items:center;

    justify-content:center;

    gap:9px;

    padding:
        0
        24px;

    border:
        1px solid
        #17375E;

    border-radius:8px;

    background:
        linear-gradient(
            135deg,
            #17375E 0%,
            #234B7C 100%
        );

    color:#FFFFFF;

    font-family:inherit;

    font-size:.86rem;

    font-weight:700;

    letter-spacing:.1px;

    cursor:pointer;

    transition:
        transform .2s ease,
        background .2s ease,
        box-shadow .2s ease;

}


.nova-search-button:hover:not(:disabled){

    background:
        linear-gradient(
            135deg,
            #1B416D 0%,
            #315C97 100%
        );

    transform:
        translateY(-1px);

    box-shadow:
        0 9px 20px
        rgba(
            23,
            55,
            94,
            .18
        );

}


.nova-search-button:active:not(:disabled){

    transform:
        translateY(0);

    box-shadow:none;

}


.nova-search-button:disabled{

    opacity:.5;

    cursor:not-allowed;

}


/* =========================================================
   SPINNER
========================================================= */

.nova-search-spinner{

    width:15px;

    height:15px;

    flex-shrink:0;

    border:
        2px solid
        rgba(
            255,
            255,
            255,
            .35
        );

    border-top-color:#FFFFFF;

    border-radius:50%;

    animation:
        novaSearchSpin
        .8s
        linear
        infinite;

}


@keyframes novaSearchSpin{

    from{

        transform:
            rotate(0deg);

    }

    to{

        transform:
            rotate(360deg);

    }

}


/* =========================================================
   FOOTER
========================================================= */

.nova-search-footer{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:16px;

    margin-top:13px;

    color:#7B8998;

    font-size:.76rem;

    line-height:1.5;

}


/* AYUDA */

.nova-search-help{

    min-width:0;

    display:flex;

    align-items:center;

    gap:8px;

}


.help-dot{

    width:5px;

    height:5px;

    flex:0 0 5px;

    border-radius:50%;

    background:#C9A45C;

}


/* ATAJO */

.nova-search-shortcut{

    flex-shrink:0;

    padding:
        5px
        10px;

    color:#7A6440;

    font-size:.68rem;

    font-weight:700;

    letter-spacing:.15px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .25
        );

    border-radius:6px;

    background:
        rgba(
            201,
            164,
            92,
            .055
        );

}


/* =========================================================
   TABLET
========================================================= */

@media(max-width:900px){

    .nova-search-input{

        padding:30px;

    }

    .nova-search-input-heading h2{

        font-size:1.5rem;

    }

}


/* =========================================================
   TABLET PEQUEÑO
========================================================= */

@media(max-width:700px){

    .nova-search-input{

        padding:28px 24px;

    }


    .nova-search-input-header{

        gap:22px;

    }


    .nova-search-seal{

        width:64px;

        height:64px;

        flex-basis:64px;

    }


    .nova-search-input-heading h2{

        font-size:1.35rem;

    }


    .nova-search-field{

        align-items:stretch;

        flex-wrap:wrap;

        padding:8px;

    }


    .nova-search-icon-wrapper{

        margin:4px 0 4px 4px;

    }


    .nova-search-control{

        flex:1;

        min-width:180px;

    }


    .nova-search-button{

        width:100%;

        min-height:50px;

    }

}


/* =========================================================
   MOBILE
========================================================= */

@media(max-width:576px){

    .nova-search-input{

        padding:23px 18px;

        border-radius:12px;

    }


    .nova-search-input-header{

        gap:18px;

        margin-bottom:22px;

    }


    .nova-search-seal{

        display:none;

    }


    .nova-search-input-heading h2{

        font-size:1.2rem;

    }


    .nova-search-input-heading p{

        font-size:.86rem;

        line-height:1.7;

    }


    .nova-search-field{

        flex-direction:column;

        align-items:stretch;

    }


    .nova-search-icon-wrapper{

        display:none;

    }


    .nova-search-control{

        padding:
            14px
            12px;

    }


    .nova-search-button{

        width:100%;

    }


    .nova-search-footer{

        flex-direction:column;

        align-items:flex-start;

        gap:8px;

    }

}

</style>