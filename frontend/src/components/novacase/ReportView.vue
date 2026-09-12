<template>

    <section
        class="report-view"
        :class="{
            'report-ready': report
        }"
    >

        <!-- =====================================================
             CABECERA DEL INFORME
        ====================================================== -->

        <header class="report-header">

            <div class="report-heading">

                <div class="report-eyebrow">

                    <span class="eyebrow-line"></span>

                    NOVACASE · INFORME JURÍDICO

                </div>

                <h2>
                    Informe Jurídico
                </h2>

                <p>
                    Documento estructurado generado automáticamente
                    a partir del análisis integral del caso.
                </p>

            </div>


            <!-- =================================================
                 HERRAMIENTAS
            ================================================== -->

            <div class="report-toolbar">

                <button
                    type="button"
                    class="toolbar-button primary"
                    title="Copiar informe"
                    @click="copyReport"
                >

                    <span class="button-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >

                            <rect
                                x="8"
                                y="8"
                                width="11"
                                height="11"
                                rx="1.5"
                            />

                            <path
                                d="M16 8V6.5A1.5 1.5 0 0 0 14.5 5h-8A1.5 1.5 0 0 0 5 6.5v8A1.5 1.5 0 0 0 6.5 16H8"
                            />

                        </svg>

                    </span>

                    <span>
                        Copiar
                    </span>

                </button>


                <button
                    type="button"
                    class="toolbar-button"
                    title="Exportar PDF"
                    @click="exportPdf"
                >

                    <span class="button-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >

                            <path
                                d="M6 3.5h8l4 4V20.5H6z"
                            />

                            <path
                                d="M14 3.5v4h4"
                            />

                            <path
                                d="M9 15h6"
                            />

                        </svg>

                    </span>

                    <span>
                        PDF
                    </span>

                </button>


                <button
                    type="button"
                    class="toolbar-button"
                    title="Exportar DOCX"
                    @click="exportDocx"
                >

                    <span class="button-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >

                            <path
                                d="M6 3.5h8l4 4V20.5H6z"
                            />

                            <path
                                d="M14 3.5v4h4"
                            />

                            <path
                                d="M9 12h6"
                            />

                            <path
                                d="M9 15.5h4"
                            />

                        </svg>

                    </span>

                    <span>
                        DOCX
                    </span>

                </button>


                <button
                    type="button"
                    class="toolbar-button"
                    title="Imprimir informe"
                    @click="printReport"
                >

                    <span class="button-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            aria-hidden="true"
                        >

                            <path
                                d="M7 9V4.5h10V9"
                            />

                            <path
                                d="M6 17H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-1"
                            />

                            <path
                                d="M7 14h10v6H7z"
                            />

                            <path
                                d="M17 12h.01"
                            />

                        </svg>

                    </span>

                    <span>
                        Imprimir
                    </span>

                </button>

            </div>

        </header>


        <!-- =====================================================
             INFORMACIÓN DEL DOCUMENTO
        ====================================================== -->

        <section class="report-meta">

            <!-- Fecha -->

            <div class="meta-item">

                <span class="meta-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        aria-hidden="true"
                    >

                        <rect
                            x="4"
                            y="5"
                            width="16"
                            height="15"
                            rx="2"
                        />

                        <path
                            d="M8 3v4"
                        />

                        <path
                            d="M16 3v4"
                        />

                        <path
                            d="M4 9h16"
                        />

                    </svg>

                </span>

                <div class="meta-content">

                    <span class="meta-label">
                        Fecha de generación
                    </span>

                    <strong class="meta-value">
                        {{ currentDate }}
                    </strong>

                </div>

            </div>


            <!-- Palabras -->

            <div class="meta-item">

                <span class="meta-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        aria-hidden="true"
                    >

                        <path
                            d="M5 5h14"
                        />

                        <path
                            d="M5 9h14"
                        />

                        <path
                            d="M5 13h9"
                        />

                        <path
                            d="M5 17h7"
                        />

                    </svg>

                </span>

                <div class="meta-content">

                    <span class="meta-label">
                        Extensión del informe
                    </span>

                    <strong class="meta-value">
                        {{ wordCount }} palabras
                    </strong>

                </div>

            </div>


            <!-- Estado -->

            <div class="meta-item status-item">

                <span class="meta-icon status-icon">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.7"
                        aria-hidden="true"
                    >

                        <circle
                            cx="12"
                            cy="12"
                            r="8.5"
                        />

                        <path
                            d="m8.5 12 2.3 2.3 4.7-5"
                        />

                    </svg>

                </span>

                <div class="meta-content">

                    <span class="meta-label">
                        Estado
                    </span>

                    <strong class="meta-status">
                        {{ report
                            ? "Generado correctamente"
                            : "Pendiente de generación"
                        }}
                    </strong>

                </div>

            </div>

        </section>


        <!-- =====================================================
             DOCUMENTO
        ====================================================== -->

        <div class="document-area">

            <Transition
                name="report-fade"
                mode="out-in"
                appear
            >

                <div
                    v-if="report"
                    key="report"
                    class="report-document"
                >

                    <MarkdownRenderer
                        :content="report"
                    />

                </div>


                <div
                    v-else
                    key="empty"
                    class="empty-report"
                >

                    <div class="empty-icon">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                            aria-hidden="true"
                        >

                            <path
                                d="M12 3v18"
                            />

                            <path
                                d="M5 6h14"
                            />

                            <path
                                d="M7 6l-3 6a3 3 0 0 0 6 0L7 6Z"
                            />

                            <path
                                d="M17 6l-3 6a3 3 0 0 0 6 0l-3-6Z"
                            />

                            <path
                                d="M8 21h8"
                            />

                        </svg>

                    </div>

                    <span class="empty-eyebrow">
                        NOVACASE · DOCUMENTO
                    </span>

                    <h3>
                        No hay informe disponible
                    </h3>

                    <p>
                        Cuando NovaCase termine el análisis,
                        el informe jurídico aparecerá aquí.
                    </p>

                </div>

            </Transition>

        </div>

    </section>

