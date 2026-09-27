import { API_URL } from "../config/api.js"
import { ref, reactive } from 'vue'

export function useNovaSearch() {

    // =========================================================
    // 1. ESTADO PRINCIPAL
    // =========================================================

    const searchQuery = ref('')

    const isSearching = ref(false)

    const searchError = ref(null)

    // =========================================================
    // 2. RESULTADOS
    // =========================================================

    const searchResults = ref([])

    const totalResults = ref(0)

    const searchTime = ref(null)

    // =========================================================
    // 3. RESPUESTA JURÍDICA
    // =========================================================

    const answer = ref('')

    const sources = ref([])
    const citations = ref([])
    const sourceWarnings = ref([])
    const resultStatus = ref('')

    const analysis = ref({})

    const context = ref('')

    const normalizedQuery = ref('')

    // =========================================================
    // 4. FALLBACK
    // =========================================================

    const isFallbackResponse = ref(false)

    const fallbackDisclaimer = ref('')

    // =========================================================
    // 5. ESTADO VISUAL DE LA BÚSQUEDA
    // =========================================================

    const searchStage = ref('')

    const searchProgress = ref(0)

    // =========================================================
    // 6. FILTROS
    // =========================================================

    const filters = reactive({

        modulo: 'Todos',

        tipoDocumento: 'Ambos',

        fecha: 'Reciente'

    })

    // =========================================================
    // 7. CONTROL DE PETICIONES
    // =========================================================

    let abortController = null

    let requestId = 0

    // =========================================================
    // 8. CONFIGURACIÓN
    // =========================================================

    // 10 minutos para mantener compatibilidad
    // con el tiempo máximo de NovaCase/NovaSearch.

    const REQUEST_TIMEOUT = 600000

    // =========================================================
    // 9. ETAPAS VISUALES
    // =========================================================

    const SEARCH_STAGES = [

        {
            text: 'Interpretando la consulta jurídica...',
            progress: 20
        },

        {
            text: 'Buscando en la base jurídica...',
            progress: 45
        },

        {
            text: 'Analizando coincidencias...',
            progress: 70
        },

        {
            text: 'Preparando los resultados...',
            progress: 90
        }

    ]

    let stageTimer = null

    // =========================================================
    // 10. INICIAR ETAPAS VISUALES
    // =========================================================

    const startSearchStages = () => {

        stopSearchStages()

        let index = 0

        const updateStage = () => {

            const stage = SEARCH_STAGES[index]

            searchStage.value = stage.text

            searchProgress.value = stage.progress

            index = (

                index + 1

            ) % SEARCH_STAGES.length

        }

        updateStage()

        stageTimer = setInterval(

            updateStage,

            1800

        )

    }

    // =========================================================
    // 11. DETENER ETAPAS VISUALES
    // =========================================================

    const stopSearchStages = () => {

        if (stageTimer) {

            clearInterval(stageTimer)

            stageTimer = null

        }

    }

    // =========================================================
    // 12. RESET DE ESTADO DE BÚSQUEDA
    // =========================================================

    const resetSearchState = () => {

        searchError.value = null

        answer.value = ''
        sources.value = []
        citations.value = []
        sourceWarnings.value = []
        resultStatus.value = ''

        analysis.value = {}

        context.value = ''

        normalizedQuery.value = ''

        searchResults.value = []

        totalResults.value = 0

        searchTime.value = null

        isFallbackResponse.value = false

        fallbackDisclaimer.value = ''

        searchStage.value = ''

        searchProgress.value = 0

    }

    // =========================================================
    // 13. FORMATEAR ERROR
    // =========================================================

    const getErrorMessage = (
        status,
        data
    ) => {

        if (status === 400) {

            return (

                data?.error?.message || (typeof data?.error === "string" ? data.error : "") ||

                'La consulta enviada no es válida.'

            )

        }

        if (status === 429) {

            return (

                'El servicio de búsqueda temporalmente no está disponible. Inténtalo nuevamente más tarde.'

            )

        }

        if (status >= 500) {

            return (

                'NovaSearch encontró un problema interno al procesar la consulta.'

            )

        }

        return (

            data?.error?.message || (typeof data?.error === "string" ? data.error : "") ||

            `Error del servidor: HTTP ${status}.`

        )

    }

    // =========================================================
    // 14. BÚSQUEDA PRINCIPAL
    // =========================================================

    const performSearch = async () => {

        const query = searchQuery.value.trim()

        // -----------------------------------------------------
        // VALIDACIÓN
        // -----------------------------------------------------

        if (!query) {

            searchError.value =

                'Escribe una consulta jurídica antes de buscar.'

            return

        }

        if (query.length < 5) {

            searchError.value =

                'La consulta es demasiado corta. Describe con mayor detalle el problema jurídico.'

            return

        }

        // -----------------------------------------------------
        // CANCELAR PETICIÓN ANTERIOR
        // -----------------------------------------------------

        if (abortController) {

            abortController.abort()

        }

        const controller = new AbortController()

        abortController = controller

        const currentRequestId = ++requestId

        // -----------------------------------------------------
        // TIMEOUT
        // -----------------------------------------------------

        const timeoutId = setTimeout(

            () => {

                controller.abort()

            },

            REQUEST_TIMEOUT

        )

        // -----------------------------------------------------
        // ESTADO
        // -----------------------------------------------------

        isSearching.value = true

        searchError.value = null

        startSearchStages()

        const startTime = performance.now()

        try {

            // =================================================
            // REQUEST
            // =================================================

            const response = await fetch(

                `${API_URL}/search`,

                {

                    method: 'POST',

                    headers: {

                        'Content-Type':
                            'application/json',

                        'Accept':
                            'application/json'

                    },

                    body: JSON.stringify({

                        query,

                        filtros: {

                            modulo:
                                filters.modulo,

                            tipoDocumento:
                                filters.tipoDocumento

                        }

                    }),

                    signal:
                        controller.signal

                }

            )

            // =================================================
            // LEER RESPUESTA
            // =================================================

            let data = {}

            try {

                data = await response.json()

            } catch {

                data = {}

            }

            // =================================================
            // VALIDAR HTTP
            // =================================================

            if (!response.ok) {

                throw new Error(

                    getErrorMessage(

                        response.status,

                        data

                    )

                )

            }

            // =================================================
            // VALIDAR RESPUESTA
            // =================================================

            if (!data.success) {

                throw new Error(

                    data.error?.message || (typeof data.error === "string" ? data.error : "") ||

                    'NovaSearch no pudo completar la búsqueda.'

                )

            }

            // =================================================
            // EVITAR RESPUESTAS OBSOLETAS
            // =================================================

            if (

                currentRequestId !== requestId

            ) {

                return

            }

            // =================================================
            // PROCESAR RESULTADOS
            // =================================================

            answer.value =

                data.answer || ''

            sources.value = Array.isArray(data.sources) ? data.sources : []
            citations.value = Array.isArray(data.citations) ? data.citations : []
            sourceWarnings.value = Array.isArray(data.warnings) ? data.warnings : []
            resultStatus.value = data.result_status || (data.documents?.length ? 'completed' : 'no_results')

            analysis.value =

                data.analysis || {}

            context.value =

                data.context || ''

            normalizedQuery.value =

                data.query_normalizada ||

                query

            searchResults.value =

                Array.isArray(
                    data.documents
                )

                    ? data.documents

                    : []

            totalResults.value =

                Number.isFinite(
                    data.total
                )

                    ? data.total

                    : searchResults.value.length

            searchTime.value = Math.round(

                performance.now() -

                startTime

            )

            // =================================================
            // FALLBACK
            // =================================================

            isFallbackResponse.value =

                Boolean(

                    data.is_fallback

                )

            if (

                isFallbackResponse.value

            ) {

                fallbackDisclaimer.value =

                    'No se encontraron coincidencias suficientes en la base jurídica. La respuesta fue generada mediante IA.'

            } else {

                fallbackDisclaimer.value = ''

            }

            // =================================================
            // COMPLETADO
            // =================================================

            searchStage.value =

                'Búsqueda completada.'

            searchProgress.value = 100

        }

        catch (error) {

            // =================================================
            // PETICIÓN CANCELADA
            // =================================================

            if (

                error?.name ===

                'AbortError'

            ) {

                // Si existe una búsqueda más reciente,
                // no mostramos ningún error.

                if (

                    currentRequestId !== requestId

                ) {

                    return

                }

                searchError.value =

                    'La búsqueda tardó demasiado y fue cancelada. Inténtalo nuevamente.'

                return

            }

            // =================================================
            // ERROR DE RED
            // =================================================

            if (

                error instanceof TypeError

            ) {

                searchError.value =

                    'No fue posible conectar con NovaSearch. Verifica que el servidor backend esté ejecutándose.'

                return

            }

            // =================================================
            // ERROR CONTROLADO
            // =================================================

            console.error(

                'NovaSearch error:',

                error

            )

            searchError.value =

                error?.message ||

                'Ocurrió un error al procesar la búsqueda.'

        }

        finally {

            clearTimeout(

                timeoutId

            )

            stopSearchStages()

            // Solo la petición vigente puede
            // modificar el estado global.

            if (

                currentRequestId === requestId

            ) {

                isSearching.value = false

                abortController = null

            }

        }

    }

    // =========================================================
    // 15. ACTUALIZAR FILTROS
    // =========================================================

    const updateFilter = (

        key,

        value

    ) => {

        if (

            Object.prototype.hasOwnProperty.call(

                filters,

                key

            )

        ) {

            filters[key] = value

        }

    }

    // =========================================================
    // 16. LIMPIAR BÚSQUEDA
    // =========================================================

    const clearSearch = () => {

        if (abortController) {

            abortController.abort()

            abortController = null

        }

        requestId++

        stopSearchStages()

        searchQuery.value = ''

        resetSearchState()

        isSearching.value = false

    }

    // =========================================================
    // 17. EXPORTAR
    // =========================================================

    return {

        // -----------------------------------------------------
        // Estado principal
        // -----------------------------------------------------

        searchQuery,

        isSearching,

        searchError,

        // -----------------------------------------------------
        // Resultados
        // -----------------------------------------------------

        searchResults,

        totalResults,

        searchTime,

        // -----------------------------------------------------
        // Respuesta jurídica
        // -----------------------------------------------------

        answer,

        sources,
        citations,
        sourceWarnings,
        resultStatus,

        analysis,

        context,

        normalizedQuery,

        // -----------------------------------------------------
        // Fallback
        // -----------------------------------------------------

        isFallbackResponse,

        fallbackDisclaimer,

        // -----------------------------------------------------
        // Progreso visual
        // -----------------------------------------------------

        searchStage,

        searchProgress,

        // -----------------------------------------------------
        // Filtros
        // -----------------------------------------------------

        filters,

        // -----------------------------------------------------
        // Funciones
        // -----------------------------------------------------

        performSearch,

        updateFilter,

        clearSearch

    }

}
