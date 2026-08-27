<template>

    <article class="nova-search-result-card">

        <!-- ===================================================
             CABECERA DEL RESULTADO
        ==================================================== -->

        <header class="nova-search-result-header">

            <div class="nova-search-result-heading">

                <span class="nova-search-result-type">

                    {{ result.tipo_documento || 'Documento jurídico' }}

                </span>

                <h3 class="nova-search-result-title">

                    {{ result.titulo }}

                </h3>

            </div>


            <!-- SCORE -->

            <div
                v-if="hasScore"
                class="nova-search-score"
            >

                <span class="nova-search-score-label">
                    RELEVANCIA
                </span>

                <strong>
                    {{ scorePercentage }}%
                </strong>

            </div>

        </header>


        <!-- ===================================================
             METADATA PRINCIPAL
        ==================================================== -->

        <div
            v-if="
                result.rama ||
                result.organo_emisor
            "
            class="nova-search-result-meta"
        >

            <span
                v-if="result.rama"
                class="nova-search-meta-item"
            >

                <span class="nova-search-meta-label">
                    Rama
                </span>

                {{ result.rama }}

            </span>


            <span
                v-if="result.organo_emisor"
                class="nova-search-meta-item"
            >

                <span class="nova-search-meta-label">
                    Órgano
                </span>

                {{ result.organo_emisor }}

            </span>

        </div>


        <!-- ===================================================
             INFORMACIÓN DEL DOCUMENTO
        ==================================================== -->

        <div
            v-if="
                result.expediente ||
                result.numero ||
                result.fecha_resolucion
            "
            class="nova-search-document-data"
        >

            <span
                v-if="result.expediente"
                class="nova-search-document-item"
            >

                <span class="nova-search-document-label">
                    EXPEDIENTE
                </span>

                {{ result.expediente }}

            </span>


            <span
                v-if="result.numero"
                class="nova-search-document-item"
            >

                <span class="nova-search-document-label">
                    NÚMERO
                </span>

                {{ result.numero }}

            </span>


            <span
                v-if="result.fecha_resolucion"
                class="nova-search-document-item"
            >

                <span class="nova-search-document-label">
                    FECHA
                </span>

                {{ result.fecha_resolucion }}

            </span>

        </div>


        <!-- ===================================================
             MATERIA
        ==================================================== -->

        <div
            v-if="result.materia"
            class="nova-search-materia"
        >

            <span>
                {{ result.materia }}
            </span>

        </div>


        <!-- ===================================================
             PRECEDENTE VINCULANTE
        ==================================================== -->

        <div
            v-if="result.precedente_vinculante"
            class="nova-search-precedente"
        >

            <span class="nova-search-precedente-mark">
                ◆
            </span>

            <span>
                Precedente vinculante
            </span>

        </div>


        <!-- ===================================================
             RESUMEN IA
        ==================================================== -->

        <div
            v-if="result.resumen_ia"
            class="nova-search-summary"
        >

            <span class="nova-search-section-label">
                SÍNTESIS JURÍDICA
            </span>

            <p>
                {{ result.resumen_ia }}
            </p>

        </div>


        <!-- ===================================================
             EXTRACTO
        ==================================================== -->

        <details
            v-if="result.extracto_exacto"
            class="nova-search-details"
        >

            <summary>

                <span>
                    Consultar extracto jurídico
                </span>

                <span class="nova-search-details-symbol">
                    +
                </span>

            </summary>


            <div class="nova-search-extract">

                {{ result.extracto_exacto }}

            </div>

        </details>

    </article>

</template>


<script setup>

import { computed } from "vue"


const props = defineProps({

    result: {

        type: Object,

        required: true

    }

})


const hasScore = computed(() => {

    return typeof props.result.score === "number"

})


const scorePercentage = computed(() => {

    if (!hasScore.value) {

        return 0

    }

    return Math.round(

        props.result.score * 100

    )

})

</script>


<style scoped>

/* =======================================================
   NOVA SEARCH — RESULT CARD
======================================================= */

.nova-search-result-card{

    width:100%;

    padding:26px 28px;

    margin-bottom:16px;

    background:#FFFFFF;

    border:

        1px solid
        #DCE4EC;

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

        border-color
        .22s
        ease,

        box-shadow
        .22s
        ease;

}


.nova-search-result-card:hover{

    transform:

        translateY(
            -2px
        );

    border-color:#B8C8D9;

    box-shadow:

        0 14px 32px
        rgba(
            23,
            55,
            94,
            .075
        );

}


/* =======================================================
   CABECERA
======================================================= */

.nova-search-result-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:24px;

}


.nova-search-result-heading{

    flex:1;

    min-width:0;

}


.nova-search-result-type{

    display:inline-flex;

    align-items:center;

    min-height:24px;

    padding:

        0
        9px;

    margin-bottom:10px;

    border:

        1px solid
        #D5DFEA;

    border-radius:999px;

    background:#F7F9FC;

    color:#315C97;

    font-size:.65rem;

    font-weight:800;

    letter-spacing:.75px;

    text-transform:uppercase;

}