</template>


<script setup>

import {
    computed
} from "vue"

import MarkdownRenderer
    from "@/components/common/MarkdownRenderer.vue"


/* =========================================================
   PROPS
========================================================= */

const props = defineProps({

    report: {

        type: String,

        required: true

    }

})


/* =========================================================
   FECHA
========================================================= */

const currentDate = computed(() => {

    return new Intl.DateTimeFormat(

        "es-PE",

        {

            dateStyle: "long",

            timeStyle: "short"

        }

    ).format(

        new Date()

    )

})


/* =========================================================
   CONTADOR DE PALABRAS
========================================================= */

const wordCount = computed(() => {

    if (!props.report) {

        return 0

    }

    return props.report
        .trim()
        .split(/\s+/)
        .length

})


/* =========================================================
   COPIAR
========================================================= */

async function copyReport() {

    try {

        await navigator.clipboard.writeText(
            props.report
        )

        console.info(
            "Informe copiado."
        )

    }

    catch (error) {

        console.error(
            "No fue posible copiar el informe.",
            error
        )

    }

}


/* =========================================================
   IMPRIMIR
========================================================= */

function printReport() {

    window.print()

}


/* =========================================================
   EXPORTAR PDF
========================================================= */

function exportPdf() {

    console.info(
        "Exportación PDF pendiente."
    )

}


/* =========================================================
   EXPORTAR DOCX
========================================================= */

function exportDocx() {

    console.info(
        "Exportación DOCX pendiente."
    )

}

</script>


<style scoped>

/* =========================================================
   NOVACASE — REPORT VIEW
========================================================= */

