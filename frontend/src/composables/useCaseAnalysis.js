import { ref } from "vue"

import { analyzeCase } from "@/services/caseService"

export function useCaseAnalysis(){

    const loading = ref(false)

    const report = ref("")

    const result = ref(null)

    const error = ref("")

    async function analyze(caseText){

        loading.value = true

        error.value = ""

        report.value = ""

        try{

            const response = await analyzeCase(caseText)

            result.value = response

            report.value = response.report || response.answer || ""

        }

        catch(e){

            error.value =

                e.response?.data?.error ||

                e.message ||

                "Error desconocido"

        }

        finally{

            loading.value = false

        }

    }

    return{

        loading,

        report,

        result,

        error,

        analyze

    }

}