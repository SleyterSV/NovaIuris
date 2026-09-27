<template>
  <section class="document-upload" aria-label="Documentos de este expediente">
    <div class="upload-heading">
      <div><strong>Documentos del expediente</strong><p>PDF, DOCX y TXT · aislados por case_id</p></div>
      <label class="choose-files" :class="{disabled: disabled || batchBusy}">Añadir archivos
        <input type="file" multiple accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain" :disabled="disabled || batchBusy || !caseId" @change="choose">
      </label>
    </div>
    <p v-if="error" class="upload-error" role="alert">{{ error }}</p>
    <div v-if="batchBusy" class="batch-progress" aria-live="polite">
      <span>{{ stageMessage }}</span>
      <progress v-if="stage === 'uploading'" max="100" :value="uploadProgress" aria-label="Progreso real del envío" />
      <span v-else-if="completedDocuments !== null">{{ completedDocuments }} de {{ totalDocuments }} documentos completados</span>
    </div>
    <ul v-if="items.length" class="file-list">
      <li v-for="item in items" :key="item.key">
        <label v-if="isUsable(item)" class="selection"><input v-model="item.selected" type="checkbox" @change="emitIds"><span>Usar</span></label>
        <div class="file-meta">
          <strong>{{ item.file.name }}</strong><small>{{ formatSize(item.file.size) }} · {{ item.message }}</small>
          <span v-if="item.phase === 'failed'" class="upload-error">{{ item.error }}</span>
        </div>
        <span class="file-state" :class="item.phase">{{ labelFor(item.phase) }}</span>
        <button type="button" :disabled="disabled || ['uploading','indexing'].includes(item.phase)" :aria-label="`Quitar ${item.file.name} de la selección`" @click="remove(item)">Quitar</button>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { listCaseDocuments, uploadCaseDocuments } from '@/services/documentService.js'

const props = defineProps({
  caseId: { type:String, required:true },
  disabled: { type:Boolean, default:false },
  initialDocumentIds: { type:Array, default:() => [] },
  loadExisting: { type:Boolean, default:false }
})
const emit = defineEmits(['update:documentIds'])
const items = ref([])
const error = ref('')
const batchBusy = ref(false)
const stage = ref('')
const stageMessage = ref('')
const uploadProgress = ref(0)
const completedDocuments = ref(null)
const totalDocuments = ref(0)
let sequence = 0
let activeController = null

const stageLabels = {
  validating:'Validando formato, tamaño e identidad', extracting:'Extrayendo texto y páginas',
  normalizing:'Normalizando el contenido extraído', chunking:'Fragmentando por contenido y procedencia',
  indexing:'Indexando fragmentos con embeddings', finalizing:'Finalizando el corpus',
  completed:'Procesamiento documental completado', uploaded:'Archivos recibidos'
}

watch(() => props.caseId, () => {
  activeController?.abort()
  items.value = []
  error.value = ''
  emitIds()
  loadExistingDocuments()
})

