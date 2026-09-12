<template>

    <section class="novacourt-input">

        <!-- =========================================
             ENCABEZADO
        ========================================== -->

        <header class="input-header">

            <div class="section-heading">

                <span class="section-eyebrow">
                    NOVACOURT · SIMULACIÓN JUDICIAL
                </span>

                <h2>
                    Caso para simulación
                </h2>

                <div class="title-accent"></div>

                <p>
                    Describe los hechos relevantes del caso.
                    NovaCourt utilizará esta información para analizar
                    argumentos, evidencia, riesgos y posibles escenarios judiciales.
                </p>

            </div>

        </header>


        <!-- =========================================
             FORMULARIO
        ========================================== -->

        <div class="input-body">

            <div class="field-header">

                <div class="field-title">

                    <span class="field-index">
                        01
                    </span>

                    <label
                        class="input-label"
                        for="case-description"
                    >
                        Descripción del caso
                    </label>

                </div>

                <span class="minimum-hint">
                    Mínimo 20 caracteres
                </span>

            </div>


            <!-- =====================================
                 TEXTAREA
            ====================================== -->

            <div class="textarea-wrapper">

                <textarea
                    id="case-description"
                    v-model="localValue"
                    class="case-textarea"
                    placeholder="Describe los hechos relevantes, las partes involucradas, pretensiones, argumentos, evidencia disponible y cualquier información jurídica importante..."
                    rows="12"
                    :disabled="loading"
                ></textarea>

                <div class="textarea-corner">
                    NOVACOURT
                </div>

            </div>


            <!-- =====================================
                 PIE DEL FORMULARIO
            ====================================== -->

            <div class="input-footer">

                <div class="input-status">

                    <div class="character-row">

                        <span class="character-count">
                            {{ localValue.length }} caracteres
                        </span>

                        <span
                            v-if="localValue.trim().length > 0 && localValue.trim().length < 20"
                            class="validation-message"
                        >
                            Faltan {{ 20 - localValue.trim().length }}
                        </span>

                        <span
                            v-else-if="localValue.trim().length >= 20"
                            class="ready-message"
                        >
                            Caso listo para análisis
                        </span>

                    </div>

                    <div class="status-line">

                        <span
                            class="status-indicator"
                            :class="{
                                'is-ready': localValue.trim().length >= 20
                            }"
                        ></span>

                        <span>
                            {{ localValue.trim().length >= 20
                                ? "Información suficiente para iniciar"
                                : "Ingresa la información del caso"
                            }}
                        </span>

                    </div>

                </div>


                <!-- =================================
                     BOTÓN
                ================================== -->

                <button
                    type="button"
                    class="simulate-button"
                    :disabled="!canSimulate"
                    @click="handleSimulate"
                >

                    <span class="button-content">

                        <span
                            v-if="loading"
                            class="button-spinner"
                        ></span>

                        <span>
                            {{ loading
                                ? "Analizando escenario..."
                                : "Iniciar simulación"
                            }}
                        </span>

                        <span
                            v-if="!loading"
                            class="button-arrow"
                        >
                            →
                        </span>

                    </span>

                </button>

            </div>

        </div>

    </section>

</template>


<script setup>

import {
    computed,
    ref,
    watch
} from "vue"


/* =========================================
   PROPS
========================================= */

const props = defineProps({

    modelValue: {

        type: String,

        default: ""

    },

    loading: {

        type: Boolean,

        default: false

    }

})


/* =========================================
   EVENTOS
========================================= */

const emit = defineEmits([

    "update:modelValue",

    "simulate"

])


/* =========================================
   ESTADO LOCAL
========================================= */

const localValue = ref(

    props.modelValue

)


/* =========================================
   SINCRONIZACIÓN
========================================= */

watch(

    () => props.modelValue,

    value => {

        localValue.value = value

    }

)


watch(

    localValue,

    value => {

        emit(

            "update:modelValue",

            value

        )

    }

)


/* =========================================
   VALIDACIÓN
========================================= */

const canSimulate = computed(() =>

    localValue.value
        .trim()
        .length >= 20 &&

    !props.loading

)


/* =========================================
   SIMULACIÓN
========================================= */

function handleSimulate() {

    if (!canSimulate.value) {

        return

    }

    emit(

        "simulate",

        localValue.value.trim()

    )

}

</script>


<style scoped>

/* =====================================================
   NOVACOURT INPUT
   IDENTIDAD VISUAL

   NOVA IURIS
   ─────────────────────────────────────────────────────
   • Institucional
   • Jurídico
   • Premium
   • Blanco / Navy / Azul
   • Líneas finas
   • Espaciado editorial
   • Sin apariencia de card genérica
===================================================== */


/* =====================================================
   CONTENEDOR PRINCIPAL
===================================================== */

.novacourt-input {

    width: 100%;

    margin: 0;

    padding: 46px 52px 48px;

    background: #FFFFFF;

    color: #17375E;

    box-sizing: border-box;

}


/* =====================================================
   ENCABEZADO
===================================================== */

