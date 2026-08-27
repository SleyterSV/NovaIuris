/* =========================================================
   NOVACOURT SERVICE
   Comunicación entre el frontend y el backend de NovaCourt.
========================================================= */


/* =========================================================
   CONFIGURACIÓN BASE
========================================================= */

const API_BASE_URL = (

    import.meta.env.VITE_API_URL ||

    "http://localhost:8000"

).replace(

    /\/$/,

    ""

)


const NOVACOURT_ENDPOINT =

    `${API_BASE_URL}/api/novacourt`


/* =========================================================
   ERROR PERSONALIZADO
========================================================= */

class NovaCourtServiceError extends Error {

    constructor(

        message,

        status = null,

        data = null

    ) {

        super(message)

        this.name = "NovaCourtServiceError"

        this.status = status

        this.data = data

    }

}


/* =========================================================
   HELPER:
   CONSTRUIR ERROR DESDE RESPUESTA DEL BACKEND
========================================================= */

function getErrorMessage(

    data,

    fallback = "No fue posible procesar la solicitud."

) {

    if (

        !data

    ) {

        return fallback

    }


    if (

        typeof data === "string"

    ) {

        return data

    }


    if (

        typeof data.detail === "string"

    ) {

        return data.detail

    }


    if (

        typeof data.message === "string"

    ) {

        return data.message

    }


    if (

        typeof data.error === "string"

    ) {

        return data.error

    }


    return fallback

}


/* =========================================================
   HELPER:
   PROCESAR RESPUESTA HTTP
========================================================= */

async function parseResponse(

    response

) {

    let data = null


    const contentType =

        response.headers.get(

            "content-type"

        ) || ""


    try {

        if (

            contentType.includes(

                "application/json"

            )

        ) {

            data = await response.json()

        }

        else {

            data = await response.text()

        }

    }

    catch {

        data = null

    }


    if (

        !response.ok

    ) {

        throw new NovaCourtServiceError(

            getErrorMessage(

                data,

                `Error del servidor (${response.status}).`

            ),

            response.status,

            data

        )

    }


    return data

}


/* =========================================================
   ANALIZAR CASO
========================================================= */

export async function analyzeNovaCourtCase(

    caseText,

    options = {}

) {

    if (

        typeof caseText !== "string" ||

        !caseText.trim()

    ) {

        throw new NovaCourtServiceError(

            "Debes ingresar una descripción válida del caso."

        )

    }


    const {

        signal = null,

        language = "es"

    } = options


    try {

        const response = await fetch(

            `${NOVACOURT_ENDPOINT}/analyze`,

            {

                method: "POST",

                headers: {

                    "Content-Type":

                        "application/json",

                    "Accept":

                        "application/json"

                },

                body: JSON.stringify(

                    {

                        case_text:

                            caseText.trim(),

                        language

                    }

                ),

                signal

            }

        )


        return await parseResponse(

            response

        )

    }

    catch (

        error

    ) {

        if (

            error.name === "AbortError"

        ) {

            throw new NovaCourtServiceError(

                "El análisis fue cancelado."

            )

        }


        if (

            error instanceof NovaCourtServiceError

        ) {

            throw error

        }


        throw new NovaCourtServiceError(

            error.message ||

            "No fue posible conectar con el servidor de NovaCourt."

        )

    }

}


/* =========================================================
   OBTENER RESULTADO POR ID
========================================================= */

export async function getNovaCourtResult(

    analysisId,

    options = {}

) {

    if (

        !analysisId

    ) {

        throw new NovaCourtServiceError(

            "No se proporcionó un identificador de análisis."

        )

    }


    const {

        signal = null

    } = options


    try {

        const response = await fetch(

            `${NOVACOURT_ENDPOINT}/results/${encodeURIComponent(analysisId)}`,

            {

                method: "GET",

                headers: {

                    "Accept":

                        "application/json"

                },

                signal

            }

        )


        return await parseResponse(

            response

        )

    }

    catch (

        error

    ) {

        if (

            error.name === "AbortError"

        ) {

            throw new NovaCourtServiceError(

                "La consulta fue cancelada."

            )

        }


        if (

            error instanceof NovaCourtServiceError

        ) {

            throw error

        }


        throw new NovaCourtServiceError(

            error.message ||

            "No fue posible obtener el resultado del análisis."

        )

    }

}


/* =========================================================
   EXPORTACIÓN DEL SERVICIO
========================================================= */

const novaCourtService = {

    analyzeCase:

        analyzeNovaCourtCase,

    getResult:

        getNovaCourtResult

}


export {

    NovaCourtServiceError

}


export default novaCourtService
