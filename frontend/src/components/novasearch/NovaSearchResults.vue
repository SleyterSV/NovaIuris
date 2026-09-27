<template>

    <section
        v-if="results?.length"
        class="nova-search-results"
    >

        <!-- =====================================================
             CABECERA DE RESULTADOS
        ====================================================== -->

        <header class="results-header">

            <div class="results-heading">

                <div class="results-heading-accent"></div>

                <div>

                    <span class="results-eyebrow">
                        NOVA SEARCH · RECUPERACIÓN JURÍDICA
                    </span>

                    <h2>
                        Fuentes jurídicas relevantes
                    </h2>

                    <p>
                        Se encontraron
                        <strong>{{ results.length }}</strong>
                        {{
                            results.length === 1
                                ? 'resultado relevante'
                                : 'resultados relevantes'
                        }}
                        para tu consulta.
                    </p>

                </div>

            </div>


            <!-- TOTAL -->

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


        <!-- =====================================================
             LISTA DE RESULTADOS
        ====================================================== -->

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

                <!-- =================================================
                     INDICADOR SUPERIOR
                ================================================== -->

                <div class="result-top-line"></div>


                <!-- =================================================
                     CABECERA DEL RESULTADO
                ================================================== -->

                <header class="result-card-header">

                    <div class="result-main-heading">

                        <!-- POSICIÓN -->

                        <div
                            class="result-position"
                            :aria-label="`Resultado ${index + 1}`"
                        >

                            {{ formatPosition(index) }}

                        </div>


                        <!-- TÍTULO -->

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
                                    class="result-meta-item"
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
                                    /
                                </span>


                                <span
                                    v-if="result.organo_emisor"
                                    class="result-meta-item"
                                >
                                    {{ result.organo_emisor }}
                                </span>

                            </div>

                        </div>

                    </div>


                </header>


                <!-- =================================================
                     INFORMACIÓN DEL DOCUMENTO
                ================================================== -->

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


                <!-- =================================================
                     CLASIFICACIÓN
                ================================================== -->

                <div
                    v-if="
                        result.materia ||
                        result.precedente_vinculante
                    "
                    class="result-classification"
                >

                    <!-- MATERIA -->

                    <span
                        v-if="result.materia"
                        class="result-chip"
                    >

                        <span class="chip-label">
                            Materia
                        </span>

                        <span class="chip-value">
                            {{ result.materia }}
                        </span>

                    </span>


                    <!-- PRECEDENTE -->

                    <span
                        v-if="
                            isBindingPrecedent(
                                result.precedente_vinculante
                            )
                        "
                        class="precedent-chip"
                    >

                        <span class="precedent-mark">
                            ★
                        </span>

                        <span>
                            Precedente vinculante
                        </span>

                    </span>

                </div>


                <!-- =================================================
                     SÍNTESIS JURÍDICA
                ================================================== -->

                <section
                    v-if="result.resumen_ia"
                    class="result-summary-section"
                >

                    <div class="section-heading">

                        <span class="section-heading-mark"></span>

                        <span class="summary-label">
                            SÍNTESIS JURÍDICA
                        </span>

                    </div>


                    <p class="result-summary">
                        {{ result.resumen_ia }}
                    </p>

                </section>


                <!-- =================================================
                     EXTRACTO
                ================================================== -->

                <details
                    v-if="result.extracto_exacto"
                    class="result-details"
                >

                    <summary>

                        <span class="details-label">

                            <span class="details-label-icon">

                                <svg
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="1.7"
                                    aria-hidden="true"
                                >

                                    <path
                                        d="M5 4.5h14v15H5z"
                                    />

                                    <path
                                        d="M8 8h8"
                                    />

                                    <path
                                        d="M8 12h8"
                                    />

                                    <path
                                        d="M8 16h5"
                                    />

                                </svg>

                            </span>

                            <span>
                                Ver fundamento o extracto relevante
                            </span>

                        </span>


                        <span
                            class="details-icon"
                            aria-hidden="true"
                        >
                            +
                        </span>

                    </summary>


                    <div class="extract-wrapper">

                        <div class="extract-accent"></div>

                        <div class="extract-content">

                            {{ result.extracto_exacto }}

                        </div>

                    </div>

                </details>


                <!-- =================================================
                     FOOTER
                ================================================== -->

                <footer class="result-card-footer">

                    <span class="footer-result">

                        <span class="footer-result-dot"></span>

                        Resultado {{ index + 1 }}

                    </span>


                    <span
                        v-if="result.tipo_documento"
                        class="footer-document-type"
                    >
                        {{ result.tipo_documento }}
                    </span>

                </footer>

            </article>

        </TransitionGroup>

    </section>

