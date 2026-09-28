<template>

    <section class="case-tabs">

        <!-- =====================================================
             NAVEGACIÓN
        ====================================================== -->

        <div class="tabs-header">

            <button
                v-for="tab in visibleTabs"
                :key="tab.id"
                type="button"
                class="tab-button"
                :class="{
                    active: activeTab === tab.id
                }"
                :aria-selected="activeTab === tab.id"
                @click="activeTab = tab.id"
            >

                <span class="tab-icon">

                    <!-- INFORME -->
                    <svg
                        v-if="tab.id === 'report'"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        aria-hidden="true"
                    >
                        <path
                            d="M6 3.5h8l4 4V20.5H6z"
                        />

                        <path
                            d="M14 3.5v4h4"
                        />

                        <path
                            d="M9 12h6"
                        />

                        <path
                            d="M9 15.5h6"
                        />

                    </svg>


                    <!-- ANÁLISIS -->
                    <svg
                        v-else-if="tab.id === 'analysis'"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        aria-hidden="true"
                    >
                        <path
                            d="M12 3v18"
                        />

                        <path
                            d="M5 6h14"
                        />

                        <path
                            d="M7 6l-3 6a3 3 0 0 0 6 0L7 6Z"
                        />

                        <path
                            d="M17 6l-3 6a3 3 0 0 0 6 0l-3-6Z"
                        />

                        <path
                            d="M8 21h8"
                        />

                    </svg>


                    <!-- EVIDENCIA -->
                    <svg
                        v-else-if="tab.id === 'evidence'"
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
                            rx="1.5"
                        />

                        <path
                            d="M8.5 8h7"
                        />

                        <path
                            d="M8.5 11.5h7"
                        />

                        <path
                            d="M8.5 15h4.5"
                        />

                    </svg>


                    <!-- RIESGOS -->
                    <svg
                        v-else-if="tab.id === 'risk'"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        aria-hidden="true"
                    >
                        <path
                            d="M12 3.5L21 20H3L12 3.5Z"
                        />

                        <path
                            d="M12 9v5"
                        />

                        <path
                            d="M12 17h.01"
                        />

                    </svg>


                    <!-- CONTRAARGUMENTOS -->
                    <svg
                        v-else-if="tab.id === 'counter'"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        aria-hidden="true"
                    >
                        <path
                            d="M4 6.5h16"
                        />

                        <path
                            d="M4 12h11"
                        />

                        <path
                            d="M4 17.5h7"
                        />

                        <path
                            d="M17 14l3 3-3 3"
                        />

                        <path
                            d="M20 17h-6"
                        />

                    </svg>


                    <!-- ESTRATEGIA -->
                    <svg
                        v-else
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

                        <circle
                            cx="12"
                            cy="12"
                            r="3"
                        />

                        <path
                            d="M12 4V2.5"
                        />

                        <path
                            d="M12 21.5V20"
                        />

                        <path
                            d="M4 12H2.5"
                        />

                        <path
                            d="M21.5 12H20"
                        />

                    </svg>

                </span>


                <span class="tab-label">
                    {{ tab.label }}
                </span>

            </button>

        </div>


        <!-- =====================================================
             CONTENIDO
        ====================================================== -->

        <div class="tabs-content">

            <slot
                :name="activeTab"
            ></slot>

        </div>

    </section>

</template>


<script setup>

import {
    computed,
    ref,
    watch
} from "vue"


/* =========================================================
   PROPS
========================================================= */

const props = defineProps({

    defaultTab: {

        type: String,

        default: "report"

    },

    availableTabs: {
        type: Array,
        default: () => []

    }

})


/* =========================================================
   EVENTOS
========================================================= */

const emit = defineEmits([
    "change"
])


/* =========================================================
   PESTAÑAS
========================================================= */

const tabs = [

    { id: "summary", label: "Resumen" },

    {
        id: "report",
        label: "Informe"
    },

    {
        id: "analysis",
        label: "Análisis"
    },

    { id: "arguments", label: "Argumentos" },

    {
        id: "evidence",
        label: "Evidencia"
    },

    {
        id: "risk",
        label: "Riesgos"
    },

    {
        id: "counter",
        label: "Contraargumentos"
    },

    {
        id: "strategy",
        label: "Estrategia"
    },

    { id: "sources", label: "Fuentes" }

]


/* =========================================================
   ESTADO
========================================================= */

const activeTab = ref(
    props.defaultTab
)

const visibleTabs = computed(() => props.availableTabs.length
    ? tabs.filter(tab => props.availableTabs.includes(tab.id))
    : tabs)

