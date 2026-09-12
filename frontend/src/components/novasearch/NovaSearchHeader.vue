<template>
    <header class="nova-search-header">

        <div class="nova-search-header-inner">

            <!-- =====================================
                 IDENTIDAD NOVA SEARCH
            ====================================== -->

            <div class="nova-search-brand">

                <!-- LOGO NOVA SEARCH -->

                <div
                    class="nova-search-brand-mark"
                    aria-hidden="true"
                >

                    <svg
                        viewBox="0 0 48 48"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >

                        <!-- LUPA -->

                        <circle
                            cx="21"
                            cy="21"
                            r="10.5"
                            stroke="currentColor"
                            stroke-width="1.8"
                        />

                        <path
                            d="M29 29L37 37"
                            stroke="currentColor"
                            stroke-width="1.8"
                            stroke-linecap="round"
                        />

                    </svg>

                </div>


                <!-- =================================
                     INFORMACIÓN DE MARCA
                ================================== -->

                <div class="nova-search-brand-content">

                    <div class="nova-search-brand-eyebrow">

                        <span class="eyebrow-line"></span>

                        <span>NOVA IURIS</span>

                        <span class="eyebrow-separator">
                            /
                        </span>

                        <span>INTELIGENCIA JURÍDICA</span>

                    </div>


                    <h1 class="nova-search-brand-title">
                        Nova Search
                    </h1>


                    <p class="nova-search-brand-description">
                        Investigación, recuperación y análisis inteligente
                        de información jurídica.
                    </p>

                </div>

            </div>


            <!-- =====================================
                 ESTADO DEL MÓDULO
            ====================================== -->

            <div class="nova-search-module">

                <div class="nova-search-status">

                    <span class="status-indicator"></span>

                    <span>
                        MÓDULO ACTIVO
                    </span>

                </div>


                <span class="nova-search-module-name">
                    Investigación jurídica
                </span>

            </div>

        </div>

    </header>
</template>


<script setup>
/*
    Este componente es únicamente visual.

    No se modifica ninguna conexión con:
    - useNovaSearch
    - NovaSearchView
    - filtros
    - búsqueda
    - resultados
    - API
*/
</script>


<style scoped>

/* =================================================
   NOVA SEARCH HEADER
================================================= */

.nova-search-header {

    width: 100%;

    background:
        linear-gradient(
            180deg,
            #FFFFFF 0%,
            #FBFCFE 100%
        );

    border-bottom:
        1px solid
        rgba(23, 55, 94, .12);

}


/* =================================================
   CONTENEDOR PRINCIPAL
================================================= */

.nova-search-header-inner {

    width: 100%;

    max-width: 1280px;

    margin: 0 auto;

    padding:
        30px
        32px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 40px;

}


/* =================================================
   IDENTIDAD
================================================= */

.nova-search-brand {

    display: flex;

    align-items: center;

    gap: 18px;

    min-width: 0;

}


/* =================================================
   LOGO NOVA SEARCH
================================================= */

.nova-search-brand-mark {

    position: relative;

    width: 60px;

    height: 60px;

    flex:
        0 0
        60px;

    display: flex;

    align-items: center;

    justify-content: center;

    color: #FFFFFF;

    background:
        linear-gradient(
            145deg,
            #17375E 0%,
            #0B2442 100%
        );

    border:
        1px solid
        rgba(201, 164, 92, .55);

    border-radius: 16px;

    box-shadow:
        0 10px 28px
        rgba(11, 36, 66, .16);

}


/* =================================================
   DETALLE INTERIOR DEL LOGO
================================================= */

.nova-search-brand-mark::before {

    content: "";

    position: absolute;

    inset: 5px;

    border:
        1px solid
        rgba(255, 255, 255, .12);

    border-radius: 12px;

    pointer-events: none;

}


/* =================================================
   SVG
================================================= */

.nova-search-brand-mark svg {

    position: relative;

    z-index: 1;

    width: 31px;

    height: 31px;

}


/* =================================================
   CONTENIDO DE MARCA
================================================= */

.nova-search-brand-content {

    min-width: 0;

}


/* =================================================
   EYEBROW
================================================= */

