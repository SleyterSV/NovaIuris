<template>

    <section class="court-report">

        <!-- =====================================================
             HEADER
        ====================================================== -->

        <header class="report-header">

            <div class="report-heading">

                <div class="report-icon">

                    📜

                </div>

                <div class="report-heading-content">

                    <span class="report-eyebrow">

                        NOVACOURT · INFORME FINAL

                    </span>

                    <h2>

                        Informe Judicial Inteligente

                    </h2>

                    <p>

                        Síntesis consolidada del análisis, simulación
                        y evaluación jurídica realizada por NovaCourt.

                    </p>

                </div>

            </div>


            <div
                v-if="status"
                class="report-status"
                :class="`status-${statusType}`"
            >

                <span class="status-dot"></span>

                <span>

                    {{ status }}

                </span>

            </div>

        </header>


        <!-- =====================================================
             LOADING
        ====================================================== -->

        <div
            v-if="loading"
            class="report-loading"
        >

            <div class="loading-emblem">

                <div class="loading-orbit"></div>

                <div class="loading-core">

                    ⚖️

                </div>

            </div>


            <div class="loading-content">

                <span class="loading-label">

                    PROCESAMIENTO JUDICIAL

                </span>

                <h3>

                    Generando informe judicial

                </h3>

                <p>

                    NovaCourt está consolidando el análisis del caso,
                    organizando los hallazgos y estructurando las
                    conclusiones finales.

                </p>

            </div>

        </div>


        <!-- =====================================================
             CONTENT
        ====================================================== -->

        <div
            v-else-if="content"
            class="report-content"
        >

            <div class="document-header">

                <div class="document-heading">

                    <span class="document-label">

                        DOCUMENTO DE ANÁLISIS

                    </span>

                    <span class="document-line"></span>

                </div>

                <span class="document-mark">

                    NOVACOURT AI

                </span>

            </div>


            <div class="report-document">

                <MarkdownRenderer
                    :content="content"
                />

            </div>

        </div>


        <!-- =====================================================
             EMPTY STATE
        ====================================================== -->

        <div
            v-else
            class="report-empty"
        >

            <div class="empty-emblem">

                📄

            </div>

            <span class="empty-label">

                NOVACOURT · INFORME JUDICIAL

            </span>

            <h3>

                Informe pendiente

            </h3>

            <p>

                El informe judicial consolidado aparecerá aquí
                cuando NovaCourt finalice el análisis integral
                del caso.

            </p>

        </div>


        <!-- =====================================================
             FOOTER
        ====================================================== -->

        <footer
            v-if="content && !loading"
            class="report-footer"
        >

            <div class="footer-info">

                <span class="footer-icon">

                    🏛️

                </span>

                <span>

                    Informe estructurado mediante el motor
                    de análisis judicial de NovaCourt.

                </span>

            </div>


            <div class="footer-badge">

                <span class="badge-dot"></span>

                NOVACOURT AI

            </div>

        </footer>

    </section>

</template>


<script setup>

import MarkdownRenderer from "../common/MarkdownRenderer.vue"


defineProps({

    content: {

        type: String,

        default: ""

    },

    loading: {

        type: Boolean,

        default: false

    },

    status: {

        type: String,

        default: ""

    },

    statusType: {

        type: String,

        default: "neutral"

    }

})

</script>


<style scoped>

/* =====================================================
   NOVACOURT · INFORME JUDICIAL
   SISTEMA VISUAL INSTITUCIONAL
===================================================== */

.court-report{

    width:100%;

    display:flex;

    flex-direction:column;

    gap:30px;

    padding:32px;

    background:#FFFFFF;

    border:1px solid #D6DFEA;

    border-radius:22px;

    box-shadow:

        0 10px 30px
        rgba(
            23,
            55,
            94,
            .07
        );

    animation:
        reportAppear .4s ease;

}


/* =====================================================
   HEADER
===================================================== */

.report-header{

    display:flex;

    align-items:flex-start;

    justify-content:space-between;

    gap:28px;

    padding-bottom:24px;

    border-bottom:
        1px solid #DCE4EC;

}


.report-heading{

    display:flex;

    align-items:flex-start;

    gap:18px;

    min-width:0;

}


.report-icon{

    position:relative;

    width:58px;

    height:58px;

    display:flex;

    align-items:center;

    justify-content:center;

    flex-shrink:0;

    font-size:1.45rem;

    background:#F7F9FC;

    border:1px solid #D6DFEA;

    border-radius:16px;

}


