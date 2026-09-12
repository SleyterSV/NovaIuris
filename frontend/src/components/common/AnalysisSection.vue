<template>

<section class="analysis-section">

    <!-- =====================================================
         CABECERA
    ====================================================== -->

    <header class="section-header">

        <div class="section-title">

            <div
                class="section-icon"
                :style="{
                    background: iconBackground
                }"
            >
                {{ icon }}
            </div>

            <div class="section-heading-content">

                <h3>
                    {{ title }}
                </h3>

                <small>
                    {{ subtitle }}
                </small>

            </div>

        </div>

        <span
            class="section-status"
            :class="status"
        >

            <span class="status-dot"></span>

            {{ statusLabel }}

        </span>

    </header>


    <!-- =====================================================
         CONTENIDO
    ====================================================== -->

    <section class="section-body">

        <MarkdownRenderer
            :content="content"
        />

    </section>


    <!-- =====================================================
         PIE DE INFORMACIÓN
    ====================================================== -->

    <footer class="section-footer">

        <div class="footer-left">

            <!-- Confianza -->

            <div class="footer-item">

                <span class="footer-label">
                    Nivel de confianza
                </span>

                <div class="confidence-row">

                    <strong
                        class="confidence-value"
                        :style="{
                            color: confidenceColor
                        }"
                    >
                        {{ confidence }}%
                    </strong>

                    <div class="confidence-track">

                        <div
                            class="confidence-progress"
                            :style="{
                                width: `${confidence}%`,
                                background: confidenceColor
                            }"
                        ></div>

                    </div>

                </div>

            </div>


            <!-- Estado -->

            <div class="footer-item status-item">

                <span class="footer-label">
                    Estado
                </span>

                <strong
                    class="status-value"
                    :class="status"
                >

                    <span class="status-indicator"></span>

                    {{ statusLabel }}

                </strong>

            </div>

        </div>


        <!-- Motor IA -->

        <div class="footer-right">

            <span class="footer-label">
                Motor de análisis
            </span>

            <strong>
                {{ engineName }}
            </strong>

        </div>

    </footer>

</section>

</template>


<script setup>

import { computed } from "vue"

import MarkdownRenderer
    from "@/components/common/MarkdownRenderer.vue"


const props = defineProps({

    title: {
        type: String,
        required: true
    },

    subtitle: {
        type: String,
        default: "Análisis generado por Nova Iuris"
    },

    engineName: {
        type: String,
        default: "Nova Iuris AI"
    },

    icon: {
        type: String,
        default: "📄"
    },

    content: {
        type: String,
        default: ""
    },

    confidence: {
        type: Number,
        default: 90
    },

    status: {
        type: String,
        default: "completed"
    }

})


/* ============================================================
   ESTADO
============================================================ */

const statusLabel = computed(() => {

    switch (props.status) {

        case "processing":
            return "Procesando"

        case "pending":
            return "Pendiente"

        case "error":
            return "Error"

        default:
            return "Completado"

    }

})


/* ============================================================
   COLOR DEL ICONO
============================================================ */

const iconBackground = computed(() => {

    switch (props.status) {

        case "processing":
            return "#EFF6FF"

        case "pending":
            return "#FFFBEB"

        case "error":
            return "#FEF2F2"

        default:
            return "#EFF6FF"

    }

})


/* ============================================================
   COLOR DE CONFIANZA
============================================================ */

const confidenceColor = computed(() => {

    if (props.confidence >= 90) {
        return "#15803D"
    }

    if (props.confidence >= 75) {
        return "#B45309"
    }

    return "#B91C1C"

})

</script>


<style scoped>

/* ============================================================
   VARIABLES VISUALES
============================================================ */

