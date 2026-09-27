<script setup>
import { watch } from 'vue'
import { useRoute } from 'vue-router'
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
    sources,
    citations,
    sourceWarnings,
    resultStatus,
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
    progressStages,
    searchCounts,

    performSearch,
    cancelSearch,
    updateFilter
} = useNovaSearch()

const route = useRoute()
watch(() => route.query.q, value => {
    if (typeof value === 'string') searchQuery.value = value.slice(0, 10000)
}, { immediate: true })


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
        newFilters?.modulo !== undefined &&
        newFilters.modulo !== filters.modulo
    ) {

        updateFilter(
            'modulo',
            newFilters.modulo
        )

    }


    if (
        newFilters?.solo_vigentes !== undefined &&
        newFilters.solo_vigentes !== filters.solo_vigentes
    ) {

        updateFilter(
            'solo_vigentes',
            newFilters.solo_vigentes
        )

    }

}

function resetFilters() {
    handleFiltersUpdate({ modulo: 'Todos', solo_vigentes: true })
}

function useSuggestion(value) {
    searchQuery.value = value
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
                    :stages="progressStages"
                    :counts="searchCounts"
                    @cancel="cancelSearch"
                />


                <!-- ERROR -->

                <NovaSearchError
                    v-else-if="searchError"
                    :message="searchError"
                    @retry="performSearch"
                />


                <!-- RESULTADOS -->

                <template
                    v-else-if="searchResults.length > 0"
                >

                    <NovaSearchAnswer
                        v-if="answer"
                        :answer="answer"
                        :sources="sources"
                        :citations="citations"
                        :source-warnings="sourceWarnings"
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
                    :mode="resultStatus === 'no_results' ? 'no-results' : 'initial'"
                    :query="searchQuery"
                    :show-suggestions="resultStatus !== 'no_results'"
                    @suggestion="useSuggestion"
                />
                <button v-if="resultStatus === 'no_results'" class="reset-search-filters" type="button" @click="resetFilters">
                    Restablecer filtros
                </button>

            </section>

        </section>

    </main>

</template>


<style scoped>

/* =========================================
   NOVA SEARCH
   ESTRUCTURA PRINCIPAL
========================================= */

.novasearch-view {

    width: 100%;
    min-height: 100vh;

    margin: 0;

    color: #0B1628;

    background:
        #F5F7F9;

}


/* =========================================
   HEADER
========================================= */

.novasearch-view > .nova-search-header {

    width: 100%;

}


/* =========================================
   BUSCADOR
========================================= */

.novasearch-search-section {

    width: 100%;
    max-width: 1280px;

    margin: 0 auto;

    padding:
        36px
        32px
        0;

}


/* =========================================
   ÁREA PRINCIPAL
========================================= */

.novasearch-workspace {

    width: 100%;
    max-width: 1280px;

    margin:
        28px auto 0;

    padding:
        0
        32px
        60px;

    display: grid;

    grid-template-columns:
        260px
        minmax(0, 1fr);

    align-items: start;

    gap: 28px;

}


/* =========================================
   SIDEBAR
========================================= */

.novasearch-sidebar {

    position: sticky;

    top: 96px;

    align-self: start;

}


/* =========================================
   RESULTADOS
========================================= */

.novasearch-results {

    width: 100%;

    min-width: 0;

}

.reset-search-filters {
    display: block;
    margin: 12px auto 0;
    padding: 8px 12px;
    border: 1px solid #ced8e3;
    border-radius: 7px;
    background: #fff;
    color: #315c97;
    font: inherit;
    cursor: pointer;
}

.reset-search-filters:focus-visible {
    outline: 2px solid #315c97;
    outline-offset: 2px;
}


/* =========================================
   TABLET
========================================= */

@media (max-width: 900px) {

    .novasearch-search-section {

        padding:
            30px
            24px
            0;

    }


    .novasearch-workspace {

        grid-template-columns:
            1fr;

        gap: 20px;

        padding:
            0
            24px
            50px;

    }


    .novasearch-sidebar {

        position: static;

        width: 100%;

    }

}


/* =========================================
   MOBILE
========================================= */

@media (max-width: 576px) {

    .novasearch-search-section {

        padding:
            24px
            18px
            0;

    }


    .novasearch-workspace {

        margin-top:
            20px;

        padding:
            0
            18px
            40px;

        gap:
            16px;

    }

}

</style>
