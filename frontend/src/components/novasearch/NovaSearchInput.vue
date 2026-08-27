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


            <div
                class="nova-search-seal"
                aria-hidden="true"
            >

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

                <svg
                    class="nova-search-icon"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    aria-hidden="true"
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


                <input
                    :value="modelValue"
                    type="text"
                    class="nova-search-control"
                    placeholder="Ejemplo: Nulidad de acto jurídico por falta de manifestación de voluntad..."
                    :disabled="loading"
                    autocomplete="off"
                    @input="updateValue"
                />


                <button
                    type="submit"
                    class="nova-search-button"
                    :disabled="loading || !modelValue.trim()"
                >

                    <span
                        v-if="loading"
                        class="nova-search-spinner"
                    ></span>


                    <span
                        v-if="loading"
                    >
                        Analizando
                    </span>


                    <span
                        v-else
                    >
                        Buscar
                    </span>

                </button>

            </div>


            <!-- =========================================
                 INFORMACIÓN COMPLEMENTARIA
            ========================================== -->

            <div class="nova-search-footer">

                <span class="nova-search-help">

                    Busca jurisprudencia, legislación y contenido
                    jurídico relevante.

                </span>


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


    emit(

        "search"

    )

}

</script>


<style scoped>

/* =========================================
   NOVA SEARCH INPUT
   CONTENEDOR PRINCIPAL
========================================= */

.nova-search-input{

    width:100%;

    padding:32px;

    overflow:hidden;

    background:

        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FBFCFE 62%,
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
   CABECERA
========================================= */

.nova-search-input-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:28px;

    margin-bottom:26px;

}


.nova-search-input-heading{

    min-width:0;

    flex:1;

}


/* =========================================
   EYEBROW
========================================= */

.nova-search-eyebrow{

    display:block;

    margin-bottom:9px;

    color:#7A6440;

    font-size:.68rem;

    font-weight:800;

    letter-spacing:1.45px;

}


/* =========================================
   TÍTULO
========================================= */

.nova-search-input-heading h2{

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


/* =========================================
   DESCRIPCIÓN
========================================= */

.nova-search-input-heading p{

    max-width:800px;

    margin:0;

    color:#5E6D7E;

    font-size:.94rem;

    line-height:1.75;

}


/* =========================================
   SELLO NS
========================================= */

.nova-search-seal{

    position:relative;

    width:72px;

    height:72px;

    display:flex;

    align-items:center;

    justify-content:center;

    flex-shrink:0;

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .55
        );

    border-radius:50%;

}


.nova-search-seal::before{

    content:"";

    position:absolute;

    inset:7px;

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .32
        );

    border-radius:50%;

}


.nova-search-seal span{

    position:relative;

    z-index:1;

    color:#7A6440;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:.95rem;

    font-weight:600;

    letter-spacing:1.8px;

}


/* =========================================
   FORMULARIO
========================================= */

.nova-search-form{

    width:100%;

}


/* =========================================
   CAMPO PRINCIPAL
========================================= */

.nova-search-field{

    display:flex;

    align-items:center;

    width:100%;

    min-height:66px;

    padding:7px;

    background:#FFFFFF;

    border:

        1px solid
        #C9D5E3;

    border-radius:10px;

    transition:

        border-color
        .2s
        ease,

        box-shadow
        .2s
        ease;

}


.nova-search-field:focus-within{

    border-color:#315C97;

    box-shadow:

        0 0 0 4px
        rgba(
            49,
            92,
            151,
            .09
        );

}


/* =========================================
   ICONO
========================================= */

.nova-search-icon{

    width:22px;

    height:22px;

    flex-shrink:0;

    margin-left:16px;

    color:#315C97;

}


/* =========================================
   INPUT
========================================= */

.nova-search-control{

    flex:1;

    width:100%;

    min-width:0;

    padding:17px 16px;

    border:none;

    outline:none;

    background:transparent;

    color:#17375E;

    font-family:

        inherit;

    font-size:.95rem;

    line-height:1.5;

}


.nova-search-control::placeholder{

    color:#93A0AE;

}


.nova-search-control:disabled{

    cursor:not-allowed;

    opacity:.75;

}


/* =========================================
   BOTÓN DE BÚSQUEDA
========================================= */

.nova-search-button{

    min-width:130px;

    min-height:52px;

    display:inline-flex;

    align-items:center;

    justify-content:center;

    gap:9px;

    padding:0 25px;

    border:none;

    border-radius:8px;

    background:#17375E;

    color:#FFFFFF;

    font-family:

        inherit;

    font-size:.88rem;

    font-weight:700;

    cursor:pointer;

    transition:

        transform
        .2s
        ease,

        background
        .2s
        ease,

        box-shadow
        .2s
        ease;

}


.nova-search-button:hover:not(:disabled){

    background:#234B7C;

    transform:

        translateY(
            -1px
        );

    box-shadow:

        0 8px 18px
        rgba(
            23,
            55,
            94,
            .16
        );

}


.nova-search-button:active:not(:disabled){

    transform:

        translateY(
            0
        );

}


.nova-search-button:disabled{

    opacity:.55;

    cursor:not-allowed;

}


/* =========================================
   SPINNER
========================================= */

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


/* =========================================
   FOOTER
========================================= */

.nova-search-footer{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:16px;

    margin-top:13px;

    color:#7B8998;

    font-size:.78rem;

    line-height:1.5;

}


.nova-search-help{

    min-width:0;

}


.nova-search-shortcut{

    flex-shrink:0;

    padding:4px 9px;

    color:#7A6440;

    font-size:.72rem;

    font-weight:700;

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .22
        );

    border-radius:5px;

    background:

        rgba(
            176,
            138,
            76,
            .045
        );

}


/* =========================================
   ANIMACIÓN
========================================= */

@keyframes novaSearchSpin{

    from{

        transform:

            rotate(
                0deg
            );

    }


    to{

        transform:

            rotate(
                360deg
            );

    }

}


/* =========================================
   RESPONSIVE
========================================= */

@media(max-width:900px){

    .nova-search-input{

        padding:30px;

    }

}


@media(max-width:700px){

    .nova-search-input{

        padding:26px 24px;

    }


    .nova-search-input-header{

        gap:22px;

    }


    .nova-search-seal{

        width:60px;

        height:60px;

    }


    .nova-search-input-heading h2{

        font-size:1.35rem;

    }


    .nova-search-field{

        align-items:stretch;

        flex-wrap:wrap;

        padding:8px;

    }


    .nova-search-icon{

        margin:

            14px
            8px
            0;

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


@media(max-width:576px){

    .nova-search-input{

        padding:22px 18px;

        border-radius:10px;

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

        font-size:.88rem;

        line-height:1.7;

    }


    .nova-search-field{

        flex-direction:column;

    }


    .nova-search-icon{

        display:none;

    }


    .nova-search-control{

        padding:14px 12px;

    }


    .nova-search-button{

        width:100%;

    }


    .nova-search-footer{

        flex-direction:column;

        align-items:flex-start;

        gap:7px;

    }

}

</style>