<template>

    <section class="court-report">

        <!-- =====================================================
             ENCABEZADO
        ====================================================== -->

        <header class="report-header">

            <div class="report-heading">

                <span class="report-eyebrow">
                    MYKE · NOVACOURT
                </span>

                <h2>
                    Informe de simulación jurídica
                </h2>

                <div class="title-accent"></div>

                <p>
                    Documento consolidado del análisis adversarial, evaluación probatoria y decisión simulada del caso.
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
                    {{ content ? 'Informe disponible' : status }}
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
                        INFORME DE SIMULACIÓN JURÍDICA
                    </span>

                    <span class="document-line"></span>

                </div>

                <h3 v-if="displayCaseTitle" class="case-title">{{ displayCaseTitle }}</h3>

            </div>

            <div class="report-toolbar" role="group" aria-label="Acciones del informe">
                <button type="button" class="report-action" :disabled="actionBusy" @click="copyReport">
                    <svg v-if="!copied" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="8" y="8" width="11" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h2"/></svg><span v-else aria-hidden="true">✓</span>{{ copied ? 'Copiado' : 'Copiar informe' }}
                </button>
                <button type="button" class="report-action" :disabled="actionBusy" @click="printReport">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M6 9V3h12v6M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><path d="M6 15h12v6H6z"/></svg>Imprimir
                </button>
                <button type="button" class="report-action primary" :disabled="!caseId || !taskId || actionBusy" @click="saveFile('pdf')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 3v12m-4-4 4 4 4-4M4 17v4h16v-4"/></svg>{{ exportBusy === 'pdf' ? 'Generando PDF…' : 'Descargar PDF' }}
                </button>
                <button type="button" class="report-action" :disabled="!caseId || !taskId || actionBusy" @click="saveFile('docx')">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 3v12m-4-4 4 4 4-4M4 17v4h16v-4"/></svg>{{ exportBusy === 'docx' ? 'Generando DOCX…' : 'Descargar DOCX' }}
                </button>
            </div>
            <p v-if="actionMessage" class="report-action-message" role="alert">{{ actionMessage }}</p>


            <!-- DOCUMENTO -->

            <article class="report-document">

                <MarkdownRenderer
                    :content="content"
                    :citations="usedCitations"
                    :sources="usedSources"
                    :case-id="caseId"
                    citation-numbers-only
                    @select-citation="openCitation"
                />
                <section v-if="referenceGroups.length" class="report-references" aria-labelledby="report-references-title">
                    <h3 id="report-references-title">Fuentes utilizadas</h3>
                    <div v-for="group in referenceGroups" :key="group.label" class="reference-group">
                        <h4>{{ group.label }}</h4>
                        <ol><li v-for="entry in group.items" :key="entry.source.source_id">
                            <span class="reference-number">{{ entry.citation.label.slice(1, -1) }}</span>
                            <span class="reference-copy"><strong>{{ sourceTitle(entry.source) }}</strong><small>{{ sourceDetails(entry.source) }}</small></span>
                            <button type="button" class="reference-action" @click="selectedSource = entry.source">
                                {{ entry.group === 'DOCUMENTOS DEL CASO' ? 'Ver documento' : 'Ver fuente' }} <span aria-hidden="true">↗</span>
                            </button>
                        </li></ol>
                    </div>
                    <p v-if="referenceGroups.some(group => group.label === 'FUENTES JURÍDICAS')" class="legal-source-note">
                        Las fuentes jurídicas sustentan el análisis normativo y no constituyen prueba de los hechos del caso.
                    </p>
                </section>

            </article>
        </div>


        <!-- =====================================================
             ESTADO VACÍO
        ====================================================== -->

        <div
            v-else
            class="report-empty"
        >

            <div class="empty-mark" aria-hidden="true">
                MYKE
            </div>

            <div class="empty-content">

                <span class="empty-label">
                    NOVACOURT · INFORME JUDICIAL
                </span>

                <h3>
                    Simulación no disponible
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
                    Documento consolidado de simulación jurídica.
                </span>

            </div>


            <div class="footer-badge">

                <span class="badge-dot"></span>

                MYKE · NOVACOURT

            </div>

        </footer>

    </section>
    <SourceModal :source="selectedSource" :case-id="caseId" @close="selectedSource = null" />

</template>


<script setup>

import { computed, onBeforeUnmount, ref } from 'vue'
import MarkdownRenderer from "../common/MarkdownRenderer.vue"
import SourceModal from '../common/SourceModal.vue'
import { downloadCourtDocx, downloadCourtPdf } from '@/services/caseExport.js'
import { normalizeSources, resolveCitations } from '@/utils/sourceContract.js'


