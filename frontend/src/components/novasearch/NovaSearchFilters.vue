<template>
    <aside class="nova-search-filters">

        <!-- =====================================
             CABECERA
        ====================================== -->

        <div class="filters-header">

            <div class="filters-header-icon">

                <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.7"
                    aria-hidden="true"
                >
                    <path d="M4 6h16" />
                    <path d="M7 12h10" />
                    <path d="M10 18h4" />
                </svg>

            </div>


            <div class="filters-header-content">

                <span class="filters-eyebrow">
                    BÚSQUEDA AVANZADA
                </span>

                <h3 class="filters-title">
                    Filtros jurídicos
                </h3>

            </div>

        </div>


        <!-- =====================================
             DESCRIPCIÓN
        ====================================== -->

        <p class="filters-description">
            Delimita las fuentes jurídicas para obtener resultados
            más precisos y relevantes.
        </p>


        <!-- =====================================
             DIVISOR
        ====================================== -->

        <div class="filters-divider"></div>


        <!-- =====================================
             TIPO DE FUENTE
        ====================================== -->

        <div class="filter-group">

            <span class="filter-label">
                Buscar en
            </span>


            <div
                class="document-options"
                role="radiogroup"
                aria-label="Tipo de fuente jurídica"
            >

                <!-- TODAS LAS FUENTES -->

                <label
                    class="document-option"
                    :class="{
                        active: tipoDocumentoModel === 'Ambos'
                    }"
                >

                    <input
                        v-model="tipoDocumentoModel"
                        type="radio"
                        name="tipo-documento"
                        value="Ambos"
                    />

                    <span
                        class="option-radio"
                        aria-hidden="true"
                    ></span>

                    <span class="option-content">

                        <strong>
                            Todas las fuentes
                        </strong>

                        <small>
                            Legislación y jurisprudencia
                        </small>

                    </span>

                </label>


                <!-- JURISPRUDENCIA -->

                <label
                    class="document-option"
                    :class="{
                        active:
                            tipoDocumentoModel === 'Jurisprudencia'
                    }"
                >

                    <input
                        v-model="tipoDocumentoModel"
                        type="radio"
                        name="tipo-documento"
                        value="Jurisprudencia"
                    />

                    <span
                        class="option-radio"
                        aria-hidden="true"
                    ></span>

                    <span class="option-content">

                        <strong>
                            Jurisprudencia
                        </strong>

                        <small>
                            Casaciones, resoluciones y precedentes
                        </small>

                    </span>

                </label>


                <!-- LEGISLACIÓN -->

                <label
                    class="document-option"
                    :class="{
                        active:
                            tipoDocumentoModel === 'Articulo'
                    }"
                >

                    <input
                        v-model="tipoDocumentoModel"
                        type="radio"
                        name="tipo-documento"
                        value="Articulo"
                    />

                    <span
                        class="option-radio"
                        aria-hidden="true"
                    ></span>

                    <span class="option-content">

                        <strong>
                            Legislación
                        </strong>

                        <small>
                            Leyes, decretos, normas y artículos
                        </small>

                    </span>

                </label>

            </div>

        </div>


        <!-- =====================================
             CONFIGURACIÓN ACTUAL
        ====================================== -->

        <div class="filters-summary">

            <span class="summary-label">
                CONFIGURACIÓN ACTUAL
            </span>


            <div class="summary-items">

                <span class="summary-chip">

                    <span class="summary-chip-dot"></span>

                    {{ tipoDocumentoLabel }}

                </span>

            </div>

        </div>


        <!-- =====================================
             RESTABLECER FILTROS
        ====================================== -->

        <button
            type="button"
            class="clear-filters-button"
            :disabled="!hasActiveFilters"
            @click="clearFilters"
        >

            <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
                aria-hidden="true"
            >
                <path
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 0 0 5.582 7.581L4 9"
                />

                <path
                    d="M20 20v-5h-.581m-15.357-2A8.001 8.001 0 0 0 18.419 16.42L20 15"
                />
            </svg>

            <span>
                Restablecer filtros
            </span>

        </button>

    </aside>
</template>


<script setup>

import { computed } from 'vue'


/* =========================================
   PROPS
========================================= */

const props = defineProps({

    filters: {

        type: Object,

        required: true

    }

})


/* =========================================
   EMITS
========================================= */

const emit = defineEmits([
    'update:filters'
])


/* =========================================
   TIPO DE DOCUMENTO CONECTADO AL PADRE
========================================= */

const tipoDocumentoModel = computed({

    get() {

        return props.filters?.tipoDocumento || 'Ambos'

    },

    set(value) {

        emit(
            'update:filters',
            {
                ...props.filters,
                tipoDocumento: value
            }
        )

    }

})