function isUsable(item) { return ['ready', 'ready_with_warnings'].includes(item.phase) }
function labelFor(phase) {
  return ({ready:'Listo', ready_with_warnings:'Listo con advertencias', ocr_required:'OCR requerido',
    failed:'Error', unknown:'Estado no confirmado', uploading:'Envío', indexing:'Procesando'})[phase] || 'Pendiente'
}
function emitIds() {
  emit('update:documentIds', [...new Set(items.value.filter(item => isUsable(item) && item.selected)
    .map(item => item.document?.document_id).filter(Boolean))])
}
function formatSize(size) {
  if (size < 1024 * 1024) return `${Math.ceil(size / 1024)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}
function presentOutcome(item, outcome) {
  if (outcome?.status === 'failed') {
    item.phase = 'failed'; item.error = outcome.error?.message || 'No se pudo procesar este documento.'
    item.message = 'No se incorporó al corpus'; item.selected = false
    return
  }
  const document = outcome?.document
  if (!document) return
  item.document = document
  item.phase = document.status === 'ready'
    ? (document.ocr_required ? 'ready_with_warnings' : 'ready')
    : 'ocr_required'
  item.selected = isUsable(item)
  item.message = item.phase === 'ready'
    ? (outcome.duplicate ? 'Documento existente; no se volvió a indexar' : `${document.chunk_count} fragmentos indexados`)
    : item.phase === 'ready_with_warnings'
      ? `${document.chunk_count} fragmentos indexados; OCR pendiente en algunas páginas`
      : 'No se detectó texto suficiente; requiere OCR y no se usará en el análisis'
}

async function loadExistingDocuments() {
  if (!props.loadExisting) return
  const caseId = props.caseId
  try {
    const documents = await listCaseDocuments(caseId)
    if (caseId !== props.caseId) return
    items.value = documents.map(document => {
      const phase = document.status === 'ready'
        ? (document.ocr_required ? 'ready_with_warnings' : 'ready') : 'ocr_required'
      return { key:`existing:${document.document_id}`, file:{name:document.filename, size:document.size_bytes},
        document, phase, selected:phase.startsWith('ready') && props.initialDocumentIds.includes(document.document_id),
        existing:true, message:phase.startsWith('ready')
          ? `${document.chunk_count} fragmentos disponibles${document.ocr_required ? '; OCR pendiente en algunas páginas' : ''}`
          : 'OCR requerido; no se usará en el análisis' }
    })
    emitIds()
  } catch (failure) { error.value = failure.message }
}

async function choose(event) {
  const files = [...(event.target.files || [])]
  event.target.value = ''
  if (!files.length || batchBusy.value) return
  error.value = ''
  activeController = new AbortController()
  const batchItems = files.map(file => {
    const item = { key:++sequence, file, phase:'uploading', selected:false, progress:0, message:'Enviando archivo' }
    items.value.push(item)
    return item
  })
  batchBusy.value = true
  stage.value = 'uploading'
  stageMessage.value = 'Enviando archivos seleccionados'
  totalDocuments.value = files.length
  completedDocuments.value = 0
  try {
    const outcomes = await uploadCaseDocuments(files, props.caseId, {
      signal:activeController.signal,
      onProgress:progress => { uploadProgress.value = progress },
      onTaskProgress:task => {
        stage.value = task.stage
        stageMessage.value = stageLabels[task.stage] || 'Procesamiento documental en curso'
        completedDocuments.value = task.completed_documents
        totalDocuments.value = task.total_documents
        task.documents?.forEach((outcome, index) => {
          const item = batchItems[index]
          if (!item) return
          if (!['ready', 'ocr_required', 'failed'].includes(outcome.status)) {
            item.phase = task.current_document_index === index + 1 ? 'indexing' : 'uploading'
            item.message = task.current_document_index === index + 1
              ? `${stageLabels[outcome.status] || stageMessage.value}${task.current_units ? ` · ${task.current_units} unidades procesadas` : ''}`
              : 'En espera de procesamiento'
          } else presentOutcome(item, outcome)
        })
        emitIds()
      }
    })
    outcomes.forEach((outcome, index) => presentOutcome(batchItems[index], outcome))
    emitIds()
  } catch (failure) {
    if (failure.name !== 'AbortError') {
      error.value = failure.message
      batchItems.filter(item => ['uploading','indexing'].includes(item.phase)).forEach(item => {
        item.phase = 'unknown'; item.error = failure.message; item.message = 'No se pudo confirmar el resultado de la ingesta'
      })
    }
  } finally {
    batchBusy.value = false
    activeController = null
    if (stage.value !== 'completed') stageMessage.value = ''
    emitIds()
  }
}

function remove(item) {
  if (item.existing) item.selected = false
  else items.value = items.value.filter(candidate => candidate !== item)
  emitIds()
}

onMounted(loadExistingDocuments)
onBeforeUnmount(() => activeController?.abort())
</script>

<style scoped>
.document-upload{margin:20px 0;padding:18px;border:1px solid #d9e0e8;border-radius:10px;background:#fff}.upload-heading{display:flex;align-items:center;justify-content:space-between;gap:16px}.upload-heading p{margin:5px 0;color:#647487;font-size:.9rem}.choose-files{position:relative;overflow:hidden;padding:9px 13px;border:1px solid #315c97;border-radius:7px;color:#17375e;cursor:pointer;white-space:nowrap}.choose-files input{position:absolute;inset:0;opacity:0;cursor:pointer}.choose-files.disabled{opacity:.5}.batch-progress{display:grid;gap:6px;margin-top:14px;color:#52657a;font-size:.88rem}.batch-progress progress{width:min(100%,480px);height:9px}.file-list{list-style:none;margin:16px 0 0;padding:0}.file-list li{display:flex;align-items:flex-start;gap:16px;padding:12px 0;border-top:1px solid #edf0f3}.selection{display:flex;align-items:center;gap:5px;color:#52657a;font-size:.8rem}.file-meta{display:grid;flex:1;gap:5px;min-width:0}.file-meta strong{overflow-wrap:anywhere}.file-meta small{color:#647487}.file-state{font-size:.85rem}.file-state.ready{color:#267254}.file-state.ready_with_warnings{color:#866510}.file-state.failed,.upload-error{color:#a32d32}.file-list button{border:0;background:transparent;color:#315c97;cursor:pointer}.file-list button:disabled{opacity:.45;cursor:wait}.upload-error{margin:10px 0}@media(max-width:600px){.upload-heading{align-items:flex-start;flex-direction:column}.file-list li{flex-wrap:wrap}}
</style>
