<template>

    <section class="novacourt-header">

        <!-- =====================================================
             DECORACIÓN DE FONDO
        ====================================================== -->

        <div
            class="header-glow header-glow-right"
            aria-hidden="true"
        ></div>

        <div
            class="header-glow header-glow-left"
            aria-hidden="true"
        ></div>


        <div
            class="header-grid"
            aria-hidden="true"
        ></div>


        <!-- =====================================================
             LÍNEA SUPERIOR INSTITUCIONAL
        ====================================================== -->

        <div
            class="header-top-line"
            aria-hidden="true"
        ></div>


        <!-- =====================================================
             CONTENIDO PRINCIPAL
        ====================================================== -->

        <div class="header-content">


            <!-- =================================================
                 EYEBROW INSTITUCIONAL
            ================================================== -->

            <div class="header-eyebrow">

                <span class="eyebrow-line"></span>

                <span class="eyebrow-primary">
                    INTELIGENCIA JUDICIAL
                </span>

                <span class="eyebrow-dot"></span>

                <span class="eyebrow-secondary">
                    NOVA IURIS
                </span>

            </div>


            <!-- =================================================
                 TÍTULO PRINCIPAL
            ================================================== -->

            <h1>
                NovaCourt
            </h1>


            <!-- =================================================
                 ACENTO DEL TÍTULO
            ================================================== -->

            <div
                class="title-accent"
                aria-hidden="true"
            >

                <span class="accent-side"></span>

                <span class="accent-center"></span>

                <span class="accent-side"></span>

            </div>


            <!-- =================================================
                 SUBTÍTULO
            ================================================== -->

            <p class="header-subtitle">

                Analizador Judicial Inteligente para evaluación
                integral de casos.

            </p>


            <!-- =================================================
                 DESCRIPCIÓN
            ================================================== -->

            <p class="header-description">

                Evalúa escenarios jurídicos, contrasta argumentos,
                analiza evidencia y riesgos, y explora posibles
                resultados mediante inteligencia artificial.

            </p>


            <!-- =================================================
                 CAPACIDADES
            ================================================== -->

            <div class="header-features">


                <div class="feature-item">

                    <span class="feature-icon">
                        ⚖
                    </span>

                    <span class="feature-text">
                        Análisis jurídico
                    </span>

                </div>


                <span
                    class="feature-divider"
                    aria-hidden="true"
                ></span>


                <div class="feature-item">

                    <span class="feature-icon">
                        ◈
                    </span>

                    <span class="feature-text">
                        Simulación de escenarios
                    </span>

                </div>


                <span
                    class="feature-divider"
                    aria-hidden="true"
                ></span>


                <div class="feature-item">

                    <span class="feature-icon">
                        ✓
                    </span>

                    <span class="feature-text">
                        Evaluación estratégica
                    </span>

                </div>

            </div>


        </div>


        <!-- =====================================================
             SÍMBOLO JUDICIAL
        ====================================================== -->

        <div
            class="header-symbol"
            aria-hidden="true"
        >

            <div class="symbol-orbit symbol-orbit-outer"></div>

            <div class="symbol-orbit symbol-orbit-large"></div>

            <div class="symbol-orbit symbol-orbit-medium"></div>

            <div class="symbol-orbit symbol-orbit-small"></div>


            <div class="symbol-axis symbol-axis-horizontal"></div>

            <div class="symbol-axis symbol-axis-vertical"></div>


            <div class="symbol-center">

                <span class="symbol-scale">
                    ⚖
                </span>

            </div>

        </div>


        <!-- =====================================================
             MARCA INFERIOR
        ====================================================== -->

        <div class="header-footer-mark">

            <span class="footer-mark-line"></span>

            <span>
                SISTEMA DE EVALUACIÓN JUDICIAL
            </span>

            <span class="footer-mark-line"></span>

        </div>


    </section>

</template>


<script setup>

</script>


<style scoped>

