<template>

    <section class="novacourt-header">

        <div class="header-content">


            <!-- TÍTULO PRINCIPAL -->
            <h1>

                NovaCourt

            </h1>


            <!-- ACENTO -->
            <div class="title-accent"></div>


            <!-- DESCRIPCIÓN PRINCIPAL -->
            <p class="header-subtitle">

                Analizador Judicial Inteligente para evaluación
                integral de casos.

            </p>


            <!-- DESCRIPCIÓN SECUNDARIA -->
            <p class="header-description">

                Evalúa escenarios jurídicos, contrasta argumentos,
                analiza evidencia y riesgos, y explora posibles
                resultados mediante inteligencia artificial.

            </p>

        </div>


        <!-- DECORACIÓN JUDICIAL -->
        <div class="header-symbol">

            <div class="symbol-ring symbol-ring-large"></div>

            <div class="symbol-ring symbol-ring-medium"></div>

            <div class="symbol-ring symbol-ring-small"></div>

            <div class="symbol-center">
                ⚖
            </div>

        </div>

    </section>

</template>


<script setup>

</script>


<style scoped>

/* =====================================================
   NOVACOURT HEADER
   IDENTIDAD: JURÍDICA · INSTITUCIONAL · INTELIGENTE
===================================================== */

.novacourt-header {
    position: relative;
    overflow: hidden;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    min-height: 240px;

    padding: 32px 48px 30px;

    text-align: center;

    background:
        linear-gradient(
            135deg,
            #FDFDFC 0%,
            #F8FAFC 52%,
            #F3F6FA 100%
        );

    border: 1px solid #D9E0E8;
    border-radius: 8px;

    box-shadow:
        0 16px 40px rgba(15, 34, 56, .07);
}


/* =====================================================
   LÍNEA SUPERIOR
===================================================== */

.novacourt-header::before {

    content: "";

    position: absolute;

    top: 0;

    left: 0;

    width: 100%;

    height: 3px;

    background:

        linear-gradient(
            90deg,
            #102A43 0%,
            #1F4F82 38%,
            #5E7FA3 68%,
            rgba(
                185,
                151,
                91,
                .45
            ) 100%
        );

}


/* =====================================================
   DECORACIÓN DE FONDO
===================================================== */

.novacourt-header::after {

    content: "";

    position: absolute;

    width: 430px;

    height: 430px;

    right: -190px;

    bottom: -260px;

    border: 1px solid rgba(
        31,
        79,
        130,
        .07
    );

    border-radius: 50%;

    pointer-events: none;

}


/* =====================================================
   CONTENIDO
===================================================== */

.header-content {

    position: relative;

    z-index: 3;

    width: 100%;

    max-width: 820px;

    display: flex;

    flex-direction: column;

    align-items: center;

}


/* =====================================================
   BADGE
===================================================== */

.header-badge {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    gap: 9px;

    padding: 8px 13px;

    margin-bottom: 20px;

    color: #1F4F82;

    background: rgba(
        255,
        255,
        255,
        .72
    );

    border: 1px solid #CDD8E5;

    border-radius: 3px;

    box-shadow:

        0 5px 14px rgba(
            15,
            34,
            56,
            .035
        );

    font-size: .67rem;

    font-weight: 800;

    letter-spacing: 1.35px;

}


.badge-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    color: #B08A4C;

    font-size: .95rem;

    line-height: 1;

}


.badge-name {

    color: #102A43;

}


.badge-divider {

    width: 1px;

    height: 14px;

    background: #CCD6E0;

}


.badge-text {

    color: #607286;

    font-size: .63rem;

    font-weight: 700;

    letter-spacing: 1.1px;

}


/* =====================================================
   TÍTULO PRINCIPAL
===================================================== */

.novacourt-header h1 {

    margin: 0;

    color: #102A43;

    font-family:

        Georgia,
        "Times New Roman",
        serif;

    font-size: 3rem;

    font-weight: 500;

    line-height: 1.1;

    letter-spacing: -.7px;

}


