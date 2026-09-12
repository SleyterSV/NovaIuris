<template>

    <section class="court-report">

        <!-- =====================================================
             ENCABEZADO
        ====================================================== -->

        <header class="report-header">

            <div class="report-heading">

                <span class="report-eyebrow">
                    NOVACOURT · INFORME FINAL
                </span>

                <h2>
                    Informe Judicial Inteligente
                </h2>

                <div class="title-accent"></div>

                <p>
                    Síntesis consolidada del análisis, simulación
                    y evaluación jurídica realizada por NovaCourt.
                </p>

            </div>


            <!-- ESTADO -->

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

            <div class="loading-line"></div>

            <div class="loading-content">

                <span class="loading-eyebrow">
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
             CONTENIDO DEL INFORME
        ====================================================== -->

        <div
            v-else-if="content"
            class="report-content"
        >

            <!-- CABECERA DEL DOCUMENTO -->

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


            <!-- DOCUMENTO -->

            <article class="report-document">

                <MarkdownRenderer
                    :content="content"
                />

            </article>

        </div>


        <!-- =====================================================
             ESTADO VACÍO
        ====================================================== -->

        <div
            v-else
            class="report-empty"
        >

            <div class="empty-mark">
                REPORT
            </div>

            <div class="empty-content">

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

        </div>


        <!-- =====================================================
             PIE DEL INFORME
        ====================================================== -->

        <footer
            v-if="content && !loading"
            class="report-footer"
        >

            <div class="footer-info">

                <span class="footer-rule"></span>

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
   NOVACOURT · COURT REPORT

   SISTEMA VISUAL
   JURÍDICO · INSTITUCIONAL · EDITORIAL · SOBRIO

   PALETA

   AZUL MARINO:
   #17375E

   AZUL INSTITUCIONAL:
   #315C97

   DORADO:
   #B08A4C

   FONDO:
   #FFFFFF

   PRINCIPIO:
   EL INFORME NO DEBE PARECER UNA CARD.
   DEBE SENTIRSE COMO UN DOCUMENTO
   INSTITUCIONAL INTEGRADO EN NOVACOURT.
===================================================== */


/* =====================================================
   CONTENEDOR PRINCIPAL
===================================================== */

.court-report {

    width: 100%;

    margin: 0;

    padding: 42px 48px 44px;

    background: #FFFFFF;

}


/* =====================================================
   ENCABEZADO
===================================================== */

.report-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 32px;

    padding-bottom: 28px;

    border-bottom:
        1px solid
        #D9E0E8;

}


.report-heading {

    flex: 1;

    min-width: 0;

    max-width: 900px;

}


/* =====================================================
   EYEBROW
===================================================== */

.report-eyebrow {

    display: block;

    margin-bottom: 16px;

    color: #315C97;

    font-size: .68rem;

    font-weight: 700;

    letter-spacing: 1.45px;

    line-height: 1.2;

}


/* =====================================================
   TÍTULO
===================================================== */

.report-heading h2 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 2rem;

    font-weight: 500;

    line-height: 1.25;

    letter-spacing: -.2px;

}


/* =====================================================
   ACENTO
===================================================== */

.title-accent {

    width: 46px;

    height: 2px;

    margin: 18px 0;

    background: #315C97;

}


/* =====================================================
   DESCRIPCIÓN
===================================================== */

.report-heading p {

    max-width: 820px;

    margin: 0;

    color: #5E6D7E;

    font-size: .97rem;

    font-weight: 400;

    line-height: 1.85;

    letter-spacing: .01em;

}


/* =====================================================
   ESTADO
===================================================== */

.report-status {

    display: inline-flex;

    align-items: center;

    gap: 9px;

    flex-shrink: 0;

    margin-top: 3px;

    padding: 9px 0;

    color: #647487;

    border-bottom:
        1px solid
        #D9E0E8;

    font-size: .76rem;

    font-weight: 700;

    line-height: 1.4;

    white-space: nowrap;

}


