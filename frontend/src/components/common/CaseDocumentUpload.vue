<template>
  <section class="document-upload" aria-label="Documentos de este expediente">
    <div class="upload-heading">
      <div><strong>{{ libraryMode ? 'Archivos del caso' : 'Documentos del expediente' }}</strong><p>PDF, DOCX y TXT · privados para este caso</p></div>
      <label class="choose-files" :class="{disabled: disabled || batchBusy}">Subir documento
        <input type="file" multiple accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain" :disabled="disabled || batchBusy || !caseId" @change="choose">
      </label>
    </div>
    <div v-if="error" class="upload-error" role="alert"><span>{{ error }}</span><button v-if="documentListFailed" type="button" :disabled="loadingDocuments" @click="loadExistingDocuments">{{ loadingDocuments ? 'Cargando…' : 'Reintentar' }}</button></div>
    <div v-if="batchBusy" class="batch-progress" aria-live="polite">
      <span>{{ stageMessage }}</span>
      <progress v-if="stage === 'uploading'" max="100" :value="uploadProgress" aria-label="Progreso real del envío" />
      <span v-else-if="completedDocuments !== null">{{ completedDocuments }} de {{ totalDocuments }} documentos completados</span>
    </div>
    <p v-if="libraryMode && loadingDocuments" class="library-state" role="status">Cargando documentos…</p>
    <p v-else-if="libraryMode && !items.length && !error" class="library-state">Aún no has agregado documentos.</p>
    <ul v-if="items.length" class="file-list">
      <li v-for="item in items" :key="item.key">
        <label v-if="!libraryMode && isUsable(item)" class="selection"><input v-model="item.selected" type="checkbox" @change="emitIds"><span>Usar</span></label>
        <div class="file-meta">
          <strong>{{ item.file.name }}</strong><small>{{ formatType(item.document || item.file) }} · {{ formatSize(item.file.size) }} · {{ item.message }}</small>
          <small v-if="libraryMode && item.document?.created_at">Agregado {{ formatDate(item.document.created_at) }}</small>
          <span v-if="item.phase === 'failed'" class="upload-error">{{ item.error }}</span>
        </div>
        <span class="file-state" :class="item.phase">{{ labelFor(item.phase) }}</span>
        <button v-if="item.existing && item.document && item.document.download_available !== false" type="button" :aria-label="`Descargar ${item.file.name}`" :disabled="downloadingKey === item.key" @click="download(item)">{{ downloadingKey === item.key ? 'Descargando…' : 'Descargar' }}</button>
        <button v-if="!libraryMode" type="button" :disabled="disabled || ['uploading','indexing'].includes(item.phase)" :aria-label="`Quitar ${item.file.name} de la selección`" @click="remove(item)">Quitar</button>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { downloadCaseDocument, listCaseDocuments, uploadCaseDocuments } from '@/services/documentService.js'
import { caseDocumentStatus, documentLibraryState, formatCaseActivityDate, formatDocumentSize, formatDocumentType, isPersistedCaseDocument } from '@/utils/caseActivityPresentation.js'

