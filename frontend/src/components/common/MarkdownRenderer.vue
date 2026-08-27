<template>

    <div class="markdown-container">

        <article

            class="markdown-body"

            v-html="renderedMarkdown"

        />

    </div>

</template>


<script setup>

import {

    computed

} from "vue"

import MarkdownIt from "markdown-it"

import hljs from "highlight.js"


/* =========================================
   PROPS
========================================= */

const props = defineProps({

    content: {

        type: String,

        default: ""

    }

})


/* =========================================
   MARKDOWN
========================================= */

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

                return `

<pre class="hljs">

<code>

${hljs.highlight(

    str,

    {

        language: lang,

        ignoreIllegals: true

    }

).value}

</code>

</pre>

`

            }

            catch{

            }

        }


        return `

<pre class="hljs">

<code>

${md.utils.escapeHtml(str)}

</code>

</pre>

`

    }

})


md.set({

    quotes: "“”‘’"

})


/* =========================================
   ENLACES EXTERNOS
========================================= */

const defaultRender =

    md.renderer.rules.link_open ||

    function(tokens, idx, options, env, self){

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

)=>{

    tokens[idx].attrSet(

        "target",

        "_blank"

    )


    tokens[idx].attrSet(

        "rel",

        "noopener noreferrer"

    )


    return defaultRender(

        tokens,

        idx,

        options,

        env,

        self

    )

}


/* =========================================
   RENDER
========================================= */

const renderedMarkdown = computed(()=>

    md.render(

        props.content

    )

)

</script>


<style scoped>

/* =========================================
   NOVACOURT MARKDOWN RENDERER
   ESTILO JURÍDICO INSTITUCIONAL
========================================= */

.markdown-container{

    width:100%;

}


/* =========================================
   CUERPO PRINCIPAL
========================================= */

.markdown-body{

    width:100%;

    color:#334155;

    font-size:.96rem;

    font-weight:400;

    line-height:1.85;

    letter-spacing:.005em;

}


/* =========================================
   TÍTULOS
========================================= */

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6){

    color:#102238;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-weight:500;

    line-height:1.35;

    letter-spacing:-.015em;

}


.markdown-body :deep(h1){

    margin:32px 0 16px;

    font-size:1.7rem;

}


.markdown-body :deep(h2){

    margin:30px 0 15px;

    padding-bottom:11px;

    border-bottom:1px solid #D6DFEA;

    font-size:1.42rem;

}


.markdown-body :deep(h3){

    margin:26px 0 13px;

    font-size:1.18rem;

}


.markdown-body :deep(h4){

    margin:22px 0 11px;

    font-size:1.04rem;

    font-weight:600;

}


.markdown-body :deep(h5),
.markdown-body :deep(h6){

    margin:20px 0 10px;

    font-size:.95rem;

    font-weight:600;

}


/* Primer título sin espacio excesivo */

.markdown-body :deep(h1:first-child),
.markdown-body :deep(h2:first-child),
.markdown-body :deep(h3:first-child){

    margin-top:0;

}


/* =========================================
   PÁRRAFOS
========================================= */

.markdown-body :deep(p){

    margin:0 0 17px;

    color:#596575;

}


.markdown-body :deep(p:last-child){

    margin-bottom:0;

}


/* =========================================
   TEXTO DESTACADO
========================================= */

.markdown-body :deep(strong){

    color:#17375E;

    font-weight:700;

}


.markdown-body :deep(em){

    color:#596575;

}


/* =========================================
   LISTAS
========================================= */

.markdown-body :deep(ul),
.markdown-body :deep(ol){

    margin:0 0 20px;

    padding-left:25px;

}


.markdown-body :deep(li){

    margin-bottom:9px;

    padding-left:3px;

    color:#596575;

}


.markdown-body :deep(li::marker){

    color:#315C97;

}


/* =========================================
   ENLACES
========================================= */

.markdown-body :deep(a){

    color:#315C97;

    font-weight:600;

    text-decoration:none;

    border-bottom:1px solid
        rgba(
            49,
            92,
            151,
            .25
        );

    transition:

        color .2s ease,
        border-color .2s ease;

}


.markdown-body :deep(a:hover){

    color:#17375E;

    border-bottom-color:#17375E;

}


/* =========================================
   CITA / BLOQUE JURÍDICO
========================================= */

