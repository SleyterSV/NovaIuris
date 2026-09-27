<template>

    <section class="nova-case-input">

        <!-- ===================================================
             CABECERA
        ==================================================== -->

        <header class="input-header">

            <div class="input-heading">

                <div class="input-eyebrow">

                    <span class="eyebrow-line"></span>

                    NOVACASE · INGRESO DEL CASO

                </div>

                <h2>
                    Describe el caso jurídico
                </h2>

                <p>
                    Expón los hechos, antecedentes y circunstancias
                    relevantes del caso para que NovaCase pueda
                    estructurar el análisis jurídico.
                </p>

            </div>

            <div class="input-badge">

                <span class="badge-dot"></span>

                Análisis jurídico

            </div>

        </header>


        <!-- ===================================================
             ÁREA DE INGRESO
        ==================================================== -->

        <div class="input-area">

            <div class="textarea-header">

                <div>

                    <span class="textarea-label">
                        DESCRIPCIÓN DEL CASO
                    </span>

                    <span class="textarea-hint">
                        Proporciona la mayor cantidad de información relevante posible.
                    </span>

                </div>

                <span class="required-label">
                    Información requerida
                </span>

            </div>


            <div class="textarea-wrapper">

                <textarea
                    v-model="caseText"
                    class="case-textarea"
                    placeholder="Ejemplo:

Un trabajador fue despedido luego de publicar comentarios críticos sobre su empleador en redes sociales. La empresa alega pérdida de confianza. El trabajador sostiene que se vulneró su libertad de expresión y solicita su reposición..."
                    aria-label="Descripción del caso jurídico"
                    @keydown.ctrl.enter="submitCase"
                    @keydown.meta.enter="submitCase"
                ></textarea>


                <div class="textarea-footer">

                    <span class="writing-hint">

                        <span class="keyboard-key">
                            Ctrl
                        </span>

                        <span>+</span>

                        <span class="keyboard-key">
                            Enter
                        </span>

                        para analizar

                    </span>

                    <span
                        class="characters"
                        :class="{
                            'has-content': caseText.length > 0
                        }"
                    >
                        {{ caseText.length }} caracteres
                    </span>

                </div>

            </div>

        </div>


        <CaseDocumentUpload :case-id="caseId" :disabled="loading" @update:document-ids="documentIds = $event" />

        <!-- ===================================================
             PIE / ACCIÓN
        ==================================================== -->

        <footer class="input-footer">

            <div class="footer-information">

                <span class="footer-mark">
                    ✓
                </span>

                <span>
                    La información será utilizada para estructurar
                    el análisis jurídico del caso.
                </span>

            </div>


            <button
                type="button"
                class="analyze-button"
                :disabled="loading || (!caseText.trim() && documentIds.length === 0)"
                @click="submitCase"
            >

                <span
                    v-if="!loading"
                    class="button-content"
                >

                    <span>
                        Analizar caso
                    </span>

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.8"
                        aria-hidden="true"
                    >

                        <path
                            d="M5 12h13"
                        />

                        <path
                            d="m13 6 6 6-6 6"
                        />

                    </svg>

                </span>


                <span
                    v-else
                    class="button-content"
                >

                    <span class="loading-spinner"></span>

                    <span>
                        Analizando caso...
                    </span>

                </span>

            </button>

        </footer>

    </section>

</template>


<script setup>

import { ref } from "vue"
import CaseDocumentUpload from "@/components/common/CaseDocumentUpload.vue"


/* =========================================================
   EVENTOS
========================================================= */

const props = defineProps({ caseId: { type:String, required:true }, loading: { type:Boolean, default:false } })
const emit = defineEmits(["analyze"])


/* =========================================================
   ESTADO
========================================================= */

const caseText = ref("")

const documentIds = ref([])


/* =========================================================
   ENVÍO DEL CASO
========================================================= */

async function submitCase(){

    if(
        props.loading ||
        (!caseText.value.trim() && documentIds.value.length === 0)
    ){

        return

    }


    const text = caseText.value.trim() || "Analiza los documentos jurídicos aportados para este caso."
    emit("analyze", { caseText:text, caseId:props.caseId, documentIds:[...documentIds.value] })

}

</script>


<style scoped>

/* =======================================================
   NOVACASE — CASE INPUT
======================================================= */

.nova-case-input{

    width:100%;

    box-sizing:border-box;

    display:flex;

    flex-direction:column;

    background:
        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FBFCFE 100%
        );

    border:
        1px solid
        #DCE4EC;

    border-radius:14px;

    box-shadow:
        0 10px 28px
        rgba(
            23,
            55,
            94,
            .045
        );

    overflow:hidden;

    animation:
        novaCaseInputEnter
        .4s
        ease-out;

}