const props = defineProps({
  caseId: { type:String, required:true },
  disabled: { type:Boolean, default:false },
  initialDocumentIds: { type:Array, default:() => [] },
  loadExisting: { type:Boolean, default:false },
  libraryMode: { type:Boolean, default:false },
  initialDocuments: { type:Array, default:() => [] }
})
const emit = defineEmits(['update:documentIds','documents-updated'])
function itemForDocument(document) {
  const state = documentLibraryState(document)
  const phase = state === 'ready'
    ? (document.ocr_required ? 'ready_with_warnings' : 'ready')
    : state === 'processing' || state === 'uploaded' ? 'indexing'
      : state === 'failed' ? 'failed' : document.status === 'ready' ? 'ready' : 'ocr_required'
  const availableForAnalysis = phase === 'ready' || phase === 'ready_with_warnings'
  return { key:`existing:${document.document_id}`, file:{name:document.filename || document.original_filename || 'Documento del caso', size:document.size_bytes},
    document, phase, selected:availableForAnalysis && props.initialDocumentIds.includes(document.document_id),
    existing:true, message:props.libraryMode ? caseDocumentStatus(state) : availableForAnalysis
      ? `${document.chunk_count ?? 0} fragmentos disponibles${document.ocr_required ? '; OCR pendiente en algunas páginas' : ''}`
      : state === 'processing' || state === 'uploaded' ? 'El archivo está guardado y su procesamiento continúa.'
        : state === 'failed' ? 'No fue posible procesar el archivo.' : 'OCR requerido; no se usará en el análisis' }
}
function visibleDocuments(documents) {
  return props.libraryMode ? documents.filter(isPersistedCaseDocument) : documents
}
const items = ref(visibleDocuments(props.initialDocuments).map(itemForDocument))
const error = ref('')
const loadingDocuments = ref(false)
const documentListFailed = ref(false)
const batchBusy = ref(false)
const stage = ref('')
const stageMessage = ref('')
const uploadProgress = ref(0)
const completedDocuments = ref(null)
const totalDocuments = ref(0)
const downloadingKey = ref(null)
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
  return ({ready:'Disponible', ready_with_warnings:'Disponible · OCR pendiente', ocr_required:'OCR requerido',
    failed:'Error', unknown:'Estado no confirmado', uploading:'Subiendo', indexing:'Procesando'})[phase] || 'Pendiente'
}
function emitIds() {
  emit('update:documentIds', [...new Set(items.value.filter(item => isUsable(item) && item.selected)
    .map(item => item.document?.document_id).filter(Boolean))])
}
function formatSize(size) { return formatDocumentSize(size) }
function formatType(document) { return formatDocumentType(document) }
function formatDate(value) { return formatCaseActivityDate(value) }
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
  loadingDocuments.value = true
  error.value = ''
  documentListFailed.value = false
  try {
    const documents = await listCaseDocuments(caseId)
    if (caseId !== props.caseId) return
    const durableDocuments = visibleDocuments(documents)
    items.value = durableDocuments.map(itemForDocument)
    emitIds()
    emit('documents-updated', durableDocuments)
  } catch { error.value = 'No fue posible cargar los documentos del caso. Inténtalo nuevamente.'; documentListFailed.value = true }
  finally { if (caseId === props.caseId) loadingDocuments.value = false }
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
        const stageText = stageLabels[task.stage] || 'Procesamiento documental en curso'
        stageMessage.value = task.status === 'queued'
          ? 'Documento guardado. En espera de procesamiento.'
          : `Documento guardado. ${stageText}`
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
    if (props.loadExisting) await loadExistingDocuments()
  } catch (failure) {
    if (failure.name !== 'AbortError') {
      error.value = 'No fue posible completar la carga del documento. Inténtalo nuevamente.'
      batchItems.filter(item => ['uploading','indexing'].includes(item.phase)).forEach(item => {
        item.phase = 'unknown'; item.error = error.value; item.message = 'No se pudo confirmar el resultado de la ingesta'
      })
    }
  } finally {
    batchBusy.value = false
    activeController = null
    if (stage.value !== 'completed') stageMessage.value = ''
    emitIds()
  }
}

async function download(item) {
  if (downloadingKey.value) return
  downloadingKey.value = item.key
  error.value = ''
  try { await downloadCaseDocument(props.caseId, item.document) }
  catch { error.value = 'No fue posible descargar el documento. Inténtalo nuevamente.' }
  finally { downloadingKey.value = null }
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
.choose-files:focus-within{outline:2px solid #b68a3a;outline-offset:3px}.upload-error button{margin-left:10px;border:0;background:transparent;color:#17324f;text-decoration:underline;font:inherit;font-weight:600;cursor:pointer}.upload-error button:focus-visible,.file-list button:focus-visible{outline:2px solid #b68a3a;outline-offset:3px}
</style>
