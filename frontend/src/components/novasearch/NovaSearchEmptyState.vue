<template>

    <section class="nova-search-empty-state">

        <!-- ===================================================
             EMBLEMA
        ==================================================== -->

        <div class="empty-emblem">

            <div class="empty-emblem-ring"></div>

            <div class="empty-emblem-inner">

                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.6"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    aria-hidden="true"
                >

                    <circle
                        cx="10.8"
                        cy="10.8"
                        r="5.8"
                    />

                    <path
                        d="M15.2 15.2L20 20"
                    />

                    <path
                        d="M8.2 10.8h5.2"
                    />

                    <path
                        d="M10.8 8.2v5.2"
                    />

                </svg>

            </div>

        </div>


        <!-- ===================================================
             CONTENIDO PRINCIPAL
        ==================================================== -->

        <div class="empty-content">

            <span class="empty-eyebrow">

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
            class="empty-suggestions"
        >

            <div class="suggestions-heading">

                <span class="suggestions-line"></span>

                <span class="suggestions-label">
                    PUEDES BUSCAR POR
                </span>

                <span class="suggestions-line"></span>

            </div>


            <div class="suggestions-list">

                <button
                    type="button"
                    class="suggestion-button"
                    @click="
                        $emit(
                            'suggestion',
                            'Jurisprudencia sobre despido arbitrario'
                        )
                    "
                >

                    <span class="suggestion-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >

                            <path
                                d="M6 3h12"
                            />

                            <path
                                d="M6 3v4"
                            />

                            <path
                                d="M18 3v4"
                            />

                            <path
                                d="M4 7h16"
                            />

                            <path
                                d="M7 11h4"
                            />

                            <path
                                d="M7 15h7"
                            />

                            <path
                                d="M7 19h5"
                            />

                        </svg>

                    </span>

                    <span>
                        Jurisprudencia
                    </span>

                </button>


                <button
                    type="button"
                    class="suggestion-button"
                    @click="
                        $emit(
                            'suggestion',
                            'Nulidad de acto jurídico'
                        )
                    "
                >

                    <span class="suggestion-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >

                            <rect
                                x="5"
                                y="4"
                                width="14"
                                height="16"
                                rx="2"
                            />

                            <path
                                d="M8 8h8"
                            />

                            <path
                                d="M8 12h5"
                            />

                            <path
                                d="M8 16h7"
                            />

                        </svg>

                    </span>

                    <span>
                        Actos jurídicos
                    </span>

                </button>


                <button
                    type="button"
                    class="suggestion-button"
                    @click="
                        $emit(
                            'suggestion',
                            'Casación laboral'
                        )
                    "
                >

                    <span class="suggestion-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >

                            <path
                                d="M5 4h14"
                            />

                            <path
                                d="M7 4v4"
                            />

                            <path
                                d="M17 4v4"
                            />

                            <path
                                d="M7 8h10"
                            />

                            <path
                                d="M9 12h6"
                            />

                            <path
                                d="M8 16h8"
                            />

                            <path
                                d="M10 20h4"
                            />

                        </svg>

                    </span>

                    <span>
                        Casaciones
                    </span>

                </button>


                <button
                    type="button"
                    class="suggestion-button"
                    @click="
                        $emit(
                            'suggestion',
                            'Derechos fundamentales'
                        )
                    "
                >

                    <span class="suggestion-icon">

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
                                r="8"
                            />

                            <path
                                d="M12 8v8"
                            />

                            <path
                                d="M8 12h8"
                            />

                        </svg>

                    </span>

                    <span>
                        Derechos fundamentales
                    </span>

                </button>

            </div>

        </div>


        <!-- ===================================================
             FIRMA INSTITUCIONAL
        ==================================================== -->

        <div class="empty-footer">

            <span class="footer-mark"></span>

            <span>
                Búsqueda jurídica inteligente
            </span>

        </div>

    </section>

</template>


<script setup>

import { computed } from "vue"