watch(visibleTabs, (available) => {
    if (available.length && !available.some(tab => tab.id === activeTab.value)) {
        activeTab.value = available[0].id
    }
}, { immediate: true })


/* =========================================================
   CAMBIO DE PESTAÑA
========================================================= */

watch(
    activeTab,
    (value) => {

        emit(
            "change",
            value
        )

    }
)

</script>


<style scoped>

/* =========================================================
   NOVACASE — CASE TABS
========================================================= */

.case-tabs {

    width: 100%;

    background: #FFFFFF;

    border:
        1px solid
        #DCE5EE;

    border-radius: 14px;

    overflow: hidden;

    box-shadow:
        0 8px 24px
        rgba(
            23,
            55,
            94,
            .045
        );

}


/* =========================================================
   CABECERA DE PESTAÑAS
========================================================= */

.tabs-header {

    display: flex;

    align-items: stretch;

    gap: 0;

    width: 100%;

    padding:
        0 8px;

    background:
        #FBFCFD;

    border-bottom:
        1px solid
        #DCE5EE;

    overflow-x: auto;

    scrollbar-width: none;

}

.tabs-header::-webkit-scrollbar {

    display: none;

}


/* =========================================================
   BOTÓN
========================================================= */

.tab-button {

    position: relative;

    display: inline-flex;

    align-items: center;

    justify-content: center;

    gap: 8px;

    min-height: 58px;

    padding:
        0 19px;

    border: none;

    border-bottom:
        2px solid
        transparent;

    background:
        transparent;

    color: #748397;

    font-family: inherit;

    font-size: .70rem;

    font-weight: 750;

    letter-spacing: .15px;

    white-space: nowrap;

    cursor: pointer;

    transition:
        color .20s ease,
        background-color .20s ease,
        border-color .20s ease;

}


/* =========================================================
   ICONO
========================================================= */

.tab-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 25px;

    height: 25px;

    flex: 0 0 25px;

    color: #8997A7;

    transition:
        color .20s ease;

}


.tab-icon svg {

    width: 17px;

    height: 17px;

}


/* =========================================================
   TEXTO
========================================================= */

.tab-label {

    line-height: 1;

}


/* =========================================================
   HOVER
========================================================= */

.tab-button:hover {

    color: #315C97;

    background:
        #F7F9FB;

}

.tab-button:hover .tab-icon {

    color: #315C97;

}


/* =========================================================
   ACTIVO
========================================================= */

.tab-button.active {

    color: #17375E;

    background:
        #FFFFFF;

    border-bottom-color:
        #B08A4C;

}


.tab-button.active .tab-icon {

    color: #8A6A36;

}


/* =========================================================
   INDICADOR SUPERIOR SUTIL
========================================================= */

.tab-button.active::before {

    content: "";

    position: absolute;

    top: 0;

    left: 18px;

    right: 18px;

    height: 2px;

    background:
        #B08A4C;

    opacity: .85;

}


/* =========================================================
   CONTENIDO
========================================================= */

.tabs-content {

    min-height: 500px;

    padding: 30px;

    background:
        #FFFFFF;

}


/* =========================================================
   FOCUS
========================================================= */

.tab-button:focus-visible {

    outline:
        2px solid
        rgba(
            49,
            92,
            151,
            .35
        );

    outline-offset:
        -3px;

}


/* =========================================================
   1000 PX
========================================================= */

@media (max-width: 1000px) {

    .tab-button {

        padding:
            0 15px;

        font-size: .67rem;

    }

    .tabs-content {

        padding: 26px;

    }

}


/* =========================================================
   760 PX
========================================================= */

@media (max-width: 760px) {

    .case-tabs {

        border-radius: 12px;

    }

    .tabs-header {

        padding:
            0 4px;

    }

    .tab-button {

        min-height: 54px;

        padding:
            0 13px;

        gap: 7px;

    }

    .tab-icon {

        width: 22px;

        height: 22px;

        flex-basis: 22px;

    }

    .tab-icon svg {

        width: 16px;

        height: 16px;

    }

    .tabs-content {

        min-height: 400px;

        padding: 22px;

    }

}


/* =========================================================
   520 PX
========================================================= */

@media (max-width: 520px) {

    .tab-button {

        min-height: 51px;

        padding:
            0 12px;

    }

    .tab-label {

        font-size: .64rem;

    }

    .tabs-content {

        padding: 18px;

    }

    .tab-button.active::before {

        left: 12px;

        right: 12px;

    }

}


/* =========================================================
   REDUCIR MOVIMIENTO
========================================================= */

@media (
    prefers-reduced-motion: reduce
) {

    .tab-button,
    .tab-icon {

        transition: none;

    }

}

</style>