</template>


<script setup>

/* =========================================================
   PROPS
========================================================= */

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


/* =========================================================
   UTILIDADES
========================================================= */

function formatPosition(index){

    return String(index + 1).padStart(2, "0")

}


/* =========================================================
   SCORE
========================================================= */

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

            value
                .toLowerCase()
                .trim()

        )

    }


    return false

}


/* =========================================================
   FECHA
========================================================= */

function formatDate(dateValue){

    if(!dateValue){

        return ""

    }


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

            day: "2-digit",

            month: "long",

            year: "numeric"

        }

    ).format(date)

}

</script>


<style scoped>

/* =========================================================
   NOVA SEARCH — RESULTS
   Sistema visual institucional Nova Iuris
========================================================= */

.nova-search-results{

    width:100%;

}


/* =========================================================
   HEADER
========================================================= */

.results-header{

    display:flex;

    align-items:flex-end;

    justify-content:space-between;

    gap:28px;

    padding:
        0
        4px
        22px;

    margin-bottom:22px;

    border-bottom:
        1px solid
        #DCE4ED;

}


/* =========================================================
   HEADING
========================================================= */

.results-heading{

    display:flex;

    align-items:flex-start;

    gap:13px;

    min-width:0;

}


.results-heading-accent{

    width:3px;

    min-height:55px;

    margin-top:3px;

    flex-shrink:0;

    border-radius:999px;

    background:
        linear-gradient(
            to bottom,
            #B08A4C,
            rgba(
                176,
                138,
                76,
                .25
            )
        );

}


.results-eyebrow{

    display:block;

    margin-bottom:7px;

    color:#7A6440;

    font-size:.65rem;

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

    font-size:1.5rem;

    font-weight:600;

    line-height:1.3;

}


.results-heading p{

    margin:0;

    color:#687789;

    font-size:.86rem;

    line-height:1.6;

}


.results-heading p strong{

    color:#315C97;

    font-weight:800;

}


/* =========================================================
   TOTAL
========================================================= */

.results-total{

    min-width:72px;

    padding:
        9px
        14px;

    display:flex;

    flex-direction:column;

    align-items:center;

    justify-content:center;

    flex-shrink:0;

    background:#FFFFFF;

    border:
        1px solid
        #D5DFE9;

    border-radius:9px;

    box-shadow:
        0
        4px
        12px
        rgba(
            23,
            55,
            94,
            .035
        );

}


.results-total-label{

    color:#8B97A5;

    font-size:.55rem;

    font-weight:800;

    letter-spacing:1.1px;

}


.results-total strong{

    margin-top:2px;

    color:#17375E;

    font-size:1.05rem;

    font-weight:800;

}


/* =========================================================
   LISTA
========================================================= */

.results-list{

    display:flex;

    flex-direction:column;

    gap:15px;

}


/* =========================================================
   TARJETA
========================================================= */

.nova-result-card{

    position:relative;

    overflow:hidden;

    padding:
        25px
        26px
        0;

    background:#FFFFFF;

    border:
        1px solid
        #D9E2EC;

    border-radius:11px;

    box-shadow:
        0
        7px
        22px
        rgba(
            23,
            55,
            94,
            .042
        );

    transition:
        transform
        .22s
        ease,

        border-color
        .22s
        ease,

        box-shadow
        .22s
        ease;

}


.nova-result-card:hover{

    transform:
        translateY(
            -2px
        );

    border-color:#BDCAD8;

    box-shadow:
        0
        13px
        30px
        rgba(
            23,
            55,
            94,
            .07
        );

}


/* =========================================================
   LÍNEA SUPERIOR
========================================================= */

.result-top-line{

    position:absolute;

    top:0;

    left:0;

    width:100%;

    height:2px;

    background:
        linear-gradient(
            90deg,
            #17375E 0%,
            #315C97 65%,
            rgba(
                176,
                138,
                76,
                .55
            ) 100%
        );

    opacity:.85;

}


/* =========================================================
   CABECERA
========================================================= */

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

    width:35px;

    height:35px;

    flex:
        0 0
        35px;

    display:flex;

    align-items:center;

    justify-content:center;

    margin-top:1px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .40
        );

    border-radius:50%;

    background:
        linear-gradient(
            135deg,
            #FFFFFF,
            #FAF8F4
        );

    color:#80683F;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:.76rem;

    font-weight:600;

}


.result-title-wrapper{

    min-width:0;

}


.document-type{

    display:block;

    margin-bottom:6px;

    color:#315C97;

    font-size:.63rem;

    font-weight:800;

    letter-spacing:.95px;

    line-height:1.4;

    text-transform:uppercase;

}