.report-view {

    display: flex;

    flex-direction: column;

    gap: 26px;

    width: 100%;

    box-sizing: border-box;

    padding: 28px;

    background: #FFFFFF;

    border:
        1px solid
        #DCE5EE;

    border-radius: 14px;

    box-shadow:
        0 8px 24px
        rgba(
            23,
            55,
            94,
            .045
        );

}


/* =========================================================
   CABECERA
========================================================= */

.report-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    gap: 28px;

    padding-bottom: 22px;

    border-bottom:
        1px solid
        #DCE5EE;

}


.report-heading {

    min-width: 0;

}


.report-eyebrow {

    display: flex;

    align-items: center;

    gap: 8px;

    margin-bottom: 9px;

    color: #8A6A36;

    font-size: .55rem;

    font-weight: 800;

    letter-spacing: 1.35px;

}


.eyebrow-line {

    width: 20px;

    height: 1px;

    background: #B08A4C;

}


.report-header h2 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.55rem;

    font-weight: 600;

    line-height: 1.3;

}


.report-header p {

    max-width: 620px;

    margin:
        7px
        0
        0;

    color: #718090;

    font-size: .77rem;

    line-height: 1.65;

}


/* =========================================================
   HERRAMIENTAS
========================================================= */

.report-toolbar {

    display: flex;

    align-items: center;

    justify-content: flex-end;

    gap: 7px;

    flex-wrap: wrap;

    flex-shrink: 0;

}


.toolbar-button {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    gap: 7px;

    min-height: 34px;

    padding:
        0
        11px;

    border:
        1px solid
        #D8E2EC;

    border-radius: 8px;

    background: #FFFFFF;

    color: #53677E;

    font-family: inherit;

    font-size: .63rem;

    font-weight: 750;

    cursor: pointer;

    transition:
        background-color .2s ease,
        border-color .2s ease,
        color .2s ease,
        transform .2s ease,
        box-shadow .2s ease;

}


.button-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 16px;

    height: 16px;

}


.button-icon svg {

    width: 15px;

    height: 15px;

}


.toolbar-button:hover {

    border-color: #B9C9D9;

    background: #F8FAFC;

    color: #315C97;

    transform:
        translateY(-1px);

    box-shadow:
        0 3px 10px
        rgba(
            23,
            55,
            94,
            .06
        );

}


.toolbar-button.primary {

    border-color: #315C97;

    background: #315C97;

    color: #FFFFFF;

}


.toolbar-button.primary:hover {

    border-color: #17375E;

    background: #17375E;

    color: #FFFFFF;

}


/* =========================================================
   METADATOS
========================================================= */

.report-meta {

    display: grid;

    grid-template-columns:
        repeat(
            3,
            minmax(
                0,
                1fr
            )
        );

    gap: 12px;

}


.meta-item {

    display: flex;

    align-items: center;

    gap: 11px;

    min-width: 0;

    padding:
        13px
        15px;

    background: #F8FAFC;

    border:
        1px solid
        #E1E8EF;

    border-radius: 10px;

}


.meta-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 31px;

    height: 31px;

    flex:
        0 0
        31px;

    border:
        1px solid
        #D8E2EC;

    border-radius: 7px;

    background: #FFFFFF;

    color: #6E8298;

}


.meta-icon svg {

    width: 16px;

    height: 16px;

}


.meta-content {

    display: flex;

    flex-direction: column;

    gap: 3px;

    min-width: 0;

}


.meta-label {

    color: #8291A2;

    font-size: .54rem;

    font-weight: 800;

    letter-spacing: .7px;

    text-transform: uppercase;

}


.meta-value {

    overflow: hidden;

    color: #304C6C;

    font-size: .70rem;

    font-weight: 750;

    line-height: 1.4;

    text-overflow: ellipsis;

    white-space: nowrap;

}


.status-icon {

    border-color:
        #D8E7DD;

    background:
        #F7FAF8;

    color: #668B70;

}


