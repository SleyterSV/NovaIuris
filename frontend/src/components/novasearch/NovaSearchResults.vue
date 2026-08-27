<template>
    <section
        v-if="results?.length"
        class="nova-search-results"
    >

        <!-- =========================================
             HEADER DE RESULTADOS
        ========================================== -->

        <header class="results-header">

            <div class="results-heading">

                <span class="results-eyebrow">
                    RESULTADOS RECUPERADOS
                </span>

                <h2>
                    Fuentes jurídicas relevantes
                </h2>

                <p>
                    Se encontraron
                    <strong>{{ results.length }}</strong>
                    {{ results.length === 1
                        ? 'resultado relevante para tu consulta.'
                        : 'resultados relevantes para tu consulta.'
                    }}
                </p>

            </div>


            <div
                v-if="totalResults !== null"
                class="results-total"
            >

                <span class="results-total-label">
                    TOTAL
                </span>

                <strong>
                    {{ totalResults }}
                </strong>

            </div>

        </header>


        <!-- =========================================
             LISTA DE RESULTADOS
        ========================================== -->

        <TransitionGroup
            name="nova-result"
            tag="div"
            class="results-list"
        >

            <article
                v-for="(result, index) in results"
                :key="result.id || index"
                class="nova-result-card"
            >

                <!-- =====================================
                     CABECERA
                ====================================== -->

                <header class="result-card-header">

                    <div class="result-main-heading">

                        <div class="result-position">

                            {{ formatPosition(index) }}

                        </div>


                        <div class="result-title-wrapper">

                            <span
                                v-if="result.tipo_documento"
                                class="document-type"
                            >
                                {{ result.tipo_documento }}
                            </span>


                            <h3 class="result-title">

                                {{ result.titulo || 'Documento jurídico' }}

                            </h3>


                            <div
                                v-if="
                                    result.rama ||
                                    result.organo_emisor
                                "
                                class="result-meta"
                            >

                                <span
                                    v-if="result.rama"
                                >
                                    {{ result.rama }}
                                </span>


                                <span
                                    v-if="
                                        result.rama &&
                                        result.organo_emisor
                                    "
                                    class="meta-separator"
                                >
                                    ·
                                </span>


                                <span
                                    v-if="result.organo_emisor"
                                >
                                    {{ result.organo_emisor }}
                                </span>

                            </div>

                        </div>

                    </div>


                    <!-- SCORE -->

                    <div
                        v-if="hasScore(result)"
                        class="relevance-score"
                    >

                        <span class="score-label">
                            RELEVANCIA
                        </span>

                        <strong>
                            {{ formatScore(result.score) }}
                        </strong>

                    </div>

                </header>


                <!-- =====================================
                     INFORMACIÓN DEL DOCUMENTO
                ====================================== -->

                <div
                    v-if="
                        result.expediente ||
                        result.numero ||
                        result.fecha_resolucion
                    "
                    class="result-information"
                >

                    <div
                        v-if="result.expediente"
                        class="result-info-item"
                    >

                        <span class="info-label">
                            Expediente
                        </span>

                        <strong>
                            {{ result.expediente }}
                        </strong>

                    </div>


                    <div
                        v-if="result.numero"
                        class="result-info-item"
                    >

                        <span class="info-label">
                            Número
                        </span>

                        <strong>
                            {{ result.numero }}
                        </strong>

                    </div>


                    <div
                        v-if="result.fecha_resolucion"
                        class="result-info-item"
                    >

                        <span class="info-label">
                            Fecha
                        </span>

                        <strong>
                            {{ formatDate(result.fecha_resolucion) }}
                        </strong>

                    </div>

                </div>


                <!-- =====================================
                     CLASIFICACIÓN
                ====================================== -->

                <div
                    v-if="
                        result.materia ||
                        result.precedente_vinculante
                    "
                    class="result-classification"
                >

                    <span
                        v-if="result.materia"
                        class="result-chip"
                    >

                        <span class="chip-label">
                            Materia
                        </span>

                        {{ result.materia }}

                    </span>


                    <span
                        v-if="isBindingPrecedent(
                            result.precedente_vinculante
                        )"
                        class="precedent-chip"
                    >

                        <span class="precedent-star">
                            ★
                        </span>

                        Precedente vinculante

                    </span>

                </div>


                <!-- =====================================
                     RESUMEN
                ====================================== -->

                <div
                    v-if="result.resumen_ia"
                    class="result-summary-section"
                >

                    <span class="summary-label">
                        SÍNTESIS JURÍDICA
                    </span>

                    <p class="result-summary">
                        {{ result.resumen_ia }}
                    </p>

                </div>


                <!-- =====================================
                     EXTRACTO
                ====================================== -->

                <details
                    v-if="result.extracto_exacto"
                    class="result-details"
                >

                    <summary>

                        <span>
                            Ver fundamento o extracto relevante
                        </span>

                        <span class="details-icon">
                            +
                        </span>

                    </summary>


                    <div class="extract-wrapper">

                        <div class="extract-line"></div>

                        <div class="extract-content">
                            {{ result.extracto_exacto }}
                        </div>

                    </div>

                </details>


                <!-- =====================================
                     FOOTER
                ====================================== -->

                <footer class="result-card-footer">

                    <span>
                        Resultado {{ index + 1 }}
                    </span>


                    <span
                        v-if="result.tipo_documento"
                    >
                        {{ result.tipo_documento }}
                    </span>

                </footer>

            </article>

        </TransitionGroup>

    </section>