.input-header {

    padding-bottom: 30px;

    border-bottom: 1px solid #DCE3EB;

}


.section-heading {

    width: 100%;

    max-width: 940px;

}


/* =====================================================
   EYEBROW
===================================================== */

.section-eyebrow {

    display: inline-flex;

    align-items: center;

    margin-bottom: 14px;

    color: #315C97;

    font-size: .68rem;

    font-weight: 750;

    letter-spacing: 1.55px;

    line-height: 1.2;

    text-transform: uppercase;

}


/* =====================================================
   TÍTULO
===================================================== */

.input-header h2 {

    margin: 0;

    color: #17375E;

    font-family:
        Georgia,
        "Times New Roman",
        serif;

    font-size: 2.05rem;

    font-weight: 500;

    line-height: 1.25;

    letter-spacing: -.25px;

}


/* =====================================================
   ACENTO DE IDENTIDAD
===================================================== */

.title-accent {

    width: 48px;

    height: 2px;

    margin: 18px 0 17px;

    background: #315C97;

}


/* =====================================================
   DESCRIPCIÓN
===================================================== */

.input-header p {

    max-width: 880px;

    margin: 0;

    color: #5E6D7E;

    font-size: .95rem;

    font-weight: 400;

    line-height: 1.85;

    letter-spacing: .005em;

}


/* =====================================================
   CUERPO DEL FORMULARIO
===================================================== */

.input-body {

    margin-top: 32px;

}


/* =====================================================
   CABECERA DEL CAMPO
===================================================== */

.field-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 20px;

    margin-bottom: 12px;

}


.field-title {

    display: flex;

    align-items: center;

    gap: 10px;

}


.field-index {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    min-width: 26px;

    height: 22px;

    padding: 0 7px;

    box-sizing: border-box;

    border: 1px solid #D4DFEB;

    color: #315C97;

    background: #F7F9FC;

    font-size: .65rem;

    font-weight: 750;

    letter-spacing: .5px;

}


.input-label {

    color: #17375E;

    font-size: .87rem;

    font-weight: 700;

    letter-spacing: .01em;

}


.minimum-hint {

    color: #7A8795;

    font-size: .75rem;

    line-height: 1.4;

}


/* =====================================================
   CONTENEDOR DEL TEXTAREA
===================================================== */

.textarea-wrapper {

    position: relative;

    width: 100%;

}


/* =====================================================
   ÁREA DE TEXTO
===================================================== */

.case-textarea {

    display: block;

    width: 100%;

    min-height: 330px;

    box-sizing: border-box;

    resize: vertical;

    padding: 22px 24px 42px;

    outline: none;

    background: #FFFFFF;

    color: #24364A;

    border: 1px solid #C9D3DE;

    border-radius: 2px;

    font-family: inherit;

    font-size: .95rem;

    font-weight: 400;

    line-height: 1.85;

    transition:
        border-color .2s ease,
        box-shadow .2s ease,
        background .2s ease;

}


.case-textarea::placeholder {

    color: #8A96A3;

    opacity: 1;

}


.case-textarea:hover:not(:disabled) {

    border-color: #9EAFBF;

}


.case-textarea:focus {

    background: #FFFFFF;

    border-color: #315C97;

    box-shadow:
        0 0 0 3px
        rgba(
            49,
            92,
            151,
            .07
        );

}


.case-textarea:disabled {

    cursor: not-allowed;

    background: #F7F8FA;

    color: #6F7C89;

}


/* =====================================================
   MARCA INTERNA
===================================================== */

.textarea-corner {

    position: absolute;

    right: 14px;

    bottom: 11px;

    pointer-events: none;

    color: #A3AFBB;

    font-size: .58rem;

    font-weight: 750;

    letter-spacing: 1.1px;

    opacity: .75;

}


/* =====================================================
   PIE DEL FORMULARIO
===================================================== */

.input-footer {

    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 28px;

    margin-top: 18px;

}


.input-status {

    display: flex;

    flex-direction: column;

    gap: 7px;

}


.character-row {

    display: flex;

    align-items: center;

    gap: 12px;

}


.character-count {

    color: #687789;

    font-size: .76rem;

    line-height: 1.4;

}


.validation-message {

    padding-left: 12px;

    border-left: 1px solid #D7E0E9;

    color: #315C97;

    font-size: .76rem;

    line-height: 1.4;

}


.ready-message {

    padding-left: 12px;

    border-left: 1px solid #D7E0E9;

    color: #315C97;

    font-size: .76rem;

    font-weight: 650;

    line-height: 1.4;

}


/* =====================================================
   ESTADO
===================================================== */

.status-line {

    display: flex;

    align-items: center;

    gap: 7px;

    color: #8793A0;

    font-size: .7rem;

    line-height: 1.4;

}


.status-indicator {

    width: 6px;

    height: 6px;

    flex-shrink: 0;

    border-radius: 50%;

    background: #CBD5E1;

    transition:
        background .2s ease,
        box-shadow .2s ease;

}


