<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import CaseDocumentUpload from '@/components/common/CaseDocumentUpload.vue'
import { caseRunStatus, caseToolName, formatCaseActivityDate, isPersistedCaseDocument } from '@/utils/caseActivityPresentation.js'

const props = defineProps({ caseRecord:{ type:Object, default:null }, runs:{ type:Array, default:() => [] }, documents:{ type:Array, default:() => [] }, loading:Boolean, error:{ type:String, default:'' }, onUpdateCase:{ type:Function, default:async() => { throw new Error('CASE_UPDATE_UNAVAILABLE') } } })
const emit = defineEmits(['retry','back','continue-case','documents-updated'])
const renameOpen = ref(false), renameValue = ref(''), renameBusy = ref(false), mutationError = ref(''), confirmArchive = ref(false), archiveBusy = ref(false)
const renameInput = ref(null), renameButton = ref(null)
const activeSection = ref('history')
const durableDocumentCount = computed(() => props.documents.filter(isPersistedCaseDocument).length)
function moveSection(event) {
  if (!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return
  event.preventDefault()
  activeSection.value = event.key === 'Home' || event.key === 'ArrowLeft' ? 'history' : 'documents'
  nextTick(() => document.getElementById(`${activeSection.value}-tab`)?.focus())
}
watch(() => props.caseRecord?.title, value => { if (!renameOpen.value) renameValue.value = value || '' })
watch(renameOpen, async open => { if (open) { mutationError.value = ''; await nextTick(); renameInput.value?.focus(); renameInput.value?.select() } })
function date(value) { return formatCaseActivityDate(value) }
function toolName(tool) { return caseToolName(tool) }
function historicalLink(run, caseId) { return `/?tool=${encodeURIComponent(run.tool)}&case_id=${encodeURIComponent(caseId)}&run_id=${encodeURIComponent(run.id)}` }
function openRename() { renameValue.value = props.caseRecord?.title || ''; renameOpen.value = true }
function closeRename() { if (renameBusy.value) return; renameOpen.value = false; mutationError.value = ''; nextTick(() => renameButton.value?.focus()) }
async function saveRename() {
  if (renameBusy.value || !props.caseRecord) return
  const title = renameValue.value.trim()
  if (!title || title.length > 240) { mutationError.value = 'El título es obligatorio y admite hasta 240 caracteres.'; return }
  renameBusy.value = true; mutationError.value = ''
  try { await props.onUpdateCase(props.caseRecord.id, { title }); renameOpen.value = false }
  catch { mutationError.value = 'No fue posible cambiar el título. Inténtalo nuevamente.' }
  finally { renameBusy.value = false }
}
async function restoreCase() {
  if (archiveBusy.value || !props.caseRecord) return
  archiveBusy.value = true; mutationError.value = ''
  try { await props.onUpdateCase(props.caseRecord.id, { status:'active' }) }
  catch { mutationError.value = 'No fue posible restaurar el caso. Inténtalo nuevamente.' }
  finally { archiveBusy.value = false }
}
async function archiveCase() {
  if (archiveBusy.value || !props.caseRecord) return
  archiveBusy.value = true; mutationError.value = ''
  try { await props.onUpdateCase(props.caseRecord.id, { status:'archived' }); confirmArchive.value = false }
  catch { mutationError.value = 'No fue posible archivar el caso. Inténtalo nuevamente.' }
  finally { archiveBusy.value = false }
}
</script>

<template>
  <section class="case-detail" aria-labelledby="case-detail-title">
    <button class="back-link" type="button" @click="$emit('back')">← <span>Mis casos</span></button>
    <div v-if="loading" class="detail-loading" role="status">Cargando la información del caso…</div>
    <div v-else-if="error" class="detail-error" role="alert"><h1>No fue posible abrir el caso</h1><p>{{ error }}</p><button type="button" @click="$emit('retry')">Reintentar</button></div>
    <div v-else-if="caseRecord" class="detail-content">
      <header class="detail-heading"><div><p class="page-kicker">EXPEDIENTE · {{ caseRecord.status === 'archived' ? 'ARCHIVADO' : 'ACTIVO' }}</p><h1 id="case-detail-title">{{ caseRecord.title || 'Caso jurídico' }}</h1><p>{{ caseRecord.description || 'Información y actividad guardadas para este caso.' }}</p>
        <div class="case-actions"><button ref="renameButton" type="button" @click="openRename">Renombrar</button><button v-if="caseRecord.status !== 'archived'" type="button" class="archive-action" @click="confirmArchive = true">Archivar</button><button v-else type="button" :disabled="archiveBusy" @click="restoreCase">{{ archiveBusy ? 'Restaurando…' : 'Restaurar' }}</button></div>
      </div><button class="primary-action" type="button" @click="$emit('continue-case', caseRecord)">Continuar en NovaCase</button></header>
      <p v-if="mutationError && !renameOpen && !confirmArchive" role="alert" class="mutation-error">{{ mutationError }}</p>
      <div class="case-sections">
        <div class="section-tabs" role="tablist" aria-label="Contenido del caso">
          <button id="history-tab" type="button" role="tab" :aria-selected="activeSection === 'history'" aria-controls="history-panel" :tabindex="activeSection === 'history' ? 0 : -1" @keydown="moveSection" @click="activeSection = 'history'">Historial <span>{{ runs.length }}</span></button>
          <button id="documents-tab" type="button" role="tab" :aria-selected="activeSection === 'documents'" aria-controls="documents-panel" :tabindex="activeSection === 'documents' ? 0 : -1" @keydown="moveSection" @click="activeSection = 'documents'">Documentos <span>{{ durableDocumentCount }}</span></button>
        </div>
        <section id="history-panel" class="detail-section" role="tabpanel" aria-labelledby="history-tab" v-show="activeSection === 'history'">
          <header><div><p class="page-kicker">ACTIVIDAD DEL EXPEDIENTE</p><h2>Historial de análisis</h2></div></header>
          <p v-if="!runs.length" class="section-empty">Aún no hay análisis en este caso.</p>
          <ol v-else class="run-list"><li v-for="run in runs" :key="run.id"><div class="run-marker" :class="`state-${run.status}`" aria-hidden="true"></div><div class="run-copy"><strong>{{ toolName(run.tool) }}</strong><span class="run-status">{{ caseRunStatus(run.status) }}</span><small>{{ date(run.created_at || run.started_at) }}</small><small v-if="run.tool === 'court' && run.parent_run_id" class="run-relation">Relacionado con un análisis NovaCase</small></div><a v-if="['case','court'].includes(run.tool) && ['completed','partial'].includes(run.status)" :href="historicalLink(run,caseRecord.id)" :aria-label="`Abrir resultado histórico de ${toolName(run.tool)} · ${date(run.created_at || run.started_at)}`">Abrir resultado <span aria-hidden="true">→</span></a></li></ol>
        </section>
        <section id="documents-panel" class="detail-section documents-section" role="tabpanel" aria-labelledby="documents-tab" v-show="activeSection === 'documents'">
          <CaseDocumentUpload :key="caseRecord.id" :case-id="caseRecord.id" :load-existing="true" :library-mode="true" :initial-documents="documents" @documents-updated="emit('documents-updated',$event)" />
        </section>
      </div>
    </div>
    <div v-if="renameOpen" class="dialog-backdrop" @keydown.esc="closeRename" @click.self="closeRename"><section class="case-dialog" role="dialog" aria-modal="true" aria-labelledby="rename-case-title"><button class="dialog-close" type="button" aria-label="Cerrar" :disabled="renameBusy" @click="closeRename">×</button><p class="page-kicker">EDITAR EXPEDIENTE</p><h2 id="rename-case-title">Renombrar caso</h2><form @submit.prevent="saveRename"><label>Nuevo título<input ref="renameInput" v-model="renameValue" required maxlength="240"></label><p v-if="mutationError" role="alert" class="mutation-error">{{ mutationError }}</p><div class="dialog-actions"><button type="button" :disabled="renameBusy" @click="closeRename">Cancelar</button><button class="primary-action" type="submit" :disabled="renameBusy">{{ renameBusy ? 'Guardando…' : 'Guardar' }}</button></div></form></section></div>
    <div v-if="confirmArchive" class="dialog-backdrop" @keydown.esc="confirmArchive = false" @click.self="confirmArchive = false"><section class="case-dialog" role="dialog" aria-modal="true" aria-labelledby="archive-case-title"><p class="page-kicker">CONFIRMAR ACCIÓN</p><h2 id="archive-case-title">Archivar caso</h2><p>El caso, sus documentos y su historial se conservarán. Podrás restaurarlo cuando quieras.</p><p v-if="mutationError" role="alert" class="mutation-error">{{ mutationError }}</p><div class="dialog-actions"><button type="button" :disabled="archiveBusy" @click="confirmArchive = false">Cancelar</button><button type="button" class="danger-action" :disabled="archiveBusy" @click="archiveCase">{{ archiveBusy ? 'Archivando…' : 'Archivar' }}</button></div></section></div>
  </section>
</template>

<style scoped>
.case-detail{width:min(1120px,100%);margin:0 auto}.back-link{border:0;background:none;color:#526b80;cursor:pointer;font:600 13px Inter,system-ui,sans-serif;padding:5px 0}.back-link span{text-decoration:underline;text-underline-offset:3px}.back-link:focus-visible,.detail-error button:focus-visible,.primary-action:focus-visible{outline:2px solid #b68a3a;outline-offset:3px}.detail-loading,.detail-error{margin:40px 0;padding:22px;border:1px solid #e0e5e8;border-radius:8px;background:#fffdfa;color:#52677a}.detail-error h1{font:normal 25px Georgia,serif;color:#17324f}.detail-error p{margin:9px 0 14px}.detail-error button{padding:9px 14px;border:1px solid #cbd4db;border-radius:6px;background:#fff;color:#17324f}.detail-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;margin:27px 0 31px;padding-bottom:27px;border-bottom:1px solid #dfe4e7}.page-kicker{color:#9a7c50;font-size:10px;font-weight:700;letter-spacing:.16em}.detail-heading h1{margin:9px 0;font:normal clamp(30px,4vw,43px)/1.15 Georgia,serif;color:#15314e;overflow-wrap:anywhere}.detail-heading p:not(.page-kicker){max-width:690px;color:#64768a;font-size:14px;line-height:1.6}.primary-action{flex:none;border:0;border-radius:7px;background:#17324f;color:white;padding:12px 16px;font-weight:600;cursor:pointer}.case-actions{display:flex;flex-wrap:wrap;gap:7px;margin-top:15px}.case-actions button{padding:8px 11px;border:1px solid #d6dee4;border-radius:6px;background:white;color:#34536e;font-size:12px;font-weight:600;cursor:pointer}.case-actions button:hover{background:#f4f6f6}.case-actions .archive-action{color:#83564d}.mutation-error{color:#9b4d43;font-size:13px}.detail-columns{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:22px}.detail-section{min-width:0;padding:22px 23px;background:#fffdfa;border:1px solid #e0e5e8;border-radius:9px}.detail-section>header{display:flex;align-items:center;justify-content:space-between;padding-bottom:17px;border-bottom:1px solid #e7eaec}.detail-section h2{margin-top:6px;font:normal 23px Georgia,serif;color:#17324f}.section-count{display:grid;place-items:center;min-width:28px;height:28px;border-radius:50%;background:#f0eadf;color:#876c43;font-size:12px;font-weight:700}.section-empty{padding:20px 0;color:#718091;font-size:13px}.document-list,.run-list{list-style:none;margin:0;padding:0}.document-list li{display:flex;align-items:center;gap:12px;padding:14px 0;border-bottom:1px solid #edf0f1}.document-list li:last-child,.run-list li:last-child{border-bottom:0}.document-type{display:grid;place-items:center;flex:none;width:39px;height:39px;border-radius:7px;background:#edf2f3;color:#426176;font-size:9px;font-weight:700}.document-copy,.run-copy{display:grid;gap:4px;min-width:0}.document-copy strong,.run-copy strong{overflow-wrap:anywhere;color:#263f57;font-size:13px}.document-copy small,.run-copy small{color:#758494;font-size:11px}.run-list li{position:relative;display:flex;align-items:center;gap:13px;padding:15px 0;border-bottom:1px solid #edf0f1}.run-marker{flex:none;width:9px;height:9px;border-radius:50%;background:#b89b6b;box-shadow:0 0 0 4px #f1ece3}.run-copy{flex:1}.run-status{color:#50697c;font-size:11px}.run-list a{color:#254d6b;text-decoration:none;font-size:12px;font-weight:700}.run-list a:hover{text-decoration:underline}.run-list a:focus-visible,.case-actions button:focus-visible{outline:2px solid #b68a3a;outline-offset:3px}.dialog-backdrop{position:fixed;inset:0;z-index:80;display:grid;place-items:center;padding:20px;background:#12283db8}.case-dialog{position:relative;width:min(490px,100%);padding:29px;border:1px solid #dce1e5;border-radius:12px;background:#fffdfa;box-shadow:0 22px 70px #10233840}.case-dialog h2{margin:8px 0 18px;color:#17324f;font:normal 27px Georgia,serif}.case-dialog label{display:grid;gap:8px;color:#445a6d;font-size:12px;font-weight:600}.case-dialog input{width:100%;box-sizing:border-box;padding:11px;border:1px solid #ccd6dd;border-radius:6px;background:white;color:#243f56}.case-dialog input:focus{outline:2px solid #91aabe;outline-offset:1px}.case-dialog form{display:grid;gap:15px}.dialog-actions{display:flex;justify-content:flex-end;gap:9px;margin-top:7px}.dialog-actions button{padding:10px 14px;border:1px solid #cbd4db;border-radius:6px;background:white;color:#28445d;font-weight:600;cursor:pointer}.dialog-actions button:focus-visible,.dialog-close:focus-visible{outline:2px solid #b68a3a;outline-offset:2px}.dialog-actions .primary-action{border-color:#17324f;background:#17324f;color:#fff}.danger-action{border-color:#a65248!important;color:#934a42!important}.dialog-close{position:absolute;right:14px;top:12px;border:0;background:none;color:#627487;font-size:23px;cursor:pointer}.dialog-close:focus-visible{outline:2px solid #b68a3a;outline-offset:2px}.dialog-actions button:disabled{opacity:.6;cursor:wait}@media(max-width:780px){.detail-heading{align-items:flex-start;flex-direction:column}.detail-columns{grid-template-columns:1fr}}
.case-sections{min-width:0}.section-tabs{display:flex;gap:7px;border-bottom:1px solid #dfe4e7;margin-bottom:18px}.section-tabs button{display:flex;align-items:center;gap:9px;padding:12px 14px;border:0;border-bottom:2px solid transparent;background:transparent;color:#64768a;font:600 13px Inter,system-ui,sans-serif;cursor:pointer}.section-tabs button[aria-selected="true"]{border-color:#b68a3a;color:#17324f}.section-tabs button span{display:grid;place-items:center;min-width:20px;height:20px;padding:0 4px;border-radius:10px;background:#f0eadf;color:#876c43;font-size:10px}.section-tabs button:focus-visible{outline:2px solid #b68a3a;outline-offset:2px}.documents-section{padding:0;border:0;background:transparent}.documents-section :deep(.document-upload){margin:0;padding:22px 23px;border:1px solid #e0e5e8;border-radius:9px;background:#fffdfa}.run-marker.state-completed{background:#527d68}.run-marker.state-failed,.run-marker.state-timeout{background:#9b6259}.run-marker.state-processing,.run-marker.state-running{background:#b68a3a}.run-relation{color:#967847!important}.documents-section :deep(.file-list li){align-items:center}.documents-section :deep(.file-meta){gap:5px}.documents-section :deep(.file-state){flex:none;color:#52697a}.documents-section :deep(.file-state.ready){color:#527d68}.documents-section :deep(.file-state.failed){color:#9b6259}.documents-section :deep(.file-list button){padding:7px 10px;border:1px solid #d6dee4;border-radius:6px;background:#fff;color:#254d6b;font-size:12px;font-weight:600}.documents-section :deep(.library-state){padding:18px 0;color:#718091;font-size:13px}.documents-section :deep(.upload-error){font-size:13px}
</style>