</template>


<script setup>

/* =========================================
   PROPS
========================================= */

const props = defineProps({

    results: {

        type: Array,

        default: () => []

    },

    totalResults: {

        type: Number,

        default: null

    }

})


/* =========================================
   UTILIDADES
========================================= */

function formatPosition(index){

    return String(index + 1).padStart(2, "0")

}


function hasScore(result){

    return (

        result.score !== null &&

        result.score !== undefined &&

        !Number.isNaN(
            Number(result.score)
        )

    )

}


function formatScore(score){

    const numericScore = Number(score)

    /*
       El backend actual trabaja normalmente
       con valores entre 0 y 1.

       Si en el futuro devuelve valores de 0 a 100,
       el componente también podrá mostrarlos.
    */

    const percentage =

        numericScore <= 1

            ? numericScore * 100

            : numericScore


    return `${Math.round(percentage)}%`

}


function isBindingPrecedent(value){

    if(

        value === true ||

        value === 1 ||

        value === "1"

    ){

        return true

    }


    if(

        typeof value === "string"

    ){

        return [

            "true",

            "si",

            "sí",

            "yes"

        ].includes(

            value.toLowerCase().trim()

        )

    }


    return false

}


function formatDate(dateValue){

    if(!dateValue){

        return ""

    }


    /*
       Si el backend ya entrega la fecha
       como texto legible, evitamos modificarla.
    */

    const date = new Date(dateValue)


    if(

        Number.isNaN(
            date.getTime()
        )

    ){

        return dateValue

    }


    return new Intl.DateTimeFormat(

        "es-PE",

        {

            day:"2-digit",

            month:"long",

            year:"numeric"

        }

    ).format(date)

}

</script>


<style scoped>

/* =========================================
   NOVA SEARCH — RESULTS
========================================= */

.nova-search-results{

    width:100%;

}


/* =========================================
   HEADER
========================================= */

.results-header{

    display:flex;

    align-items:flex-end;

    justify-content:space-between;

    gap:24px;

    padding:

        0
        4px
        20px;

    margin-bottom:20px;

    border-bottom:

        1px solid
        #DCE5EE;

}


.results-heading{

    min-width:0;

}


.results-eyebrow{

    display:block;

    margin-bottom:7px;

    color:#7A6440;

    font-size:.68rem;

    font-weight:800;

    letter-spacing:1.45px;

}


.results-heading h2{

    margin:0 0 7px;

    color:#17375E;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1.55rem;

    font-weight:600;

    line-height:1.3;

}


.results-heading p{

    margin:0;

    color:#6A7888;

    font-size:.88rem;

    line-height:1.6;

}


.results-heading p strong{

    color:#315C97;

    font-weight:800;

}


/* =========================================
   TOTAL
========================================= */

.results-total{

    min-width:70px;

    padding:10px 13px;

    display:flex;

    flex-direction:column;

    align-items:center;

    justify-content:center;

    background:#FFFFFF;

    border:

        1px solid
        #D6DFEA;

    border-radius:9px;

}