.report-icon::after{

    content:"";

    position:absolute;

    left:12px;

    right:12px;

    bottom:8px;

    height:2px;

    background:#B08A4C;

    border-radius:999px;

}


.report-heading-content{

    min-width:0;

}


.report-eyebrow{

    display:flex;

    align-items:center;

    gap:8px;

    margin-bottom:8px;

    color:#315C97;

    font-size:.72rem;

    font-weight:700;

    letter-spacing:1.1px;

}


.report-eyebrow::before{

    content:"";

    width:5px;

    height:5px;

    background:#B08A4C;

    border-radius:50%;

}


.report-heading h2{

    margin:0;

    color:#17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:1.55rem;

    font-weight:700;

    line-height:1.3;

    letter-spacing:-.2px;

}


.report-heading p{

    max-width:680px;

    margin:9px 0 0;

    color:#5E6D80;

    font-size:.94rem;

    line-height:1.7;

}


/* =====================================================
   STATUS
===================================================== */

.report-status{

    display:inline-flex;

    align-items:center;

    gap:8px;

    flex-shrink:0;

    padding:9px 13px;

    border:1px solid #D6DFEA;

    border-radius:999px;

    background:#F8FAFC;

    color:#5E6D80;

    font-size:.78rem;

    font-weight:700;

    white-space:nowrap;

}


.status-dot{

    width:7px;

    height:7px;

    flex-shrink:0;

    border-radius:50%;

    background:#8A99AA;

}


/* Neutral */

.status-neutral{

    background:#F7F9FC;

    border-color:#D6DFEA;

    color:#5E6D80;

}


/* Processing */

.status-processing{

    background:#F1F5FA;

    border-color:#D6DFEA;

    color:#315C97;

}


.status-processing .status-dot{

    background:#315C97;

    animation:pulse 1.5s ease-in-out infinite;

}


/* Success */

.status-success,

.status-completed{

    background:#F3F8F5;

    border-color:#D6E6DB;

    color:#35664B;

}


.status-success .status-dot,

.status-completed .status-dot{

    background:#4D8A66;

}


/* Warning */

.status-warning{

    background:#FCF8F0;

    border-color:#E8D9B9;

    color:#8B6A2F;

}


.status-warning .status-dot{

    background:#B08A4C;

}


/* Error */

.status-error{

    background:#FCF5F5;

    border-color:#EBD7D7;

    color:#8D4141;

}


.status-error .status-dot{

    background:#B65A5A;

}


/* =====================================================
   CONTENT
===================================================== */

.report-content{

    width:100%;

}


.document-header{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:20px;

    margin-bottom:14px;

    padding:0 4px;

}


.document-heading{

    display:flex;

    align-items:center;

    gap:12px;

    flex:1;

    min-width:0;

}


.document-label{

    flex-shrink:0;

    color:#315C97;

    font-size:.68rem;

    font-weight:700;

    letter-spacing:1px;

}


.document-line{

    width:100%;

    height:1px;

    background:#DCE4EC;

}


.document-mark{

    flex-shrink:0;

    color:#B08A4C;

    font-size:.67rem;

    font-weight:700;

    letter-spacing:.9px;

}


.report-document{

    padding:30px;

    background:#FFFFFF;

    border:1px solid #D6DFEA;

    border-radius:18px;

}


.report-document :deep(.markdown-body){

    max-width:100%;

}


/* =====================================================
   LOADING
===================================================== */

.report-loading{

    min-height:340px;

    display:flex;

    flex-direction:column;

    align-items:center;

    justify-content:center;

    text-align:center;

    padding:42px;

    background:#F8FAFC;

    border:1px dashed #C8D3E0;

    border-radius:20px;

}


.loading-emblem{

    position:relative;

    width:88px;

    height:88px;

    display:flex;

    align-items:center;

    justify-content:center;

    margin-bottom:22px;

}


.loading-orbit{

    position:absolute;

    inset:0;

    border:2px solid #D6DFEA;

    border-top-color:#315C97;

    border-right-color:#B08A4C;

    border-radius:50%;

    animation:spin 1.2s linear infinite;

}


.loading-core{

    width:58px;

    height:58px;

    display:flex;

    align-items:center;

    justify-content:center;

    background:#FFFFFF;

    border:1px solid #D6DFEA;

    border-radius:50%;

    font-size:1.4rem;

}