.status-dot {

    width: 7px;

    height: 7px;

    flex-shrink: 0;

    border-radius: 50%;

    background: #8A97A5;

}


/* =====================================================
   ESTADO · NEUTRAL
===================================================== */

.status-neutral {

    color: #647487;

}


/* =====================================================
   ESTADO · PROCESANDO
===================================================== */

.status-processing {

    color: #315C97;

}


.status-processing .status-dot {

    background: #315C97;

    animation:
        pulse
        1.5s
        ease-in-out
        infinite;

}


/* =====================================================
   ESTADO · COMPLETADO
===================================================== */

.status-success,
.status-completed {

    color: #35664B;

}


.status-success .status-dot,
.status-completed .status-dot {

    background: #4D8A66;

}


/* =====================================================
   ESTADO · ADVERTENCIA
===================================================== */

.status-warning {

    color: #8B6A2F;

}


.status-warning .status-dot {

    background: #B08A4C;

}


/* =====================================================
   ESTADO · ERROR
===================================================== */

.status-error {

    color: #8D4141;

}


.status-error .status-dot {

    background: #B65A5A;

}


/* =====================================================
   CONTENIDO
===================================================== */

.report-content {

    width: 100%;

    padding-top: 34px;

}


/* =====================================================
   CABECERA DEL DOCUMENTO
===================================================== */

.document-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    margin-bottom: 18px;

}


.document-heading {

    display: flex;

    align-items: center;

    gap: 12px;

    flex: 1;

    min-width: 0;

}


.document-label {

    flex-shrink: 0;

    color: #315C97;

    font-size: .67rem;

    font-weight: 700;

    letter-spacing: 1.25px;

    line-height: 1.3;

}


.document-line {

    width: 100%;

    height: 1px;

    background: #DCE4EC;

}


.document-mark {

    flex-shrink: 0;

    color: #B08A4C;

    font-size: .65rem;

    font-weight: 700;

    letter-spacing: 1px;

}


/* =====================================================
   DOCUMENTO

   IMPORTANTE:
   No parece una segunda card.
   Se mantiene limpio y editorial.
===================================================== */

.report-document {

    width: 100%;

    padding: 30px 4px 10px;

    color: #24364A;

}


/* =====================================================
   MARKDOWN

   Se mantiene compatible con
   MarkdownRenderer existente.
===================================================== */

.report-document :deep(.markdown-body) {

    width: 100%;

    max-width: 100%;

}


/* =====================================================
   LOADING
===================================================== */

.report-loading {

    display: flex;

    align-items: flex-start;

    gap: 22px;

    min-height: 170px;

    padding: 32px 0;

    border-bottom:
        1px solid
        #E1E6EC;

}


.loading-line {

    width: 3px;

    min-height: 78px;

    flex-shrink: 0;

    background:
        linear-gradient(
            180deg,
            #17375E 0%,
            #315C97 70%,
            #B08A4C 100%
        );

}


.loading-content {

    display: flex;

    flex-direction: column;

    gap: 7px;

    padding-top: 1px;

}


.loading-eyebrow {

    color: #315C97;

    font-size: .66rem;

    font-weight: 700;

    letter-spacing: 1.35px;

    line-height: 1.3;

}


.report-loading h3 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.25rem;

    font-weight: 500;

    line-height: 1.4;

}


.report-loading p {

    max-width: 650px;

    margin: 2px 0 0;

    color: #647487;

    font-size: .91rem;

    line-height: 1.8;

}


/* =====================================================
   ESTADO VACÍO
===================================================== */

.report-empty {

    display: flex;

    align-items: flex-start;

    gap: 28px;

    min-height: 210px;

    padding: 38px 0;

    border-bottom:
        1px solid
        #E1E6EC;

}


.empty-mark {

    flex-shrink: 0;

    padding-top: 3px;

    color: #315C97;

    font-size: .62rem;

    font-weight: 700;

    letter-spacing: 1.6px;

    writing-mode: vertical-rl;

    transform:
        rotate(180deg);

}