.results-total-label{

    color:#8A96A4;

    font-size:.58rem;

    font-weight:800;

    letter-spacing:1px;

}


.results-total strong{

    margin-top:2px;

    color:#17375E;

    font-size:1.05rem;

    font-weight:800;

}


/* =========================================
   LISTA
========================================= */

.results-list{

    display:flex;

    flex-direction:column;

    gap:16px;

}


/* =========================================
   TARJETA
========================================= */

.nova-result-card{

    position:relative;

    overflow:hidden;

    padding:25px 26px 0;

    background:#FFFFFF;

    border:

        1px solid
        #D9E2EC;

    border-radius:12px;

    box-shadow:

        0 8px 24px
        rgba(
            23,
            55,
            94,
            .045
        );

    transition:

        transform
        .22s
        ease,

        box-shadow
        .22s
        ease,

        border-color
        .22s
        ease;

}


.nova-result-card:hover{

    transform:

        translateY(
            -2px
        );

    border-color:#BECBDC;

    box-shadow:

        0 14px 30px
        rgba(
            23,
            55,
            94,
            .075
        );

}


/* =========================================
   CABECERA CARD
========================================= */

.result-card-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:24px;

}


.result-main-heading{

    display:flex;

    align-items:flex-start;

    gap:15px;

    min-width:0;

}


.result-position{

    width:34px;

    height:34px;

    flex:

        0 0
        34px;

    display:flex;

    align-items:center;

    justify-content:center;

    margin-top:2px;

    border-radius:50%;

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .45
        );

    color:#7A6440;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:.78rem;

    font-weight:600;

}


.result-title-wrapper{

    min-width:0;

}


.document-type{

    display:inline-block;

    margin-bottom:7px;

    color:#315C97;

    font-size:.68rem;

    font-weight:800;

    text-transform:uppercase;

    letter-spacing:.9px;

}


.result-title{

    margin:0;

    color:#17375E;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1.16rem;

    font-weight:600;

    line-height:1.5;

}


.result-meta{

    display:flex;

    flex-wrap:wrap;

    align-items:center;

    gap:6px;

    margin-top:8px;

    color:#748294;

    font-size:.78rem;

    line-height:1.5;

}


.meta-separator{

    color:#B08A4C;

}


/* =========================================
   SCORE
========================================= */

.relevance-score{

    min-width:78px;

    padding:9px 11px;

    display:flex;

    flex-direction:column;

    align-items:flex-end;

    flex-shrink:0;

    border-left:

        2px solid
        #B08A4C;

    background:

        linear-gradient(
            90deg,
            rgba(
                176,
                138,
                76,
                .03
            ),
            rgba(
                176,
                138,
                76,
                .08
            )
        );

}


.score-label{

    color:#8A96A4;

    font-size:.56rem;

    font-weight:800;

    letter-spacing:.9px;

}


.relevance-score strong{

    margin-top:3px;

    color:#17375E;

    font-size:1rem;

    font-weight:800;

}


/* =========================================
   INFORMACIÓN
========================================= */

.result-information{

    display:flex;

    flex-wrap:wrap;

    gap:24px;

    margin-top:20px;

    padding:

        15px
        0;

    border-top:

        1px solid
        #EDF1F5;

    border-bottom:

        1px solid
        #EDF1F5;

}


.result-info-item{

    display:flex;

    flex-direction:column;

    gap:3px;

}


.info-label{

    color:#8B97A5;

    font-size:.62rem;

    font-weight:800;

    text-transform:uppercase;

    letter-spacing:.85px;

}


.result-info-item strong{

    color:#30465F;

    font-size:.82rem;

    font-weight:650;

}


/* =========================================
   CLASIFICACIÓN
========================================= */

.result-classification{

    display:flex;

    flex-wrap:wrap;

    gap:9px;

    margin-top:18px;

}


.result-chip{

    display:inline-flex;

    align-items:center;

    gap:7px;

    min-height:30px;

    padding:

        5px
        11px;

    background:#F5F8FB;

    border:

        1px solid
        #DDE6EF;

    border-radius:999px;

    color:#315C97;

    font-size:.74rem;

    font-weight:650;

}