.loading-content{

    display:flex;

    flex-direction:column;

    align-items:center;

}


.loading-label{

    margin-bottom:9px;

    color:#315C97;

    font-size:.68rem;

    font-weight:700;

    letter-spacing:1px;

}


.report-loading h3{

    margin:0;

    color:#17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:1.18rem;

    font-weight:700;

}


.report-loading p{

    max-width:500px;

    margin:10px 0 0;

    color:#5E6D80;

    font-size:.92rem;

    line-height:1.7;

}


/* =====================================================
   EMPTY STATE
===================================================== */

.report-empty{

    min-height:300px;

    display:flex;

    flex-direction:column;

    align-items:center;

    justify-content:center;

    padding:42px 25px;

    text-align:center;

    background:#F8FAFC;

    border:1px dashed #C8D3E0;

    border-radius:20px;

}


.empty-emblem{

    position:relative;

    width:68px;

    height:68px;

    display:flex;

    align-items:center;

    justify-content:center;

    margin-bottom:17px;

    background:#FFFFFF;

    border:1px solid #D6DFEA;

    border-radius:18px;

    font-size:1.8rem;

}


.empty-emblem::after{

    content:"";

    position:absolute;

    width:26px;

    height:2px;

    bottom:9px;

    background:#B08A4C;

    border-radius:999px;

}


.empty-label{

    margin-bottom:8px;

    color:#315C97;

    font-size:.67rem;

    font-weight:700;

    letter-spacing:1px;

}


.report-empty h3{

    margin:0;

    color:#17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:1.16rem;

    font-weight:700;

}


.report-empty p{

    max-width:480px;

    margin:10px 0 0;

    color:#5E6D80;

    font-size:.92rem;

    line-height:1.7;

}


/* =====================================================
   FOOTER
===================================================== */

.report-footer{

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:20px;

    padding-top:22px;

    border-top:
        1px solid #DCE4EC;

}


.footer-info{

    display:flex;

    align-items:center;

    gap:9px;

    color:#68788A;

    font-size:.83rem;

    line-height:1.5;

}


.footer-icon{

    display:flex;

    align-items:center;

    justify-content:center;

    width:28px;

    height:28px;

    flex-shrink:0;

    background:#F4F7FA;

    border:1px solid #DCE4EC;

    border-radius:8px;

    font-size:.85rem;

}


.footer-badge{

    display:inline-flex;

    align-items:center;

    gap:7px;

    flex-shrink:0;

    padding:7px 11px;

    color:#17375E;

    background:#FFFFFF;

    border:1px solid #D6DFEA;

    border-radius:8px;

    font-size:.66rem;

    font-weight:700;

    letter-spacing:.8px;

}


.badge-dot{

    width:5px;

    height:5px;

    background:#B08A4C;

    border-radius:50%;

}


/* =====================================================
   ANIMATIONS
===================================================== */

@keyframes reportAppear{

    from{

        opacity:0;

        transform:translateY(12px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}


@keyframes spin{

    to{

        transform:rotate(360deg);

    }

}


@keyframes pulse{

    0%,
    100%{

        transform:scale(1);

        opacity:1;

    }

    50%{

        transform:scale(1.3);

        opacity:.55;

    }

}


/* =====================================================
   RESPONSIVE
===================================================== */

@media(max-width:768px){

    .court-report{

        gap:24px;

        padding:24px;

    }


    .report-header{

        flex-direction:column;

        gap:18px;

    }


    .report-status{

        align-self:flex-start;

    }


    .report-document{

        padding:24px;

    }


    .report-footer{

        flex-direction:column;

        align-items:flex-start;

    }

}


@media(max-width:576px){

    .court-report{

        padding:18px;

        border-radius:18px;

    }


    .report-heading{

        gap:13px;

    }


    .report-icon{

        width:50px;

        height:50px;

        border-radius:14px;

        font-size:1.25rem;

    }


    .report-heading h2{

        font-size:1.3rem;

    }


    .document-header{

        align-items:flex-start;

    }


    .document-mark{

        display:none;

    }


    .report-document{

        padding:18px;

        border-radius:14px;

    }


    .report-loading,

    .report-empty{

        min-height:270px;

        padding:32px 20px;

    }


    .footer-info{

        align-items:flex-start;

    }

}

</style>