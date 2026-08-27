<template>

<section

    class="report-view"

    :class="{

        'report-ready': report

    }"

>
    <!-- Encabezado -->

    <header class="report-header">

        <div>

            <h2>

                Informe Jurídico

            </h2>

            <p>

                Generado automáticamente por NovaCase

            </p>

        </div>

        <div class="report-toolbar">

            <button

                class="toolbar-button primary"

                @click="copyReport"

                title="Copiar informe"

            >

                <span>📋</span>

                <span>Copiar</span>

            </button>

            <button

                class="toolbar-button"

                @click="exportPdf"

                title="Exportar PDF"

            >

                <span>📄</span>

                <span>PDF</span>

            </button>

            <button

                class="toolbar-button"

                @click="exportDocx"

                title="Exportar DOCX"

            >

                <span>📝</span>

                <span>DOCX</span>

            </button>

            <button

                class="toolbar-button"

                @click="printReport"

                title="Imprimir"

            >

                <span>🖨</span>

                <span>Imprimir</span>

            </button>

        </div>

    </header>

    <!-- Información -->

    <section class="report-meta">

        <div class="meta-item">

            <span class="meta-label">

                📅 Fecha de generación

            </span>

            <strong class="meta-value">

                {{ currentDate }}

            </strong>

        </div>

        <div class="meta-item">

            <span class="meta-label">

                📄 Palabras

            </span>

            <strong class="meta-value">

                {{ wordCount }}

            </strong>

        </div>

        <div class="meta-item">

            <span class="meta-label">

                ✅ Estado

            </span>

            <strong class="meta-status">

                Generado correctamente

            </strong>

        </div>

    </section>

    <!-- Documento -->

    <Transition

        name="report-fade"

        mode="out-in"

        appear

    >

        <MarkdownRenderer

            v-if="report"

            :content="report"

        />

        <div

            v-else

            class="empty-report"

        >

            <div class="empty-icon">

                ⚖️

            </div>

            <h3>

                No hay informe disponible

            </h3>

            <p>

                Cuando NovaCase termine el análisis,

                el informe jurídico aparecerá aquí.

            </p>

        </div>

    </Transition>

</section>

</template>

<script setup>

import { computed } from "vue"

import MarkdownRenderer from "@/components/common/MarkdownRenderer.vue"

const props = defineProps({

    report: {

        type: String,

        required: true

    }

})

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

const wordCount = computed(() => {

    if (

        !props.report

    ) {

        return 0

    }

    return props.report

        .trim()

        .split(/\s+/)

        .length

})

async function copyReport() {

    try {

        await navigator.clipboard.writeText(

            props.report

        )

        console.info(

            "Informe copiado."

        )

    }

    catch (

        error

    ) {

        console.error(

            "No fue posible copiar el informe.",

            error

        )

    }

}

function printReport() {

    window.print()

}

function exportPdf() {

    console.info(

        "Exportación PDF pendiente."

    )

}

function exportDocx() {

    console.info(

        "Exportación DOCX pendiente."

    )

}

</script>

<style scoped>

.report-view{

    display:flex;

    flex-direction:column;

    gap:28px;

    padding:32px;

    border-radius:24px;

    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    box-shadow: 0 8px 24px rgba(15, 39, 71, 0.06);

}

.report-header{

    display:flex;

    justify-content:space-between;

    align-items:flex-start;

    gap:24px;

    padding-bottom:24px;

    border-bottom:1px solid rgba(255,255,255,.08);

}

.report-header h2{

    margin:0;

    color:#F8FAFC;

    font-size:1.8rem;

    font-weight:700;

}

.report-header p{

    margin-top:8px;

    color:#94A3B8;

    font-size:.95rem;

}

.report-toolbar{

    display:flex;

    gap:12px;

    flex-wrap:wrap;

}

.toolbar-button{

    display:flex;

    align-items:center;

    gap:8px;

    padding:10px 18px;

    border:none;

    border-radius:12px;

    cursor:pointer;

    font-size:.9rem;

    font-weight:600;

    background:#1E293B;

    color:#E2E8F0;

    transition:

        all .25s ease;

}

.toolbar-button:hover{

    background:#334155;

    transform:translateY(-2px);

}

.toolbar-button.primary{

    background:#2563EB;

    color:#FFFFFF;

}

.toolbar-button.primary:hover{

    background:#1D4ED8;

}

.report-meta{

    display:grid;

    grid-template-columns:

        repeat(

            auto-fit,

            minmax(

                220px,

                1fr

            )

        );

    gap:18px;

}

.meta-item{

    display:flex;

    flex-direction:column;

    gap:8px;

    padding:18px;

    border-radius:16px;

    background:rgba(255,255,255,.03);

    border:1px solid rgba(255,255,255,.05);

}

.meta-label{

    color:#94A3B8;

    font-size:.8rem;

    text-transform:uppercase;

    letter-spacing:.6px;

}

.meta-value{

    color:#F8FAFC;

    font-size:1rem;

    font-weight:700;

}

.meta-status{

    color:#22C55E;

    font-weight:700;

}

:deep(.markdown-container){

    margin-top:8px;

}

@media (max-width:900px){

    .report-view{

        padding:22px;

    }

    .report-header{

        flex-direction:column;

    }

    .report-toolbar{

        width:100%;

    }

    .toolbar-button{

        flex:1;

        justify-content:center;

    }

}

@media print{

    .report-toolbar{

        display:none;

    }

    .report-view{

        box-shadow:none;

        border:none;

        padding:0;

        background:#FFFFFF;

    }

}

.report-ready{

    animation:

        reportAppear

        .45s ease;

}

.empty-report{

    display:flex;

    flex-direction:column;

    align-items:center;

    justify-content:center;

    padding:80px 20px;

    text-align:center;

    color:#94A3B8;

    border:2px dashed rgba(255,255,255,.08);

    border-radius:18px;

}

.empty-icon{

    font-size:64px;

    margin-bottom:18px;

}

.empty-report h3{

    color:#F8FAFC;

    margin-bottom:10px;

}

.empty-report p{

    max-width:460px;

    line-height:1.8;

}

.report-fade-enter-active{

    transition:

        opacity .35s ease,

        transform .35s ease;

}

.report-fade-enter-from{

    opacity:0;

    transform:translateY(16px);

}

@keyframes reportAppear{

    from{

        opacity:0;

        transform:translateY(20px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

</style>