.chip-label{

    color:#7C8997;

    font-size:.65rem;

    font-weight:700;

}


.precedent-chip{

    display:inline-flex;

    align-items:center;

    gap:7px;

    min-height:30px;

    padding:

        5px
        11px;

    border-radius:999px;

    background:

        rgba(
            176,
            138,
            76,
            .09
        );

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .30
        );

    color:#7A6440;

    font-size:.74rem;

    font-weight:700;

}


.precedent-star{

    color:#B08A4C;

    font-size:.78rem;

}


/* =========================================
   SÍNTESIS
========================================= */

.result-summary-section{

    margin-top:20px;

}


.summary-label{

    display:block;

    margin-bottom:8px;

    color:#7A6440;

    font-size:.64rem;

    font-weight:800;

    letter-spacing:1px;

}


.result-summary{

    margin:0;

    color:#4F5F70;

    font-size:.9rem;

    line-height:1.8;

}


/* =========================================
   DETALLES / EXTRACTO
========================================= */

.result-details{

    margin-top:20px;

    padding-top:17px;

    border-top:

        1px solid
        #E8EDF2;

}


.result-details summary{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:16px;

    color:#315C97;

    font-size:.82rem;

    font-weight:700;

    cursor:pointer;

    list-style:none;

}


.result-details summary::-webkit-details-marker{

    display:none;

}


.details-icon{

    width:25px;

    height:25px;

    display:flex;

    align-items:center;

    justify-content:center;

    flex-shrink:0;

    border-radius:50%;

    border:

        1px solid
        #D7E0EA;

    color:#315C97;

    font-size:1rem;

    transition:

        transform
        .2s
        ease;

}


.result-details[open]
.details-icon{

    transform:

        rotate(
            45deg
        );

}


.extract-wrapper{

    display:flex;

    gap:14px;

    margin-top:17px;

    padding:

        18px
        0
        3px;

}


.extract-line{

    width:2px;

    flex-shrink:0;

    background:

        linear-gradient(
            to bottom,
            #B08A4C,
            rgba(
                176,
                138,
                76,
                .20
            )
        );

    border-radius:999px;

}


.extract-content{

    color:#526273;

    font-size:.88rem;

    line-height:1.85;

    white-space:pre-wrap;

}


/* =========================================
   FOOTER
========================================= */

.result-card-footer{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:16px;

    margin-top:22px;

    margin-left:-26px;

    margin-right:-26px;

    padding:

        12px
        26px;

    background:#FAFBFC;

    border-top:

        1px solid
        #E9EEF3;

    color:#94A0AD;

    font-size:.68rem;

}


/* =========================================
   TRANSICIONES
========================================= */

.nova-result-enter-active{

    transition:

        opacity
        .35s
        ease,

        transform
        .35s
        ease;

}


.nova-result-enter-from{

    opacity:0;

    transform:

        translateY(
            12px
        );

}


.nova-result-leave-active{

    position:absolute;

    transition:

        opacity
        .2s
        ease;

}


.nova-result-leave-to{

    opacity:0;

}


/* =========================================
   RESPONSIVE
========================================= */

@media(max-width:760px){

    .results-header{

        align-items:flex-start;

        flex-direction:column;

    }


    .results-total{

        align-items:flex-start;

    }


    .result-card-header{

        flex-direction:column;

        gap:16px;

    }


    .relevance-score{

        align-items:flex-start;

        width:100%;

        border-left:

            2px solid
            #B08A4C;

    }


    .result-information{

        gap:16px;

    }

}


@media(max-width:576px){

    .results-heading h2{

        font-size:1.3rem;

    }


    .nova-result-card{

        padding:

            20px
            18px
            0;

    }


    .result-main-heading{

        gap:11px;

    }


    .result-position{

        width:30px;

        height:30px;

        flex-basis:30px;

        font-size:.72rem;

    }


    .result-title{

        font-size:1.02rem;

    }


    .result-information{

        flex-direction:column;

        gap:13px;

    }


    .result-card-footer{

        margin-left:-18px;

        margin-right:-18px;

        padding:

            12px
            18px;

    }


    .result-card-footer span:last-child{

        display:none;

    }

}

</style>