/* =====================================================
   ACENTO
===================================================== */

.title-accent {

    width: 44px;

    height: 2px;

    margin: 18px 0 16px;

    background:

        linear-gradient(
            90deg,
            #1F4F82,
            #5C82AC
        );

}


/* =====================================================
   SUBTÍTULO
===================================================== */

.header-subtitle {

    margin: 0;

    color: #40566E;

    font-size: 1.05rem;

    font-weight: 500;

    line-height: 1.7;

    letter-spacing: .01em;

}


/* =====================================================
   DESCRIPCIÓN
===================================================== */

.header-description {

    max-width: 720px;

    margin: 10px 0 0;

    color: #6B7A8C;

    font-size: .94rem;

    font-weight: 400;

    line-height: 1.8;

}


/* =====================================================
   SÍMBOLO JUDICIAL DECORATIVO
===================================================== */

.header-symbol {

    position: absolute;

    z-index: 1;

    right: 58px;

    top: 50%;

    width: 132px;

    height: 132px;

    transform: translateY(-50%);

    display: flex;

    align-items: center;

    justify-content: center;

}


.symbol-ring {

    position: absolute;

    border-radius: 50%;

    pointer-events: none;

}


.symbol-ring-large {

    width: 128px;

    height: 128px;

    border: 1px solid rgba(
        31,
        79,
        130,
        .12
    );

}


.symbol-ring-medium {

    width: 104px;

    height: 104px;

    border: 1px solid rgba(
        31,
        79,
        130,
        .16
    );

}


.symbol-ring-small {

    width: 82px;

    height: 82px;

    border: 1px solid rgba(
        176,
        138,
        76,
        .32
    );

}


.symbol-center {

    position: relative;

    z-index: 2;

    width: 58px;

    height: 58px;

    display: flex;

    align-items: center;

    justify-content: center;

    color: #B08A4C;

    background: rgba(
        255,
        255,
        255,
        .78
    );

    border: 1px solid #D7E0E9;

    border-radius: 50%;

    box-shadow:

        0 8px 20px rgba(
            15,
            34,
            56,
            .06
        );

    font-size: 1.75rem;

}


/* =====================================================
   RESPONSIVE - TABLET
===================================================== */

@media (max-width: 1050px) {

    .novacourt-header {

        min-height: 300px;

    }

    .header-symbol {

        right: 32px;

        opacity: .85;

    }

}


@media (max-width: 900px) {

    .novacourt-header {

        min-height: 290px;

        padding: 42px 36px;

    }

    .novacourt-header h1 {

        font-size: 2.6rem;

    }

    .header-symbol {

        right: 24px;

        transform:

            translateY(-50%)
            scale(.85);

        transform-origin: right center;

    }

}


/* =====================================================
   RESPONSIVE - MOBILE
===================================================== */

@media (max-width: 768px) {

    .novacourt-header {

        min-height: auto;

        padding: 38px 28px;

    }

    .header-symbol {

        display: none;

    }

    .novacourt-header h1 {

        font-size: 2.25rem;

    }

    .header-subtitle {

        font-size: 1rem;

    }

}


@media (max-width: 576px) {

    .novacourt-header {

        padding: 32px 20px;

        border-radius: 6px;

    }

    .header-badge {

        gap: 7px;

        padding: 7px 10px;

        margin-bottom: 18px;

    }

    .badge-text {

        display: none;

    }

    .badge-divider {

        display: none;

    }

    .novacourt-header h1 {

        font-size: 1.9rem;

    }

    .title-accent {

        margin: 15px 0 13px;

    }

    .header-subtitle {

        font-size: .92rem;

        line-height: 1.65;

    }

    .header-description {

        font-size: .86rem;

        line-height: 1.7;

    }

}

</style>