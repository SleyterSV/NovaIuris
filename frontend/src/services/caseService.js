import axios from "axios"

const api = axios.create({

    baseURL: "http://127.0.0.1:5001/api",

    timeout: 600000

})

export async function analyzeCase(caseText){

    const response = await api.post(

        "/case",

        {

            case: caseText

        }

    )

    return response.data

}