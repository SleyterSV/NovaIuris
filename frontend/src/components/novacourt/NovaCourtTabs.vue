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
                        active: activeTab === tab.id
                    }"
                    :aria-selected="activeTab === tab.id"
                    :aria-controls="`panel-${tab.id}`"
                    :tabindex="activeTab === tab.id ? 0 : -1"
                    role="tab"
                    @click="selectTab(tab.id)"
                    @keydown.right.prevent="focusNextTab(tab.id)"
                    @keydown.left.prevent="focusPreviousTab(tab.id)"
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
            :id="`panel-${activeTab}`"
            :aria-labelledby="`tab-${activeTab}`"
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
                    ></slot>

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

    isValidTab(props.defaultTab)

        ? props.defaultTab

        : "overview"

)


/* =========================================
   VALIDAR PESTAÑA
========================================= */

function isValidTab(tabId) {

    return tabs.some(

        tab => tab.id === tabId

    )

}


/* =========================================
   SELECCIONAR PESTAÑA
========================================= */

function selectTab(tabId) {

    if (!isValidTab(tabId)) {

        return

    }

    if (activeTab.value === tabId) {

        return

    }

    activeTab.value = tabId

}


/* =========================================
   NAVEGACIÓN CON TECLADO
========================================= */

function focusTab(tabId) {

    const index = tabs.findIndex(

        tab => tab.id === tabId

    )

    if (index === -1) {

        return

    }

    const nextTab = tabs[index]

    activeTab.value = nextTab.id

    emit(

        "change",

        nextTab.id

    )

}


function focusNextTab(tabId) {

    const index = tabs.findIndex(

        tab => tab.id === tabId

    )

    if (index === -1) {

        return

    }

    const nextIndex =

        (index + 1) % tabs.length

    const nextTab = tabs[nextIndex]

    focusTab(nextTab.id)

}


function focusPreviousTab(tabId) {

    const index = tabs.findIndex(

        tab => tab.id === tabId

    )

    if (index === -1) {

        return

    }

    const previousIndex =

        (index - 1 + tabs.length) %

        tabs.length

    const previousTab = tabs[previousIndex]

    focusTab(previousTab.id)

}


/* =========================================
   EMITIR CAMBIOS
========================================= */

watch(

    activeTab,

    value => {

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

    value => {

        if (

            value &&

            isValidTab(value) &&

            value !== activeTab.value

        ) {

            activeTab.value = value

        }

    }

)

</script>


<style scoped>

/* =====================================================
   NOVACOURT TABS

   IDENTIDAD:
   JURÍDICA · INSTITUCIONAL · SOBRIA · PREMIUM

   PALETA:
   AZUL PROFUNDO  #17375E
   AZUL            #315C97
   DORADO          #B08A4C
   TEXTO           #24364A
   GRIS            #687789

   OBJETIVO:
   Las pestañas deben sentirse como navegación
   institucional de una plataforma jurídica profesional,
   no como botones genéricos.
===================================================== */


/* =====================================================
   CONTENEDOR PRINCIPAL
===================================================== */

.novacourt-tabs {

    width: 100%;

    margin-top: 34px;

}


/* =====================================================
   CABECERA
===================================================== */

.tabs-header {

    position: relative;

    width: 100%;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #F8FAFC 100%
        );

    border-top:
        1px solid
        #D6DFEA;

    border-bottom:
        1px solid
        #C9D4DF;

}


/* =====================================================
   LÍNEA INSTITUCIONAL SUPERIOR
===================================================== */

.tabs-header::before {

    content: "";

    position: absolute;

    top: -1px;

    left: 0;

    width: 118px;

    height: 2px;

    background:
        linear-gradient(
            90deg,
            #17375E 0%,
            #315C97 70%,
            rgba(49,92,151,0) 100%
        );

    z-index: 2;

}


/* =====================================================
   NAVEGACIÓN
===================================================== */

.tabs-nav {

    display: flex;

    align-items: stretch;

    width: 100%;

    overflow-x: auto;

    scrollbar-width: none;

    -webkit-overflow-scrolling: touch;

}

.tabs-nav::-webkit-scrollbar {

    display: none;

}


/* =====================================================
   BOTÓN
===================================================== */

.tab-button {

    position: relative;

    display: inline-flex;

    align-items: center;

    justify-content: center;

    gap: 9px;

    flex: 0 0 auto;

    min-height: 62px;

    padding: 0 22px;

    border: none;

    border-right:
        1px solid
        rgba(
            201,
            210,
            220,
            .62
        );

    cursor: pointer;

    white-space: nowrap;

    background: transparent;

    color: #748092;

    font-family: inherit;

    font-size: .71rem;

    font-weight: 700;

    letter-spacing: .065em;

    text-transform: uppercase;

    transition:
        color .22s ease,
        background-color .22s ease;

}

