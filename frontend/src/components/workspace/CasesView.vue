<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { filterOwnedCases } from '@/services/workspaceService.js'

const props = defineProps({
  cases:{ type:Array, default:() => [] }, loading:Boolean, error:{ type:String, default:'' },
  onCreateCase:{ type:Function, default:async() => { throw new Error('CASE_CREATE_UNAVAILABLE') } },
  onUpdateCase:{ type:Function, default:async() => { throw new Error('CASE_UPDATE_UNAVAILABLE') } }
})
const emit = defineEmits(['retry','open-case'])
const search = ref(''), filter = ref('active'), createOpen = ref(false), createTitle = ref(''), createDescription = ref('')
const createBusy = ref(false), createError = ref(''), renameTarget = ref(null), renameTitle = ref(''), renameBusy = ref(false)
const archiveTarget = ref(null), archiveBusy = ref(false), mutationError = ref('')
const createTitleInput = ref(null), renameTitleInput = ref(null), addButton = ref(null)
const visibleCases = computed(() => filterOwnedCases(props.cases, search.value, filter.value))
const emptyMessage = computed(() => search.value.trim()
  ? `No encontramos casos para “${search.value.trim()}”.`
  : filter.value === 'archived' ? 'No hay casos archivados.' : 'Aún no tienes casos.')
watch(createOpen, async open => { if (open) { createError.value = ''; await nextTick(); createTitleInput.value?.focus() } })
watch(renameTarget, async target => { if (target) { await nextTick(); renameTitleInput.value?.focus(); renameTitleInput.value?.select() } })
function formatDate(value) {
  if (!value) return 'Sin actividad registrada'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'Sin actividad registrada' : new Intl.DateTimeFormat('es-PE', { dateStyle:'medium' }).format(date)
}
function closeCreate() { if (createBusy.value) return; createOpen.value = false; createTitle.value = ''; createDescription.value = ''; createError.value = ''; nextTick(() => addButton.value?.focus()) }
async function submitCreate() {
  if (createBusy.value) return
  const title = createTitle.value.trim(), description = createDescription.value.trim()
  if (!title || title.length > 240 || description.length > 4000) { createError.value = 'El título es obligatorio y admite hasta 240 caracteres. La descripción admite hasta 4.000.'; return }
  createBusy.value = true; createError.value = ''
  try { const created = await props.onCreateCase({ title, description }); createBusy.value = false; closeCreate(); emit('open-case', created) }
  catch { createError.value = 'No fue posible crear el caso. Inténtalo nuevamente.' }
  finally { createBusy.value = false }
}
function beginRename(item) { renameTarget.value = item; renameTitle.value = item.title || ''; mutationError.value = '' }
function closeRename() { if (renameBusy.value) return; const id = renameTarget.value?.id || renameTarget.value?.case_id; renameTarget.value = null; mutationError.value = ''; nextTick(() => document.querySelector(`[data-case-id="${CSS.escape(String(id || ''))}"]`)?.focus()) }
async function submitRename() {
  if (renameBusy.value || !renameTarget.value) return
  const title = renameTitle.value.trim()
  if (!title || title.length > 240) { mutationError.value = 'El título es obligatorio y admite hasta 240 caracteres.'; return }
  const target = renameTarget.value
  renameBusy.value = true; mutationError.value = ''
  try { await props.onUpdateCase(target.id || target.case_id, { title }); renameTarget.value = null }
  catch { mutationError.value = 'No fue posible cambiar el título. Inténtalo nuevamente.' }
  finally { renameBusy.value = false }
}
async function confirmArchive() {
  if (archiveBusy.value || !archiveTarget.value) return
  const target = archiveTarget.value
  archiveBusy.value = true; mutationError.value = ''
  try { await props.onUpdateCase(target.id || target.case_id, { status:'archived' }); archiveTarget.value = null }
  catch { mutationError.value = 'No fue posible archivar el caso. Inténtalo nuevamente.' }
  finally { archiveBusy.value = false }
}
async function restore(item) {
  if (archiveBusy.value) return
  archiveBusy.value = true; mutationError.value = ''
  try { await props.onUpdateCase(item.id || item.case_id, { status:'active' }) }
  catch { mutationError.value = 'No fue posible restaurar el caso. Inténtalo nuevamente.' }
  finally { archiveBusy.value = false }
}
</script>