/* =======================================================
   CABECERA
======================================================= */

.input-header{

    display:flex;

    align-items:flex-end;

    justify-content:space-between;

    gap:24px;

    padding:
        26px
        28px
        22px;

    border-bottom:
        1px solid
        #DCE5EE;

}


.input-heading{

    min-width:0;

}


.input-eyebrow{

    display:flex;

    align-items:center;

    gap:8px;

    margin-bottom:9px;

    color:#7A6440;

    font-size:.61rem;

    font-weight:800;

    letter-spacing:1.4px;

}


.eyebrow-line{

    width:22px;

    height:1px;

    flex-shrink:0;

    background:#B08A4C;

}


.input-heading h2{

    margin:0 0 8px;

    color:#17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:1.55rem;

    font-weight:600;

    line-height:1.3;

}


.input-heading p{

    max-width:720px;

    margin:0;

    color:#697888;

    font-size:.85rem;

    line-height:1.7;

}


/* =======================================================
   BADGE
======================================================= */

.input-badge{

    display:inline-flex;

    align-items:center;

    gap:8px;

    flex-shrink:0;

    min-height:30px;

    padding:
        0
        12px;

    background:#F8FAFC;

    border:
        1px solid
        #D8E1EA;

    border-radius:999px;

    color:#68798A;

    font-size:.61rem;

    font-weight:750;

    letter-spacing:.35px;

}


.badge-dot{

    width:6px;

    height:6px;

    border-radius:50%;

    background:#B08A4C;

    box-shadow:
        0 0 0 3px
        rgba(
            176,
            138,
            76,
            .10
        );

}


/* =======================================================
   ÁREA DE INGRESO
======================================================= */

.input-area{

    padding:
        24px
        28px
        0;

}


.textarea-header{

    display:flex;

    align-items:flex-end;

    justify-content:space-between;

    gap:18px;

    margin-bottom:9px;

}


.textarea-header > div{

    min-width:0;

}


.textarea-label{

    display:block;

    margin-bottom:4px;

    color:#526477;

    font-size:.61rem;

    font-weight:800;

    letter-spacing:1px;

}


.textarea-hint{

    display:block;

    color:#8A97A4;

    font-size:.72rem;

    line-height:1.5;

}


.required-label{

    flex-shrink:0;

    color:#9AA5B0;

    font-size:.59rem;

    font-weight:700;

}


/* =======================================================
   CONTENEDOR TEXTAREA
======================================================= */

.textarea-wrapper{

    position:relative;

    border:
        1px solid
        #D2DCE6;

    border-radius:10px;

    background:#FFFFFF;

    overflow:hidden;

    transition:
        border-color
        .22s
        ease,
        box-shadow
        .22s
        ease;

}


.textarea-wrapper:focus-within{

    border-color:#9FB5CB;

    box-shadow:
        0 0 0 4px
        rgba(
            49,
            92,
            151,
            .065
        );

}


/* =======================================================
   TEXTAREA
======================================================= */

.case-textarea{

    display:block;

    width:100%;

    min-height:315px;

    box-sizing:border-box;

    resize:vertical;

    padding:
        19px
        20px;

    border:0;

    outline:none;

    background:#FFFFFF;

    color:#26394D;

    font-family:
        inherit;

    font-size:.88rem;

    line-height:1.8;

}


.case-textarea::placeholder{

    color:#A2ACB7;

    opacity:1;

}


.case-textarea:focus{

    outline:none;

}


/* =======================================================
   FOOTER DEL TEXTAREA
======================================================= */

.textarea-footer{

    min-height:36px;

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:15px;

    padding:
        0
        13px;

    background:#FAFBFC;

    border-top:
        1px solid
        #EDF1F4;

}


.writing-hint{

    display:inline-flex;

    align-items:center;

    gap:5px;

    color:#9AA5B0;

    font-size:.59rem;

}


.keyboard-key{

    display:inline-flex;

    align-items:center;

    justify-content:center;

    min-width:22px;

    height:18px;

    padding:
        0
        4px;

    border:
        1px solid
        #D8E0E7;

    border-radius:4px;

    background:#FFFFFF;

    color:#7B8997;

    font-size:.53rem;

    font-weight:750;

}


.characters{

    flex-shrink:0;

    color:#9AA5B0;

    font-size:.61rem;

    font-weight:700;

    transition:
        color
        .2s
        ease;

}


.characters.has-content{

    color:#718090;

}


/* =======================================================
   PIE PRINCIPAL
======================================================= */

.input-footer{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:20px;

    margin:
        20px
        28px
        26px;

    padding-top:18px;

    border-top:
        1px solid
        #E7ECF1;

}


