import { ref } from "vue"

import {
    analyzeNovaCourtCase
} from "@/services/novaCourtService"


export function useNovaCourt(){

    /* =========================================================
       ESTADO
    ========================================================= */

    const caseText = ref("")

    const isAnalyzing = ref(false)

    const error = ref("")

    const progress = ref(0)

    const currentStage = ref("")

    const result = ref(null)


    /* =========================================================
       ANALIZAR CASO
    ========================================================= */

    async function analyzeCase(text = caseText.value){

        /*
            Recibimos el texto directamente desde NovaCourtView.
            Esto evita que existan dos fuentes diferentes para
            la descripción del caso.
        */

        const normalizedText = String(
            text ?? ""
        ).trim()


        /* =====================================================
           VALIDACIÓN
        ===================================================== */

        if(!normalizedText){

            error.value =
                "Ingresa la descripción del caso antes de iniciar el análisis."

            return null

        }


        /*
            Guardamos el texto utilizado para el análisis.
        */

        caseText.value =
            normalizedText


        /* =====================================================
           INICIO DEL PROCESAMIENTO
        ===================================================== */

        isAnalyzing.value = true

        error.value = ""

        result.value = null

        progress.value = 10

        currentStage.value =
            "Preparando información del caso..."


        try{

            /* =================================================
               ETAPA 1
            ================================================= */

            progress.value = 25

            currentStage.value =
                "Analizando los hechos del caso..."


            /* =================================================
               LLAMADA AL BACKEND
            ================================================= */

            const response =
                await analyzeNovaCourtCase(

                    normalizedText,

                    {
                        language: "es"
                    }

                )


            /* =================================================
               ETAPA 2
            ================================================= */

            progress.value = 75

            currentStage.value =
                "Procesando el análisis judicial..."


            /*
                Guardamos la respuesta completa.
            */

            result.value =
                response


            /* =================================================
               FINALIZACIÓN
            ================================================= */

            progress.value = 100

            currentStage.value =
                "Análisis judicial completado"


            return response

        }


        catch(e){

            console.error(
                "[NovaCourt] Error durante el análisis:",
                e
            )


            error.value =

                e?.message ||

                "Ocurrió un error durante el análisis judicial."


            progress.value = 0

            currentStage.value = ""


            return null

        }


        finally{

            isAnalyzing.value = false

        }

    }


    /* =========================================================
       REINICIAR
    ========================================================= */

    function resetAnalysis(){

        caseText.value = ""

        isAnalyzing.value = false

        error.value = ""

        progress.value = 0

        currentStage.value = ""

        result.value = null

    }


    /* =========================================================
       LIMPIAR ERROR
    ========================================================= */

    function clearError(){

        error.value = ""

    }


    /* =========================================================
       API PÚBLICA DEL COMPOSABLE
    ========================================================= */

    return {

        caseText,

        isAnalyzing,

        error,

        progress,

        currentStage,

        result,

        analyzeCase,

        resetAnalysis,

        clearError

    }

}