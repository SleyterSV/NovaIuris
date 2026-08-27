import { ref } from "vue"

import {
    analyzeNovaCourtCase
} from "@/services/novaCourtService"


export function useNovaCourt(){

    const caseText = ref("")

    const isAnalyzing = ref(false)

    const error = ref("")

    const progress = ref(0)

    const currentStage = ref("")

    const result = ref(null)


    async function analyzeCase(){

        if(
            !caseText.value.trim()
        ){

            error.value =
                "Ingresa la descripción del caso antes de iniciar el análisis."

            return

        }


        isAnalyzing.value = true

        error.value = ""

        result.value = null

        progress.value = 10

        currentStage.value =
            "Preparando información del caso..."


        try{

            progress.value = 25

            currentStage.value =
                "Analizando los hechos del caso..."


            const response =
                await analyzeNovaCourtCase(

                    caseText.value,

                    {
                        language: "es"
                    }

                )


            progress.value = 75

            currentStage.value =
                "Procesando el análisis judicial..."


            result.value = response


            progress.value = 100

            currentStage.value =
                "Análisis judicial completado"

        }

        catch(e){

            error.value =

                e.message ||

                "Ocurrió un error durante el análisis judicial."

            progress.value = 0

            currentStage.value = ""

        }

        finally{

            isAnalyzing.value = false

        }

    }


    function resetAnalysis(){

        caseText.value = ""

        isAnalyzing.value = false

        error.value = ""

        progress.value = 0

        currentStage.value = ""

        result.value = null

    }


    function clearError(){

        error.value = ""

    }


    return{

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