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
                    stroke-width="1.8"
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
                stroke-width="1.8"
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

/* =========================================
   CONTENEDOR PRINCIPAL
========================================= */

.nova-search-filters {

    width: 100%;
    box-sizing: border-box;

    background: #FFFFFF;

    border: 1px solid #DCE3EB;
    border-radius: 12px;

    padding: 24px;

    box-shadow:
        0 12px 30px
        rgba(23, 55, 94, 0.045);

}


/* =========================================
   CABECERA
========================================= */

.filters-header {

    display: flex;
    align-items: center;

    gap: 13px;

}

.filters-header-icon {

    width: 42px;
    height: 42px;

    display: flex;
    align-items: center;
    justify-content: center;

    flex: 0 0 42px;

    border: 1px solid #E0E6ED;
    border-radius: 10px;

    background: #F5F7FA;

    color: #315C97;

}

.filters-header-icon svg {

    width: 20px;
    height: 20px;

}

.filters-header-content {

    min-width: 0;

}

.filters-eyebrow {

    display: block;

    margin-bottom: 4px;

    color: #7A6440;

    font-size: 0.62rem;
    font-weight: 800;

    letter-spacing: 1.25px;

}

.filters-title {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.2rem;
    font-weight: 600;

    line-height: 1.3;

}


/* =========================================
   DESCRIPCIÓN
========================================= */

.filters-description {

    margin: 16px 0 0;

    color: #6D7B8B;

    font-size: 0.83rem;
    line-height: 1.65;

}


/* =========================================
   DIVISOR
========================================= */

.filters-divider {

    width: 100%;
    height: 1px;

    margin: 22px 0;

    background: #E4E9EF;

}


/* =========================================
   GRUPO
========================================= */

.filter-group {

    margin-bottom: 26px;

}

.filter-label {

    display: block;

    margin-bottom: 10px;

    color: #334B66;

    font-size: 0.75rem;
    font-weight: 800;

    letter-spacing: 0.25px;

}


/* =========================================
   OPCIONES DE DOCUMENTO
========================================= */

.document-options {

    display: flex;
    flex-direction: column;

    gap: 10px;

}

.document-option {

    position: relative;

    display: flex;
    align-items: center;

    gap: 11px;

    width: 100%;
    box-sizing: border-box;

    padding: 13px 12px;

    border: 1px solid #E0E6ED;
    border-radius: 9px;

    background: #FFFFFF;

    cursor: pointer;
    user-select: none;

    transition:
        border-color 0.2s ease,
        background 0.2s ease,
        box-shadow 0.2s ease;

}

.document-option:hover {

    border-color: #BFCBD8;

    background: #FBFCFE;

}

.document-option.active {

    border-color:
        rgba(49, 92, 151, 0.55);

    background: #F7F9FC;

    box-shadow:
        0 4px 14px
        rgba(49, 92, 151, 0.06);

}


/* =========================================
   INPUT RADIO
========================================= */

.document-option input {

    position: absolute;

    width: 1px;
    height: 1px;

    opacity: 0;

    pointer-events: none;

}


/* =========================================
   RADIO PERSONALIZADO
========================================= */

.option-radio {

    width: 16px;
    height: 16px;

    flex: 0 0 16px;

    position: relative;

    box-sizing: border-box;

    border: 1.5px solid #B6C1CD;
    border-radius: 50%;

    background: #FFFFFF;

    transition:
        border-color 0.2s ease,
        background 0.2s ease;

}

.document-option.active .option-radio {

    border-color: #315C97;

}

.document-option.active .option-radio::after {

    content: "";

    position: absolute;

    inset: 3px;

    border-radius: 50%;

    background: #315C97;

}


/* =========================================
   CONTENIDO
========================================= */

.option-content {

    display: flex;
    flex-direction: column;

    gap: 3px;

    min-width: 0;

}

.option-content strong {

    color: #29415D;

    font-size: 0.78rem;
    font-weight: 700;

}

.option-content small {

    color: #8794A2;

    font-size: 0.7rem;

    line-height: 1.4;

}


/* =========================================
   CONFIGURACIÓN ACTUAL
========================================= */

.filters-summary {

    padding: 16px 0;

    border-top: 1px solid #E4E9EF;

}

.summary-label {

    display: block;

    margin-bottom: 10px;

    color: #98A3AE;

    font-size: 0.61rem;
    font-weight: 800;

    letter-spacing: 1.15px;

}

.summary-items {

    display: flex;
    flex-wrap: wrap;

    gap: 7px;

}

.summary-chip {

    display: inline-flex;
    align-items: center;

    padding: 6px 10px;

    border: 1px solid #E1E7ED;
    border-radius: 6px;

    background: #F4F7FA;

    color: #52657A;

    font-size: 0.7rem;
    font-weight: 700;

}


/* =========================================
   BOTÓN RESTABLECER
========================================= */

.clear-filters-button {

    width: 100%;
    min-height: 42px;

    display: flex;
    align-items: center;
    justify-content: center;

    gap: 8px;

    padding: 0 14px;

    border: 1px solid #D4DDE7;
    border-radius: 8px;

    background: #FFFFFF;

    color: #52657A;

    font-size: 0.78rem;
    font-weight: 700;

    cursor: pointer;

    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        color 0.2s ease;

}

.clear-filters-button svg {

    width: 16px;
    height: 16px;

}

.clear-filters-button:hover:not(:disabled) {

    background: #F7F9FC;

    border-color: #BFCBD8;

    color: #17375E;

}

.clear-filters-button:disabled {

    opacity: 0.45;

    cursor: not-allowed;

}


/* =========================================
   RESPONSIVE
========================================= */

@media (max-width: 900px) {

    .nova-search-filters {

        padding: 22px;

    }

}

@media (max-width: 640px) {

    .nova-search-filters {

        padding: 20px;

    }

}
</style>