/* ============================================================
   NOVACOURT
   IDENTIDAD VISUAL
   JURÍDICA · INSTITUCIONAL · PREMIUM · INTELIGENTE
============================================================ */

.novacourt-header {

    /* ========================================================
       PALETA NOVA IURIS
    ======================================================== */

    --court-navy: #0F2747;

    --court-navy-deep: #102238;

    --court-blue: #2563EB;

    --court-blue-dark: #1D4ED8;

    --court-blue-soft: #EFF6FF;

    --court-blue-border: #BFDBFE;

    --court-gold: #B08A4C;

    --court-gold-dark: #9A753E;

    --court-gold-soft: #F8F4EC;

    --court-text: #334155;

    --court-text-soft: #52647A;

    --court-muted: #64748B;

    --court-light: #94A3B8;

    --court-border: #DDE5EE;

    --court-border-soft: #E8EDF3;

    --court-background: #FFFFFF;


    position: relative;

    display: flex;

    align-items: center;

    justify-content: center;

    min-height: 350px;

    padding:
        54px
        190px
        48px
        54px;

    overflow: hidden;

    isolation: isolate;

    background:

        linear-gradient(
            135deg,
            #FFFFFF 0%,
            #FDFEFF 44%,
            #F7FAFE 100%
        );

    border:
        1px solid
        var(--court-border);

    border-radius: 22px;

    box-shadow:

        0 10px 30px
        rgba(
            15,
            39,
            71,
            .055
        ),

        0 2px 6px
        rgba(
            15,
            39,
            71,
            .025
        );

    animation:
        courtHeaderAppear
        .55s
        ease
        both;

}


/* ============================================================
   LÍNEA SUPERIOR
============================================================ */

.header-top-line {

    position: absolute;

    z-index: 10;

    top: 0;

    left: 0;

    width: 100%;

    height: 3px;

    background:

        linear-gradient(
            90deg,
            #0F2747 0%,
            #1D4ED8 36%,
            #2563EB 58%,
            #B08A4C 100%
        );

}


/* ============================================================
   DECORACIÓN SUPERIOR IZQUIERDA
============================================================ */

.header-glow {

    position: absolute;

    pointer-events: none;

    border-radius: 50%;

}


/* ============================================================
   CÍRCULO AZUL DERECHO
============================================================ */

.header-glow-right {

    z-index: -2;

    width: 480px;

    height: 480px;

    right: -285px;

    bottom: -315px;

    border:
        1px solid
        rgba(
            37,
            99,
            235,
            .08
        );

    box-shadow:

        0 0 0 65px
        rgba(
            37,
            99,
            235,
            .018
        ),

        0 0 0 130px
        rgba(
            37,
            99,
            235,
            .009
        );

}


/* ============================================================
   CÍRCULO DORADO IZQUIERDO
============================================================ */

.header-glow-left {

    z-index: -2;

    width: 290px;

    height: 290px;

    left: -210px;

    top: -215px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .10
        );

}


/* ============================================================
   GRID DECORATIVO SUTIL
============================================================ */

.header-grid {

    position: absolute;

    z-index: -1;

    inset: 0;

    opacity: .28;

    pointer-events: none;

    background-image:

        linear-gradient(
            rgba(
                37,
                99,
                235,
                .018
            ) 1px,
            transparent 1px
        ),

        linear-gradient(
            90deg,
            rgba(
                37,
                99,
                235,
                .018
            ) 1px,
            transparent 1px
        );

    background-size:
        46px 46px;

    mask-image:

        linear-gradient(
            to bottom,
            transparent 0%,
            rgba(0,0,0,.7) 40%,
            transparent 100%
        );

}


/* ============================================================
   CONTENIDO
============================================================ */

.header-content {

    position: relative;

    z-index: 5;

    display: flex;

    flex-direction: column;

    align-items: center;

    width: 100%;

    max-width: 850px;

    text-align: center;

    animation:

        contentAppear
        .6s
        .05s
        ease
        both;

}