.result-title{

    margin:0;

    color:#17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:1.13rem;

    font-weight:600;

    line-height:1.5;

    word-break:break-word;

}


.result-meta{

    display:flex;

    flex-wrap:wrap;

    align-items:center;

    gap:7px;

    margin-top:8px;

    color:#718093;

    font-size:.76rem;

    line-height:1.5;

}


.result-meta-item{

    font-weight:500;

}


.meta-separator{

    color:#B08A4C;

    font-weight:700;

}


/* =========================================================
   SCORE
========================================================= */

.relevance-score{

    min-width:76px;

    padding:
        8px
        11px;

    display:flex;

    flex-direction:column;

    align-items:flex-end;

    flex-shrink:0;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .30
        );

    border-radius:8px;

    background:
        linear-gradient(
            135deg,
            #FFFCF8,
            #FFF9F0
        );

}


.score-label{

    color:#94764A;

    font-size:.53rem;

    font-weight:800;

    letter-spacing:.85px;

}


.relevance-score strong{

    margin-top:2px;

    color:#17375E;

    font-size:.98rem;

    font-weight:800;

    line-height:1.2;

}


/* =========================================================
   INFORMACIÓN DEL DOCUMENTO
========================================================= */

.result-information{

    display:grid;

    grid-template-columns:
        repeat(
            3,
            minmax(
                0,
                1fr
            )
        );

    gap:0;

    margin-top:20px;

    padding:
        14px
        0;

    border-top:
        1px solid
        #EDF1F5;

    border-bottom:
        1px solid
        #EDF1F5;

}


.result-info-item{

    min-width:0;

    display:flex;

    flex-direction:column;

    gap:4px;

    padding:
        0
        18px;

    border-right:
        1px solid
        #E8EDF2;

}


.result-info-item:first-child{

    padding-left:0;

}


.result-info-item:last-child{

    padding-right:0;

    border-right:none;

}


.info-label{

    color:#8B97A5;

    font-size:.58rem;

    font-weight:800;

    letter-spacing:.85px;

    text-transform:uppercase;

}


.result-info-item strong{

    overflow:hidden;

    color:#30465F;

    font-size:.79rem;

    font-weight:650;

    line-height:1.45;

    text-overflow:ellipsis;

    word-break:break-word;

}


/* =========================================================
   CLASIFICACIÓN
========================================================= */

.result-classification{

    display:flex;

    flex-wrap:wrap;

    align-items:center;

    gap:8px;

    margin-top:17px;

}


.result-chip{

    display:inline-flex;

    align-items:center;

    gap:7px;

    min-height:29px;

    max-width:100%;

    padding:
        5px
        10px;

    border:
        1px solid
        #DCE5EE;

    border-radius:999px;

    background:#F6F8FB;

    color:#315C97;

    font-size:.71rem;

    font-weight:650;

}


.chip-label{

    color:#7D8997;

    font-size:.61rem;

    font-weight:800;

    letter-spacing:.25px;

}


.chip-value{

    overflow:hidden;

    text-overflow:ellipsis;

}


.precedent-chip{

    display:inline-flex;

    align-items:center;

    gap:7px;

    min-height:29px;

    padding:
        5px
        10px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .28
        );

    border-radius:999px;

    background:
        rgba(
            176,
            138,
            76,
            .075
        );

    color:#78613C;

    font-size:.71rem;

    font-weight:700;

}


.precedent-mark{

    color:#B08A4C;

    font-size:.7rem;

}


/* =========================================================
   SÍNTESIS
========================================================= */

.result-summary-section{

    margin-top:20px;

}


.section-heading{

    display:flex;

    align-items:center;

    gap:8px;

    margin-bottom:8px;

}


.section-heading-mark{

    width:15px;

    height:2px;

    border-radius:999px;

    background:#B08A4C;

}


.summary-label{

    color:#7A6440;

    font-size:.61rem;

    font-weight:800;

    letter-spacing:1.05px;

}


.result-summary{

    margin:0;

    color:#4C5D6E;

    font-size:.88rem;

    line-height:1.82;

}


/* =========================================================
   DETALLES / EXTRACTO
========================================================= */

.result-details{

    margin-top:20px;

    padding-top:16px;

    border-top:
        1px solid
        #E8EDF2;

}


.result-details summary{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:16px;

    cursor:pointer;

    list-style:none;

    color:#315C97;

    font-size:.78rem;

    font-weight:700;

    user-select:none;

}


.result-details summary::-webkit-details-marker{

    display:none;

}


.details-label{

    display:inline-flex;

    align-items:center;

    gap:8px;

}