.analysis-section {

    --nova-navy: #0F2747;

    --nova-blue: #2563EB;

    --nova-blue-dark: #1D4ED8;

    --nova-blue-light: #EFF6FF;

    --nova-blue-border: #BFDBFE;

    --nova-text: #334155;

    --nova-muted: #64748B;

    --nova-subtle: #94A3B8;

    --nova-border: #E2E8F0;

    --nova-soft: #F8FAFC;

    --nova-white: #FFFFFF;

    display: flex;

    flex-direction: column;

    min-width: 0;

    overflow: hidden;

    background: var(--nova-white);

    border: 1px solid var(--nova-border);

    border-radius: 20px;

    box-shadow:
        0 4px 14px rgba(15, 39, 71, .045);

    transition:
        transform .25s ease,
        border-color .25s ease,
        box-shadow .25s ease;

}


/* ============================================================
   HOVER PRINCIPAL
============================================================ */

.analysis-section:hover {

    transform: translateY(-3px);

    border-color: var(--nova-blue-border);

    box-shadow:
        0 10px 28px rgba(15, 39, 71, .08);

}


/* ============================================================
   CABECERA
============================================================ */

.section-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    padding: 20px 22px;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #FCFDFF 100%
        );

    border-bottom:
        1px solid var(--nova-border);

}


/* ============================================================
   TÍTULO
============================================================ */

.section-title {

    display: flex;

    align-items: center;

    min-width: 0;

    gap: 14px;

}


.section-heading-content {

    min-width: 0;

}


.section-title h3 {

    margin: 0;

    color: var(--nova-navy);

    font-size: 1.02rem;

    line-height: 1.35;

    font-weight: 750;

    letter-spacing: -.015em;

}


.section-title small {

    display: block;

    margin-top: 4px;

    overflow: hidden;

    color: var(--nova-muted);

    font-size: .78rem;

    line-height: 1.45;

    text-overflow: ellipsis;

    white-space: nowrap;

}


/* ============================================================
   ICONO
============================================================ */

.section-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 46px;

    height: 46px;

    flex-shrink: 0;

    border:
        1px solid var(--nova-blue-border);

    border-radius: 13px;

    color: var(--nova-blue);

    font-size: 1.15rem;

    box-shadow:
        0 3px 10px rgba(37, 99, 235, .07);

    transition:
        transform .25s ease,
        box-shadow .25s ease;

}


.analysis-section:hover .section-icon {

    transform: translateY(-1px);

    box-shadow:
        0 6px 14px rgba(37, 99, 235, .12);

}


/* ============================================================
   ESTADO SUPERIOR
============================================================ */

.section-status {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    flex-shrink: 0;

    padding: 6px 10px;

    border-radius: 999px;

    font-size: .65rem;

    font-weight: 800;

    letter-spacing: .055em;

    text-transform: uppercase;

}


/* COMPLETADO */

.section-status.completed {

    color: #15803D;

    background: #F0FDF4;

    border:
        1px solid #BBF7D0;

}


/* PROCESANDO */

.section-status.processing {

    color: var(--nova-blue);

    background: var(--nova-blue-light);

    border:
        1px solid var(--nova-blue-border);

}


/* PENDIENTE */

.section-status.pending {

    color: #B45309;

    background: #FFFBEB;

    border:
        1px solid #FDE68A;

}


/* ERROR */

.section-status.error {

    color: #B91C1C;

    background: #FEF2F2;

    border:
        1px solid #FECACA;

}


/* PUNTO */

.status-dot {

    width: 6px;

    height: 6px;

    flex-shrink: 0;

    border-radius: 50%;

    background: currentColor;

}


/* ============================================================
   CUERPO
============================================================ */

.section-body {

    min-height: 120px;

    padding: 24px;

    background: var(--nova-white);

}


/* Markdown compartido */

.section-body :deep(.markdown-body) {

    color: var(--nova-text);

}


.section-body :deep(p) {

    color: var(--nova-text);

    line-height: 1.75;

}


.section-body :deep(h1),
.section-body :deep(h2),
.section-body :deep(h3),
.section-body :deep(h4) {

    color: var(--nova-navy);

}