/* ============================================================
   EYEBROW
============================================================ */

.header-eyebrow {

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 9px;

    margin-bottom: 15px;

    color:
        var(--court-muted);

    font-size: .64rem;

    font-weight: 800;

    line-height: 1;

    letter-spacing: .145em;

}


/* Línea azul */

.eyebrow-line {

    width: 25px;

    height: 2px;

    background:
        var(--court-blue);

    border-radius: 999px;

}


/* Inteligencia judicial */

.eyebrow-primary {

    color:
        #667991;

}


/* Punto dorado */

.eyebrow-dot {

    width: 4px;

    height: 4px;

    flex-shrink: 0;

    border-radius: 50%;

    background:
        var(--court-gold);

    box-shadow:

        0 0 0 2px
        rgba(
            176,
            138,
            76,
            .08
        );

}


/* Nova Iuris */

.eyebrow-secondary {

    color:
        var(--court-gold-dark);

}


/* ============================================================
   TÍTULO PRINCIPAL
============================================================ */

.novacourt-header h1 {

    margin: 0;

    color:
        var(--court-navy);

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 3.35rem;

    font-weight: 600;

    line-height: 1.05;

    letter-spacing:
        -.045em;

    text-rendering:
        optimizeLegibility;

}


/* ============================================================
   ACENTO DEL TÍTULO
============================================================ */

.title-accent {

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 4px;

    width: 58px;

    height: 4px;

    margin:
        17px
        0
        16px;

}


.title-accent span {

    display: block;

    height: 2px;

    border-radius: 999px;

}


.accent-side {

    width: 11px;

    background:
        var(--court-blue);

    opacity: .42;

}


.accent-center {

    width: 27px;

    background:
        var(--court-gold);

}


/* ============================================================
   SUBTÍTULO
============================================================ */

.header-subtitle {

    max-width: 740px;

    margin: 0;

    color:
        #40566E;

    font-size: 1.07rem;

    font-weight: 600;

    line-height: 1.65;

    letter-spacing:
        .002em;

}


/* ============================================================
   DESCRIPCIÓN
============================================================ */

.header-description {

    max-width: 750px;

    margin:
        10px
        0
        0;

    color:
        var(--court-muted);

    font-size: .9rem;

    font-weight: 400;

    line-height: 1.78;

}


/* ============================================================
   CARACTERÍSTICAS
============================================================ */

.header-features {

    display: flex;

    align-items: center;

    justify-content: center;

    gap: 16px;

    margin-top: 24px;

    padding:
        9px
        15px;

    background:

        rgba(
            255,
            255,
            255,
            .72
        );

    border:
        1px solid
        var(--court-border);

    border-radius: 10px;

    box-shadow:

        0 4px 14px
        rgba(
            15,
            39,
            71,
            .028
        );

    backdrop-filter:
        blur(8px);

}


/* ============================================================
   FEATURE
============================================================ */

.feature-item {

    display: flex;

    align-items: center;

    gap: 8px;

    color:
        #52647A;

    font-size: .66rem;

    font-weight: 700;

    line-height: 1;

    letter-spacing:
        .01em;

    white-space: nowrap;

}


/* ============================================================
   ICONOS
============================================================ */

.feature-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 23px;

    height: 23px;

    color:
        var(--court-blue);

    background:
        var(--court-blue-soft);

    border:
        1px solid
        var(--court-blue-border);

    border-radius: 6px;

    font-size: .72rem;

    line-height: 1;

    transition:

        background .2s ease,

        border-color .2s ease,

        transform .2s ease;

}


/* ============================================================
   DIVISORES
============================================================ */

.feature-divider {

    width: 1px;

    height: 19px;

    background:
        #D9E1EA;

}


/* ============================================================
   SÍMBOLO JUDICIAL
============================================================ */

.header-symbol {

    position: absolute;

    z-index: 4;

    top: 50%;

    right: 45px;

    display: flex;

    align-items: center;

    justify-content: center;

    width: 142px;

    height: 142px;

    transform:
        translateY(-50%);

    animation:

        symbolAppear
        .75s
        .15s
        ease
        both;

}


