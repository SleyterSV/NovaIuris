<template>

    <section
        class="novacourt-tabs"
        aria-label="Navegación del análisis judicial"
    >

        <!-- =========================================
             CABECERA DE NAVEGACIÓN
        ========================================== -->

        <div class="tabs-header">

            <div
                class="tabs-nav"
                role="tablist"
                aria-label="Secciones del análisis"
            >

                <button

                    v-for="tab in tabs"

                    :key="tab.id"

                    type="button"

                    class="tab-button"

                    :class="{

                        active:
                        activeTab === tab.id

                    }"

                    :aria-selected="
                        activeTab === tab.id
                    "

                    role="tab"

                    @click="selectTab(tab.id)"

                >

                    <span
                        class="tab-icon"
                        aria-hidden="true"
                    >

                        {{ tab.icon }}

                    </span>


                    <span class="tab-label">

                        {{ tab.label }}

                    </span>

                </button>

            </div>

        </div>


        <!-- =========================================
             CONTENIDO ACTIVO
        ========================================== -->

        <div
            class="tabs-content"
            role="tabpanel"
        >

            <Transition
                name="tab-content"
                mode="out-in"
            >

                <div
                    :key="activeTab"
                    class="tab-panel"
                >

                    <slot
                        :name="activeTab"
                    />

                </div>

            </Transition>

        </div>

    </section>

</template>


<script setup>

import {

    ref,

    watch

} from "vue"


/* =========================================
   PROPS
========================================= */

const props = defineProps({

    defaultTab: {

        type: String,

        default: "overview"

    }

})


/* =========================================
   EVENTS
========================================= */

const emit = defineEmits([

    "change"

])


/* =========================================
   CONFIGURACIÓN DE PESTAÑAS
========================================= */

const tabs = [

    {

        id: "overview",

        label: "Resumen",

        icon: "⌘"

    },

    {

        id: "arguments",

        label: "Argumentos",

        icon: "§"

    },

    {

        id: "evidence",

        label: "Evidencia",

        icon: "▤"

    },

    {

        id: "risks",

        label: "Riesgos",

        icon: "△"

    },

    {

        id: "strategy",

        label: "Estrategia",

        icon: "◈"

    },

    {

        id: "prediction",

        label: "Proyección",

        icon: "↗"

    },

    {

        id: "graph",

        label: "Grafo Jurídico",

        icon: "◇"

    }

]


/* =========================================
   ESTADO ACTIVO
========================================= */

const activeTab = ref(

    props.defaultTab

)


/* =========================================
   SELECCIONAR PESTAÑA
========================================= */

function selectTab(

    tabId

){

    if(

        activeTab.value === tabId

    ){

        return

    }


    activeTab.value = tabId

}


/* =========================================
   EMITIR CAMBIOS
========================================= */

watch(

    activeTab,

    (

        value

    ) => {

        emit(

            "change",

            value

        )

    }

)


/* =========================================
   SINCRONIZAR TAB EXTERNO
========================================= */

watch(

    () => props.defaultTab,

    (

        value

    ) => {

        if(

            value &&
            value !== activeTab.value

        ){

            activeTab.value = value

        }

    }

)

</script>


<style scoped>

/* =========================================
   NOVACOURT TABS

   IDENTIDAD:
   JURÍDICA · INSTITUCIONAL · SOBRIA

   PRINCIPAL:
   AZUL PROFUNDO

   ACENTO:
   DORADO DISCRETO
========================================= */


/* =========================================
   CONTENEDOR PRINCIPAL
========================================= */

.novacourt-tabs{

    width:100%;

    margin-top:34px;

}


/* =========================================
   CABECERA
========================================= */

.tabs-header{

    position:relative;

    width:100%;

    background:

        linear-gradient(
            180deg,
            #FCFDFE 0%,
            #F8FAFC 100%
        );

    border-top:
        1px solid
        #D6DFEA;

    border-bottom:
        1px solid
        #C9D4DF;

}


/* Línea institucional superior */

.tabs-header::before{

    content:"";

    position:absolute;

    top:-1px;

    left:0;

    width:108px;

    height:2px;

    background:

        linear-gradient(
            90deg,
            #17375E 0%,
            #315C97 72%,
            transparent 100%
        );

    z-index:2;

}


/* =========================================
   NAVEGACIÓN
========================================= */

