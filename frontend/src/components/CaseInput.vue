<template>

<div class="case-input-card">

    <div class="header">

        <div>

            <h2>

                Descripción del caso

            </h2>

            <p>

                Describe los hechos del caso con el mayor detalle posible.
                NovaCase construirá automáticamente un análisis jurídico integral.

            </p>

        </div>

        <div class="counter">

            {{ characters }}/12000

        </div>

    </div>

    <textarea

        v-model="caseText"

        class="case-textarea"

        placeholder="Ejemplo:

Un trabajador fue despedido sin expresión de causa después de laborar cinco años en una empresa privada. La empresa sostiene pérdida de confianza. El trabajador solicita reposición, pago de remuneraciones devengadas y beneficios sociales..."

        maxlength="12000"

        rows="12"

        @keydown.ctrl.enter="submit"

    />

    <div class="footer">

        <div class="tips">

            <span>

                Ctrl + Enter para analizar

            </span>

        </div>

        <button

            class="analyze-button"

            @click="submit"

            :disabled="loading || !caseText.trim()"

        >

            <span
                v-if="loading"
            >

                Analizando...

            </span>

            <span
                v-else
            >

                Analizar Caso

            </span>

        </button>

    </div>

</div>

</template>

<script setup>

import { ref, computed } from "vue"

const caseText = ref("")

const loading = ref(false)

const characters = computed(() => caseText.value.length)

const submit = async () => {

    if (!caseText.value.trim()) return

    loading.value = true

    console.log(caseText.value)

    setTimeout(() => {

        loading.value = false

    },1000)

}

</script>

<style scoped>

.case-textarea {
    background: #FFFFFF;
    color: #172033;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 25px;
}

.header h2 {
    margin: 0;
    color: #0F2747;
    font-size: 24px;
    font-weight: 700;
}

.header p {
    color: #64748B;
    margin-top: 10px;
    line-height: 1.6;
}

.counter {
    background: #EFF6FF;
    color: #2563EB;
    padding: 8px 14px;
    border-radius: 30px;
    font-weight: 700;
    font-size: 13px;
    border: 1px solid #DBEAFE;
}

.case-textarea {
    width: 100%;
    min-height: 320px;
    resize: vertical;
    border: 1px solid #CBD5E1;
    border-radius: 10px;
    padding: 20px;
    font-size: 15px;
    line-height: 1.8;
    outline: none;
    transition: 0.2s;
    box-sizing: border-box;

    background: #FFFFFF;
    color: #172033;
}

.case-textarea::placeholder {
    color: #94A3B8;
}

.case-textarea:focus {
    border-color: #2563EB;
    box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.10);
}

.footer {
    margin-top: 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.tips {
    color: #64748B;
    font-size: 13px;
}

.analyze-button {
    background: #2563EB;
    color: #FFFFFF;
    border: 1px solid #2563EB;
    padding: 14px 34px;
    border-radius: 8px;
    font-weight: 700;
    cursor: pointer;
    transition: 0.25s;
}

.analyze-button:hover {
    background: #1D4ED8;
    border-color: #1D4ED8;
}

.analyze-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

@media (max-width: 768px) {

    .case-input-card {
        padding: 22px;
    }

    .header {
        flex-direction: column;
        gap: 15px;
    }

    .counter {
        align-self: flex-start;
    }

    .case-textarea {
        min-height: 260px;
    }

    .footer {
        flex-direction: column;
        align-items: stretch;
        gap: 16px;
    }

    .analyze-button {
        width: 100%;
    }

}

</style>