/* ============================================================
   ÓRBITAS
============================================================ */

.symbol-orbit {

    position: absolute;

    border-radius: 50%;

    pointer-events: none;

}


/* Órbita exterior */

.symbol-orbit-outer {

    width: 140px;

    height: 140px;

    border:
        1px solid
        rgba(
            37,
            99,
            235,
            .055
        );

}


/* Órbita principal */

.symbol-orbit-large {

    width: 122px;

    height: 122px;

    border:
        1px solid
        rgba(
            37,
            99,
            235,
            .11
        );

}


/* Órbita intermedia */

.symbol-orbit-medium {

    width: 98px;

    height: 98px;

    border:
        1px solid
        rgba(
            37,
            99,
            235,
            .15
        );

}


/* Órbita dorada */

.symbol-orbit-small {

    width: 74px;

    height: 74px;

    border:
        1px solid
        rgba(
            176,
            138,
            76,
            .34
        );

}


/* ============================================================
   EJES
============================================================ */

.symbol-axis {

    position: absolute;

    pointer-events: none;

    background:
        rgba(
            176,
            138,
            76,
            .17
        );

}


.symbol-axis-horizontal {

    width: 102px;

    height: 1px;

}


.symbol-axis-vertical {

    width: 1px;

    height: 102px;

}


/* ============================================================
   CENTRO DEL SÍMBOLO
============================================================ */

.symbol-center {

    position: relative;

    z-index: 5;

    display: flex;

    align-items: center;

    justify-content: center;

    width: 58px;

    height: 58px;

    background:

        rgba(
            255,
            255,
            255,
            .96
        );

    border:
        1px solid
        #D9E1EA;

    border-radius: 50%;

    box-shadow:

        0 8px 22px
        rgba(
            15,
            39,
            71,
            .075
        ),

        0 0 0 5px
        rgba(
            255,
            255,
            255,
            .55
        );

}


/* ============================================================
   BALANZA
============================================================ */

.symbol-scale {

    color:
        var(--court-gold);

    font-size: 1.72rem;

    line-height: 1;

    filter:

        drop-shadow(
            0
            2px
            3px
            rgba(
                176,
                138,
                76,
                .14
            )
        );

}


/* ============================================================
   MARCA INFERIOR
============================================================ */

.header-footer-mark {

    position: absolute;

    z-index: 5;

    left: 50%;

    bottom: 14px;

    display: flex;

    align-items: center;

    gap: 9px;

    transform:
        translateX(-50%);

    color:
        #98A7B8;

    font-size: .53rem;

    font-weight: 800;

    line-height: 1;

    letter-spacing:
        .145em;

    white-space: nowrap;

}


.footer-mark-line {

    width: 18px;

    height: 1px;

    background:
        #CBD5E1;

}


/* ============================================================
   HOVER
============================================================ */

.novacourt-header:hover
.symbol-orbit-small {

    border-color:
        rgba(
            176,
            138,
            76,
            .48
        );

}


.novacourt-header:hover
.symbol-center {

    box-shadow:

        0 10px 26px
        rgba(
            15,
            39,
            71,
            .095
        ),

        0 0 0 5px
        rgba(
            255,
            255,
            255,
            .62
        );

}


.novacourt-header:hover
.feature-icon {

    background:
        #EAF2FF;

    border-color:
        #B8D1F8;

}


.novacourt-header:hover
.accent-center {

    background:
        var(--court-gold-dark);

}


/* ============================================================
   RESPONSIVE — 1100px
============================================================ */

@media (max-width: 1100px) {

    .novacourt-header {

        padding-right:
            170px;

    }


    .header-symbol {

        right: 28px;

        transform:
            translateY(-50%)
            scale(.9);

    }

}


/* ============================================================
   RESPONSIVE — 900px
============================================================ */