.tabs-nav{

    display:flex;

    align-items:stretch;

    width:100%;

    overflow-x:auto;

    scrollbar-width:none;

    -webkit-overflow-scrolling:touch;

}


.tabs-nav::-webkit-scrollbar{

    display:none;

}


/* =========================================
   BOTÓN
========================================= */

.tab-button{

    position:relative;

    display:inline-flex;

    align-items:center;

    justify-content:center;

    gap:9px;

    flex-shrink:0;

    min-height:62px;

    padding:0 21px;

    border:none;

    border-right:

        1px solid
        rgba(
            201,
            210,
            220,
            .62
        );

    cursor:pointer;

    white-space:nowrap;

    background:transparent;

    color:#697687;

    font-family:inherit;

    font-size:.72rem;

    font-weight:700;

    letter-spacing:.065em;

    text-transform:uppercase;

    transition:

        color .22s ease,

        background .22s ease;

}


.tab-button:first-child{

    border-left:

        1px solid
        rgba(
            201,
            210,
            220,
            .42
        );

}


/* =========================================
   INDICADOR ACTIVO
========================================= */

.tab-button::after{

    content:"";

    position:absolute;

    left:19px;

    right:19px;

    bottom:-1px;

    height:2px;

    background:transparent;

    transform:scaleX(.45);

    transform-origin:center;

    transition:

        background .22s ease,

        transform .22s ease;

}


/* =========================================
   HOVER
========================================= */

.tab-button:hover{

    color:#17375E;

    background:

        rgba(
            49,
            92,
            151,
            .035
        );

}


.tab-button:hover .tab-icon{

    color:#315C97;

    opacity:1;

}


/* =========================================
   ESTADO ACTIVO
========================================= */

.tab-button.active{

    color:#17375E;

    background:#FFFFFF;

}


.tab-button.active::after{

    background:#B08A4C;

    transform:scaleX(1);

}


/* =========================================
   ICONO
========================================= */

.tab-icon{

    display:flex;

    align-items:center;

    justify-content:center;

    width:18px;

    height:18px;

    flex-shrink:0;

    color:#7A8795;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1rem;

    font-weight:600;

    line-height:1;

    opacity:.78;

    transition:

        color .22s ease,

        opacity .22s ease;

}


.tab-button.active .tab-icon{

    color:#315C97;

    opacity:1;

}


/* =========================================
   TEXTO
========================================= */

.tab-label{

    line-height:1;

}


/* =========================================
   FOCUS
========================================= */

.tab-button:focus-visible{

    z-index:3;

    outline:

        2px solid
        rgba(
            49,
            92,
            151,
            .45
        );

    outline-offset:-2px;

}


/* =========================================
   CONTENIDO
========================================= */

.tabs-content{

    width:100%;

    min-height:320px;

    padding-top:30px;

}


.tab-panel{

    width:100%;

}


/* =========================================
   TRANSICIÓN DE CONTENIDO
========================================= */

.tab-content-enter-active,

.tab-content-leave-active{

    transition:

        opacity .22s ease,

        transform .22s ease;

}


.tab-content-enter-from{

    opacity:0;

    transform:

        translateY(
            8px
        );

}


.tab-content-leave-to{

    opacity:0;

    transform:

        translateY(
            -4px
        );

}


/* =========================================
   RESPONSIVE - TABLET
========================================= */

@media(max-width:900px){

    .novacourt-tabs{

        margin-top:30px;

    }


    .tabs-header::before{

        width:88px;

    }


    .tab-button{

        min-height:59px;

        padding:0 18px;

        font-size:.7rem;

    }


    .tabs-content{

        min-height:280px;

        padding-top:26px;

    }

}


/* =========================================
   RESPONSIVE - MOBILE
========================================= */

@media(max-width:576px){

    .novacourt-tabs{

        margin-top:24px;

    }


    .tabs-header::before{

        width:62px;

    }


    .tab-button{

        min-height:55px;

        gap:7px;

        padding:0 15px;

        font-size:.66rem;

        letter-spacing:.045em;

    }


    .tab-button::after{

        left:14px;

        right:14px;

    }


    .tab-icon{

        width:16px;

        height:16px;

        font-size:.88rem;

    }


    .tabs-content{

        min-height:250px;

        padding-top:22px;

    }

}

</style>