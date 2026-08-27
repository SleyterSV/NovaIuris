<script setup>
import { useNovaSearch } from '@/composables/useNovaSearch'

import NovaSearchHeader from '@/components/novasearch/NovaSearchHeader.vue'
import NovaSearchInput from '@/components/novasearch/NovaSearchInput.vue'
import NovaSearchFilters from '@/components/novasearch/NovaSearchFilters.vue'
import NovaSearchProgress from '@/components/novasearch/NovaSearchProgress.vue'
import NovaSearchAnswer from '@/components/novasearch/NovaSearchAnswer.vue'
import NovaSearchAnalysis from '@/components/novasearch/NovaSearchAnalysis.vue'
import NovaSearchResults from '@/components/novasearch/NovaSearchResults.vue'
import NovaSearchFallback from '@/components/novasearch/NovaSearchFallback.vue'
import NovaSearchEmptyState from '@/components/novasearch/NovaSearchEmptyState.vue'
import NovaSearchError from '@/components/novasearch/NovaSearchError.vue'


/* =========================================
   NOVA SEARCH - ESTADO Y LÓGICA
========================================= */

const {
    searchQuery,
    isSearching,
    searchError,

    answer,
    analysis,
    normalizedQuery,

    searchResults,
    totalResults,
    searchTime,

    filters,

    isFallbackResponse,
    fallbackDisclaimer,

    searchStage,
    searchProgress,

    performSearch,
    updateFilter
} = useNovaSearch()


/* =========================================
   ÁREAS JURÍDICAS DISPONIBLES
========================================= */

const modulosDisponibles = [

    'Todos',

    'Derecho Civil',

    'Derecho Laboral',

    'Derecho Penal',

    'Derecho Constitucional',

    'Derecho Administrativo',

    'Derecho de Familia',

    'Derecho Tributario',

    'Derecho Corporativo',

    'Derecho del Consumidor',

    'Derecho Procesal Civil',

    'Derecho Procesal Penal',

    'Jurisprudencia'

]


/* =========================================
   ACTUALIZAR FILTROS
========================================= */

function handleFiltersUpdate(newFilters) {

    if (
        newFilters?.modulo !== undefined
        &&
        newFilters.modulo !== filters.modulo
    ) {

        updateFilter(
            'modulo',
            newFilters.modulo
        )

    }


    if (
        newFilters?.tipoDocumento !== undefined
        &&
        newFilters.tipoDocumento !== filters.tipoDocumento
    ) {

        updateFilter(
            'tipoDocumento',
            newFilters.tipoDocumento
        )

    }


    if (
        newFilters?.fecha !== undefined
        &&
        newFilters.fecha !== filters.fecha
    ) {

        updateFilter(
            'fecha',
            newFilters.fecha
        )

    }

}
</script>


<template>

    <main
        class="novasearch-view"
        aria-label="NOVA SEARCH"
    >

        <!-- =====================================
             CABECERA DEL MÓDULO
        ====================================== -->

        <NovaSearchHeader />


        <!-- =====================================
             CONSULTA PRINCIPAL
        ====================================== -->

        <section
            class="novasearch-search-section"
            aria-label="Consulta jurídica"
        >

            <NovaSearchInput
                v-model="searchQuery"
                :loading="isSearching"
                @search="performSearch"
            />

        </section>


        <!-- =====================================
             ÁREA DE TRABAJO
        ====================================== -->

        <section class="novasearch-workspace">


            <!-- =================================
                 FILTROS
            ================================== -->

            <aside
                class="novasearch-sidebar"
                aria-label="Filtros jurídicos"
            >

                <NovaSearchFilters
                    :filters="filters"
                    :modulos="modulosDisponibles"
                    @update:filters="handleFiltersUpdate"
                />

            </aside>


            <!-- =================================
                 RESULTADOS
            ================================== -->

            <section
                class="novasearch-results"
                aria-live="polite"
            >


                <!-- PROGRESO -->

                <NovaSearchProgress
                    v-if="isSearching"
                    :stage="searchStage"
                    :progress="searchProgress"
                />


                <!-- ERROR -->

                <NovaSearchError
                    v-else-if="searchError"
                    :message="searchError"
                />


                <!-- RESULTADOS -->

                <template
                    v-else-if="searchResults.length > 0"
                >

                    <NovaSearchAnswer
                        v-if="answer"
                        :answer="answer"
                        :search-time="searchTime"
                        :total-results="totalResults"
                        :analysis="analysis"
                    />


                    <NovaSearchAnalysis
                        v-if="Object.keys(analysis).length > 0"
                        :analysis="analysis"
                        :normalized-query="normalizedQuery"
                    />


                    <NovaSearchFallback
                        v-if="isFallbackResponse"
                        :message="fallbackDisclaimer"
                    />


                    <NovaSearchResults
                        :results="searchResults"
                        :total-results="totalResults"
                    />

                </template>


                <!-- ESTADO VACÍO -->

                <NovaSearchEmptyState
                    v-else
                    :has-query="Boolean(searchQuery.trim())"
                />

            </section>

        </section>

    </main>

</template>


<style scoped>

/* =========================================
   NOVA SEARCH VIEW
========================================= */

.novasearch-view {

    width: 100%;
    max-width: 1440px;

    margin: 0 auto;

    padding:
        32px
        28px
        56px;

    color: #17375E;

}


/* =========================================
   SECCIÓN DE BÚSQUEDA
========================================= */

.novasearch-search-section {

    width: 100%;

    margin-top: 24px;

}


/* =========================================
   ÁREA PRINCIPAL
========================================= */

.novasearch-workspace {

    display: grid;

    grid-template-columns:
        270px
        minmax(0, 1fr);

    align-items: start;

    gap: 28px;

    width: 100%;

    margin-top: 28px;

}


/* =========================================
   SIDEBAR DE FILTROS
========================================= */

.novasearch-sidebar {

    position: sticky;

    top: 24px;

    align-self: start;

}


/* =========================================
   ÁREA DE RESULTADOS
========================================= */

.novasearch-results {

    width: 100%;

    min-width: 0;

}


/* =========================================
   RESPONSIVE - TABLET
========================================= */

@media (max-width: 900px) {

    .novasearch-view {

        padding:
            24px
            20px
            44px;

    }


    .novasearch-workspace {

        grid-template-columns: 1fr;

        gap: 20px;

    }


    .novasearch-sidebar {

        position: static;

        width: 100%;

    }

}


/* =========================================
   RESPONSIVE - MOBILE
========================================= */

@media (max-width: 576px) {

    .novasearch-view {

        padding:
            16px
            14px
            36px;

    }


    .novasearch-search-section {

        margin-top: 16px;

    }


    .novasearch-workspace {

        margin-top: 20px;

        gap: 16px;

    }

}

</style>