.empty-content {

    max-width: 580px;

}


.empty-label {

    display: block;

    margin-bottom: 9px;

    color: #315C97;

    font-size: .65rem;

    font-weight: 700;

    letter-spacing: 1.3px;

}


.report-empty h3 {

    margin: 0 0 11px;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.3rem;

    font-weight: 500;

    line-height: 1.35;

}


.report-empty p {

    margin: 0;

    color: #647487;

    font-size: .93rem;

    line-height: 1.8;

}


/* =====================================================
   FOOTER
===================================================== */

.report-footer {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 24px;

    margin-top: 30px;

    padding-top: 20px;

    border-top:
        1px solid
        #DCE4EC;

}


.footer-info {

    display: flex;

    align-items: center;

    gap: 10px;

    min-width: 0;

    color: #687789;

    font-size: .79rem;

    line-height: 1.5;

}


.footer-rule {

    width: 24px;

    height: 1px;

    flex-shrink: 0;

    background: #B08A4C;

}


.footer-badge {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    flex-shrink: 0;

    color: #17375E;

    font-size: .64rem;

    font-weight: 700;

    letter-spacing: .9px;

}


.badge-dot {

    width: 5px;

    height: 5px;

    flex-shrink: 0;

    border-radius: 50%;

    background: #B08A4C;

}


/* =====================================================
   ANIMACIONES
===================================================== */

@keyframes pulse {

    0%,
    100% {

        transform:
            scale(1);

        opacity: 1;

    }

    50% {

        transform:
            scale(1.35);

        opacity: .55;

    }

}


/* =====================================================
   RESPONSIVE · TABLET
===================================================== */

@media (max-width: 768px) {

    .court-report {

        padding:
            34px
            30px
            36px;

    }


    .report-header {

        flex-direction: column;

        gap: 20px;

    }


    .report-status {

        align-self: flex-start;

        margin-top: 0;

    }


    .report-heading h2 {

        font-size: 1.8rem;

    }


    .report-content {

        padding-top: 28px;

    }


    .report-document {

        padding:
            26px
            0
            8px;

    }


    .report-footer {

        align-items: flex-start;

    }

}


/* =====================================================
   RESPONSIVE · MOBILE
===================================================== */

@media (max-width: 576px) {

    .court-report {

        padding:
            28px
            20px
            30px;

    }


    .report-header {

        padding-bottom: 24px;

    }


    .report-eyebrow {

        margin-bottom: 13px;

        font-size: .64rem;

    }


    .report-heading h2 {

        font-size: 1.55rem;

    }


    .title-accent {

        width: 38px;

        margin:
            16px
            0;

    }


    .report-heading p {

        font-size: .9rem;

        line-height: 1.75;

    }


    .report-content {

        padding-top: 24px;

    }


    .document-header {

        align-items: flex-start;

        gap: 12px;

    }


    .document-label {

        font-size: .62rem;

    }


    .document-mark {

        display: none;

    }


    .report-document {

        padding:
            22px
            0
            6px;

    }


    .report-loading {

        gap: 16px;

        min-height: 145px;

        padding:
            26px
            0;

    }


    .loading-line {

        min-height: 72px;

    }


    .loading-eyebrow {

        font-size: .62rem;

    }


    .report-loading h3 {

        font-size: 1.08rem;

    }


    .report-loading p {

        font-size: .87rem;

        line-height: 1.7;

    }


    .report-empty {

        gap: 20px;

        min-height: 180px;

        padding:
            30px
            0;

    }


    .empty-mark {

        font-size: .58rem;

    }


    .empty-label {

        font-size: .61rem;

    }


    .report-empty h3 {

        font-size: 1.15rem;

    }


    .report-empty p {

        font-size: .88rem;

        line-height: 1.75;

    }


    .report-footer {

        flex-direction: column;

        align-items: flex-start;

        gap: 14px;

        margin-top: 24px;

    }


    .footer-info {

        align-items: flex-start;

        font-size: .76rem;

    }

}

</style>