.details-label-icon{

    width:27px;

    height:27px;

    display:flex;

    align-items:center;

    justify-content:center;

    flex-shrink:0;

    border:
        1px solid
        #D8E1EB;

    border-radius:7px;

    background:#F8FAFC;

    color:#315C97;

}


.details-label-icon svg{

    width:14px;

    height:14px;

}


.details-icon{

    width:26px;

    height:26px;

    display:flex;

    align-items:center;

    justify-content:center;

    flex-shrink:0;

    border:
        1px solid
        #D5DFE9;

    border-radius:50%;

    color:#315C97;

    font-size:.95rem;

    font-weight:500;

    transition:
        transform
        .2s
        ease,

        background
        .2s
        ease;

}


.result-details summary:hover
.details-icon{

    background:#F5F8FB;

}


.result-details[open]
.details-icon{

    transform:
        rotate(
            45deg
        );

}


/* =========================================================
   EXTRACTO
========================================================= */

.extract-wrapper{

    display:flex;

    gap:13px;

    margin-top:15px;

    padding:
        16px
        0
        4px;

}


.extract-accent{

    width:2px;

    flex-shrink:0;

    border-radius:999px;

    background:
        linear-gradient(
            to bottom,
            #B08A4C,
            rgba(
                176,
                138,
                76,
                .18
            )
        );

}


.extract-content{

    min-width:0;

    color:#526273;

    font-size:.85rem;

    line-height:1.85;

    white-space:pre-wrap;

    word-break:break-word;

}


/* =========================================================
   FOOTER
========================================================= */

.result-card-footer{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:16px;

    margin-top:21px;

    margin-left:-26px;

    margin-right:-26px;

    padding:
        11px
        26px;

    background:#FAFBFC;

    border-top:
        1px solid
        #E9EEF3;

    color:#98A3AF;

    font-size:.64rem;

}


.footer-result{

    display:inline-flex;

    align-items:center;

    gap:7px;

}


.footer-result-dot{

    width:5px;

    height:5px;

    border-radius:50%;

    background:#B08A4C;

}


.footer-document-type{

    overflow:hidden;

    max-width:50%;

    text-overflow:ellipsis;

    white-space:nowrap;

}


/* =========================================================
   TRANSICIONES
========================================================= */

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
            10px
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


/* =========================================================
   RESPONSIVE — TABLET
========================================================= */

@media(max-width:800px){

    .results-header{

        align-items:flex-start;

    }


    .result-information{

        grid-template-columns:
            repeat(
                3,
                minmax(
                    0,
                    1fr
                )
            );

    }


    .result-info-item{

        padding:
            0
            12px;

    }

}


/* =========================================================
   RESPONSIVE — MOBILE
========================================================= */

@media(max-width:640px){

    .results-header{

        flex-direction:column;

        gap:16px;

        padding-bottom:18px;

    }


    .results-heading{

        width:100%;

    }


    .results-total{

        align-items:flex-start;

    }


    .result-card-header{

        flex-direction:column;

        gap:16px;

    }


    .result-main-heading{

        gap:12px;

    }


    .relevance-score{

        width:100%;

        align-items:flex-start;

        padding:
            9px
            11px;

    }


    .result-information{

        grid-template-columns:1fr;

        gap:0;

    }


    .result-info-item{

        padding:
            10px
            0;

        border-right:none;

        border-bottom:
            1px solid
            #EDF1F5;

    }


    .result-info-item:first-child{

        padding-top:0;

    }


    .result-info-item:last-child{

        padding-bottom:0;

        border-bottom:none;

    }

}


/* =========================================================
   RESPONSIVE — SMALL MOBILE
========================================================= */

@media(max-width:480px){

    .nova-result-card{

        padding:
            21px
            18px
            0;

        border-radius:10px;

    }


    .results-heading-accent{

        min-height:50px;

    }


    .results-heading h2{

        font-size:1.27rem;

    }


    .results-heading p{

        font-size:.82rem;

    }


    .result-position{

        width:30px;

        height:30px;

        flex-basis:30px;

        font-size:.7rem;

    }


    .result-title{

        font-size:1.01rem;

        line-height:1.48;

    }


    .document-type{

        font-size:.59rem;

    }


    .result-meta{

        font-size:.72rem;

    }


    .result-summary{

        font-size:.85rem;

        line-height:1.78;

    }


    .result-details{

        margin-top:18px;

    }


    .details-label{

        font-size:.74rem;

    }


    .result-card-footer{

        margin-left:-18px;

        margin-right:-18px;

        padding:
            11px
            18px;

    }


    .footer-document-type{

        display:none;

    }

}

</style>
