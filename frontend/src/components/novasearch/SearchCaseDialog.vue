<script setup>
import { computed, onMounted, ref } from 'vue'
import { listOwnedCases, startSearchCaseHandoff } from '@/services/searchCaseHandoff.js'

const props = defineProps({ result:{ type:Object, required:true } })
const emit = defineEmits(['close', 'started'])
const cases = ref([]), mode = ref('new'), caseId = ref(''), caseText = ref('')
const busy = ref(false), error = ref(''), loading = ref(true)
let handoffRequestId = null, lastSubmission = null
const title = computed(() => props.result.display_title || props.result.document_title || props.result.title || props.result.titulo || 'Fuente jurídica')
onMounted(async () => {
  try { cases.value = await listOwnedCases() }
  catch { error.value = 'No se pudieron cargar tus casos. Inténtalo de nuevo.' }
  finally { loading.value = false }
})
async function submit() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try {
    const submission = JSON.stringify([props.result.document_id, props.result.unit_id,
      mode.value, caseId.value, caseText.value.trim()])
    if (submission !== lastSubmission) {
      handoffRequestId = crypto.randomUUID()
      lastSubmission = submission
    }
    const started = await startSearchCaseHandoff({ result:props.result, caseMode:mode.value,
      caseId:caseId.value, caseText:caseText.value, handoffRequestId })
    emit('started', { ...started, caseText:caseText.value.trim() })
  } catch (failure) { error.value = failure?.message || 'No se pudo iniciar el análisis.' }
  finally { busy.value = false }
}
</script>

<template>
  <div class="handoff-backdrop" role="presentation" @click.self="!busy && emit('close')">
    <section class="handoff-dialog" role="dialog" aria-modal="true" aria-label="Analizar fuente en NovaCase">
      <header><h2>Analizar en NovaCase</h2><button type="button" :disabled="busy" aria-label="Cerrar" @click="emit('close')">×</button></header>
      <p class="source-name">{{ title }}</p>
      <p>Se enviará la referencia verificable de esta unidad. NovaCase obtendrá el texto completo desde Legal Knowledge V2.</p>
      <form @submit.prevent="submit">
        <fieldset :disabled="busy || loading">
          <legend>Destino</legend>
          <label><input v-model="mode" type="radio" value="new"> Crear caso nuevo</label>
          <label><input v-model="mode" type="radio" value="existing"> Usar un caso existente</label>
          <select v-if="mode === 'existing'" v-model="caseId" aria-label="Seleccionar caso" required>
            <option value="" disabled>Selecciona un caso autorizado</option>
            <option v-for="item in cases" :key="item.case_id" :value="item.case_id">{{ item.case_id }}</option>
          </select>
          <p v-if="mode === 'existing' && !cases.length">No hay casos existentes disponibles.</p>
          <label class="facts-label" for="handoff-facts">Hechos o pregunta del caso</label>
          <textarea id="handoff-facts" v-model="caseText" minlength="50" maxlength="50000" required rows="5" placeholder="Describe los hechos y qué necesitas analizar (mínimo 50 caracteres)." />
        </fieldset>
        <p v-if="error" class="handoff-error" role="alert">{{ error }}</p>
        <footer><button type="button" :disabled="busy" @click="emit('close')">Cancelar</button><button type="submit" :disabled="busy || loading || caseText.trim().length < 50 || (mode === 'existing' && !caseId)">{{ busy ? 'Iniciando…' : 'Iniciar análisis' }}</button></footer>
      </form>
    </section>
  </div>
</template>

<style scoped>
.handoff-backdrop{position:fixed;inset:0;z-index:1100;background:#0b162890;display:grid;place-items:center;padding:20px}
.handoff-dialog{width:min(100%,520px);max-height:90vh;overflow:auto;background:#fff;border:1px solid #dce5ee;border-radius:16px;box-shadow:0 18px 60px #0b162840;padding:24px;color:#14283d}
header,footer{display:flex;align-items:center;justify-content:space-between;gap:16px}h2{font-size:1.3rem;margin:0}p{line-height:1.45}.source-name{font-weight:700;color:#17375e}
fieldset{display:grid;gap:12px;border:0;padding:12px 0;margin:0}legend{font-weight:700}label{display:flex;align-items:center;gap:8px}.facts-label{font-weight:700;margin-top:5px}
textarea,select{width:100%;box-sizing:border-box;padding:10px;border:1px solid #aebdcb;border-radius:8px;font:inherit}textarea{resize:vertical}button{cursor:pointer;border:1px solid #b6c5d4;border-radius:8px;padding:9px 14px;background:#fff;color:#17375e;font:inherit}button[type=submit]{background:#17375e;color:#fff}button:disabled{opacity:.5;cursor:not-allowed}.handoff-error{color:#a02929}header button{font-size:1.5rem;border:0}
</style>