/* =========================================================
   PROPS
========================================================= */

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


/* =========================================================
   EVENTOS
========================================================= */

defineEmits([

    "suggestion"

])


/* =========================================================
   TEXTOS DINÁMICOS
========================================================= */

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

    position:relative;

    width:100%;

    min-height:450px;

    display:flex;

    flex-direction:column;

    align-items:center;

    justify-content:center;

    padding:56px 34px 42px;

    text-align:center;

    overflow:hidden;

    background:

        linear-gradient(
            145deg,
            #FFFFFF 0%,
            #FCFDFE 58%,
            #F7F9FC 100%
        );

    border:

        1px solid
        #D8E1EB;

    border-radius:14px;

    box-shadow:

        0 10px 30px
        rgba(
            23,
            55,
            94,
            .045
        );

}


/* =======================================================
   DETALLE SUPERIOR
======================================================= */

.nova-search-empty-state::before{

    content:"";

    position:absolute;

    top:0;

    left:50%;

    width:180px;

    height:1px;

    transform:translateX(-50%);

    background:

        linear-gradient(
            90deg,
            transparent,
            #B08A4C,
            transparent
        );

    opacity:.65;

}


/* =======================================================
   EMBLEMA
======================================================= */

.empty-emblem{

    position:relative;

    width:88px;

    height:88px;

    display:flex;

    align-items:center;

    justify-content:center;

    margin-bottom:25px;

    border-radius:50%;

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .38
        );

    background:

        radial-gradient(
            circle,
            rgba(
                176,
                138,
                76,
                .055
            ) 0%,
            transparent 68%
        );

}


/* Anillo interior */

.empty-emblem-ring{

    position:absolute;

    inset:7px;

    border-radius:50%;

    border:

        1px solid
        #E7EDF3;

}


/* Centro */

.empty-emblem-inner{

    position:relative;

    z-index:1;

    width:62px;

    height:62px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:

        linear-gradient(
            145deg,
            #F7F9FB,
            #F1F5F9
        );

    border:

        1px solid
        #DFE7EF;

    color:#315C97;

    box-shadow:

        0 4px 12px
        rgba(
            23,
            55,
            94,
            .045
        );

}


.empty-emblem-inner svg{

    width:28px;

    height:28px;

}


/* =======================================================
   CONTENIDO
======================================================= */

.empty-content{

    width:100%;

    max-width:670px;

}


.empty-eyebrow{

    display:block;

    margin-bottom:9px;

    color:#7A6440;

    font-size:.65rem;

    font-weight:800;

    letter-spacing:1.55px;

}


.empty-content h2{

    margin:0 0 12px;

    color:#17375E;

    font-family:

        Georgia,

        "Times New Roman",

        serif;

    font-size:1.58rem;

    font-weight:600;

    line-height:1.35;

}


.empty-content p{

    max-width:620px;

    margin:0 auto;

    color:#687889;

    font-size:.91rem;

    line-height:1.82;

}


/* =======================================================
   SUGERENCIAS
======================================================= */

.empty-suggestions{

    width:100%;

    max-width:700px;

    margin-top:31px;

    padding-top:22px;

    border-top:

        1px solid
        #E7EDF2;

}


/* Encabezado */

.suggestions-heading{

    display:flex;

    align-items:center;

    justify-content:center;

    gap:10px;

    margin-bottom:14px;

}


.suggestions-label{

    color:#8B98A6;

    font-size:.59rem;

    font-weight:800;

    letter-spacing:1.15px;

}


.suggestions-line{

    width:24px;

    height:1px;

    background:#D6DFE8;

}


/* Lista */

.suggestions-list{

    display:flex;

    flex-wrap:wrap;

    justify-content:center;

    gap:9px;

}


/* =======================================================
   BOTONES DE SUGERENCIA
======================================================= */

