<template>
    <header class="nova-search-header">

        <div class="nova-search-header-inner">

            <!-- IDENTIDAD -->

            <div class="nova-search-brand">

                <div class="nova-search-brand-mark">

                    <span class="brand-monogram">
                        NS
                    </span>

                </div>


                <div class="nova-search-brand-content">

                    <span class="nova-search-brand-eyebrow">
                        NOVA IURIS · INTELIGENCIA JURÍDICA
                    </span>

                    <h1 class="nova-search-brand-title">
                        NovaSearch
                    </h1>

                    <p class="nova-search-brand-description">
                        Investigación, recuperación y análisis inteligente
                        de información jurídica.
                    </p>

                </div>

            </div>


            <!-- IDENTIDAD DEL MÓDULO -->

            <div class="nova-search-module">

                <span class="nova-search-module-label">
                    MÓDULO ACTIVO
                </span>

                <span class="nova-search-module-name">
                    Investigación jurídica
                </span>

            </div>

        </div>

    </header>
</template>


<script setup>
</script>


<style scoped>

/* =========================================
   NOVA SEARCH HEADER
========================================= */

.nova-search-header{

    width:100%;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #FBFCFE 100%
        );

    border-bottom:
        1px solid
        #DCE3EB;

}


/* =========================================
   CONTENEDOR PRINCIPAL
========================================= */

.nova-search-header-inner{

    max-width:1280px;

    margin:0 auto;

    padding:
        34px
        32px;

    display:flex;

    align-items:center;

    justify-content:space-between;

    gap:32px;

}


/* =========================================
   MARCA
========================================= */

.nova-search-brand{

    display:flex;

    align-items:center;

    gap:18px;

    min-width:0;

}


/* =========================================
   MONOGRAMA
========================================= */

.nova-search-brand-mark{

    position:relative;

    width:62px;

    height:62px;

    flex:0 0 62px;

    display:flex;

    align-items:center;

    justify-content:center;

    border-radius:50%;

    background:#17375E;

    box-shadow:

        0 10px 24px
        rgba(
            23,
            55,
            94,
            .14
        );

}


/* ANILLO EXTERIOR */

.nova-search-brand-mark::before{

    content:"";

    position:absolute;

    inset:5px;

    border:

        1px solid
        rgba(
            176,
            138,
            76,
            .65
        );

    border-radius:50%;

}


/* MONOGRAMA */

.brand-monogram{

    position:relative;

    z-index:1;

    color:#FFFFFF;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:1rem;

    font-weight:600;

    letter-spacing:1.8px;

}


/* =========================================
   TEXTO DE MARCA
========================================= */

.nova-search-brand-content{

    min-width:0;

}


.nova-search-brand-eyebrow{

    display:block;

    margin-bottom:6px;

    color:#7A6440;

    font-size:.68rem;

    font-weight:800;

    letter-spacing:1.5px;

}


.nova-search-brand-title{

    margin:0;

    color:#17375E;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size:2rem;

    font-weight:600;

    line-height:1.15;

    letter-spacing:-.4px;

}


.nova-search-brand-description{

    margin:

        7px
        0
        0;

    color:#64748B;

    font-size:.9rem;

    line-height:1.6;

}


/* =========================================
   MÓDULO ACTIVO
========================================= */

.nova-search-module{

    display:flex;

    flex-direction:column;

    align-items:flex-end;

    gap:5px;

    flex-shrink:0;

    padding-left:28px;

    border-left:

        1px solid
        #DCE3EB;

}


.nova-search-module-label{

    color:#93A0AE;

    font-size:.65rem;

    font-weight:800;

    letter-spacing:1.2px;

}


.nova-search-module-name{

    color:#315C97;

    font-size:.84rem;

    font-weight:700;

}


/* =========================================
   RESPONSIVE
========================================= */

@media(max-width:900px){

    .nova-search-header-inner{

        padding:
            28px
            24px;

    }


    .nova-search-module{

        padding-left:22px;

    }

}


@media(max-width:700px){

    .nova-search-header-inner{

        align-items:flex-start;

        flex-direction:column;

        gap:22px;

    }


    .nova-search-module{

        width:100%;

        align-items:flex-start;

        padding:

            16px
            0
            0;

        border-left:none;

        border-top:

            1px solid
            #E2E8F0;

    }

}


@media(max-width:576px){

    .nova-search-header-inner{

        padding:
            24px
            18px;

    }


    .nova-search-brand{

        align-items:flex-start;

        gap:14px;

    }


    .nova-search-brand-mark{

        width:54px;

        height:54px;

        flex-basis:54px;

    }


    .nova-search-brand-title{

        font-size:1.65rem;

    }


    .nova-search-brand-description{

        font-size:.84rem;

    }


    .nova-search-brand-eyebrow{

        font-size:.6rem;

        letter-spacing:1.15px;

    }

}

</style>