/* =========================================
   RESTABLECER FILTROS
========================================= */

function clearFilters() {

    emit(
        'update:filters',
        {
            ...props.filters,
            tipoDocumento: 'Ambos'
        }
    )

}


/* =========================================
   LABEL DEL FILTRO ACTUAL
========================================= */

const tipoDocumentoLabel = computed(() => {

    const labels = {

        Ambos: 'Todas las fuentes',

        Jurisprudencia: 'Jurisprudencia',

        Articulo: 'Legislación'

    }

    return (
        labels[props.filters?.tipoDocumento]
        ||
        'Todas las fuentes'
    )

})


/* =========================================
   VALIDAR SI HAY FILTRO ACTIVO
========================================= */

const hasActiveFilters = computed(() => {

    return (
        (props.filters?.tipoDocumento || 'Ambos')
        !==
        'Ambos'
    )

})

</script>


<style scoped>

/* =================================================
   CONTENEDOR PRINCIPAL
================================================= */

.nova-search-filters {

    width: 100%;

    box-sizing: border-box;

    padding: 22px;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #FCFDFE 100%
        );

    border:
        1px solid
        rgba(
            7,
            18,
            37,
            .10
        );

    border-radius: 12px;

    box-shadow:
        0 10px 28px
        rgba(
            7,
            18,
            37,
            .045
        );

}


/* =================================================
   CABECERA
================================================= */

.filters-header {

    display: flex;

    align-items: center;

    gap: 12px;

}


/* =================================================
   ICONO
================================================= */

.filters-header-icon {

    position: relative;

    width: 40px;

    height: 40px;

    flex: 0 0 40px;

    display: flex;

    align-items: center;

    justify-content: center;

    color:
        #C9A45C;

    background:
        #0B1628;

    border:
        1px solid
        rgba(
            201,
            164,
            92,
            .40
        );

    border-radius: 9px;

    box-shadow:
        0 5px 14px
        rgba(
            7,
            18,
            37,
            .10
        );

}


.filters-header-icon::after {

    content: "";

    position: absolute;

    inset: 4px;

    border:
        1px solid
        rgba(
            201,
            164,
            92,
            .16
        );

    border-radius: 6px;

    pointer-events: none;

}


.filters-header-icon svg {

    position: relative;

    z-index: 1;

    width: 19px;

    height: 19px;

}


/* =================================================
   CONTENIDO CABECERA
================================================= */

.filters-header-content {

    min-width: 0;

}


/* =================================================
   EYEBROW
================================================= */

.filters-eyebrow {

    display: block;

    margin-bottom: 4px;

    color:
        #9A7A42;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .58rem;

    font-weight:
        800;

    letter-spacing:
        1.35px;

    line-height:
        1.2;

}


/* =================================================
   TÍTULO
================================================= */

.filters-title {

    margin: 0;

    color:
        #0B1628;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:
        1.15rem;

    font-weight:
        500;

    line-height:
        1.25;

    letter-spacing:
        -.15px;

}


/* =================================================
   DESCRIPCIÓN
================================================= */

.filters-description {

    margin:
        15px
        0
        0;

    color:
        #687386;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .78rem;

    line-height:
        1.65;

}


/* =================================================
   DIVISOR
================================================= */

.filters-divider {

    width: 100%;

    height: 1px;

    margin:
        19px
        0;

    background:
        rgba(
            7,
            18,
            37,
            .09
        );

}


/* =================================================
   GRUPO
================================================= */

.filter-group {

    margin-bottom:
        22px;

}


.filter-label {

    display: flex;

    align-items: center;

    gap: 7px;

    margin-bottom:
        10px;

    color:
        #24354F;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .70rem;

    font-weight:
        800;

    letter-spacing:
        .35px;

}


.filter-label::before {

    content: "";

    width: 3px;

    height: 12px;

    background:
        #C9A45C;

    border-radius:
        2px;

}


/* =================================================
   OPCIONES
================================================= */

.document-options {

    display:
        flex;

    flex-direction:
        column;

    gap:
        8px;

}


/* =================================================
   OPCIÓN INDIVIDUAL
================================================= */

.document-option {

    position: relative;

    display: flex;

    align-items: center;

    gap: 10px;

    width: 100%;

    box-sizing: border-box;

    padding:
        11px
        10px;

    background:
        #FFFFFF;

    border:
        1px solid
        #E2E7ED;

    border-radius:
        8px;

    cursor:
        pointer;

    user-select:
        none;

    transition:
        border-color .2s ease,
        background .2s ease,
        box-shadow .2s ease,
        transform .2s ease;

}