.footer-information{

    display:flex;

    align-items:center;

    gap:8px;

    max-width:580px;

    color:#8996A3;

    font-size:.69rem;

    line-height:1.5;

}


.footer-mark{

    width:18px;

    height:18px;

    flex:
        0 0 18px;

    display:flex;

    align-items:center;

    justify-content:center;

    border:
        1px solid
        #D7E3DB;

    border-radius:50%;

    background:#F5F9F6;

    color:#66806D;

    font-size:.58rem;

    font-weight:800;

}


/* =======================================================
   BOTÓN
======================================================= */

.analyze-button{

    display:inline-flex;

    align-items:center;

    justify-content:center;

    flex-shrink:0;

    min-width:165px;

    min-height:43px;

    padding:
        0
        18px;

    border:
        1px solid
        #315C97;

    border-radius:8px;

    background:#315C97;

    color:#FFFFFF;

    font-family:inherit;

    font-size:.74rem;

    font-weight:750;

    letter-spacing:.1px;

    cursor:pointer;

    transition:
        background
        .22s
        ease,
        border-color
        .22s
        ease,
        transform
        .22s
        ease,
        box-shadow
        .22s
        ease;

}


.button-content{

    display:inline-flex;

    align-items:center;

    justify-content:center;

    gap:9px;

}


.analyze-button svg{

    width:15px;

    height:15px;

}


.analyze-button:hover:not(:disabled){

    background:#284E80;

    border-color:#284E80;

    transform:
        translateY(
            -1px
        );

    box-shadow:
        0 7px 17px
        rgba(
            49,
            92,
            151,
            .18
        );

}


.analyze-button:active:not(:disabled){

    transform:
        translateY(
            0
        );

    box-shadow:none;

}


.analyze-button:disabled{

    opacity:.52;

    cursor:not-allowed;

    transform:none;

    box-shadow:none;

}


/* =======================================================
   LOADING
======================================================= */

.loading-spinner{

    width:13px;

    height:13px;

    flex-shrink:0;

    border:
        2px solid
        rgba(
            255,
            255,
            255,
            .35
        );

    border-top-color:#FFFFFF;

    border-radius:50%;

    animation:
        novaCaseSpinner
        .8s
        linear
        infinite;

}


/* =======================================================
   ANIMACIONES
======================================================= */

@keyframes novaCaseInputEnter{

    from{

        opacity:0;

        transform:
            translateY(
                10px
            );

    }

    to{

        opacity:1;

        transform:
            translateY(
                0
            );

    }

}


@keyframes novaCaseSpinner{

    from{

        transform:
            rotate(
                0deg
            );

    }

    to{

        transform:
            rotate(
                360deg
            );

    }

}


/* =======================================================
   REDUCIR MOVIMIENTO
======================================================= */

@media(
    prefers-reduced-motion:reduce
){

    .nova-case-input,
    .loading-spinner{

        animation:none;

    }

}


/* =======================================================
   TABLET
======================================================= */

@media(max-width:800px){

    .input-header{

        align-items:flex-start;

        flex-direction:column;

        padding:
            24px
            24px
            20px;

        gap:15px;

    }


    .input-badge{

        align-self:flex-start;

    }


    .input-area{

        padding:
            22px
            24px
            0;

    }


    .input-footer{

        margin:
            20px
            24px
            24px;

    }

}


/* =======================================================
   MOBILE
======================================================= */

@media(max-width:600px){

    .nova-case-input{

        border-radius:11px;

    }


    .input-heading h2{

        font-size:1.35rem;

    }


    .input-heading p{

        font-size:.8rem;

    }


    .textarea-header{

        align-items:flex-start;

        flex-direction:column;

        gap:5px;

    }


    .required-label{

        display:none;

    }


    .case-textarea{

        min-height:270px;

        padding:
            17px;

        font-size:.84rem;

    }


    .writing-hint{

        display:none;

    }


    .textarea-footer{

        justify-content:flex-end;

    }


    .input-footer{

        align-items:stretch;

        flex-direction:column;

        margin:
            18px
            20px
            20px;

        gap:15px;

    }


    .footer-information{

        max-width:none;

    }


    .analyze-button{

        width:100%;

    }

}


/* =======================================================
   MOBILE PEQUEÑO
======================================================= */

@media(max-width:420px){

    .input-header{

        padding:
            20px
            18px
            18px;

    }


    .input-area{

        padding:
            19px
            18px
            0;

    }


    .input-footer{

        margin:
            17px
            18px
            18px;

    }


    .input-eyebrow{

        font-size:.56rem;

        letter-spacing:1.1px;

    }


    .input-heading h2{

        font-size:1.25rem;

    }


    .case-textarea{

        min-height:245px;

    }

}

</style>