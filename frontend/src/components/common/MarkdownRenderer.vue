<template>

    <div class="markdown-container">

        <article
            class="markdown-body"
            @click="handleCitationClick"
            v-html="renderedMarkdown"
        ></article>

    </div>

</template>


<script setup>

import {
    computed
} from "vue"

import { normalizeRenderableContent, EMPTY_CONTENT } from "@/utils/content.js"
import MarkdownIt from "markdown-it"

import hljs from "highlight.js"
import { resolveCitations } from "@/utils/sourceContract.js"


/* ============================================================
   PROPS
============================================================ */

const props = defineProps({

    content: {

        type: [String, Object, Array, Number],

        default: ""

    },

    citations: { type: Array, default: () => [] },
    sources: { type: Array, default: () => [] },
    caseId: { type: String, default: null }

})
const emit = defineEmits(["select-citation"])
const resolved = computed(() => resolveCitations(props.citations, props.sources, props.caseId))
const citationByLabel = computed(() => new Map(resolved.value.citations.map(item => [item.label, item])))


/* ============================================================
   MARKDOWN ENGINE
============================================================ */

const md = new MarkdownIt({

    html: false,

    xhtmlOut: false,

    breaks: true,

    linkify: true,

    typographer: true,

    highlight(str, lang){

        if(
            lang &&
            hljs.getLanguage(lang)
        ){

            try{

                const highlighted = hljs.highlight(
                    str,
                    {
                        language: lang,
                        ignoreIllegals: true
                    }
                ).value

                return `
                    <pre class="hljs">
                        <code>${highlighted}</code>
                    </pre>
                `

            }

            catch{

                /* Fallback below */

            }

        }

        return `
            <pre class="hljs">
                <code>${md.utils.escapeHtml(str)}</code>
            </pre>
        `

    }

})


/* ============================================================
   TIPOGRAFÍA MARKDOWN
============================================================ */

md.set({

    quotes: "“”‘’"

})


/* ============================================================
   ENLACES EXTERNOS
============================================================ */

const defaultLinkOpen =
    md.renderer.rules.link_open ||
    function(
        tokens,
        idx,
        options,
        env,
        self
    ){

        return self.renderToken(
            tokens,
            idx,
            options
        )

    }


md.renderer.rules.link_open = (
    tokens,
    idx,
    options,
    env,
    self
) => {

    tokens[idx].attrSet(
        "target",
        "_blank"
    )

    tokens[idx].attrSet(
        "rel",
        "noopener noreferrer"
    )

    return defaultLinkOpen(
        tokens,
        idx,
        options,
        env,
        self
    )

}

md.renderer.rules.text = (tokens, idx) => {
    const text = tokens[idx].content
    const pattern = /\[\d+\]/g
    let output = ""
    let cursor = 0
    for (const match of text.matchAll(pattern)) {
        output += md.utils.escapeHtml(text.slice(cursor, match.index))
        const citation = citationByLabel.value.get(match[0])
        if (!citation) output += md.utils.escapeHtml(match[0])
        else {
            const citationId = md.utils.escapeHtml(citation.citation_id)
            output += `<button type="button" class="citation-inline" data-citation-id="${citationId}" aria-label="Abrir fuente ${match[0]}">${match[0]}</button>`
        }
        cursor = match.index + match[0].length
    }
    return output + md.utils.escapeHtml(text.slice(cursor))
}


/* ============================================================
   RENDER
============================================================ */

const renderedMarkdown = computed(() => {

    return md.render(
        normalizeRenderableContent(props.content) || EMPTY_CONTENT
    )

})

function handleCitationClick(event) {
    const button = event.target?.closest?.("button[data-citation-id]")
    if (!button) return
    const citation = resolved.value.citations.find(item => item.citation_id === button.dataset.citationId)
    if (citation) emit("select-citation", citation)
}

</script>


<style scoped>

/* ============================================================
   NOVA MARKDOWN RENDERER
   Sistema visual institucional Nova Iuris
============================================================ */

.markdown-container{

    width:100%;

    min-width:0;

}


/* ============================================================
   CUERPO PRINCIPAL
============================================================ */

.markdown-body{

    width:100%;

    min-width:0;

    color:#334155;

    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    font-size:.95rem;

    font-weight:400;

    line-height:1.8;

    letter-spacing:.002em;

    overflow-wrap:anywhere;

}