.status-indicator.is-ready {

    background: #315C97;

    box-shadow:
        0 0 0 3px
        rgba(
            49,
            92,
            151,
            .09
        );

}


/* =====================================================
   BOTÓN PRINCIPAL
===================================================== */

.simulate-button {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    flex-shrink: 0;

    min-width: 238px;

    min-height: 50px;

    padding: 13px 24px;

    box-sizing: border-box;

    border: 1px solid #17375E;

    border-radius: 2px;

    cursor: pointer;

    background: #17375E;

    color: #FFFFFF;

    font-family: inherit;

    font-size: .76rem;

    font-weight: 750;

    letter-spacing: .07em;

    text-transform: uppercase;

    transition:
        background .2s ease,
        border-color .2s ease,
        transform .2s ease,
        box-shadow .2s ease,
        opacity .2s ease;

}


.button-content {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    gap: 11px;

    white-space: nowrap;

}


.button-arrow {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    font-size: 1rem;

    line-height: 1;

    transition:
        transform .2s ease;

}


/* =====================================================
   HOVER
===================================================== */

.simulate-button:hover:not(:disabled) {

    background: #102A49;

    border-color: #102A49;

    box-shadow:
        0 7px 18px
        rgba(
            23,
            55,
            94,
            .14
        );

    transform:
        translateY(-1px);

}


.simulate-button:hover:not(:disabled)
.button-arrow {

    transform:
        translateX(3px);

}


/* =====================================================
   ACTIVE
===================================================== */

.simulate-button:active:not(:disabled) {

    box-shadow: none;

    transform:
        translateY(0);

}


/* =====================================================
   DISABLED
===================================================== */

.simulate-button:disabled {

    cursor: not-allowed;

    opacity: .42;

}


/* =====================================================
   SPINNER
===================================================== */

.button-spinner {

    width: 13px;

    height: 13px;

    box-sizing: border-box;

    border:
        2px solid
        rgba(
            255,
            255,
            255,
            .35
        );

    border-top-color: #FFFFFF;

    border-radius: 50%;

    animation:
        novacourt-spin .75s linear infinite;

}


@keyframes novacourt-spin {

    to {

        transform:
            rotate(360deg);

    }

}


/* =====================================================
   RESPONSIVE — TABLET
===================================================== */

@media (max-width: 900px) {

    .novacourt-input {

        padding:
            40px
            36px
            42px;

    }


    .input-header h2 {

        font-size: 1.9rem;

    }


    .case-textarea {

        min-height: 300px;

    }

}


/* =====================================================
   RESPONSIVE — TABLET PEQUEÑA
===================================================== */

@media (max-width: 768px) {

    .novacourt-input {

        padding:
            34px
            30px
            38px;

    }


    .input-header {

        padding-bottom: 26px;

    }


    .input-header h2 {

        font-size: 1.8rem;

    }


    .input-header p {

        font-size: .92rem;

    }


    .case-textarea {

        min-height: 280px;

    }


    .input-footer {

        align-items: stretch;

        flex-direction: column;

    }


    .simulate-button {

        width: 100%;

        min-width: 0;

    }

}


/* =====================================================
   RESPONSIVE — MOBILE
===================================================== */

@media (max-width: 576px) {

    .novacourt-input {

        padding:
            28px
            20px
            32px;

    }


    .input-header {

        padding-bottom: 24px;

    }


    .section-eyebrow {

        margin-bottom: 12px;

        font-size: .61rem;

        letter-spacing: 1.25px;

    }


    .input-header h2 {

        font-size: 1.55rem;

        line-height: 1.3;

    }


    .title-accent {

        width: 38px;

        height: 2px;

        margin:
            15px
            0;

    }


    .input-header p {

        font-size: .88rem;

        line-height: 1.75;

    }


    .input-body {

        margin-top: 24px;

    }


    .field-header {

        align-items: flex-start;

        flex-direction: column;

        gap: 7px;

    }


    .minimum-hint {

        font-size: .7rem;

    }


    .case-textarea {

        min-height: 250px;

        padding:
            17px
            17px
            38px;

        font-size: .9rem;

        line-height: 1.75;

    }


    .textarea-corner {

        right: 11px;

        bottom: 9px;

        font-size: .52rem;

    }


    .input-footer {

        gap: 18px;

        margin-top: 17px;

    }


    .character-row {

        align-items: flex-start;

        flex-direction: column;

        gap: 6px;

    }


    .validation-message,
    .ready-message {

        padding-left: 0;

        border-left: none;

    }


    .simulate-button {

        min-height: 48px;

        padding:
            12px
            18px;

        font-size: .71rem;

    }

}


/* =====================================================
   RESPONSIVE — MOBILE PEQUEÑO
===================================================== */

@media (max-width: 400px) {

    .novacourt-input {

        padding:
            24px
            16px
            28px;

    }


    .input-header h2 {

        font-size: 1.4rem;

    }


    .field-title {

        gap: 8px;

    }


    .case-textarea {

        min-height: 230px;

    }

}

</style>