.markdown-body :deep(blockquote){

    position:relative;

    margin:22px 0;

    padding:16px 20px;

    color:#596575;

    background:#F5F7FA;

    border-top:1px solid #D6DFEA;

    border-right:1px solid #D6DFEA;

    border-bottom:1px solid #D6DFEA;

    border-left:3px solid #315C97;

    border-radius:0 6px 6px 0;

}


.markdown-body :deep(blockquote p){

    color:#596575;

}


.markdown-body :deep(blockquote p:last-child){

    margin-bottom:0;

}


/* =========================================
   SEPARADOR
========================================= */

.markdown-body :deep(hr){

    margin:30px 0;

    border:0;

    border-top:1px solid #D6DFEA;

}


/* =========================================
   CÓDIGO
========================================= */

.markdown-body :deep(pre){

    margin:22px 0;

    padding:18px;

    overflow-x:auto;

    background:#F4F6F8;

    border:1px solid #D6DFEA;

    border-radius:7px;

}


.markdown-body :deep(code){

    font-family:

        "JetBrains Mono",
        "Fira Code",
        Consolas,
        monospace;

    font-size:.87rem;

}


.markdown-body :deep(pre code){

    color:#17375E;

    line-height:1.7;

}


.markdown-body :deep(:not(pre) > code){

    padding:3px 6px;

    color:#17375E;

    background:#F1F4F7;

    border:1px solid #DCE4EC;

    border-radius:4px;

}


/* =========================================
   TABLAS
========================================= */

.markdown-body :deep(table){

    width:100%;

    margin:22px 0;

    border-collapse:separate;

    border-spacing:0;

    overflow:hidden;

    background:#FFFFFF;

    border:1px solid #D6DFEA;

    border-radius:7px;

}


.markdown-body :deep(th){

    padding:13px 15px;

    text-align:left;

    color:#17375E;

    background:#F3F6F9;

    border-bottom:1px solid #D6DFEA;

    font-size:.86rem;

    font-weight:700;

}


.markdown-body :deep(td){

    padding:13px 15px;

    color:#596575;

    border-bottom:1px solid #DCE4EC;

    font-size:.9rem;

    line-height:1.65;

}


.markdown-body :deep(th + th),
.markdown-body :deep(td + td){

    border-left:1px solid #DCE4EC;

}


.markdown-body :deep(tr:last-child td){

    border-bottom:none;

}


/* =========================================
   FILAS
========================================= */

.markdown-body :deep(tbody tr){

    transition:background .2s ease;

}


.markdown-body :deep(tbody tr:hover){

    background:#F8FAFC;

}


/* =========================================
   IMÁGENES
========================================= */

.markdown-body :deep(img){

    display:block;

    max-width:100%;

    height:auto;

    margin:22px 0;

    border:1px solid #D6DFEA;

    border-radius:7px;

}


/* =========================================
   DETAILS
========================================= */

.markdown-body :deep(details){

    margin:18px 0;

    padding:14px 16px;

    background:#F7F8FA;

    border:1px solid #D6DFEA;

    border-radius:6px;

}


.markdown-body :deep(summary){

    color:#17375E;

    font-weight:700;

    cursor:pointer;

}


/* =========================================
   SELECCIÓN
========================================= */

.markdown-body :deep(::selection){

    color:#102238;

    background:
        rgba(
            49,
            92,
            151,
            .16
        );

}


/* =========================================
   RESPONSIVE
========================================= */

@media(max-width:768px){

    .markdown-body{

        font-size:.93rem;

        line-height:1.8;

    }


    .markdown-body :deep(h1){

        font-size:1.5rem;

    }


    .markdown-body :deep(h2){

        font-size:1.28rem;

    }


    .markdown-body :deep(h3){

        font-size:1.1rem;

    }


    .markdown-body :deep(pre){

        padding:15px;

    }


    .markdown-body :deep(th),
    .markdown-body :deep(td){

        padding:11px 12px;

    }

}


@media(max-width:576px){

    .markdown-body{

        font-size:.9rem;

        line-height:1.75;

    }


    .markdown-body :deep(h1){

        font-size:1.38rem;

    }


    .markdown-body :deep(h2){

        margin-top:25px;

        font-size:1.2rem;

    }


    .markdown-body :deep(h3){

        margin-top:22px;

        font-size:1.05rem;

    }


    .markdown-body :deep(blockquote){

        margin:18px 0;

        padding:14px 16px;

    }


    .markdown-body :deep(pre){

        padding:13px;

        font-size:.82rem;

    }


    .markdown-body :deep(table){

        display:block;

        overflow-x:auto;

        white-space:normal;

    }

}

</style>