/* ============================================================
   TÍTULOS
============================================================ */

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6){

    color:#0F2747;

    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    line-height:1.35;

    letter-spacing:-.02em;

}


/* ============================================================
   H1
============================================================ */

.markdown-body :deep(h1){

    position:relative;

    margin:30px 0 18px;

    padding-bottom:14px;

    font-size:1.65rem;

    font-weight:750;

}


.markdown-body :deep(h1::after){

    content:"";

    position:absolute;

    left:0;

    bottom:0;

    width:42px;

    height:3px;

    border-radius:999px;

    background:#2563EB;

}


/* ============================================================
   H2
============================================================ */

.markdown-body :deep(h2){

    margin:28px 0 15px;

    padding-bottom:10px;

    border-bottom:1px solid #E2E8F0;

    font-size:1.35rem;

    font-weight:700;

}


/* ============================================================
   H3
============================================================ */

.markdown-body :deep(h3){

    margin:24px 0 12px;

    font-size:1.15rem;

    font-weight:700;

}


/* ============================================================
   H4
============================================================ */

.markdown-body :deep(h4){

    margin:21px 0 10px;

    font-size:1.02rem;

    font-weight:700;

}


/* ============================================================
   H5 / H6
============================================================ */

.markdown-body :deep(h5),
.markdown-body :deep(h6){

    margin:18px 0 9px;

    font-size:.94rem;

    font-weight:700;

}


/* ============================================================
   PRIMER TÍTULO
============================================================ */

.markdown-body :deep(h1:first-child),
.markdown-body :deep(h2:first-child),
.markdown-body :deep(h3:first-child){

    margin-top:0;

}


/* ============================================================
   PÁRRAFOS
============================================================ */

.markdown-body :deep(p){

    margin:0 0 16px;

    color:#475569;

}


.markdown-body :deep(p:last-child){

    margin-bottom:0;

}


/* ============================================================
   TEXTO FUERTE
============================================================ */

.markdown-body :deep(strong){

    color:#17375E;

    font-weight:700;

}


/* ============================================================
   TEXTO EN CURSIVA
============================================================ */

.markdown-body :deep(em){

    color:#475569;

}


/* ============================================================
   LISTAS
============================================================ */

.markdown-body :deep(ul),
.markdown-body :deep(ol){

    margin:0 0 19px;

    padding-left:25px;

}


.markdown-body :deep(ul){

    list-style-type:disc;

}


.markdown-body :deep(ol){

    list-style-type:decimal;

}


.markdown-body :deep(li){

    margin-bottom:8px;

    padding-left:3px;

    color:#475569;

    line-height:1.75;

}


.markdown-body :deep(li:last-child){

    margin-bottom:0;

}


.markdown-body :deep(li::marker){

    color:#2563EB;

    font-weight:700;

}


/* ============================================================
   ENLACES
============================================================ */

.markdown-body :deep(a){

    color:#2563EB;

    font-weight:600;

    text-decoration:none;

    border-bottom:1px solid
        rgba(
            37,
            99,
            235,
            .25
        );

    transition:
        color .2s ease,
        border-color .2s ease;

}


.markdown-body :deep(a:hover){

    color:#0F2747;

    border-bottom-color:#2563EB;

}


/* ============================================================
   CITAS JURÍDICAS
============================================================ */

.markdown-body :deep(blockquote){

    position:relative;

    margin:22px 0;

    padding:17px 20px 17px 22px;

    background:#F8FAFC;

    border:1px solid #E2E8F0;

    border-left:3px solid #2563EB;

    border-radius:0 12px 12px 0;

    color:#475569;

}


.markdown-body :deep(blockquote::before){

    content:"";

    position:absolute;

    top:0;

    left:-3px;

    width:3px;

    height:35%;

    border-radius:0 0 4px 4px;

    background:#1D4ED8;

}


.markdown-body :deep(blockquote p){

    margin:0;

    color:#475569;

}


.markdown-body :deep(blockquote p + p){

    margin-top:12px;

}


/* ============================================================
   SEPARADORES
============================================================ */

.markdown-body :deep(hr){

    height:1px;

    margin:28px 0;

    border:0;

    background:#E2E8F0;

}


/* ============================================================
   CÓDIGO INLINE
============================================================ */

