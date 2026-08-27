<template>

    <section class="novacourt-input">

        <!-- =========================================
             ENCABEZADO
        ========================================== -->

        <header class="input-header">

            <div class="section-heading">

                <span class="section-eyebrow">
                    SIMULACIÓN JUDICIAL
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

                <label
                    class="input-label"
                    for="case-description"
                >
                    Descripción del caso
                </label>

                <span class="minimum-hint">
                    Mínimo 20 caracteres
                </span>

            </div>


            <textarea
                id="case-description"
                v-model="localValue"
                class="case-textarea"
                placeholder="Describe los hechos relevantes, las partes involucradas, pretensiones, argumentos, evidencia disponible y cualquier información jurídica importante..."
                rows="12"
                :disabled="loading"
            />


            <div class="input-footer">

                <div class="input-status">

                    <span class="character-count">
                        {{ localValue.length }} caracteres
                    </span>

                    <span
                        v-if="localValue.trim().length > 0 && localValue.trim().length < 20"
                        class="validation-message"
                    >
                        Añade al menos {{ 20 - localValue.trim().length }} caracteres más
                    </span>

                    <span
                        v-else-if="localValue.trim().length >= 20"
                        class="ready-message"
                    >
                        Listo para iniciar la simulación
                    </span>

                </div>


                <button
                    class="simulate-button"
                    :disabled="!canSimulate"
                    @click="handleSimulate"
                >

                    <span
                        v-if="loading"
                        class="button-content"
                    >
                        Analizando escenario...
                    </span>

                    <span
                        v-else
                        class="button-content"
                    >
                        Iniciar simulación
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


const emit = defineEmits([
    "update:modelValue",
    "simulate"
])


const localValue = ref(
    props.modelValue
)


watch(

    () => props.modelValue,

    (value) => {

        localValue.value = value

    }

)


watch(

    localValue,

    (value) => {

        emit(
            "update:modelValue",
            value
        )

    }

)


const canSimulate = computed(() =>

    localValue.value
        .trim()
        .length >= 20 &&

    !props.loading

)


function handleSimulate() {

    if (
        !canSimulate.value
    ) {

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

   DIRECCIÓN VISUAL:
   JURÍDICA · SOBRIA · INSTITUCIONAL · ELEGANTE

   IMPORTANTE:
   ESTA SECCIÓN NO DEBE FUNCIONAR COMO UNA "CARD".
   LA ESTRUCTURA DEBE SENTIRSE COMO UNA SECCIÓN
   DE UNA WEB INSTITUCIONAL, SIMILAR A LA LANDING
   PRINCIPAL DE NOVA IURIS.
===================================================== */


/* =====================================================
   CONTENEDOR PRINCIPAL
===================================================== */

.novacourt-input {

    width: 100%;

    margin: 0;

    padding: 42px 48px 44px;

    background: #FFFFFF;

}


/* =====================================================
   ENCABEZADO
===================================================== */

.input-header {

    padding-bottom: 28px;

    border-bottom:
        1px solid
        #D9E0E8;

}


.section-heading {

    width: 100%;

    max-width: 920px;

}


/* =====================================================
   EYEBROW
===================================================== */

.section-eyebrow {

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

.input-header h2 {

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
   LÍNEA DE IDENTIDAD
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

.input-header p {

    max-width: 900px;

    margin: 0;

    color: #5E6D7E;

    font-size: .97rem;

    font-weight: 400;

    line-height: 1.85;

    letter-spacing: .01em;

}


/* =====================================================
   CUERPO DEL FORMULARIO
===================================================== */

.input-body {

    margin-top: 30px;

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


.input-label {

    color: #17375E;

    font-size: .88rem;

    font-weight: 700;

    letter-spacing: .01em;

}


.minimum-hint {

    color: #7A8795;

    font-size: .78rem;

    line-height: 1.4;

}


/* =====================================================
   ÁREA DE TEXTO
===================================================== */

.case-textarea {

    display: block;

    width: 100%;

    min-height: 320px;

    box-sizing: border-box;

    resize: vertical;

    padding: 21px 22px;

    outline: none;

    background: #FFFFFF;

    color: #24364A;

    border:
        1px solid
        #C9D3DE;

    border-radius: 0;

    font-family: inherit;

    font-size: .96rem;

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

    border-color: #9DAEBD;

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
            .08
        );

}


.case-textarea:disabled {

    cursor: not-allowed;

    background: #F7F8FA;

    color: #6F7C89;

}


/* =====================================================
   PIE DEL FORMULARIO
===================================================== */

.input-footer {

    display: flex;

    align-items: flex-end;

    justify-content: space-between;

    gap: 24px;

    margin-top: 20px;

}


.input-status {

    display: flex;

    flex-direction: column;

    gap: 5px;

}


.character-count {

    color: #687789;

    font-size: .79rem;

    line-height: 1.4;

}


.validation-message {

    color: #315C97;

    font-size: .79rem;

    line-height: 1.4;

}


.ready-message {

    color: #315C97;

    font-size: .79rem;

    font-weight: 600;

    line-height: 1.4;

}


/* =====================================================
   BOTÓN PRINCIPAL
===================================================== */

.simulate-button {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    flex-shrink: 0;

    min-width: 220px;

    min-height: 48px;

    padding: 13px 26px;

    border:
        1px solid
        #17375E;

    border-radius: 0;

    cursor: pointer;

    background: #17375E;

    color: #FFFFFF;

    font-family: inherit;

    font-size: .82rem;

    font-weight: 700;

    letter-spacing: .04em;

    text-transform: uppercase;

    transition:
        background .2s ease,
        border-color .2s ease,
        transform .2s ease,
        opacity .2s ease;

}


.button-content {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    text-align: center;

}


/* =====================================================
   INTERACCIONES
===================================================== */

.simulate-button:hover:not(:disabled) {

    background: #102A49;

    border-color: #102A49;

    transform:
        translateY(-1px);

}


.simulate-button:active:not(:disabled) {

    transform:
        translateY(0);

}


.simulate-button:disabled {

    cursor: not-allowed;

    opacity: .45;

}


/* =====================================================
   RESPONSIVE - TABLET
===================================================== */

@media (max-width: 768px) {

    .novacourt-input {

        padding:
            34px
            30px
            36px;

    }


    .input-header h2 {

        font-size: 1.8rem;

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

    }

}


/* =====================================================
   RESPONSIVE - MOBILE
===================================================== */

@media (max-width: 576px) {

    .novacourt-input {

        padding:
            28px
            20px
            30px;

    }


    .input-header {

        padding-bottom: 24px;

    }


    .section-eyebrow {

        margin-bottom: 13px;

        font-size: .64rem;

    }


    .input-header h2 {

        font-size: 1.55rem;

    }


    .title-accent {

        width: 38px;

        margin:
            16px
            0;

    }


    .input-header p {

        font-size: .9rem;

        line-height: 1.75;

    }


    .input-body {

        margin-top: 24px;

    }


    .field-header {

        align-items: flex-start;

        flex-direction: column;

        gap: 5px;

    }


    .case-textarea {

        min-height: 250px;

        padding: 17px;

        font-size: .92rem;

        line-height: 1.75;

    }


    .input-footer {

        margin-top: 18px;

    }


    .simulate-button {

        min-width: 0;

        min-height: 46px;

        padding: 12px 20px;

        font-size: .76rem;

    }

}

</style>