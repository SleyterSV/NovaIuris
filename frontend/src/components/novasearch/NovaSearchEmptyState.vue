<template>

    <section class="nova-search-empty-state">

        <!-- ===================================================
             EMBLEMA
        ==================================================== -->

        <div class="nova-search-empty-emblem">

            <div class="nova-search-empty-emblem-inner">

                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    aria-hidden="true"
                >

                    <!-- Lupa -->

                    <circle
                        cx="10.8"
                        cy="10.8"
                        r="5.8"
                    />

                    <path
                        d="M15.2 15.2L20 20"
                    />

                </svg>

            </div>

        </div>


        <!-- ===================================================
             CONTENIDO
        ==================================================== -->

        <div class="nova-search-empty-content">

            <span class="nova-search-empty-eyebrow">

                {{ eyebrowText }}

            </span>


            <h2>

                {{ titleText }}

            </h2>


            <p>

                {{ descriptionText }}

            </p>

        </div>


        <!-- ===================================================
             SUGERENCIAS
        ==================================================== -->

        <div
            v-if="showSuggestions"
            class="nova-search-suggestions"
        >

            <span class="nova-search-suggestions-label">
                PUEDES BUSCAR POR
            </span>


            <div class="nova-search-suggestions-list">

                <button
                    type="button"
                    class="nova-search-suggestion"
                    @click="$emit('suggestion', 'Jurisprudencia sobre despido arbitrario')"
                >
                    Jurisprudencia
                </button>


                <button
                    type="button"
                    class="nova-search-suggestion"
                    @click="$emit('suggestion', 'Nulidad de acto jurídico')"
                >
                    Actos jurídicos
                </button>


                <button
                    type="button"
                    class="nova-search-suggestion"
                    @click="$emit('suggestion', 'Casación laboral')"
                >
                    Casaciones
                </button>


                <button
                    type="button"
                    class="nova-search-suggestion"
                    @click="$emit('suggestion', 'Derechos fundamentales')"
                >
                    Derechos fundamentales
                </button>

            </div>

        </div>

    </section>

</template>


<script setup>

import { computed } from "vue"


const props = defineProps({

    mode: {

        type: String,

        default: "initial",

        validator(value){

            return [

                "initial",

                "no-results"

            ].includes(value)

        }

    },

    query: {

        type: String,

        default: ""

    },

    showSuggestions: {

        type: Boolean,

        default: true

    }

})


defineEmits([

    "suggestion"

])


const eyebrowText = computed(() => {

    return props.mode === "no-results"

        ? "RESULTADOS DE LA CONSULTA"

        : "NOVA SEARCH"

})


const titleText = computed(() => {

    return props.mode === "no-results"

        ? "No encontramos coincidencias relevantes"

        : "Consulta el conocimiento jurídico de Nova"

})


const descriptionText = computed(() => {

    if (

        props.mode === "no-results"

        &&

        props.query.trim()

    ){

        return `No se identificaron resultados relevantes para "${props.query}". Puedes reformular la consulta, utilizar términos jurídicos más generales o seleccionar otro módulo legal.`

    }


    if (

        props.mode === "no-results"

    ){

        return "No se identificaron resultados relevantes. Intenta reformular tu consulta o utilizar otros términos jurídicos."

    }


    return "Formula una consulta jurídica para recuperar jurisprudencia, legislación y contenido relevante mediante el sistema de búsqueda y análisis inteligente de Nova."

})

</script>


<style scoped>

/* =======================================================
   NOVA SEARCH — EMPTY STATE
======================================================= */

.nova-search-empty-state{

    width:100%;

    min-height:430px;

    display:flex;

    flex-direction:column;

    align-items:center;

    justify-content:center;

    padding:52px 32px;

    text-align:center;

    background:

        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FBFCFE 100%
        );

    border:

        1px solid
        #DCE4EC;

    border-radius:14px;

    box-shadow:

        0 10px 28px
        rgba(
            23,
            55,
            94,
            .045
        );

}


/* =======================================================
   EMBLEMA
======================================================= */

.nova-search-empty-emblem{

    width:82px;

    height:82px;

    display:flex;

    align-items:center;

    justify-content:center;

    margin-bottom:24px;

    border-radius:50%;

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .42
        );

    background:

        #FCFDFE;

}


.nova-search-empty-emblem-inner{

    width:64px;

    height:64px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#F4F7FA;

    color:#315C97;

}


.nova-search-empty-emblem-inner svg{

    width:29px;

    height:29px;

}


/* =======================================================
   CONTENIDO
======================================================= */

.nova-search-empty-content{

    max-width:620px;

}


.nova-search-empty-eyebrow{

    display:block;

    margin-bottom:10px;

    color:#7A6440;

    font-size:.66rem;

    font-weight:800;

    letter-spacing:1.5px;

}


.nova-search-empty-content h2{

    margin:0 0 12px;

    color:#17375E;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1.55rem;

    font-weight:600;

    line-height:1.35;

}


.nova-search-empty-content p{

    margin:0;

    color:#697888;

    font-size:.92rem;

    line-height:1.8;

}


/* =======================================================
   SUGERENCIAS
======================================================= */

.nova-search-suggestions{

    width:100%;

    max-width:650px;

    margin-top:30px;

    padding-top:24px;

    border-top:

        1px solid
        #E7EDF2;

}


.nova-search-suggestions-label{

    display:block;

    margin-bottom:13px;

    color:#95A1AD;

    font-size:.6rem;

    font-weight:800;

    letter-spacing:1px;

}


.nova-search-suggestions-list{

    display:flex;

    flex-wrap:wrap;

    justify-content:center;

    gap:9px;

}


.nova-search-suggestion{

    padding:

        8px
        13px;

    background:#FFFFFF;

    border:

        1px solid
        #D7E0E9;

    border-radius:999px;

    color:#315C97;

    font-size:.72rem;

    font-weight:700;

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
        ease;

}


.nova-search-suggestion:hover{

    background:#F6F8FB;

    border-color:#B08A4C;

    color:#17375E;

    transform:

        translateY(
            -1px
        );

}


/* =======================================================
   RESPONSIVE
======================================================= */

@media(max-width:640px){

    .nova-search-empty-state{

        min-height:380px;

        padding:42px 22px;

    }


    .nova-search-empty-emblem{

        width:72px;

        height:72px;

    }


    .nova-search-empty-emblem-inner{

        width:56px;

        height:56px;

    }


    .nova-search-empty-content h2{

        font-size:1.3rem;

    }


    .nova-search-suggestions-list{

        flex-direction:column;

        align-items:stretch;

    }


    .nova-search-suggestion{

        width:100%;

    }

}
</style>