.markdown-body :deep(:not(pre) > code){

    display:inline-block;

    padding:2px 6px;

    color:#17375E;

    background:#F1F5F9;

    border:1px solid #E2E8F0;

    border-radius:6px;

    font-family:
        "JetBrains Mono",
        "Fira Code",
        Consolas,
        monospace;

    font-size:.84em;

}


/* ============================================================
   BLOQUES DE CÓDIGO
============================================================ */

.markdown-body :deep(pre){

    margin:22px 0;

    padding:18px 20px;

    overflow-x:auto;

    background:#F8FAFC;

    border:1px solid #E2E8F0;

    border-radius:12px;

    box-shadow:
        0 4px 12px
        rgba(
            15,
            39,
            71,
            .035
        );

}


.markdown-body :deep(pre code){

    display:block;

    color:#334155;

    font-family:
        "JetBrains Mono",
        "Fira Code",
        Consolas,
        monospace;

    font-size:.84rem;

    line-height:1.7;

    white-space:pre;

}


/* ============================================================
   TABLAS
============================================================ */

.markdown-body :deep(table){

    width:100%;

    margin:22px 0;

    border-collapse:separate;

    border-spacing:0;

    background:#FFFFFF;

    border:1px solid #E2E8F0;

    border-radius:12px;

    overflow:hidden;

    box-shadow:
        0 4px 14px
        rgba(
            15,
            39,
            71,
            .035
        );

}


/* ============================================================
   CABECERA DE TABLA
============================================================ */

.markdown-body :deep(th){

    padding:13px 15px;

    text-align:left;

    color:#0F2747;

    background:#F8FAFC;

    border-bottom:1px solid #E2E8F0;

    font-size:.82rem;

    font-weight:750;

    line-height:1.5;

}


/* ============================================================
   CELDAS
============================================================ */

.markdown-body :deep(td){

    padding:13px 15px;

    color:#475569;

    border-bottom:1px solid #E2E8F0;

    font-size:.88rem;

    line-height:1.65;

    vertical-align:top;

}


/* ============================================================
   DIVISORES VERTICALES
============================================================ */

.markdown-body :deep(th + th),
.markdown-body :deep(td + td){

    border-left:1px solid #E2E8F0;

}


/* ============================================================
   ÚLTIMA FILA
============================================================ */

.markdown-body :deep(tr:last-child td){

    border-bottom:none;

}


/* ============================================================
   HOVER TABLAS
============================================================ */

.markdown-body :deep(tbody tr){

    transition:
        background-color .2s ease;

}


.markdown-body :deep(tbody tr:hover){

    background:#F8FAFC;

}


/* ============================================================
   IMÁGENES
============================================================ */

.markdown-body :deep(img){

    display:block;

    max-width:100%;

    height:auto;

    margin:22px auto;

    border:1px solid #E2E8F0;

    border-radius:12px;

    box-shadow:
        0 6px 18px
        rgba(
            15,
            39,
            71,
            .06
        );

}


/* ============================================================
   FIGURAS / IMÁGENES CON TEXTO
============================================================ */

.markdown-body :deep(figure){

    margin:24px 0;

}


.markdown-body :deep(figcaption){

    margin-top:8px;

    color:#64748B;

    font-size:.78rem;

    line-height:1.5;

    text-align:center;

}


/* ============================================================
   DETAILS
============================================================ */

.markdown-body :deep(details){

    margin:18px 0;

    padding:0;

    background:#FFFFFF;

    border:1px solid #E2E8F0;

    border-radius:12px;

    overflow:hidden;

}


.markdown-body :deep(summary){

    padding:14px 17px;

    color:#0F2747;

    background:#F8FAFC;

    font-weight:700;

    cursor:pointer;

    transition:
        background-color .2s ease,
        color .2s ease;

}


.markdown-body :deep(summary:hover){

    color:#2563EB;

    background:#EFF6FF;

}


.markdown-body :deep(details > :not(summary)){

    margin-left:17px;

    margin-right:17px;

}


.markdown-body :deep(details > :last-child){

    margin-bottom:17px;

}


/* ============================================================
   CHECKLIST / TASKS
============================================================ */

.markdown-body :deep(input[type="checkbox"]){

    width:15px;

    height:15px;

    margin-right:7px;

    vertical-align:-2px;

    accent-color:#2563EB;

}


/* ============================================================
   MARK / TEXTO DESTACADO
============================================================ */