.nova-search-brand-eyebrow {

    display: flex;

    align-items: center;

    gap: 8px;

    margin-bottom: 7px;

    color:
        #8A6D3B;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .61rem;

    font-weight:
        800;

    letter-spacing:
        1.65px;

    line-height:
        1;

    text-transform:
        uppercase;

}


/* =================================================
   LÍNEA DORADA
================================================= */

.eyebrow-line {

    width: 22px;

    height: 1px;

    flex: 0 0 22px;

    background:
        #C9A45C;

}


/* =================================================
   SEPARADOR
================================================= */

.eyebrow-separator {

    color:
        #C9A45C;

    font-weight:
        700;

}


/* =================================================
   TÍTULO
================================================= */

.nova-search-brand-title {

    margin: 0;

    color:
        #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:
        2rem;

    font-weight:
        600;

    line-height:
        1.08;

    letter-spacing:
        -.45px;

}


/* =================================================
   DESCRIPCIÓN
================================================= */

.nova-search-brand-description {

    max-width:
        620px;

    margin:
        8px
        0
        0;

    color:
        #687386;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .88rem;

    line-height:
        1.55;

}


/* =================================================
   MÓDULO ACTIVO
================================================= */

.nova-search-module {

    display: flex;

    flex-direction: column;

    align-items: flex-end;

    gap: 7px;

    flex-shrink: 0;

    padding-left:
        30px;

    border-left:
        1px solid
        rgba(23, 55, 94, .13);

}


/* =================================================
   ESTADO
================================================= */

.nova-search-status {

    display: flex;

    align-items: center;

    gap: 8px;

    color:
        #8A6D3B;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size:
        .61rem;

    font-weight:
        800;

    letter-spacing:
        1.35px;

}


/* =================================================
   INDICADOR DE ESTADO
================================================= */

.status-indicator {

    position: relative;

    width: 7px;

    height: 7px;

    flex: 0 0 7px;

    border-radius:
        50%;

    background:
        #C9A45C;

    box-shadow:
        0 0 0 3px
        rgba(201, 164, 92, .13);

}


/* =================================================
   NOMBRE DEL MÓDULO
================================================= */

.nova-search-module-name {

    color:
        #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size:
        .91rem;

    font-weight:
        600;

    letter-spacing:
        -.1px;

}


/* =================================================
   HOVER SUTIL
================================================= */

.nova-search-brand-mark {

    transition:
        transform .25s ease,
        box-shadow .25s ease;

}


.nova-search-brand-mark:hover {

    transform:
        translateY(-1px);

    box-shadow:
        0 14px 30px
        rgba(11, 36, 66, .20);

}


/* =================================================
   TABLET
================================================= */

@media (max-width: 900px) {

    .nova-search-header-inner {

        padding:
            26px
            24px;

        gap:
            28px;

    }


    .nova-search-module {

        padding-left:
            22px;

    }

}


/* =================================================
   MOBILE
================================================= */

@media (max-width: 700px) {

    .nova-search-header-inner {

        flex-direction:
            column;

        align-items:
            flex-start;

        gap:
            22px;

    }


    .nova-search-module {

        width:
            100%;

        align-items:
            flex-start;

        padding:
            17px
            0
            0;

        border-left:
            none;

        border-top:
            1px solid
            rgba(23, 55, 94, .11);

    }

}


/* =================================================
   MOBILE PEQUEÑO
================================================= */

@media (max-width: 576px) {

    .nova-search-header-inner {

        padding:
            23px
            18px;

    }


    .nova-search-brand {

        align-items:
            flex-start;

        gap:
            14px;

    }


    .nova-search-brand-mark {

        width:
            52px;

        height:
            52px;

        flex-basis:
            52px;

        border-radius:
            14px;

    }


    .nova-search-brand-mark::before {

        border-radius:
            10px;

    }


    .nova-search-brand-mark svg {

        width:
            27px;

        height:
            27px;

    }


    .nova-search-brand-title {

        font-size:
            1.65rem;

    }


    .nova-search-brand-description {

        font-size:
            .82rem;

    }


    .nova-search-brand-eyebrow {

        flex-wrap:
            wrap;

        font-size:
            .56rem;

        letter-spacing:
            1.2px;

    }


    .eyebrow-line {

        width:
            18px;

        flex-basis:
            18px;

    }

}

</style>