.suggestion-button{

    display:inline-flex;

    align-items:center;

    gap:7px;

    min-height:35px;

    padding:

        7px

        13px;

    border:

        1px solid
        #D7E1EA;

    border-radius:8px;

    background:#FFFFFF;

    color:#315C97;

    font-family:inherit;

    font-size:.72rem;

    font-weight:700;

    cursor:pointer;

    box-shadow:

        0 2px 7px
        rgba(
            23,
            55,
            94,
            .025
        );

    transition:

        transform
        .2s
        ease,

        border-color
        .2s
        ease,

        background
        .2s
        ease,

        color
        .2s
        ease,

        box-shadow
        .2s
        ease;

}


.suggestion-button:hover{

    transform:

        translateY(
            -1px
        );

    background:#F8FAFC;

    border-color:#B8C9DB;

    color:#17375E;

    box-shadow:

        0 5px 13px
        rgba(
            23,
            55,
            94,
            .055
        );

}


.suggestion-button:focus-visible{

    outline:

        2px solid
        rgba(
            49,
            92,
            151,
            .28
        );

    outline-offset:2px;

}


/* =======================================================
   ICONOS DE SUGERENCIAS
======================================================= */

.suggestion-icon{

    width:22px;

    height:22px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:6px;

    background:#F4F7FA;

    border:

        1px solid
        #E1E8EF;

    color:#315C97;

}


.suggestion-icon svg{

    width:13px;

    height:13px;

}


/* =======================================================
   FOOTER
======================================================= */

.empty-footer{

    display:flex;

    align-items:center;

    justify-content:center;

    gap:8px;

    margin-top:27px;

    color:#9AA5B1;

    font-size:.64rem;

    font-weight:600;

    letter-spacing:.15px;

}


.footer-mark{

    width:16px;

    height:1px;

    background:#B08A4C;

    opacity:.75;

}


/* =======================================================
   MODO SIN RESULTADOS
======================================================= */

.nova-search-empty-state:has(
    .empty-eyebrow
){

    /* Mantiene la misma identidad visual
       para estado inicial y no-results */

}


/* =======================================================
   RESPONSIVE — TABLET
======================================================= */

@media(max-width:760px){

    .nova-search-empty-state{

        min-height:420px;

        padding:

            48px
            26px
            38px;

    }


    .empty-emblem{

        width:80px;

        height:80px;

        margin-bottom:22px;

    }


    .empty-emblem-inner{

        width:57px;

        height:57px;

    }


    .empty-emblem-inner svg{

        width:26px;

        height:26px;

    }


    .empty-content h2{

        font-size:1.4rem;

    }


    .empty-content p{

        font-size:.88rem;

    }


    .empty-suggestions{

        margin-top:27px;

    }

}


/* =======================================================
   RESPONSIVE — MÓVIL
======================================================= */

@media(max-width:576px){

    .nova-search-empty-state{

        min-height:390px;

        padding:

            40px
            18px
            32px;

        border-radius:11px;

    }


    .empty-emblem{

        width:72px;

        height:72px;

        margin-bottom:20px;

    }


    .empty-emblem-ring{

        inset:6px;

    }


    .empty-emblem-inner{

        width:52px;

        height:52px;

    }


    .empty-emblem-inner svg{

        width:23px;

        height:23px;

    }


    .empty-eyebrow{

        font-size:.6rem;

        letter-spacing:1.3px;

    }


    .empty-content h2{

        margin-bottom:10px;

        font-size:1.24rem;

        line-height:1.4;

    }


    .empty-content p{

        font-size:.84rem;

        line-height:1.75;

    }


    .empty-suggestions{

        margin-top:24px;

        padding-top:19px;

    }


    .suggestions-heading{

        margin-bottom:12px;

    }


    .suggestions-list{

        flex-direction:column;

        align-items:stretch;

        gap:7px;

    }


    .suggestion-button{

        width:100%;

        justify-content:center;

        min-height:38px;

    }


    .empty-footer{

        margin-top:22px;

        font-size:.6rem;

    }

}

</style>