.document-option:hover {

    background:
        #FAFBFC;

    border-color:
        #C8D2DE;

    transform:
        translateY(-1px);

}


.document-option.active {

    background:
        linear-gradient(
            135deg,
            #F8FAFC 0%,
            #F3F6F9 100%
        );

    border-color:
        rgba(
            201,
            164,
            92,
            .52
        );

    box-shadow:
        inset 3px 0 0
        #C9A45C;

}


/* =================================================
   RADIO NATIVO OCULTO
================================================= */

.document-option input {

    position:
        absolute;

    width:
        1px;

    height:
        1px;

    opacity:
        0;

    pointer-events:
        none;

}


/* =================================================
   RADIO PERSONALIZADO
================================================= */

.option-radio {

    position:
        relative;

    width:
        16px;

    height:
        16px;

    flex:
        0 0 16px;

    box-sizing:
        border-box;

    background:
        #FFFFFF;

    border:
        1.5px solid
        #B7C2CE;

    border-radius:
        50%;

    transition:
        border-color .2s ease,
        background .2s ease,
        box-shadow .2s ease;

}


.document-option:hover .option-radio {

    border-color:
        #8E9CAC;

}


.document-option.active .option-radio {

    border-color:
        #C9A45C;

    box-shadow:
        0 0 0 3px
        rgba(
            201,
            164,
            92,
            .10
        );

}


.document-option.active .option-radio::after {

    content: "";

    position:
        absolute;

    inset:
        3px;

    background:
        #C9A45C;

    border-radius:
        50%;

}


/* =================================================
   CONTENIDO DE OPCIÓN
================================================= */

.option-content {

    display:
        flex;

    flex-direction:
        column;

    gap:
        3px;

    min-width:
        0;

}


.option-content strong {

    color:
        #24354F;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .75rem;

    font-weight:
        700;

    line-height:
        1.3;

}


.option-content small {

    color:
        #8793A1;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .66rem;

    line-height:
        1.4;

}


/* =================================================
   CONFIGURACIÓN ACTUAL
================================================= */

.filters-summary {

    padding:
        15px
        0;

    border-top:
        1px solid
        rgba(
            7,
            18,
            37,
            .08
        );

}


.summary-label {

    display:
        block;

    margin-bottom:
        9px;

    color:
        #8C98A6;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .57rem;

    font-weight:
        800;

    letter-spacing:
        1.15px;

}


.summary-items {

    display:
        flex;

    flex-wrap:
        wrap;

    gap:
        6px;

}


.summary-chip {

    display:
        inline-flex;

    align-items:
        center;

    gap:
        6px;

    padding:
        6px
        9px;

    color:
        #52657A;

    background:
        #F4F6F8;

    border:
        1px solid
        #E1E6EB;

    border-radius:
        6px;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .66rem;

    font-weight:
        700;

}


.summary-chip-dot {

    width:
        5px;

    height:
        5px;

    flex:
        0 0 5px;

    background:
        #C9A45C;

    border-radius:
        50%;

}


/* =================================================
   BOTÓN RESTABLECER
================================================= */

.clear-filters-button {

    width:
        100%;

    min-height:
        40px;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    gap:
        8px;

    padding:
        0
        13px;

    color:
        #687386;

    background:
        #FFFFFF;

    border:
        1px solid
        #D7DEE6;

    border-radius:
        7px;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .72rem;

    font-weight:
        700;

    cursor:
        pointer;

    transition:
        background .2s ease,
        border-color .2s ease,
        color .2s ease,
        transform .2s ease;

}


.clear-filters-button svg {

    width:
        15px;

    height:
        15px;

}


.clear-filters-button:hover:not(:disabled) {

    color:
        #0B1628;

    background:
        #F7F9FB;

    border-color:
        #BFCAD6;

    transform:
        translateY(-1px);

}


.clear-filters-button:active:not(:disabled) {

    transform:
        translateY(0);

}


.clear-filters-button:disabled {

    opacity:
        .42;

    cursor:
        not-allowed;

}


/* =================================================
   RESPONSIVE
================================================= */

@media (max-width: 900px) {

    .nova-search-filters {

        padding:
            21px;

    }

}


@media (max-width: 640px) {

    .nova-search-filters {

        padding:
            19px;

    }

}


@media (max-width: 576px) {

    .nova-search-filters {

        border-radius:
            10px;

    }

    .filters-description {

        font-size:
            .76rem;

    }

    .document-option {

        padding:
            11px
            9px;

    }

}

</style>