/* ============================================================
   FOOTER
============================================================ */

.section-footer {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 24px;

    padding: 16px 22px;

    background: var(--nova-soft);

    border-top:
        1px solid var(--nova-border);

}


/* ============================================================
   BLOQUE IZQUIERDO
============================================================ */

.footer-left {

    display: flex;

    align-items: center;

    gap: 30px;

    min-width: 0;

}


.footer-item,
.footer-right {

    display: flex;

    flex-direction: column;

    gap: 5px;

    min-width: 0;

}


/* ============================================================
   LABELS
============================================================ */

.footer-label {

    color: var(--nova-subtle);

    font-size: .62rem;

    font-weight: 800;

    letter-spacing: .075em;

    line-height: 1.2;

    text-transform: uppercase;

}


/* ============================================================
   CONFIANZA
============================================================ */

.confidence-row {

    display: flex;

    align-items: center;

    gap: 10px;

}


.confidence-value {

    min-width: 38px;

    font-size: .9rem;

    font-weight: 800;

}


.confidence-track {

    width: 72px;

    height: 5px;

    overflow: hidden;

    border-radius: 999px;

    background: #E2E8F0;

}


.confidence-progress {

    height: 100%;

    border-radius: inherit;

    transition:
        width .45s ease;

}


/* ============================================================
   ESTADO INFERIOR
============================================================ */

.status-value {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    font-size: .82rem;

    font-weight: 750;

}


.status-value.completed {

    color: #15803D;

}


.status-value.processing {

    color: var(--nova-blue);

}


.status-value.pending {

    color: #B45309;

}


.status-value.error {

    color: #B91C1C;

}


.status-indicator {

    width: 6px;

    height: 6px;

    border-radius: 50%;

    background: currentColor;

}


/* ============================================================
   MOTOR IA
============================================================ */

.footer-right {

    align-items: flex-end;

    text-align: right;

}


.footer-right strong {

    color: var(--nova-navy);

    font-size: .78rem;

    font-weight: 750;

}


/* ============================================================
   RESPONSIVE — 992PX
============================================================ */

@media (max-width: 992px) {

    .section-footer {

        align-items: flex-start;

        flex-direction: column;

        gap: 18px;

    }


    .footer-left {

        width: 100%;

        justify-content: flex-start;

    }


    .footer-right {

        align-items: flex-start;

        text-align: left;

    }

}


/* ============================================================
   RESPONSIVE — 768PX
============================================================ */

@media (max-width: 768px) {

    .section-header {

        align-items: flex-start;

        flex-direction: column;

        padding: 18px 20px;

    }


    .section-title {

        width: 100%;

    }


    .section-status {

        align-self: flex-start;

    }


    .section-body {

        padding: 20px;

    }


    .section-footer {

        padding: 18px 20px;

    }


    .footer-left {

        align-items: flex-start;

        flex-direction: column;

        gap: 16px;

    }

}


/* ============================================================
   RESPONSIVE — 576PX
============================================================ */

@media (max-width: 576px) {

    .analysis-section {

        border-radius: 17px;

    }


    .section-header {

        padding: 16px 17px;

    }


    .section-icon {

        width: 42px;

        height: 42px;

        border-radius: 12px;

        font-size: 1.05rem;

    }


    .section-title {

        gap: 12px;

    }


    .section-title h3 {

        font-size: .95rem;

    }


    .section-title small {

        max-width: 210px;

        font-size: .74rem;

    }


    .section-body {

        min-height: 100px;

        padding: 17px;

    }


    .section-footer {

        padding: 16px 17px;

    }


    .confidence-track {

        width: 60px;

    }


    .footer-right strong {

        font-size: .75rem;

    }

}


/* ============================================================
   ACCESIBILIDAD
============================================================ */

@media (prefers-reduced-motion: reduce) {

    .analysis-section,
    .section-icon,
    .confidence-progress {

        transition: none;

    }

}

</style>