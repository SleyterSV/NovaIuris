<template>

<section class="analysis-section">

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

            <div>

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

            {{ statusLabel }}

        </span>

    </header>

    <section class="section-body">

        <MarkdownRenderer

            :content="content"

        />

    </section>

    <footer class="section-footer">

        <div class="footer-left">

            <div class="confidence-block">

                <span class="footer-label">

                    Nivel de confianza

                </span>

                <strong

                    class="confidence-value"

                    :style="{

                        color: confidenceColor

                    }"

                >

                    {{ confidence }}%

                </strong>

            </div>

            <div class="status-block">

                <span class="footer-label">

                    Estado

                </span>

                <strong

                    class="status-value"

                    :class="status"

                >

                    {{ statusLabel }}

                </strong>

            </div>

        </div>

        <div class="footer-right">

            <span class="footer-label">

                Motor IA

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

import MarkdownRenderer from "@/components/common/MarkdownRenderer.vue"

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

const statusLabel = computed(() => {

    switch(props.status){

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

const iconBackground = computed(() => {
    switch (props.status) {
        case "processing":
            return "#EFF6FF"

        case "pending":
            return "#FFFBEB"

        case "error":
            return "#FEF2F2"

        default:
            return "#F0FDF4"
    }
})

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

.analysis-section {
    display: flex;
    flex-direction: column;

    background: #FFFFFF;

    border: 1px solid #E2E8F0;

    border-radius: 22px;

    overflow: hidden;

    box-shadow:
        0 8px 24px rgba(15, 39, 71, 0.06);

    transition:
        all .28s ease;
}

.analysis-section:hover {
    transform: translateY(-3px);

    border-color: #BFDBFE;

    box-shadow:
        0 12px 30px rgba(15, 39, 71, 0.08);
}

.section-header{

    display:flex;

    justify-content:space-between;

    align-items:center;

    gap:18px;

    padding:22px 24px;

    border-bottom: 1px solid #E2E8F0;

}

.section-title{

    display:flex;

    align-items:center;

    gap:16px;

}

.section-icon{

    width:56px;

    height:56px;

    border-radius:16px;

    display:flex;

    justify-content:center;

    align-items:center;

    font-size:1.45rem;

    flex-shrink:0;

}

.section-title h3 {
    margin: 0;

    color: #0F2747;

    font-size: 1.1rem;

    font-weight: 700;
}

.section-title small {
    display: block;

    margin-top: 4px;

    color: #64748B;

    font-size: .85rem;
}

.section-status{

    padding:8px 14px;

    border-radius:999px;

    font-size:.75rem;

    font-weight:700;

    text-transform:uppercase;

    letter-spacing:.5px;

}

.section-status.completed {
    background: #F0FDF4;
    color: #15803D;
    border: 1px solid #BBF7D0;
}

.section-status.processing {
    background: #EFF6FF;
    color: #2563EB;
    border: 1px solid #BFDBFE;
}

.section-status.pending {
    background: #FFFBEB;
    color: #B45309;
    border: 1px solid #FDE68A;
}

.section-status.error {
    background: #FEF2F2;
    color: #B91C1C;
    border: 1px solid #FECACA;
}

.section-body {
    padding: 26px;

    background: #FFFFFF;
}

.section-footer{

    display:flex;

    justify-content:space-between;

    align-items:center;

    gap:24px;

    padding:18px 24px;

    border-top: 1px solid #E2E8F0;

    background: #F8FAFC;

}

.footer-left{

    display:flex;

    gap:32px;

    align-items:center;

}

.confidence-block,

.status-block,

.footer-right{

    display:flex;

    flex-direction:column;

    gap:4px;

}

.footer-label {
    font-size: .72rem;

    color: #64748B;

    text-transform: uppercase;

    letter-spacing: .5px;
}

.confidence-value{

    font-size:1rem;

    font-weight:700;

}

.status-value{

    font-size:.95rem;

    font-weight:700;

}

.status-value.completed {
    color: #15803D;
}

.status-value.processing {
    color: #2563EB;
}

.status-value.pending {
    color: #B45309;
}

.status-value.error {
    color: #B91C1C;
}

.footer-right strong {
    color: #0F2747;

    font-weight: 700;
}

/* =====================================================
   RESPONSIVE
===================================================== */

@media (max-width:1200px){

    .section-header{

        align-items:flex-start;

    }

}

@media (max-width:992px){

    .section-footer{

        flex-direction:column;

        align-items:flex-start;

        gap:20px;

    }

    .footer-left{

        width:100%;

        justify-content:space-between;

    }

}

@media (max-width:768px){

    .analysis-section{

        border-radius:18px;

    }

    .section-header{

        flex-direction:column;

        align-items:flex-start;

        gap:18px;

        padding:20px;

    }

    .section-title{

        width:100%;

    }

    .section-status{

        align-self:flex-start;

    }

    .section-body{

        padding:20px;

    }

    .section-footer{

        padding:20px;

    }

    .footer-left{

        flex-direction:column;

        align-items:flex-start;

        gap:18px;

    }

}

@media (max-width:576px){

    .analysis-section{

        border-radius:16px;

    }

    .section-header{

        padding:18px;

    }

    .section-icon{

        width:48px;

        height:48px;

        font-size:1.2rem;

        border-radius:14px;

    }

    .section-title h3{

        font-size:1rem;

    }

    .section-title small{

        font-size:.8rem;

    }

    .section-body{

        padding:18px;

    }

    .section-footer{

        padding:18px;

    }

    .confidence-value,

    .status-value,

    .footer-right strong{

        font-size:.9rem;

    }

}

/* =====================================================
   ANIMACIONES
===================================================== */

.analysis-section{

    animation:

        sectionFadeIn

        .45s ease;

}

.section-header{

    animation:

        headerSlideDown

        .45s ease;

}

.section-body{

    animation:

        bodyFadeIn

        .55s ease;

}

.section-footer{

    animation:

        footerFadeUp

        .65s ease;

}

.section-icon{

    transition:

        transform .25s ease,

        box-shadow .25s ease;

}

.analysis-section:hover .section-icon{

    transform:scale(1.08);

    box-shadow:

        0 0 18px rgba(37,99,235,.28);

}

.section-status{

    transition:

        transform .25s ease,

        opacity .25s ease;

}

.analysis-section:hover .section-status{

    transform:scale(1.05);

}

.confidence-value{

    transition:

        color .25s ease,

        transform .25s ease;

}

.analysis-section:hover .confidence-value{

    transform:scale(1.08);

}

@keyframes sectionFadeIn{

    from{

        opacity:0;

        transform:translateY(20px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

@keyframes headerSlideDown{

    from{

        opacity:0;

        transform:translateY(-12px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}

@keyframes bodyFadeIn{

    from{

        opacity:0;

    }

    to{

        opacity:1;

    }

}

@keyframes footerFadeUp{

    from{

        opacity:0;

        transform:translateY(10px);

    }

    to{

        opacity:1;

        transform:translateY(0);

    }

}


</style>