.meta-status {

    color: #668B70;

    font-size: .70rem;

    font-weight: 750;

    line-height: 1.4;

}


/* =========================================================
   ÁREA DEL DOCUMENTO
========================================================= */

.document-area {

    width: 100%;

}


.report-document {

    width: 100%;

    box-sizing: border-box;

}


/* =========================================================
   MARKDOWN
========================================================= */

:deep(.markdown-container) {

    margin-top: 0;

    color: #334E68;

}


/* =========================================================
   ESTADO VACÍO
========================================================= */

.empty-report {

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    min-height: 360px;

    padding:
        55px
        20px;

    text-align: center;

    background:
        #FBFCFD;

    border:
        1px dashed
        #CBD8E4;

    border-radius: 11px;

}


.empty-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 54px;

    height: 54px;

    margin-bottom: 16px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .35
        );

    border-radius: 10px;

    background:
        #FCF9F4;

    color: #8A6A36;

}


.empty-icon svg {

    width: 27px;

    height: 27px;

}


.empty-eyebrow {

    margin-bottom: 7px;

    color: #8A6A36;

    font-size: .53rem;

    font-weight: 800;

    letter-spacing: 1.15px;

}


.empty-report h3 {

    margin:
        0
        0
        7px;

    color: #304C6C;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 1.05rem;

    font-weight: 600;

}


.empty-report p {

    max-width: 430px;

    margin: 0;

    color: #8391A1;

    font-size: .72rem;

    line-height: 1.7;

}


/* =========================================================
   ANIMACIÓN
========================================================= */

.report-ready {

    animation:
        reportAppear
        .4s
        ease-out;

}


.report-fade-enter-active {

    transition:
        opacity .3s ease,
        transform .3s ease;

}


.report-fade-enter-from {

    opacity: 0;

    transform:
        translateY(10px);

}


@keyframes reportAppear {

    from {

        opacity: 0;

        transform:
            translateY(10px);

    }

    to {

        opacity: 1;

        transform:
            translateY(0);

    }

}


/* =========================================================
   1000 PX
========================================================= */

@media (max-width: 1000px) {

    .report-header {

        flex-direction: column;

        gap: 18px;

    }


    .report-toolbar {

        justify-content: flex-start;

    }

}


/* =========================================================
   800 PX
========================================================= */

@media (max-width: 800px) {

    .report-view {

        padding: 22px;

    }


    .report-meta {

        grid-template-columns:
            1fr;

    }

}


/* =========================================================
   600 PX
========================================================= */

@media (max-width: 600px) {

    .report-view {

        gap: 20px;

        padding: 18px;

        border-radius: 11px;

    }


    .report-header {

        padding-bottom: 18px;

    }


    .report-header h2 {

        font-size: 1.35rem;

    }


    .report-header p {

        font-size: .72rem;

    }


    .report-toolbar {

        width: 100%;

    }


    .toolbar-button {

        flex: 1;

        min-width: 0;

        padding:
            0
            8px;

    }


    .empty-report {

        min-height: 300px;

        padding:
            40px
            16px;

    }

}


/* =========================================================
   REDUCIR MOVIMIENTO
========================================================= */

@media (
    prefers-reduced-motion: reduce
) {

    .report-ready {

        animation: none;

    }


    .report-fade-enter-active {

        transition: none;

    }


    .toolbar-button {

        transition: none;

    }

}


/* =========================================================
   IMPRESIÓN
========================================================= */

@media print {

    .report-view {

        display: block;

        padding: 0;

        border: none;

        border-radius: 0;

        box-shadow: none;

        background: #FFFFFF;

    }


    .report-toolbar {

        display: none;

    }


    .report-meta {

        grid-template-columns:
            repeat(
                3,
                1fr
            );

        margin-bottom: 25px;

    }


    .meta-item {

        background: #FFFFFF;

    }


    .empty-report {

        border: none;

        background: #FFFFFF;

    }

}

</style>