<template>
  <section class="cases-page" aria-labelledby="cases-title">
    <header class="page-heading">
      <div><p class="page-kicker">ESPACIO PERSONAL</p><h1 id="cases-title">Mis casos</h1><p>Expedientes y análisis guardados en tu espacio de trabajo.</p></div>
      <button ref="addButton" class="primary-action" type="button" @click="createOpen = true">Nuevo caso</button>
    </header>

    <div class="case-controls" aria-label="Buscar y filtrar casos">
      <label class="case-search"><span class="sr-only">Buscar por título o descripción</span><input v-model="search" type="search" placeholder="Buscar casos…" autocomplete="off"><button v-if="search" type="button" aria-label="Limpiar búsqueda" @click="search = ''">Limpiar</button></label>
      <div class="case-filters" role="group" aria-label="Filtrar casos por estado">
        <button v-for="item in [{id:'active',label:'Activos'},{id:'archived',label:'Archivados'},{id:'all',label:'Todos'}]" :key="item.id" type="button" :aria-pressed="filter === item.id" :class="{selected:filter === item.id}" @click="filter = item.id">{{ item.label }}</button>
      </div>
    </div>
    <p v-if="mutationError" class="mutation-error" role="alert">{{ mutationError }}</p>
    <div v-if="loading" class="case-grid" role="status" aria-label="Cargando casos"><div v-for="n in 3" :key="n" class="case-skeleton"><span></span><span></span><span></span></div></div>
    <div v-else-if="error" class="cases-message cases-error" role="alert"><h2>No fue posible cargar tus casos</h2><p>{{ error }}</p><button type="button" @click="emit('retry')">Reintentar</button></div>
    <div v-else-if="visibleCases.length === 0" class="cases-message cases-empty">
      <span class="empty-mark" aria-hidden="true">MYKE</span><h2>{{ emptyMessage }}</h2>
      <p v-if="!search.trim() && filter === 'active'">Crea tu primer caso para comenzar a organizar el trabajo jurídico.</p>
      <button v-if="!search.trim() && filter === 'active'" class="primary-action" type="button" @click="createOpen = true">Crear un caso</button>
      <button v-else-if="search.trim()" type="button" class="clear-search" @click="search = ''">Limpiar búsqueda</button>
    </div>
    <ul v-else class="case-grid" aria-label="Casos guardados">
      <li v-for="item in visibleCases" :key="item.id || item.case_id" class="case-card">
        <div class="case-card-top"><span class="case-status" :class="{ archived:item.status === 'archived' }">{{ item.status === 'archived' ? 'Archivado' : 'Activo' }}</span><span class="case-date">{{ formatDate(item.updated_at || item.created_at) }}</span>
          <details class="case-menu"><summary :aria-label="`Acciones para ${item.title || 'caso'}`">•••</summary><div class="case-menu-items"><button type="button" @click="beginRename(item)">Renombrar</button><button v-if="item.status !== 'archived'" type="button" @click="archiveTarget = item">Archivar</button><button v-else type="button" :disabled="archiveBusy" @click="restore(item)">{{ archiveBusy ? 'Restaurando…' : 'Restaurar' }}</button></div></details>
        </div>
        <h2>{{ item.title || 'Caso jurídico' }}</h2><p v-if="item.description" class="case-description">{{ item.description }}</p>
        <dl class="case-meta"><div><dt>Creado</dt><dd>{{ formatDate(item.created_at) }}</dd></div><div><dt>Última actividad</dt><dd>{{ formatDate(item.updated_at || item.created_at) }}</dd></div></dl>
        <button class="case-open" type="button" :data-case-id="item.id || item.case_id" @click="emit('open-case', item)">Ver caso <span aria-hidden="true">→</span></button>
      </li>
    </ul>

    <div v-if="createOpen" class="dialog-backdrop" @keydown.esc="closeCreate" @click.self="closeCreate">
      <section class="case-dialog" role="dialog" aria-modal="true" aria-labelledby="create-title">
        <button class="dialog-close" type="button" aria-label="Cerrar" :disabled="createBusy" @click="closeCreate">×</button><p class="page-kicker">NUEVO EXPEDIENTE</p><h2 id="create-title">Crear caso</h2>
        <form @submit.prevent="submitCreate"><label>Título <input ref="createTitleInput" v-model="createTitle" required maxlength="240" autocomplete="off" placeholder="Nombre del caso"></label><label>Descripción <textarea v-model="createDescription" maxlength="4000" rows="3" placeholder="Contexto breve, opcional"></textarea></label>
          <p v-if="createError" role="alert" class="dialog-error">{{ createError }}</p><div class="dialog-actions"><button type="button" :disabled="createBusy" @click="closeCreate">Cancelar</button><button class="primary-action" type="submit" :disabled="createBusy">{{ createBusy ? 'Creando…' : 'Crear caso' }}</button></div>
        </form>
      </section>
    </div>

    <div v-if="renameTarget" class="dialog-backdrop" @keydown.esc="closeRename" @click.self="closeRename">
      <section class="case-dialog" role="dialog" aria-modal="true" aria-labelledby="rename-title"><button class="dialog-close" type="button" aria-label="Cerrar" :disabled="renameBusy" @click="closeRename">×</button><p class="page-kicker">EDITAR EXPEDIENTE</p><h2 id="rename-title">Renombrar caso</h2>
        <form @submit.prevent="submitRename"><label>Nuevo título <input ref="renameTitleInput" v-model="renameTitle" required maxlength="240"></label><p v-if="mutationError" role="alert" class="dialog-error">{{ mutationError }}</p><div class="dialog-actions"><button type="button" :disabled="renameBusy" @click="closeRename">Cancelar</button><button class="primary-action" type="submit" :disabled="renameBusy">{{ renameBusy ? 'Guardando…' : 'Guardar' }}</button></div></form>
      </section>
    </div>

    <div v-if="archiveTarget" class="dialog-backdrop" @keydown.esc="archiveTarget = null" @click.self="archiveTarget = null">
      <section class="case-dialog" role="dialog" aria-modal="true" aria-labelledby="archive-title"><p class="page-kicker">CONFIRMAR ACCIÓN</p><h2 id="archive-title">Archivar caso</h2><p>El caso y sus documentos e historial se conservarán. Podrás restaurarlo cuando quieras.</p><p v-if="mutationError" role="alert" class="dialog-error">{{ mutationError }}</p><div class="dialog-actions"><button type="button" :disabled="archiveBusy" @click="archiveTarget = null">Cancelar</button><button class="danger-action" type="button" :disabled="archiveBusy" @click="confirmArchive">{{ archiveBusy ? 'Archivando…' : 'Archivar' }}</button></div></section>
    </div>
  </section>