const props = defineProps({

    content: {
        type: String,
        default: ""
    },
    citations: { type: Array, default: () => [] },
    sources: { type: Array, default: () => [] },
    caseId: { type: String, default: null },
    taskId: { type: String, default: null },
    caseTitle: { type: String, default: '' },

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
const selectedSource = ref(null)
const copied = ref(false)
const exportBusy = ref('')
const actionMessage = ref('')
const actionBusy = computed(() => Boolean(exportBusy.value))
const displayCaseTitle = computed(() => cleanDisplay(props.caseTitle))
const normalizedSources = computed(() => normalizeSources(props.sources, props.caseId))
const resolvedCitations = computed(() => resolveCitations(props.citations, normalizedSources.value, props.caseId).citations)
const usedCitations = computed(() => resolvedCitations.value.filter(item => item.label && props.content.includes(item.label)))
const usedSources = computed(() => normalizedSources.value.filter(source => usedCitations.value.some(item => item.source_id === source.source_id)))
const referenceGroups = computed(() => {
    const groups = [
        { label:'DOCUMENTOS DEL CASO', items:[] },
        { label:'FUENTES JURÍDICAS', items:[] }
    ]
    const seen = new Set()
    for (const citation of usedCitations.value) {
        if (seen.has(citation.source_id)) continue
        const source = usedSources.value.find(item => item.source_id === citation.source_id)
        if (!source) continue
        seen.add(citation.source_id)
        const group = ['case', 'private_case'].includes(source.source_scope) ? groups[0] : groups[1]
        group.items.push({ citation, source, group:group.label })
    }
    return groups.filter(group => group.items.length)
})
let copyReset, printReset
onBeforeUnmount(() => { clearTimeout(copyReset); clearTimeout(printReset); window.removeEventListener('afterprint', finishPrint) })
const openCitation = citation => { selectedSource.value = usedSources.value.find(source => source.source_id === citation.source_id) || null }
function sourceTitle(source) { return cleanDisplay(source.display_title || source.title || 'Fuente utilizada').replace(/^\d+[_\s-]+/, '').replace(/\.[a-z0-9]{2,5}$/i, '').replace(/_/g, ' ') }
function sourceDetails(source) {
    const metadata = [source.source_scope === 'case' || source.source_scope === 'private_case'
        ? 'Documento aportado' : source.court || source.issuer || 'Fuente jurídica']
    if (source.unit_type === 'foundation' && source.unit_number) metadata.push(`Fundamento ${source.unit_number}`)
    else if (source.unit_type === 'article' && source.unit_number) metadata.push(`Artículo ${source.unit_number}`)
    if (source.page_start) metadata.push(`pág. ${source.page_start}${source.page_end && source.page_end !== source.page_start ? `–${source.page_end}` : ''}`)
    return metadata.join(' · ')
}
async function copyReport() {
    actionMessage.value = ''
    if (!props.content || !navigator.clipboard?.writeText) { actionMessage.value = 'No fue posible copiar el informe en este navegador.'; return }
    try {
        const copiedSections = referenceGroups.value.map(group => `${group.label}\n${group.items.map(entry =>
            `${entry.citation.label} ${sourceTitle(entry.source)}${sourceDetails(entry.source) ? ` · ${sourceDetails(entry.source)}` : ''}`
        ).join('\n')}`).join('\n\n')
        const reportText = ['INFORME DE SIMULACIÓN JURÍDICA', displayCaseTitle.value,
            'Simulación jurídica. No constituye una resolución judicial real ni sustituye la evaluación profesional.',
            props.content, 'FUENTES UTILIZADAS', copiedSections].filter(Boolean).join('\n\n')
        await navigator.clipboard.writeText(cleanReportText(reportText))
        copied.value = true
        clearTimeout(copyReset)
        copyReset = setTimeout(() => { copied.value = false }, 1800)
    } catch { copied.value = false; actionMessage.value = 'No fue posible copiar el informe. Inténtalo nuevamente.' }
}
function finishPrint() { document.body.classList.remove('novacourt-report-print') }
function printReport() {
    actionMessage.value = ''
    document.body.classList.add('novacourt-report-print')
    window.addEventListener('afterprint', finishPrint, { once: true })
    try { window.print(); printReset = setTimeout(finishPrint, 30000) }
    catch { finishPrint(); actionMessage.value = 'No fue posible abrir la impresión del informe.' }
}
async function saveFile(format) {
    if (!props.caseId || !props.taskId || actionBusy.value) return
    actionMessage.value = ''
    exportBusy.value = format
    try {
        const blob = format === 'pdf'
            ? await downloadCourtPdf(props.caseId, props.taskId)
            : await downloadCourtDocx(props.caseId, props.taskId)
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `MYKE_NovaCourt_${safeFilename(displayCaseTitle.value) || 'Informe_Simulacion_Juridica'}.${format}`
        document.body.appendChild(link)
        link.click()
        link.remove()
        setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch {
        actionMessage.value = format === 'pdf'
            ? 'No fue posible generar el PDF. Inténtalo nuevamente.'
            : 'No fue posible generar el DOCX. Inténtalo nuevamente.'
    } finally { exportBusy.value = '' }
}
function cleanDisplay(value) {
    return String(value || '').replace(/\b(?:SRC|FACT|ISSUE)-[A-Z0-9_-]+\b/gi, '')
        .replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, '')
        .replace(/\s+/g, ' ').trim()
}
function safeFilename(value) {
    return cleanDisplay(value).normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
        .replace(/[^A-Za-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 60)
}
function cleanReportText(value) {
    return String(value || '').split(/\r?\n/).map(line => line
        .replace(/^\s*#{1,6}\s*/, '').replace(/^\s*[-*]\s+/, '• ')
        .replace(/\*\*(.*?)\*\*/g, '$1').replace(/`([^`]*)`/g, '$1')
        .replace(/\b(?:SRC|FACT|ISSUE)-[A-Z0-9_-]+\b/gi, '')
        .replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, '')
    ).join('\n').trim()
}

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

.report-toolbar{display:flex;justify-content:flex-end;flex-wrap:wrap;gap:8px;margin:18px 0 0}
.report-action svg{width:15px;height:15px;flex:none}
.report-action{display:inline-flex;align-items:center;justify-content:center;gap:7px;min-height:36px;padding:8px 12px;border:1px solid #cfdae4;border-radius:8px;background:#fff;color:#244a6a;font:600 .77rem/1.2 system-ui,sans-serif;cursor:pointer;transition:background .16s,border-color .16s}
.report-action:hover:not(:disabled){background:#f1f5f8;border-color:#aebfd0}
.report-action.primary{border-color:#17375e;background:#17375e;color:#fff}
.report-action.primary:hover:not(:disabled){background:#244a72}
.report-action:disabled{cursor:not-allowed;opacity:.55}
.report-action:focus-visible{outline:2px solid #b08a4c;outline-offset:2px}
.report-action-message{margin:10px 0 0;padding:9px 12px;border-left:2px solid #b08a4c;background:#fbf8f0;color:#634f2b;font-size:.82rem}
.case-title{margin:12px 0 0;color:#17375e;font:600 1.05rem/1.4 Georgia,'Times New Roman',serif;overflow-wrap:anywhere}
.report-toolbar~.report-document{margin-top:22px}
.report-document :deep(.citation-inline){display:inline-flex;align-items:center;justify-content:center;vertical-align:baseline;min-width:22px;height:22px;padding:0 6px;border:0;border-radius:6px;background:#102b4c;color:#fff;font-size:.72rem;font-weight:750;line-height:1;white-space:nowrap;cursor:pointer}
.report-document :deep(.citation-inline:hover){background:#1d4168}
.report-document :deep(.citation-inline:focus-visible){outline:2px solid #b08a4c;outline-offset:2px}
.report-references{margin-top:28px;padding-top:22px;border-top:1px solid #dce5ee}
.report-references h3{margin:0 0 18px;color:#17375e;font:600 1.25rem/1.35 Georgia,'Times New Roman',serif}
.reference-group+.reference-group{margin-top:22px}
.reference-group h4{margin:0 0 9px;color:#92713c;font-size:.68rem;font-weight:750;letter-spacing:.09em}
.reference-group ol{display:grid;margin:0;padding:0;border-top:1px solid #e5ebf0;list-style:none}
.reference-group li{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:12px;padding:12px 4px;border-bottom:1px solid #e8edf1}
.reference-number{display:inline-flex;align-items:center;justify-content:center;min-width:22px;height:22px;padding:0 6px;border-radius:6px;background:#102b4c;color:#fff;font-size:.72rem;font-weight:750;line-height:1;white-space:nowrap}
.reference-copy{display:grid;min-width:0;gap:3px}.reference-copy strong{color:#314a62;font-size:.85rem;font-weight:650;overflow-wrap:anywhere}.reference-copy small{color:#758495;font-size:.73rem}
.reference-action{display:inline-flex;align-items:center;gap:5px;padding:5px 0;border:0;background:none;color:#315c83;font-size:.77rem;font-weight:650;white-space:nowrap;cursor:pointer}
.reference-action:hover{text-decoration:underline;text-underline-offset:3px}.reference-action:focus-visible{outline:2px solid #b08a4c;outline-offset:3px;border-radius:3px}
.legal-source-note{margin:10px 0 0;color:#718092;font-size:.76rem;line-height:1.55}
@media(max-width:760px){.report-toolbar{justify-content:flex-start}.report-action{flex:1 1 auto}}
@media print{
  :global(body.novacourt-report-print *){visibility:hidden!important}
  :global(body.novacourt-report-print .court-report),:global(body.novacourt-report-print .court-report *){visibility:visible!important}
  :global(body.novacourt-report-print .court-report){position:absolute!important;top:0!important;left:0!important;width:100%!important;margin:0!important;padding:0!important;border:0!important;background:#fff!important;box-shadow:none!important}
  .report-toolbar,.report-action-message,.report-status,.report-footer{display:none!important}
  .reference-action{display:none!important}.reference-number{background:#fff!important;color:#17375e!important;border:1px solid #d7e2ec!important}
  .reference-group li{grid-template-columns:auto minmax(0,1fr)!important}
  .report-header{border:0;padding-bottom:10pt}.report-content{padding:0!important;border:0!important;box-shadow:none!important}
  .report-document{max-width:none!important}.report-document :deep(.citation-inline){background:#f1f5f8!important;color:#17375e!important}
}

</style>
