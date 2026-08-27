<template>

    <section class="case-input-card">

        <div class="card-header">

            <h2>

                Describe el caso jurídico

            </h2>

            <p>

                Expón los hechos relevantes con el mayor detalle posible para obtener un análisis jurídico completo.

            </p>

        </div>

        <textarea

            v-model="caseText"

            class="case-textarea"

            placeholder="Ejemplo:

Un trabajador fue despedido luego de publicar comentarios críticos sobre su empleador en redes sociales. La empresa alega pérdida de confianza. El trabajador sostiene que se vulneró su libertad de expresión y solicita su reposición..."

        />

        <div class="card-footer">

            <span class="characters">

                {{ caseText.length }} caracteres

            </span>

            <button

                class="analyze-button"

                @click="submitCase"

                :disabled="loading"

            >

                <span v-if="!loading">

                    Analizar Caso

                </span>

                <span v-else>

                    Analizando...

                </span>

            </button>

        </div>

    </section>

</template>

<script setup>

import { ref } from "vue"

const emit = defineEmits([

    "analyze"

])

const caseText = ref("")

const loading = ref(false)

async function submitCase(){

    if(

        !caseText.value.trim()

    ){

        return

    }

    loading.value = true

    await emit(

        "analyze",

        caseText.value

    )

    loading.value = false

}

</script>

<style scoped>

.case-input-card {
    width: 100%;
    box-sizing: border-box;

    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 30px;

    box-shadow: 0 8px 24px rgba(15, 39, 71, 0.06);
}

/* ================================
   ENCABEZADO
================================ */

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;

    margin-bottom: 24px;
}

.card-header h2 {
    margin: 0;

    color: #0F2747;
    font-size: 24px;
    font-weight: 700;
    line-height: 1.3;
}

.card-header p {
    margin: 10px 0 0;

    color: #64748B;
    font-size: 15px;
    line-height: 1.6;
}

/* ================================
   ÁREA DEL CASO
================================ */

.case-textarea {
    display: block;

    width: 100%;
    min-height: 320px;

    box-sizing: border-box;

    resize: vertical;

    padding: 20px;

    background: #FFFFFF;
    color: #172033;

    border: 1px solid #CBD5E1;
    border-radius: 10px;

    font-family: inherit;
    font-size: 15px;
    line-height: 1.8;

    outline: none;

    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease;
}

.case-textarea::placeholder {
    color: #94A3B8;
}

.case-textarea:focus {
    border-color: #2563EB;

    box-shadow:
        0 0 0 4px rgba(37, 99, 235, 0.10);
}

/* ================================
   PIE DE TARJETA
================================ */

.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;

    margin-top: 24px;
}

.characters {
    color: #64748B;
    font-size: 13px;
}

/* ================================
   BOTÓN
================================ */

.analyze-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    min-width: 156px;

    padding: 14px 28px;

    background: #2563EB;
    color: #FFFFFF;

    border: 1px solid #2563EB;
    border-radius: 8px;

    font-family: inherit;
    font-size: 14px;
    font-weight: 700;

    cursor: pointer;

    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.analyze-button:hover:not(:disabled) {
    background: #1D4ED8;
    border-color: #1D4ED8;

    transform: translateY(-1px);

    box-shadow:
        0 6px 16px rgba(37, 99, 235, 0.18);
}

.analyze-button:active:not(:disabled) {
    transform: translateY(0);
}

.analyze-button:disabled {
    opacity: 0.55;
    cursor: not-allowed;
}

/* ================================
   RESPONSIVE
================================ */

@media (max-width: 768px) {

    .case-input-card {
        padding: 22px;
    }

    .card-header {
        flex-direction: column;
        gap: 6px;
    }

    .card-header h2 {
        font-size: 21px;
    }

    .case-textarea {
        min-height: 260px;
        padding: 16px;
    }

    .card-footer {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
    }

    .analyze-button {
        width: 100%;
    }
}

</style>