</template>

<style scoped>
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.cases-page{width:min(1120px,100%);margin:0 auto}.page-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;padding:12px 0 27px;border-bottom:1px solid #dfe4e7}.page-kicker{color:#9a7c50;font-size:10px;font-weight:700;letter-spacing:.16em}.page-heading h1{margin:9px 0 7px;font:normal clamp(32px,4vw,44px)/1.12 Georgia,serif;color:#15314e}.page-heading p:last-child{color:#64768a;font-size:14px}.primary-action,.case-open{border:0;border-radius:7px;background:#17324f;color:#fff;padding:12px 17px;font-weight:600;cursor:pointer}.primary-action:hover,.case-open:hover{background:#254866}.primary-action:focus-visible,.case-open:focus-visible,.cases-message button:focus-visible,.case-menu summary:focus-visible,.case-menu button:focus-visible{outline:2px solid #b68a3a;outline-offset:3px}.case-controls{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:19px 0 0}.case-search{display:flex;align-items:center;gap:8px;width:min(390px,100%);padding:0 12px;border:1px solid #d9e0e5;border-radius:7px;background:#fff}.case-search:focus-within{border-color:#7692a8;box-shadow:0 0 0 2px #dce6ed}.case-search input{width:100%;min-width:0;border:0;outline:0;padding:11px 0;background:transparent;color:#263f57;font:13px inherit}.case-search button,.clear-search{border:0;background:none;color:#345c77;text-decoration:underline;cursor:pointer}.case-filters{display:flex;gap:5px}.case-filters button{border:1px solid transparent;border-radius:6px;background:transparent;color:#657587;padding:8px 11px;font-size:12px;cursor:pointer}.case-filters button.selected{border-color:#dce3e8;background:#f0f3f4;color:#1b3b56;font-weight:700}.case-filters button:focus-visible,.case-search button:focus-visible,.clear-search:focus-visible{outline:2px solid #b68a3a;outline-offset:2px}.mutation-error{color:#9b4d43;font-size:13px}.case-grid{list-style:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,310px),1fr));gap:16px;margin:21px 0 0;padding:0}.case-card,.case-skeleton,.cases-message{border:1px solid #e0e5e8;border-radius:10px;background:#fffdfa}.case-card{display:flex;flex-direction:column;min-height:226px;padding:19px}.case-card-top{display:flex;align-items:center;gap:10px}.case-status{border-radius:99px;background:#e9f2ed;color:#416b55;padding:5px 9px;font-size:10px;font-weight:700}.case-status.archived{background:#f1eee7;color:#776950}.case-date,.case-meta{color:#6b7b8b;font-size:11px}.case-card h2{margin:17px 0 8px;font:normal 21px/1.25 Georgia,serif;color:#17324f;overflow-wrap:anywhere}.case-description{margin:0;color:#617286;font-size:13px;line-height:1.55;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.case-meta{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:18px 0}.case-meta dt{color:#8a9299;font-size:10px}.case-meta dd{margin:4px 0 0;color:#42596e;font-weight:600}.case-open{display:flex;justify-content:space-between;align-items:center;margin-top:auto;text-align:left}.case-menu{position:relative;margin-left:auto}.case-menu summary{list-style:none;cursor:pointer;color:#65798b;border-radius:5px;padding:3px 7px}.case-menu summary::-webkit-details-marker{display:none}.case-menu summary:hover{background:#eef1f2}.case-menu-items{position:absolute;right:0;top:30px;z-index:2;display:grid;min-width:140px;padding:5px;border:1px solid #dfe4e7;border-radius:7px;background:#fff;box-shadow:0 8px 24px #18344d20}.case-menu-items button{border:0;border-radius:4px;background:transparent;color:#314c64;text-align:left;padding:9px;font-size:12px;cursor:pointer}.case-menu-items button:hover{background:#f2f4f5}.case-menu-items button:disabled{opacity:.6}.cases-message{max-width:650px;margin:48px auto;padding:40px 30px;text-align:center}.cases-message h2{font:normal 24px Georgia,serif;color:#17324f}.cases-message p{margin:10px auto 20px;max-width:440px;color:#68798a;line-height:1.6;font-size:14px}.cases-error{border-left:3px solid #a65248}.cases-message button:not(.primary-action){padding:10px 15px;border:1px solid #cbd4db;border-radius:6px;background:#fff;color:#17324f;cursor:pointer}.empty-mark{display:grid;place-items:center;width:54px;height:54px;margin:0 auto 15px;border-radius:50%;background:#f0eadf;color:#94744a;font:14px Georgia,serif;letter-spacing:.08em}.case-skeleton{height:226px;padding:24px;display:grid;align-content:start;gap:14px}.case-skeleton span{height:13px;border-radius:8px;background:linear-gradient(90deg,#edf0f2,#f8f7f3,#edf0f2);background-size:200% 100%;animation:shimmer 1.4s infinite}.case-skeleton span:nth-child(2){width:72%;height:28px;margin-top:17px}.case-skeleton span:nth-child(3){width:48%;margin-top:28px}@keyframes shimmer{to{background-position:-200% 0}}.dialog-backdrop{position:fixed;inset:0;z-index:80;display:grid;place-items:center;padding:20px;background:#12283db8}.case-dialog{position:relative;width:min(490px,100%);padding:29px;border:1px solid #dce1e5;border-radius:12px;background:#fffdfa;box-shadow:0 22px 70px #10233840}.case-dialog h2{margin:8px 0 18px;color:#17324f;font:normal 27px Georgia,serif}.case-dialog>p:not(.page-kicker){color:#657587;font-size:13px;line-height:1.55}.case-dialog form,.case-dialog form label{display:grid;gap:8px}.case-dialog form{gap:16px}.case-dialog form label{color:#445a6d;font-size:12px;font-weight:600}.case-dialog input,.case-dialog textarea{width:100%;box-sizing:border-box;padding:11px;border:1px solid #ccd6dd;border-radius:6px;background:white;color:#243f56;font:14px inherit}.case-dialog input:focus,.case-dialog textarea:focus{outline:2px solid #91aabe;outline-offset:1px}.dialog-close{position:absolute;right:14px;top:12px;border:0;background:none;color:#627487;font-size:23px;cursor:pointer}.dialog-actions{display:flex;justify-content:flex-end;gap:9px;margin-top:7px}.dialog-actions button{padding:10px 14px;border:1px solid #cbd4db;border-radius:6px;background:white;color:#28445d;font-weight:600;cursor:pointer}.dialog-actions button:focus-visible,.dialog-close:focus-visible{outline:2px solid #b68a3a;outline-offset:2px}.dialog-actions .primary-action{border-color:#17324f;background:#17324f;color:#fff}.danger-action{border-color:#a65248!important;color:#934a42!important}.dialog-error{color:#9b4d43;font-size:12px}.dialog-actions button:disabled,.dialog-close:disabled{opacity:.6;cursor:wait}@media(max-width:700px){.page-heading{align-items:flex-start;flex-direction:column}.case-controls{align-items:stretch;flex-direction:column}.case-search{width:auto}.case-filters{justify-content:flex-start}.case-grid{grid-template-columns:1fr}.cases-message{margin:30px auto;padding:32px 20px}.case-dialog{padding:25px 21px}}
</style>