@media (max-width: 900px) {

    .novacourt-header {

        min-height: 335px;

        padding:
            48px
            145px
            46px
            36px;

    }


    .novacourt-header h1 {

        font-size:
            2.85rem;

    }


    .header-symbol {

        right: 14px;

        transform:
            translateY(-50%)
            scale(.78);

    }


    .header-features {

        gap: 12px;

    }


    .feature-item {

        font-size:
            .61rem;

    }

}


/* ============================================================
   RESPONSIVE — 768px
============================================================ */

@media (max-width: 768px) {

    .novacourt-header {

        min-height: auto;

        padding:
            40px
            28px
            50px;

        border-radius:
            20px;

    }


    .header-symbol {

        display: none;

    }


    .novacourt-header h1 {

        font-size:
            2.4rem;

    }


    .header-subtitle {

        font-size:
            .98rem;

    }


    .header-description {

        max-width:
            650px;

        font-size:
            .87rem;

    }


    .header-features {

        max-width:
            100%;

        flex-wrap:
            wrap;

        padding:
            9px
            12px;

    }

}


/* ============================================================
   RESPONSIVE — 576px
============================================================ */

@media (max-width: 576px) {

    .novacourt-header {

        padding:
            34px
            18px
            46px;

        border-radius:
            17px;

    }


    .header-eyebrow {

        gap:
            7px;

        font-size:
            .56rem;

        letter-spacing:
            .10em;

    }


    .eyebrow-line {

        width:
            18px;

    }


    .novacourt-header h1 {

        font-size:
            2.05rem;

    }


    .title-accent {

        margin:
            14px
            0
            13px;

    }


    .header-subtitle {

        font-size:
            .9rem;

        line-height:
            1.6;

    }


    .header-description {

        margin-top:
            8px;

        font-size:
            .82rem;

        line-height:
            1.7;

    }


    .header-features {

        width:
            100%;

        flex-direction:
            column;

        align-items:
            flex-start;

        gap:
            9px;

        margin-top:
            19px;

        padding:
            11px
            12px;

    }


    .feature-divider {

        display:
            none;

    }


    .feature-item {

        width:
            100%;

        font-size:
            .64rem;

    }


    .header-footer-mark {

        gap:
            6px;

        font-size:
            .46rem;

        letter-spacing:
            .085em;

    }


    .footer-mark-line {

        width:
            11px;

    }

}


/* ============================================================
   RESPONSIVE — 380px
============================================================ */

@media (max-width: 380px) {

    .novacourt-header {

        padding:
            29px
            15px
            43px;

    }


    .header-eyebrow {

        font-size:
            .51rem;

    }


    .novacourt-header h1 {

        font-size:
            1.82rem;

    }


    .header-subtitle {

        font-size:
            .85rem;

    }


    .header-description {

        font-size:
            .77rem;

    }


    .header-footer-mark {

        font-size:
            .42rem;

    }

}


/* ============================================================
   ANIMACIONES
============================================================ */

@keyframes courtHeaderAppear {

    from {

        opacity:
            0;

        transform:
            translateY(14px);

    }

    to {

        opacity:
            1;

        transform:
            translateY(0);

    }

}


@keyframes contentAppear {

    from {

        opacity:
            0;

        transform:
            translateY(10px);

    }

    to {

        opacity:
            1;

        transform:
            translateY(0);

    }

}


@keyframes symbolAppear {

    from {

        opacity:
            0;

        transform:
            translateY(-50%)
            scale(.9);

    }

    to {

        opacity:
            1;

        transform:
            translateY(-50%)
            scale(1);

    }

}


/* ============================================================
   REDUCED MOTION
============================================================ */

@media (
    prefers-reduced-motion: reduce
) {

    .novacourt-header,
    .header-content,
    .header-symbol {

        animation:
            none;

    }


    .novacourt-header *,
    .novacourt-header *::before,
    .novacourt-header *::after {

        transition:
            none;

    }

}

</style>