.nova-search-result-title{

    margin:0;

    color:#17375E;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1.18rem;

    font-weight:600;

    line-height:1.45;

}


/* =======================================================
   RELEVANCIA
======================================================= */

.nova-search-score{

    min-width:78px;

    padding:9px 11px;

    text-align:center;

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .38
        );

    border-radius:9px;

    background:

        linear-gradient(
            135deg,
            #FFFCF7 0%,
            #FFF9EF 100%
        );

}


.nova-search-score-label{

    display:block;

    margin-bottom:3px;

    color:#8A6A37;

    font-size:.55rem;

    font-weight:800;

    letter-spacing:.8px;

}


.nova-search-score strong{

    display:block;

    color:#17375E;

    font-size:.95rem;

    font-weight:750;

}


/* =======================================================
   METADATA
======================================================= */

.nova-search-result-meta{

    display:flex;

    flex-wrap:wrap;

    gap:10px;

    margin-top:16px;

}


.nova-search-meta-item{

    display:inline-flex;

    align-items:center;

    gap:6px;

    color:#5E6D7E;

    font-size:.78rem;

}


.nova-search-meta-label{

    color:#8A98A8;

    font-size:.62rem;

    font-weight:800;

    letter-spacing:.6px;

    text-transform:uppercase;

}


/* =======================================================
   DATOS DEL DOCUMENTO
======================================================= */

.nova-search-document-data{

    display:flex;

    flex-wrap:wrap;

    gap:20px;

    margin-top:17px;

    padding-top:17px;

    border-top:

        1px solid
        #E8EDF2;

}


.nova-search-document-item{

    display:flex;

    flex-direction:column;

    gap:4px;

    color:#435568;

    font-size:.82rem;

}


.nova-search-document-label{

    color:#94A0AD;

    font-size:.58rem;

    font-weight:800;

    letter-spacing:.75px;

}


/* =======================================================
   MATERIA
======================================================= */

.nova-search-materia{

    margin-top:18px;

}


.nova-search-materia span{

    display:inline-flex;

    padding:

        7px
        12px;

    border-radius:999px;

    background:#F3F6FA;

    border:

        1px solid
        #DCE4EC;

    color:#315C97;

    font-size:.72rem;

    font-weight:700;

}


/* =======================================================
   PRECEDENTE
======================================================= */

.nova-search-precedente{

    display:inline-flex;

    align-items:center;

    gap:8px;

    margin-top:14px;

    padding:

        8px
        12px;

    border-radius:8px;

    background:#FFFAF0;

    border:

        1px solid
        #E8D8B6;

    color:#7A6440;

    font-size:.74rem;

    font-weight:750;

}


.nova-search-precedente-mark{

    color:#B08A4C;

    font-size:.7rem;

}


/* =======================================================
   SÍNTESIS
======================================================= */

.nova-search-summary{

    margin-top:20px;

}


.nova-search-section-label{

    display:block;

    margin-bottom:8px;

    color:#7A6440;

    font-size:.62rem;

    font-weight:800;

    letter-spacing:1px;

}


.nova-search-summary p{

    margin:0;

    color:#4D5C6B;

    font-size:.9rem;

    line-height:1.8;

}


/* =======================================================
   EXTRACTO
======================================================= */

.nova-search-details{

    margin-top:20px;

    padding-top:18px;

    border-top:

        1px solid
        #E8EDF2;

}


.nova-search-details summary{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:12px;

    cursor:pointer;

    list-style:none;

    color:#315C97;

    font-size:.8rem;

    font-weight:750;

}


.nova-search-details summary::-webkit-details-marker{

    display:none;

}


.nova-search-details-symbol{

    width:25px;

    height:25px;

    display:flex;

    align-items:center;

    justify-content:center;

    border:

        1px solid
        #D5DFEA;

    border-radius:50%;

    color:#7A6440;

    transition:

        transform
        .2s
        ease;

}


.nova-search-details[open]
.nova-search-details-symbol{

    transform:

        rotate(
            45deg
        );

}


.nova-search-extract{

    margin-top:16px;

    padding:18px;

    background:#F8FAFC;

    border-left:

        2px solid
        #B08A4C;

    color:#536273;

    font-size:.86rem;

    line-height:1.8;

    white-space:pre-wrap;

    border-radius:

        0
        8px
        8px
        0;

}


/* =======================================================
   RESPONSIVE
======================================================= */

@media(max-width:640px){

    .nova-search-result-card{

        padding:22px;

    }


    .nova-search-result-header{

        flex-direction:column;

        gap:14px;

    }


    .nova-search-score{

        align-self:flex-start;

    }


    .nova-search-document-data{

        flex-direction:column;

        gap:12px;

    }

}
</style>