.tab-button:first-child {

    border-left:
        1px solid
        rgba(
            201,
            210,
            220,
            .42
        );

}


/* =====================================================
   INDICADOR INACTIVO
===================================================== */

.tab-button::after {

    content: "";

    position: absolute;

    left: 20px;

    right: 20px;

    bottom: -1px;

    height: 2px;

    background: transparent;

    transform:
        scaleX(.35);

    transform-origin: center;

    transition:
        background-color .22s ease,
        transform .22s ease;

}


/* =====================================================
   HOVER
===================================================== */

.tab-button:hover {

    color: #17375E;

    background:
        rgba(
            49,
            92,
            151,
            .035
        );

}

.tab-button:hover .tab-icon {

    color: #315C97;

    opacity: 1;

}


/* =====================================================
   ESTADO ACTIVO
===================================================== */

.tab-button.active {

    color: #17375E;

    background: #FFFFFF;

}

.tab-button.active::after {

    background: #B08A4C;

    transform:
        scaleX(1);

}

.tab-button.active .tab-icon {

    color: #315C97;

    opacity: 1;

}


/* =====================================================
   ICONO
===================================================== */

.tab-icon {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    width: 18px;

    height: 18px;

    flex-shrink: 0;

    color: #8995A3;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: .98rem;

    font-weight: 600;

    line-height: 1;

    opacity: .78;

    transition:
        color .22s ease,
        opacity .22s ease;

}


/* =====================================================
   TEXTO
===================================================== */

.tab-label {

    display: inline-flex;

    align-items: center;

    line-height: 1;

}


/* =====================================================
   FOCUS ACCESIBLE
===================================================== */

.tab-button:focus {

    outline: none;

}

.tab-button:focus-visible {

    z-index: 4;

    outline:
        2px solid
        rgba(
            49,
            92,
            151,
            .45
        );

    outline-offset: -2px;

}


/* =====================================================
   CONTENIDO
===================================================== */

.tabs-content {

    width: 100%;

    min-height: 320px;

    padding-top: 30px;

}

.tab-panel {

    width: 100%;

}


/* =====================================================
   TRANSICIÓN
===================================================== */

.tab-content-enter-active,
.tab-content-leave-active {

    transition:
        opacity .22s ease,
        transform .22s ease;

}

.tab-content-enter-from {

    opacity: 0;

    transform:
        translateY(8px);

}

.tab-content-leave-to {

    opacity: 0;

    transform:
        translateY(-4px);

}


/* =====================================================
   RESPONSIVE — TABLET
===================================================== */

@media (max-width: 900px) {

    .novacourt-tabs {

        margin-top: 30px;

    }


    .tabs-header::before {

        width: 92px;

    }


    .tab-button {

        min-height: 59px;

        padding:
            0 18px;

        font-size: .69rem;

    }


    .tab-button::after {

        left: 17px;

        right: 17px;

    }


    .tabs-content {

        min-height: 280px;

        padding-top: 26px;

    }

}


/* =====================================================
   RESPONSIVE — MOBILE
===================================================== */

@media (max-width: 576px) {

    .novacourt-tabs {

        margin-top: 24px;

    }


    .tabs-header::before {

        width: 66px;

    }


    .tab-button {

        min-height: 55px;

        gap: 7px;

        padding:
            0 15px;

        font-size: .64rem;

        letter-spacing: .045em;

    }


    .tab-button::after {

        left: 14px;

        right: 14px;

    }


    .tab-icon {

        width: 16px;

        height: 16px;

        font-size: .88rem;

    }


    .tabs-content {

        min-height: 250px;

        padding-top: 22px;

    }

}


/* =====================================================
   RESPONSIVE — TELÉFONOS PEQUEÑOS
===================================================== */

@media (max-width: 400px) {

    .tab-button {

        min-height: 52px;

        gap: 6px;

        padding:
            0 13px;

        font-size: .61rem;

    }


    .tab-button::after {

        left: 12px;

        right: 12px;

    }


    .tab-icon {

        width: 15px;

        height: 15px;

        font-size: .82rem;

    }

}


/* =====================================================
   REDUCCIÓN DE MOVIMIENTO
===================================================== */

@media (prefers-reduced-motion: reduce) {

    .tab-button,
    .tab-button::after,
    .tab-icon,
    .tab-content-enter-active,
    .tab-content-leave-active {

        transition: none;

    }

}

</style>