.markdown-body :deep(mark){

    padding:2px 5px;

    color:#17375E;

    background:#DBEAFE;

    border-radius:4px;

}


/* ============================================================
   SMALL
============================================================ */

.markdown-body :deep(small){

    color:#64748B;

    font-size:.82rem;

}


/* ============================================================
   SELECCIÓN
============================================================ */

.markdown-body :deep(::selection){

    color:#0F2747;

    background:
        rgba(
            37,
            99,
            235,
            .14
        );

}


/* ============================================================
   SCROLLBAR — CÓDIGO Y TABLAS
============================================================ */

.markdown-body :deep(pre::-webkit-scrollbar),
.markdown-body :deep(table::-webkit-scrollbar){

    height:7px;

}


.markdown-body :deep(pre::-webkit-scrollbar-track),
.markdown-body :deep(table::-webkit-scrollbar-track){

    background:#F1F5F9;

}


.markdown-body :deep(pre::-webkit-scrollbar-thumb),
.markdown-body :deep(table::-webkit-scrollbar-thumb){

    background:#CBD5E1;

    border-radius:999px;

}


.markdown-body :deep(pre::-webkit-scrollbar-thumb:hover),
.markdown-body :deep(table::-webkit-scrollbar-thumb:hover){

    background:#94A3B8;

}


/* ============================================================
   RESPONSIVE — TABLET
============================================================ */

@media(max-width:768px){

    .markdown-body{

        font-size:.92rem;

        line-height:1.78;

    }


    .markdown-body :deep(h1){

        margin-top:26px;

        font-size:1.48rem;

    }


    .markdown-body :deep(h2){

        margin-top:25px;

        font-size:1.25rem;

    }


    .markdown-body :deep(h3){

        margin-top:22px;

        font-size:1.08rem;

    }


    .markdown-body :deep(pre){

        padding:15px 16px;

        border-radius:10px;

    }


    .markdown-body :deep(th),
    .markdown-body :deep(td){

        padding:11px 12px;

    }


    .markdown-body :deep(blockquote){

        padding:15px 17px 15px 18px;

    }

}


/* ============================================================
   RESPONSIVE — MOBILE
============================================================ */

@media(max-width:576px){

    .markdown-body{

        font-size:.89rem;

        line-height:1.72;

    }


    .markdown-body :deep(h1){

        margin-top:23px;

        margin-bottom:14px;

        padding-bottom:11px;

        font-size:1.36rem;

    }


    .markdown-body :deep(h1::after){

        width:34px;

        height:2px;

    }


    .markdown-body :deep(h2){

        margin-top:22px;

        margin-bottom:13px;

        padding-bottom:8px;

        font-size:1.17rem;

    }


    .markdown-body :deep(h3){

        margin-top:20px;

        font-size:1.02rem;

    }


    .markdown-body :deep(p){

        margin-bottom:14px;

    }


    .markdown-body :deep(ul),
    .markdown-body :deep(ol){

        padding-left:21px;

    }


    .markdown-body :deep(blockquote){

        margin:18px 0;

        padding:13px 14px 13px 16px;

        border-radius:0 9px 9px 0;

    }


    .markdown-body :deep(pre){

        margin:18px 0;

        padding:13px;

        border-radius:9px;

    }


    .markdown-body :deep(pre code){

        font-size:.78rem;

    }


    .markdown-body :deep(table){

        display:block;

        width:100%;

        overflow-x:auto;

        white-space:normal;

    }


    .markdown-body :deep(th),
    .markdown-body :deep(td){

        min-width:120px;

        padding:10px 11px;

        font-size:.82rem;

    }


    .markdown-body :deep(img){

        margin:18px auto;

        border-radius:9px;

    }

}


/* ============================================================
   ANIMACIÓN
============================================================ */

.markdown-body{

    animation:
        markdownAppear
        .35s
        ease
        both;

}


@keyframes markdownAppear{

    from{

        opacity:0;

        transform:
            translateY(6px);

    }

    to{

        opacity:1;

        transform:
            translateY(0);

    }

}


/* ============================================================
   REDUCED MOTION
============================================================ */

@media(prefers-reduced-motion: reduce){

    .markdown-body{

        animation:none;

    }

    .markdown-body :deep(a),
    .markdown-body :deep(summary),
    .markdown-body :deep(tbody tr){

        transition:none;

    }

}

</style>
