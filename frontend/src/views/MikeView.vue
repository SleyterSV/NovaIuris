<script setup>
import { computed, defineAsyncComponent, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CaseDocumentUpload from '@/components/common/CaseDocumentUpload.vue'
import ToolDetailModal from '@/components/common/ToolDetailModal.vue'
import CasesView from '@/components/workspace/CasesView.vue'
import CaseDetailView from '@/components/workspace/CaseDetailView.vue'
import AccountView from '@/components/workspace/AccountView.vue'
import NovaSearchFilters from '@/components/novasearch/NovaSearchFilters.vue'
import { defaultSearchFilters, legalAreas } from '@/utils/searchFilters.js'
import { createWorkspace, createTurn, normalizeTool, caseReuseContext, applySearchCaseHandoff, courtTaskIdentity, taskIdentityQuery } from '@/utils/mikeWorkspace.js'
import { canAttachDocumentsToCase } from '@/utils/novacasePresentation.js'
import { authRequired, authState, signIn, signOut, signUp, requestPasswordReset, resendConfirmation, updatePassword, startAuth } from '@/config/supabaseSession.js'
import { loadHistoricalRun, requestJson } from '@/services/taskService.js'
import { listCaseDocuments } from '@/services/documentService.js'
import { fetchCaseActivity, fetchOwnedCases } from '@/services/workspaceService.js'
import { appendTranscript, useVoiceInput } from '@/composables/useVoiceInput.js'
import { createToolHoverController } from '@/utils/toolHover.js'
import { createComposerPopovers } from '@/utils/composerPopovers.js'

const panels = {
  search:defineAsyncComponent(() => import('./NovaSearchView.vue')),
  case:defineAsyncComponent(() => import('./NovaCaseView.vue')),
  court:defineAsyncComponent(() => import('./NovaCourtView.vue'))
}
const tools = {
  search:{ name:'NovaSearch', label:'Buscar', category:'INVESTIGACIÓN JURÍDICA', description:'Busca normativa y jurisprudencia',
    short:'Busca normativa, jurisprudencia y fuentes verificables con citas y trazabilidad.',
    about:'El motor de investigación jurídica de MYKE.', purpose:'Investiga cuestiones jurídicas, normativa y jurisprudencia disponible.',
    when:'Cuando necesitas ubicar fuentes para fundamentar una consulta.', input:'Una pregunta o consulta jurídica en texto.',
    output:'Una respuesta con citas, fuentes y advertencias cuando correspondan.',
    sources:'Muestra citas, fuentes verificables y URL oficiales cuando están disponibles.',
    connection:'Puedes pasar a Analizar con una nueva consulta. El resultado de búsqueda permanece visible en esta conversación; no se convierte automáticamente en un expediente.',
    example:'Busca jurisprudencia sobre despido arbitrario.' },
  case:{ name:'NovaCase', label:'Analizar', category:'ANÁLISIS JURÍDICO', description:'Analiza y estructura casos',
    short:'Estructura hechos, problemas jurídicos, evidencia, argumentos, riesgos y estrategia.',
    about:'El motor de análisis de casos y expedientes de MYKE.', purpose:'Ordena hechos, problemas jurídicos, argumentos, contraargumentos, evidencia, riesgos y estrategia.',
    when:'Cuando tienes un caso o documentos que requieren análisis estructurado.', input:'Texto y documentos PDF, DOCX o TXT del caso.',
    output:'Análisis, fuentes e informe según los datos disponibles.',
    sources:'Mantiene el aislamiento privado del caso, las citas y la procedencia documental.',
    connection:'Un caso analizado puede continuar en Simular con el mismo case_id y sus documentos, sin repetir el análisis.',
    example:'Analiza estos hechos y el expediente adjunto.' },
  court:{ name:'NovaCourt', label:'Simular', category:'SIMULACIÓN JURÍDICA', description:'Contrasta posiciones y simula razonamiento jurídico',
    short:'Contrasta posiciones y construye una decisión simulada a partir del caso, evidencia y fuentes.',
    about:'El motor de simulación jurídica de MYKE.', purpose:'Organiza dos posiciones y una decisión simulada razonada.',
    when:'Cuando necesitas explorar argumentos contrapuestos de un caso.', input:'Texto y documentos del caso, o un análisis previo de NovaCase.',
    output:'Posición A, posición B, decisión simulada, grafo, fuentes e informe.',
    sources:'Vincula evidencia, fuentes y nodos del grafo cuando el resultado contiene esas relaciones.',
    connection:'Puede reutilizar un NovaCase existente mediante case_id, document_ids y reuse_task_id.',
    example:'Simula las posiciones de las partes en este caso.' }
}
const route = useRoute(), router = useRouter()
const workspace = ref(createWorkspace())
workspace.value.activeTool = normalizeTool(route.query.tool)
const draft = ref(typeof route.query.q === 'string' ? route.query.q.slice(0,10000) : '')
const composer = ref(null), uploader = ref(null), mobileMenu = ref(false)
const selectedDocuments = ref([]), error = ref(''), loginError = ref('')
const ownedCases = ref([]), casesLoading = ref(false), accountProfile = ref(null)
const casesError = ref(''), profileError = ref(''), detailLoading = ref(false), detailError = ref('')
const caseRuns = ref([]), caseDocuments = ref([])
let loadedOwnerId = null
let loadingCaseId = null
let casesLoadPromise = null
const email = ref(''), password = ref(''), confirmPassword = ref(''), displayName = ref(''), loginBusy = ref(false)
const authMode = ref('login'), authNotice = ref('')
const menuOpen = ref(false), detailTool = ref(null)
const popovers = createComposerPopovers()
const { selectorOpen, filtersOpen: searchFiltersOpen } = popovers
const selectorPopover = ref(null), filterPopover = ref(null)
const selectorTrigger = ref(null), filtersTrigger = ref(null)
const filterBelow = ref(false), filterAlignRight = ref(false)
const searchFilters = reactive(defaultSearchFilters())
const hover = createToolHoverController()
const infoTool = hover.active
const hoverCard = ref(null)
const toolAnchors = {}
const running = ref({ search:false, case:false, court:false })
const activeTool = computed(() => workspace.value.activeTool)
watch(activeTool, tool => { if (tool !== 'search') searchFiltersOpen.value = false })
const activeMeta = computed(() => tools[activeTool.value] || null)
const page = computed(() => route.path === '/cases' ? 'cases' : route.path === '/account' ? 'account' : route.params.caseId ? 'case-detail' : 'workspace')
const pageTitle = computed(() => ({ cases:'Mis casos', 'case-detail':'Detalle del caso', account:'Mi cuenta' })[page.value] || 'EL DERECHO, POTENCIADO POR IA')
const currentCase = computed(() => ownedCases.value.find(item => (item.id || item.case_id) === route.params.caseId) || null)
const placeholder = computed(() => ({ search:'¿Qué necesitas investigar?', case:'Describe el caso o adjunta documentos', court:'Describe el caso o reutiliza un análisis existente' })[activeTool.value] || 'Escribe tu consulta jurídica aquí…')
const canSend = computed(() => !running.value[activeTool.value || 'search'] &&
  (draft.value.trim().length > 0 || (activeTool.value !== 'search' && selectedDocuments.value.length > 0)))
const userName = computed(() => accountProfile.value?.display_name || authState.user?.user_metadata?.full_name || authState.user?.user_metadata?.name || authState.user?.email || 'Mi cuenta')
const initials = computed(() => userName.value.split(/[\s@]+/).filter(Boolean).slice(0,2).map(part => part[0].toUpperCase()).join(''))
const microphoneAvailable = computed(() => typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia && typeof MediaRecorder !== 'undefined')
const voice = useVoiceInput(text => {
  draft.value = appendTranscript(draft.value, text)
  nextTick(() => composer.value?.focus())
})
function openToolCard(key, event) {
  hover.open(key, event.currentTarget)
}
function onDiscoveryKeydown(event) {
  if (event.key === 'Escape') { hover.close(); selectorOpen.value = false }
  if (event.key === 'Tab' && !event.shiftKey && event.target.classList?.contains('tool-card') && infoTool.value) {
    event.preventDefault()
    void nextTick(() => hoverCard.value?.querySelector('.mini-learn')?.focus())
  }
}
function onHoverCardKeydown(event) {
  if (event.key === 'Escape') {
    event.preventDefault()
    const trigger = toolAnchors[infoTool.value]?.querySelector('.tool-card')
    hover.close()
    trigger?.focus()
  } else if (event.key === 'Tab' && event.shiftKey && event.target.classList?.contains('mini-learn')) {
    event.preventDefault()
    toolAnchors[infoTool.value]?.querySelector('.tool-card')?.focus()
  }
}
function openToolDetail() {
  detailTool.value = infoTool.value
  hover.close()
}
function autoGrow(event) {
  const element = event.target
  element.style.height = 'auto'
  element.style.height = `${Math.min(element.scrollHeight, 220)}px`
}
function toggleFilters() {
  if (!searchFiltersOpen.value && filtersTrigger.value && typeof window !== 'undefined') {
    const rect = filtersTrigger.value.getBoundingClientRect()
    filterBelow.value = rect.top < 235 && window.innerHeight - rect.bottom > rect.top
    filterAlignRight.value = rect.left + 276 > window.innerWidth - 16
  }
  popovers.toggleFilters()
}
function onPopoverPointer(event) {
  popovers.outsidePointer(event.target, selectorPopover.value, filterPopover.value)
}
function onPopoverKeydown(event) {
  if (event.key !== 'Escape') return
  const focus = popovers.closeOnEscape()
  if (!focus) return
  event.preventDefault()
  void nextTick(() => (focus === 'filters' ? filtersTrigger : selectorTrigger).value?.focus())
}

watch(() => route.query.tool, value => { workspace.value.activeTool = normalizeTool(value) })
watch(() => authState.user, (user, previous) => {
  const previousId = previous?.id || null, nextId = user?.id || null
  if (previousId && previousId !== nextId) {
    newConversation(); ownedCases.value = []; accountProfile.value = null
    casesError.value = ''; profileError.value = ''; caseRuns.value = []; caseDocuments.value = []
    loadedOwnerId = null
  }
  if (user && previousId !== nextId) loadOwnedCases()
  if (user && route.params.caseId) loadCaseDetail(route.params.caseId)
})
watch(() => route.params.caseId, caseId => {
  caseRuns.value = []; caseDocuments.value = []; detailError.value = ''
  if (caseId && authState.user) loadCaseDetail(caseId)
})
watch(() => route.query.case_id, caseId => {
  if (route.path !== '/' || route.query.tool !== 'case' || typeof caseId !== 'string' || route.query.run_id || route.query.task_id) return
  workspace.value.caseId = caseId
  workspace.value.casePersisted = true
  workspace.value.title = ownedCases.value.find(item => (item.id || item.case_id) === caseId)?.title || workspace.value.title
})
watch(hoverCard, element => hover.setCard(element), { flush:'post' })
watch(infoTool, value => {
  if (typeof window === 'undefined') return
  const action = value ? 'addEventListener' : 'removeEventListener'
  window[action]('resize', hover.refreshPosition)
  window[action]('scroll', hover.refreshPosition, true)
})
onUnmounted(() => {
  hover.dispose()
  document.removeEventListener('pointerdown', onPopoverPointer)
  document.removeEventListener('keydown', onPopoverKeydown)
  window.removeEventListener('resize', hover.refreshPosition)
  window.removeEventListener('scroll', hover.refreshPosition, true)
})
onMounted(async () => {
  document.addEventListener('pointerdown', onPopoverPointer)
  document.addEventListener('keydown', onPopoverKeydown)
  await startAuth()
  if (authState.user) {
    await loadOwnedCases()
    if (route.params.caseId) await loadCaseDetail(route.params.caseId)
  }
  const caseId = route.query.case_id, taskId = route.query.task_id, runId = route.query.run_id
  if (!['case', 'court'].includes(route.query.tool) || typeof caseId !== 'string') return
  if (typeof runId === 'string') {
    try {
      const historical = await loadHistoricalRun(runId, caseId, route.query.tool)
      const { run, result } = historical
      workspace.value.caseId = caseId
      workspace.value.casePersisted = true
      workspace.value.activeTool = route.query.tool
      const text = String(result.case || result.final_result?.case || 'Resultado histórico del caso.')
      addOperation(route.query.tool, text, { caseId, documentIds:result.document_ids || [],
        historicalResult:{ run, result, artifacts:historical.artifacts }, status:'completed' })
    } catch (cause) {
      error.value = 'No fue posible recuperar la ejecución solicitada.'
      if (cause?.status === 401) { await signOut(); router.replace('/') }
    }
    return
  }
  if (typeof taskId !== 'string') return
  if (route.query.tool === 'court' && !courtTaskIdentity(route.query)) {
    error.value = 'No fue posible recuperar la tarea solicitada.'
    return
  }
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(caseId) || caseId.includes('..') ||
      !/^[A-Za-z0-9-]{1,128}$/.test(taskId)) { error.value = 'No fue posible recuperar la tarea solicitada.'; return }
  const tool = route.query.tool
  try {
    const path = tool === 'court' ? '/novacourt/results' : '/tasks'
    const task = await requestJson(`${path}/${encodeURIComponent(taskId)}?case_id=${encodeURIComponent(caseId)}`)
    if (task.case_id !== caseId || task.task_id !== taskId || task.tool !== tool) {
      error.value = 'No fue posible recuperar la tarea solicitada.'
      return
    }
    workspace.value.caseId = caseId
    workspace.value.casePersisted = true
    workspace.value.activeTool = tool
    workspace.value.documentIds = [...(task.metadata?.document_ids || [])]
    addOperation(tool, task.final_result?.case || task.partial_result?.case ||
      (tool === 'court' ? 'Simulación judicial existente.' : 'Análisis del caso en curso.'),
      { caseId, documentIds:workspace.value.documentIds, existingTaskId:taskId })
  } catch (cause) {
    error.value = 'No fue posible recuperar la tarea solicitada.'
    if (cause?.status === 401) { await signOut(); router.replace('/') }
  }
})

function selectTool(value, reveal = true) {
  const tool = normalizeTool(value)
  workspace.value.activeTool = tool
  if (reveal && tool && toolAnchors[tool]) hover.open(tool, toolAnchors[tool])
  else hover.close()
  selectorOpen.value = false
  mobileMenu.value = false
  error.value = ''
  router.replace({ path:'/', query:tool ? { tool } : {} })
  nextTick(() => composer.value?.focus())
}
function newConversation() {
  workspace.value = createWorkspace()
  Object.assign(searchFilters, defaultSearchFilters())
  searchFiltersOpen.value = false
  selectedDocuments.value = []
  draft.value = ''
  error.value = ''
  running.value = { search:false, case:false, court:false }
  hover.close()
  detailTool.value = null
  selectTool(null, false)
}
async function loadOwnedCases() {
  if (!authState.user) return
  if (loadedOwnerId === authState.user.id && casesLoading.value) return casesLoadPromise
  loadedOwnerId = authState.user.id
  casesLoading.value = true
  casesError.value = ''
  profileError.value = ''
  const ownerId = authState.user.id
  const pending = Promise.allSettled([requestJson('/me'), fetchOwnedCases(requestJson)])
  casesLoadPromise = pending
  try {
    const [account, cases] = await pending
    if (authState.user?.id !== ownerId) return
    accountProfile.value = account.status === 'fulfilled' ? account.value.profile || null : null
    profileError.value = account.status === 'rejected' ? 'No fue posible cargar la información del perfil.' : ''
    if (cases.status === 'rejected') {
      ownedCases.value = []
      casesError.value = cases.reason?.status === 401 ? 'La sesión expiró. Inicia sesión nuevamente.' : 'No fue posible cargar tus casos. Inténtalo nuevamente.'
      loadedOwnerId = null
      if (cases.reason?.status === 401) { await signOut(); router.replace('/') }
    } else ownedCases.value = cases.value
  }
  finally {
    if (casesLoadPromise === pending) { casesLoading.value = false; casesLoadPromise = null }
  }
}
async function loadCaseDetail(caseId = route.params.caseId) {
  if (!authState.user || !caseId || (detailLoading.value && loadingCaseId === caseId)) return
  loadingCaseId = caseId
  detailLoading.value = true
  detailError.value = ''
  caseRuns.value = []; caseDocuments.value = []
  try {
    if (loadedOwnerId !== authState.user.id || casesError.value) await loadOwnedCases()
    const record = ownedCases.value.find(row => (row.id || row.case_id) === caseId)
    if (!record) throw Object.assign(new Error('CASE_NOT_FOUND'), { status:404 })
    const { runs, documents } = await fetchCaseActivity(requestJson, listCaseDocuments, caseId)
    if (String(route.params.caseId) !== String(caseId)) return
    caseRuns.value = runs
    caseDocuments.value = documents
  } catch (cause) {
    if (String(route.params.caseId) === String(caseId)) {
      detailError.value = cause?.status === 401 ? 'La sesión expiró. Inicia sesión nuevamente.' :
        cause?.status === 404 ? 'No tienes acceso a este caso o ya no está disponible.' : 'No fue posible cargar el caso y su actividad. Inténtalo nuevamente.'
      if (cause?.status === 401) { await signOut(); router.replace('/') }
    }
  } finally {
    if (loadingCaseId === caseId) { detailLoading.value = false; loadingCaseId = null }
  }
}
function openOwnedCase(item) {
  const caseId = item?.id || item?.case_id
  if (caseId) router.push(`/cases/${encodeURIComponent(caseId)}`)
}
function continueOwnedCase(item) {
  const caseId = item?.id || item?.case_id
  if (!caseId) return
  newConversation()
  workspace.value.caseId = caseId
  workspace.value.casePersisted = true
  workspace.value.title = item.title || 'Caso jurídico'
  workspace.value.activeTool = 'case'
  draft.value = item.description || ''
  selectedDocuments.value = []
  mobileMenu.value = false
  router.push({ path:'/', query:{ tool:'case', case_id:caseId } })
}
function runStatusLabel(status) {
  return ({ queued:'En espera', pending:'En espera', processing:'En curso', completed:'Completado', partial:'Parcial', failed:'No completado', cancelled:'Cancelado', timeout:'Tiempo agotado', interrupted:'Interrumpido' })[status] || 'Estado no disponible'
}
async function renameOwnedCase(item) {
  const caseId = item.id || item.case_id
  const current = item.title || 'Caso jurídico'
  const title = typeof window !== 'undefined' ? window.prompt('Nuevo título del caso', current) : null
  if (!title?.trim() || title.trim() === current) return
  try {
    const updated = await requestJson(`/cases/${encodeURIComponent(caseId)}`, { method:'PATCH', body:JSON.stringify({ title:title.trim() }) })
    ownedCases.value = ownedCases.value.map(row => (row.id || row.case_id) === caseId ? updated.case : row)
  } catch { error.value = 'No fue posible cambiar el título del caso.' }
}
async function archiveOwnedCase(item) {
  const caseId = item.id || item.case_id
  try {
    const updated = await requestJson(`/cases/${encodeURIComponent(caseId)}`, { method:'PATCH', body:JSON.stringify({ status:item.status === 'archived' ? 'active' : 'archived' }) })
    ownedCases.value = ownedCases.value.map(row => (row.id || row.case_id) === caseId ? updated.case : row)
  } catch { error.value = 'No fue posible actualizar el estado del caso.' }
}
function addOperation(kind, text, context = {}) {
  const request = { id:crypto.randomUUID(), text, caseId:context.caseId || workspace.value.caseId,
    documentIds:[...(context.documentIds || selectedDocuments.value)],
    ...(context.existingTaskId ? { existingTaskId:context.existingTaskId } : {}),
    ...(context.reuse ? { reuse:context.reuse } : {}),
    ...(context.historicalResult ? { historicalResult:context.historicalResult } : {}) }
  workspace.value.turns.push(createTurn('user',kind,text,{ caseId:request.caseId, documentIds:request.documentIds }))
  const assistant = createTurn('assistant',kind,'',{ caseId:request.caseId, documentIds:request.documentIds,
    resultRef:request.id, status:context.status || 'running' })
  assistant.request = request
  workspace.value.turns.push(assistant)
  workspace.value.title = text.slice(0,64)
  workspace.value.documentIds = [...request.documentIds]
  running.value = { ...running.value, [kind]:context.status !== 'completed' }
  nextTick(() => document.querySelector('.turn:last-child')?.scrollIntoView({ behavior:'smooth', block:'start' }))
}
async function submit() {
  if (!canSend.value) return
  const kind = activeTool.value || 'search'
  if (!activeTool.value) selectTool(kind, false)
  const text = draft.value.trim()
  if (kind === 'search' && text.length < 5) { error.value = 'Describe con mayor detalle la consulta jurídica.'; return }
  error.value = ''
  if (kind !== 'search' && !await ensurePersistedCase(text || 'Caso sin título')) return

  addOperation(kind, text || 'Analiza los documentos jurídicos aportados para este caso.')
  draft.value = ''
}
function onComposerKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing && !event.repeat) { event.preventDefault(); submit() }
}
function onTaskState(turn, state) {
  if (!workspace.value.turns.includes(turn)) return
  turn.status = state.status || (state.running ? 'running' : 'completed')
  if ((state.tool === 'case' || state.tool === 'court') && turn.case_id !== workspace.value.caseId) return
  if (state.taskId) {
    turn.task_id = state.taskId
    workspace.value[`${state.tool}TaskId`] = state.taskId
    if ((state.tool === 'case' || state.tool === 'court') && turn.case_id &&
        (route.query.tool !== state.tool || route.query.case_id !== turn.case_id || route.query.task_id !== state.taskId))
      router.replace({ path:route.path, query:taskIdentityQuery(state.tool, turn.case_id, state.taskId) })
  }
  running.value = { ...running.value, [state.tool]:state.running }
}
function onCaseCompleted(turn, { result, taskId, caseText }) {
  if (!workspace.value.turns.includes(turn) || result?.case_id !== workspace.value.caseId) return
  turn.task_id = taskId
  workspace.value.caseTaskId = taskId
  workspace.value.caseReuse = caseReuseContext(result,taskId,caseText)
}
function onSearchHandoff(started) {
  const context = applySearchCaseHandoff(workspace.value, started)
  if (!context) return
  selectedDocuments.value = []
  selectTool('case', false)
  addOperation('case', started.caseText, context)
}
function reuseCase(context) {
  if (!context || context.caseId !== workspace.value.caseId || running.value.court) return
  workspace.value.caseReuse = context
  workspace.value.casePersisted = true
  workspace.value.documentIds = [...context.documentIds]
  selectedDocuments.value = [...context.documentIds]
  selectTool('court',false)
  addOperation('court',context.caseText,{ caseId:context.caseId, documentIds:context.documentIds, reuse:context })
}
async function ensurePersistedCase(title = 'Caso sin título') {
  if (workspace.value.casePersisted) return true
  try {
    const created = await requestJson('/cases', { method:'POST', body:JSON.stringify({ title:title.slice(0,240) }) })
    workspace.value.caseId = created.case.id
    workspace.value.casePersisted = true
    ownedCases.value = [created.case, ...ownedCases.value]
    return true
  } catch (err) { error.value = err?.message || 'No fue posible crear el caso.'; return false }
}
async function chooseFiles() {
  if ((activeTool.value === 'case' || activeTool.value === 'court') && !await ensurePersistedCase(draft.value.trim() || 'Caso sin título')) return
  uploader.value?.$el?.querySelector('input[type="file"]')?.click()
}
async function addCaseDocuments(turn, payload) {
  if (!canAttachDocumentsToCase(payload?.caseId, workspace.value.caseId,
    workspace.value.turns.includes(turn))) return
  selectTool('case', false)
  await nextTick()
  uploader.value?.$el?.scrollIntoView({ behavior:'smooth', block:'center' })
  chooseFiles()
}
async function login() {
  if (loginBusy.value) return
  loginBusy.value = true
  loginError.value = ''
  authNotice.value = ''
  try {
    if (authState.recovery) {
      if (password.value !== confirmPassword.value) loginError.value = 'Las contraseñas no coinciden.'
      else {
        loginError.value = await updatePassword(password.value)
        if (!loginError.value) {
          password.value = ''; confirmPassword.value = ''
          authNotice.value = 'La contraseña se actualizó. Ya puedes continuar.'
        }
      }
    } else if (authMode.value === 'signup') {
      if (password.value !== confirmPassword.value) loginError.value = 'Las contraseñas no coinciden.'
      else {
        const result = await signUp(displayName.value, email.value, password.value)
        loginError.value = result.error || ''
        if (!loginError.value && result.confirmationRequired) {
          authMode.value = 'confirmation'
          password.value = ''; confirmPassword.value = ''
          authNotice.value = 'Si esa cuenta puede registrarse, recibirás un correo para confirmar la dirección.'
        }
      }
    } else if (authMode.value === 'confirmation') {
      loginError.value = await resendConfirmation(email.value)
      if (!loginError.value) authNotice.value = 'Si esa cuenta puede recibir una confirmación, llegará un correo en breve.'
    } else if (authMode.value === 'reset') {
      loginError.value = await requestPasswordReset(email.value)
      if (!loginError.value) authNotice.value = 'Si el correo corresponde a una cuenta, recibirás instrucciones para recuperar el acceso.'
    } else loginError.value = await signIn(email.value,password.value)
  } catch {
    loginError.value = 'No fue posible completar la solicitud. Inténtalo nuevamente.'
  } finally {
    if (authMode.value !== 'reset' && authMode.value !== 'confirmation') password.value = ''
    loginBusy.value = false
  }
}
async function logout() {
  menuOpen.value = false
  newConversation()
  ownedCases.value = []; accountProfile.value = null; casesError.value = ''; profileError.value = ''
  loadedOwnerId = null
  try { await signOut() } catch { loginError.value = 'Se cerró la sesión local. Vuelve a iniciar sesión.' }
}
function openAbout() { menuOpen.value = false; router.push('/about') }
function openAccount() { menuOpen.value = false; router.push('/account') }
</script>

<template>
  <div v-if="authState.loading" class="auth-screen" role="status"><div class="auth-card"><strong class="auth-brand">MYKE</strong><p>Comprobando sesión…</p></div></div>
  <div v-else-if="authState.passwordUpdated || authState.recovery || (authRequired && !authState.user)" class="auth-screen">
    <form class="auth-card" @submit.prevent="login"><strong class="auth-brand">MYKE</strong><small>LEGAL INTELLIGENCE</small><h1>{{ authState.passwordUpdated ? 'Contraseña actualizada' : authState.recovery ? 'Restablecer contraseña' : authMode === 'signup' ? 'Crear cuenta' : authMode === 'confirmation' ? 'Confirma tu correo' : authMode === 'reset' ? 'Recuperar acceso' : 'Tu espacio jurídico' }}</h1><p>{{ authState.passwordUpdated ? 'La nueva contraseña quedó guardada. Ya puedes continuar con tu sesión.' : authState.recovery ? 'Elige y confirma una contraseña nueva para tu cuenta.' : authMode === 'signup' ? 'Crea tu espacio privado de trabajo jurídico.' : authMode === 'confirmation' ? 'Confirma la dirección de correo para activar tu acceso privado.' : authMode === 'reset' ? 'Te enviaremos instrucciones al correo asociado a tu cuenta.' : 'Inicia sesión para continuar tu trabajo privado.' }}</p><template v-if="authState.passwordUpdated"><p role="status">{{ authNotice }}</p><button type="button" @click="authState.passwordUpdated = false">Continuar a MYKE</button></template><template v-else-if="!authState.error"><p v-if="authState.linkError" role="alert">{{ authState.linkError }}</p><label v-if="authMode === 'signup' && !authState.recovery">Nombre<input v-model="displayName" type="text" required maxlength="120" autocomplete="name"></label><label v-if="!authState.recovery">Correo electrónico<input v-model="email" type="email" required autocomplete="email" :readonly="authMode === 'confirmation'"></label><label v-if="(authMode !== 'reset' && authMode !== 'confirmation') || authState.recovery">{{ authState.recovery ? 'Nueva contraseña' : 'Contraseña' }}<input v-model="password" type="password" required minlength="8" :autocomplete="authState.recovery ? 'new-password' : 'current-password'"></label><label v-if="(authMode === 'signup' || authState.recovery) && !authState.error">Confirmar contraseña<input v-model="confirmPassword" type="password" required minlength="8" autocomplete="new-password"></label><p v-if="loginError" role="alert">{{ loginError }}</p><p v-if="authNotice" role="status">{{ authNotice }}</p><button type="submit" :disabled="loginBusy">{{ loginBusy ? 'Procesando…' : authState.recovery ? 'Actualizar contraseña' : authMode === 'signup' ? 'Crear cuenta' : authMode === 'confirmation' ? 'Reenviar correo' : authMode === 'reset' ? 'Enviar instrucciones' : 'Iniciar sesión' }}</button><nav v-if="!authState.recovery" class="auth-links" aria-label="Opciones de acceso"><button type="button" @click="authMode = ['signup','confirmation'].includes(authMode) ? 'login' : 'signup'; loginError = ''; authNotice = ''; authState.linkError = ''">{{ ['signup','confirmation'].includes(authMode) ? 'Volver a iniciar sesión' : 'Crear cuenta' }}</button><button v-if="!['signup','confirmation'].includes(authMode)" type="button" @click="authMode = authMode === 'reset' ? 'login' : 'reset'; loginError = ''; authNotice = ''; authState.linkError = ''">{{ authMode === 'reset' ? 'Volver a iniciar sesión' : 'Olvidé mi contraseña' }}</button></nav></template><p v-else role="alert">{{ authState.error }}</p></form>
  </div>
  <div v-else class="mike-app">
    <aside class="sidebar" :class="{ open:mobileMenu }" aria-label="Navegación de MYKE">
      <button class="brand" type="button" @click="newConversation"><span class="brand-rule"></span><span><strong>MYKE</strong><small>LEGAL INTELLIGENCE</small></span></button>
      <button class="new-chat" type="button" @click="newConversation"><span aria-hidden="true">＋</span> Nuevo análisis</button>
      <p class="side-label">HERRAMIENTAS</p>
      <nav class="tool-nav" aria-label="Herramientas de MYKE">
        <div v-for="(item,key) in tools" :key="key" :ref="element => { if (element) toolAnchors[key] = element }" class="tool-wrap" @pointerenter="openToolCard(key,$event)" @pointerleave="hover.scheduleClose()" @focusin="openToolCard(key,$event)" @focusout="hover.scheduleClose()" @keydown="onDiscoveryKeydown">
          <button class="tool-card" :class="{ active:activeTool === key }" type="button" :aria-pressed="activeTool === key" :aria-describedby="infoTool === key ? `tool-info-${key}` : undefined" @click="selectTool(key)">
            <span class="tool-icon" aria-hidden="true">{{ key === 'search' ? '⌕' : key === 'case' ? '▤' : '⚖' }}</span><span class="tool-copy"><strong>{{ item.name }}</strong><small>{{ item.description }}</small></span><span aria-hidden="true">›</span>
          </button>
        </div>
      </nav>
      <p class="side-label case-side-label">TU ESPACIO</p>
      <nav class="workspace-nav" aria-label="Espacio personal">
        <RouterLink to="/cases" class="workspace-nav-link" :class="{ active:page === 'cases' || page === 'case-detail' }" :aria-current="page === 'cases' || page === 'case-detail' ? 'page' : undefined" @click="mobileMenu = false"><span aria-hidden="true">▤</span><span>Mis casos</span><small>{{ ownedCases.length }}</small></RouterLink>
      </nav>
      <button class="sidebar-profile" type="button" @click="openAccount"><span class="avatar">{{ initials || 'M' }}</span><span><strong>{{ userName }}</strong><small>{{ authState.user?.email || 'Mi cuenta' }}</small></span></button>
    </aside>
    <button v-if="mobileMenu" class="mobile-overlay" type="button" aria-label="Cerrar menú" @click="mobileMenu = false"></button>
    <div class="main-area">
      <header class="topbar"><button class="mobile-menu" type="button" aria-label="Abrir menú" @click="mobileMenu = true">☰</button><span class="topbar-copy">{{ pageTitle }}</span><div class="top-actions"><button v-if="page === 'workspace'" class="search-shortcut" type="button" aria-label="Seleccionar Buscar" @click="selectTool('search',false)">⌕</button><div class="account"><button type="button" aria-haspopup="menu" :aria-expanded="menuOpen" :aria-label="`Menú de cuenta de ${userName}`" @click="menuOpen = !menuOpen"><span class="avatar">{{ initials || 'M' }}</span><span class="account-name">{{ userName }}</span>⌄</button><div v-if="menuOpen" class="account-menu" role="menu"><div class="account-identity"><strong>{{ userName }}</strong><small>{{ authState.user?.email }}</small></div><button type="button" role="menuitem" @click="openAccount">Mi cuenta</button><button type="button" role="menuitem" @click="openAbout">Acerca de MYKE</button><hr><button type="button" role="menuitem" @click="logout">Cerrar sesión</button></div></div></div></header>
      <main class="workspace" :class="{ conversation:workspace.turns.length, 'search-workspace': activeTool === 'search' && workspace.turns.length }">
        <CasesView v-if="page === 'cases'" :cases="ownedCases" :loading="casesLoading" :error="casesError" @retry="loadOwnedCases" @new-analysis="newConversation" @open-case="openOwnedCase" />
        <CaseDetailView v-else-if="page === 'case-detail'" :case-record="currentCase" :runs="caseRuns" :documents="caseDocuments" :loading="detailLoading" :error="detailError" @retry="loadCaseDetail()" @back="router.push('/cases')" @continue-case="continueOwnedCase" />
        <AccountView v-else-if="page === 'account'" :profile="accountProfile" :user="authState.user" :loading="casesLoading" :error="profileError" @retry="loadOwnedCases" />
        <template v-else>
        <div v-if="!workspace.turns.length" class="home"><p class="kicker">LEGAL INTELLIGENCE</p><h1>Hola, soy <span>MYKE</span></h1><p class="subtitle">Tu asistente jurídico inteligente</p><p class="intro">Investiga el derecho, analiza expedientes y explora escenarios jurídicos desde un mismo entorno.</p></div>
        <section v-else class="thread" :class="{ 'search-thread': activeTool === 'search', 'case-thread': activeTool === 'case', 'court-thread': activeTool === 'court' }" aria-label="Conversación">
          <article v-for="turn in workspace.turns" :key="turn.id" class="turn" :class="turn.role">
            <div v-if="turn.role === 'user'" class="user-bubble"><p>{{ turn.text }}</p><small>{{ tools[turn.tool].label }}</small></div>
            <div v-else class="assistant-turn"><p class="turn-label">MYKE · {{ tools[turn.tool].label }}</p><component :is="panels[turn.tool]" embedded :request="turn.request" v-bind="turn.tool === 'search' ? { searchFilters } : {}" @task-state="onTaskState(turn,$event)" @case-completed="onCaseCompleted(turn,$event)" @handoff-started="onSearchHandoff" @reuse-case="reuseCase" @add-documents="addCaseDocuments(turn,$event)" /></div>
          </article>
        </section>
        <div class="composer-region">
          <form class="composer" @submit.prevent="submit"><textarea ref="composer" v-model="draft" rows="2" :placeholder="workspace.turns.length ? placeholder : 'Escribe tu consulta jurídica aquí...'" aria-label="Consulta jurídica" @input="autoGrow" @keydown="onComposerKeydown"></textarea><div class="composer-bottom"><button class="attach" type="button" :disabled="activeTool === 'search' || !activeTool" aria-label="Adjuntar documentos" title="Adjuntar documentos" @click="chooseFiles">＋</button><div ref="selectorPopover" class="selector"><button ref="selectorTrigger" type="button" aria-haspopup="listbox" aria-controls="composer-tool-options" :aria-expanded="selectorOpen" @click="popovers.toggleSelector()">{{ activeMeta?.label || 'Buscar' }} · {{ activeMeta?.name || 'NovaSearch' }} ▾</button><div v-if="selectorOpen" id="composer-tool-options" class="selector-menu" role="listbox" aria-label="Seleccionar herramienta"><button v-for="(item,key) in tools" :key="key" type="button" role="option" :aria-selected="activeTool === key" @click="selectTool(key,false)"><strong>{{ item.label }} · {{ item.name }}</strong><small>{{ item.description }}</small></button></div></div>
            <div v-if="activeTool === 'search'" ref="filterPopover" class="composer-filters"><button ref="filtersTrigger" type="button" class="composer-filter-toggle" :class="{ active: searchFilters.modulo !== 'Todos' || searchFilters.vigencia_explicit }" aria-controls="composer-search-filters" :aria-expanded="searchFiltersOpen" @click="toggleFilters"><svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 6h16M7 12h10m-7 6h4"/><circle cx="8" cy="6" r="2" fill="currentColor" stroke="none"/><circle cx="15" cy="12" r="2" fill="currentColor" stroke="none"/></svg>Filtros<span v-if="searchFilters.modulo !== 'Todos' || searchFilters.vigencia_explicit" class="filter-indicator" aria-label="Filtros activos"></span></button><div v-if="searchFiltersOpen" id="composer-search-filters" class="composer-filter-panel" :class="{ below: filterBelow, 'align-right': filterAlignRight }"><NovaSearchFilters :filters="searchFilters" :modulos="legalAreas" @update:filters="Object.assign(searchFilters, $event)" /></div></div>
            <span class="composer-spacer"></span><span v-if="voice.state.value === 'recording'" class="voice-timer" role="status">● {{ voice.elapsed.value }}</span><span v-if="voice.state.value === 'transcribing'" class="voice-timer" role="status">Transcribiendo...</span><button type="button" class="mic" :class="{ recording:voice.state.value === 'recording' }" :disabled="voice.state.value === 'transcribing' || voice.state.value === 'requesting_permission'" :aria-label="voice.state.value === 'recording' ? 'Detener grabación' : 'Grabar consulta por voz'" :title="voice.state.value === 'recording' ? 'Detener' : microphoneAvailable ? 'Grabar por voz' : 'Micrófono no disponible'" @click="voice.state.value === 'recording' ? voice.stop() : voice.start()"><span v-if="voice.state.value === 'recording'" class="mic-stop" aria-hidden="true"></span><svg v-else class="mic-icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3m-4 0h8"/></svg></button><button class="send" type="submit" :disabled="!canSend" aria-label="Enviar consulta">➤</button></div></form>
          <p v-if="voice.message.value || ['requesting_permission','transcribing'].includes(voice.state.value)" class="voice-message" :class="{ error:voice.state.value === 'error' }" aria-live="polite">{{ voice.state.value === 'requesting_permission' ? 'Solicitando acceso al micrófono...' : voice.state.value === 'transcribing' ? 'Transcribiendo...' : voice.message.value }}</p>
          <p v-if="error" class="error" role="alert">{{ error }}</p>
          <CaseDocumentUpload v-show="activeTool === 'case' || activeTool === 'court'" :key="workspace.id" ref="uploader" :case-id="workspace.caseId" :initial-document-ids="workspace.documentIds" :disabled="running.case || running.court" @update:document-ids="selectedDocuments = $event" />
          <div v-if="!workspace.turns.length" class="quick-actions"><button v-for="(item,key) in tools" :key="key" type="button" @click="selectTool(key,false)"><span class="quick-icon" aria-hidden="true">{{ key === 'search' ? '⌕' : key === 'case' ? '▤' : '⚖' }}</span><span class="quick-copy"><strong>{{ key === 'search' ? 'Buscar jurisprudencia' : key === 'case' ? 'Analizar un expediente' : 'Simular un caso' }}</strong><small>{{ key === 'search' ? 'Normativa, jurisprudencia y doctrina' : key === 'case' ? 'Resume, estructura y extrae información' : 'Contrasta posiciones y analiza escenarios' }}</small></span><span class="quick-arrow" aria-hidden="true">→</span></button></div>
          <p v-if="!workspace.turns.length" class="home-quote">“La mejor estrategia comienza con mejor información.” <small>MYKE · LEGAL INTELLIGENCE</small></p>
        </div>
        <div class="watermark" aria-hidden="true">⚖</div>
        </template>
      </main>
    </div>
    <Teleport to="body">
      <div v-if="infoTool && tools[infoTool]" :id="`tool-info-${infoTool}`" ref="hoverCard" class="mini-card" :style="{ left:`${hover.position.value.left}px`, top:`${hover.position.value.top}px` }" @pointerenter="hover.enterCard()" @pointerleave="hover.scheduleClose()" @focusin="hover.enterCard()" @focusout="hover.scheduleClose()" @keydown="onHoverCardKeydown">
        <p class="mini-category">{{ tools[infoTool].category }}</p><strong>{{ tools[infoTool].name }}</strong><p>{{ tools[infoTool].short }}</p><p class="mini-purpose">{{ tools[infoTool].purpose }}</p>
        <button class="mini-learn" type="button" @click="openToolDetail">Conocer más <svg aria-hidden="true" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.1 0l3-3A5 5 0 0 0 13 2l-1.7 1.7M14 11a5 5 0 0 0-7.1 0l-3 3A5 5 0 0 0 11 22l1.7-1.7"/></svg></button>
        <button class="mini-close" type="button" :aria-label="`Ocultar información de ${tools[infoTool].name}`" @click="hover.close()">×</button>
      </div>
    </Teleport>
    <ToolDetailModal v-if="detailTool && detailTool !== 'account'" :tool="tools[detailTool]" @close="detailTool = null" @use="selectTool(detailTool,false); detailTool = null" />
    <div v-if="detailTool === 'account'" class="account-backdrop" @click.self="detailTool = null"><section class="account-dialog" role="dialog" aria-modal="true" aria-labelledby="account-title"><button type="button" aria-label="Cerrar" @click="detailTool = null">×</button><h2 id="account-title">Mi cuenta</h2><p>{{ userName }}</p><p>{{ authState.user?.email }}</p></section></div>
  </div>
</template>

<style scoped>
.mike-app{display:flex;min-height:100vh;background:#f8f7f3;color:#142f4d;font-family:Inter,system-ui,sans-serif}.sidebar{position:sticky;top:0;flex:0 0 286px;height:100vh;display:flex;flex-direction:column;padding:29px 19px;background:#112a46;color:#f7f5ef}.brand{display:flex;align-items:center;gap:13px;text-align:left;border:0;background:none;color:#fff;cursor:pointer;padding:2px 10px 26px}.brand-rule{height:39px;width:3px;background:#c4a474}.brand strong{display:block;font:normal 28px Georgia,serif;letter-spacing:.15em}.brand small{display:block;font-size:9px;letter-spacing:.2em;color:#d7c7a8}.new-chat{padding:13px 16px;background:#f8f7f3;border:1px solid #dccba9;border-radius:8px;color:#163554;text-align:left;font-weight:600;cursor:pointer}.new-chat span{font-size:20px;margin-right:7px}.side-label{margin:35px 11px 13px;color:#b9b9b0;font-size:10px;letter-spacing:.17em}.tool-nav{display:grid;gap:7px}.tool-card{display:flex;align-items:center;gap:10px;width:100%;text-align:left;padding:12px 9px;border:1px solid transparent;border-radius:8px;background:none;color:#f9f7f0;cursor:pointer}.tool-card:hover,.tool-card.active{border-color:#9b845d;background:#233c59}.tool-icon{display:grid;place-items:center;width:34px;min-width:34px;height:34px;border:1px solid #a8946f;border-radius:7px;color:#ddc497;font-size:23px}.tool-copy{flex:1;min-width:0}.tool-copy strong,.tool-copy small{display:block}.tool-copy strong{font:normal 16px Georgia,serif}.tool-copy small{margin-top:4px;color:#c2cbd3;font-size:11px;line-height:1.35}.mini-card{position:relative;margin:2px 4px 9px 45px;padding:11px 24px 12px 12px;border-left:2px solid #d4b57f;background:#1d3957;border-radius:0 7px 7px 0;font-size:11px;line-height:1.5;color:#e8ebee}.mini-card p{margin:5px 0}.mini-category{font-size:9px;letter-spacing:.1em;color:#ddc497}.mini-card button{border:0;background:none;color:#ecd1a1;cursor:pointer;padding:3px 0}.mini-card .mini-close{position:absolute;top:4px;right:8px;font-size:17px}.history{margin-top:25px;border-top:1px solid #42566b;padding:18px 10px}.history h2{font-size:12px;letter-spacing:.07em}.history p{font-size:12px;color:#aab9c9}.sidebar-profile{display:flex;align-items:center;gap:10px;margin-top:auto;padding:16px 8px;border-top:1px solid #42566b;min-width:0}.sidebar-profile>span:last-child{min-width:0}.sidebar-profile strong,.sidebar-profile small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.sidebar-profile strong{font-size:12px}.sidebar-profile small{font-size:10px;color:#aebbc8;margin-top:3px}.avatar{display:inline-grid;place-items:center;flex:none;width:34px;height:34px;border-radius:50%;background:#e9dbbd;color:#142f4d;font-size:11px;font-weight:700}.main-area{flex:1;min-width:0}.topbar{display:flex;justify-content:space-between;align-items:center;height:72px;padding:0 34px;border-bottom:1px solid #e4e5e4;background:#fffdfa}.topbar-copy{font-size:11px;letter-spacing:.16em;font-weight:700}.top-actions{display:flex;align-items:center;gap:16px}.top-actions button{border:0;background:none;color:#17324f;cursor:pointer}.search-shortcut{font-size:25px}.account{position:relative}.account>button{display:flex;align-items:center;gap:8px}.account-menu{position:absolute;z-index:20;right:0;top:43px;width:220px;padding:8px;background:#fff;border:1px solid #dce3e9;border-radius:10px;box-shadow:0 14px 30px #061c3022}.account-menu button{display:block;width:100%;padding:10px;text-align:left}.account-menu button:hover{background:#f2f5f7}.account-identity{padding:10px;font-size:12px;overflow-wrap:anywhere}.account-identity strong,.account-identity small{display:block}.account-menu hr{border:0;border-top:1px solid #e3e8ec}.workspace{position:relative;min-height:calc(100vh - 72px);padding:70px 32px 40px;overflow:hidden}.home,.composer-region,.thread{position:relative;z-index:1;max-width:890px;margin:auto}.home{text-align:center}.kicker{font-size:11px;letter-spacing:.2em;color:#a38358}.home h1{font:normal clamp(37px,4vw,59px) Georgia,serif;margin:18px 0 10px}.home h1 span{color:#9c7b4d}.subtitle{font:normal 23px Georgia,serif;margin:0}.intro{max-width:560px;margin:17px auto 0;color:#69798a;line-height:1.65;font-size:14px}.composer-region{margin-top:35px}.composer{padding:17px 18px 11px;border:1px solid #d9dfe4;border-radius:16px;background:#fff;box-shadow:0 12px 32px #142e4d12}.composer textarea{display:block;width:100%;min-height:72px;resize:vertical;border:0;outline:0;color:#17324f;background:none;font:15px/1.5 Inter,system-ui,sans-serif}.composer-bottom{display:flex;align-items:center;gap:9px;border-top:1px solid #edf0f2;padding-top:10px}.composer-bottom button{cursor:pointer}.attach,.mic{border:0;background:none;color:#4c6174;font-size:22px}.selector{position:relative}.selector>button{padding:8px 12px;border:1px solid #d5dee6;border-radius:7px;background:#f8fafb;color:#17324f;font-size:12px}.selector-menu{position:absolute;z-index:10;bottom:43px;left:0;width:290px;padding:6px;background:white;border:1px solid #d5dee6;border-radius:8px;box-shadow:0 12px 26px #102e4b28}.selector-menu button{display:block;width:100%;text-align:left;padding:10px;border:0;background:none;color:#17324f;border-radius:5px}.selector-menu button:hover{background:#f0f4f7}.selector-menu strong,.selector-menu small{display:block}.selector-menu small{font-size:11px;color:#64768a;margin-top:3px}.composer-spacer{flex:1}.send{width:37px;height:37px;border:0;border-radius:8px;background:#17324f;color:#fff}.send:disabled,.attach:disabled{opacity:.4;cursor:not-allowed}.mic:disabled{opacity:.45;cursor:not-allowed}.quick-actions{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:22px}.quick-actions button{padding:11px 14px;border:1px solid #e0e3e5;border-radius:8px;background:#fffdfa;color:#17324f;cursor:pointer;font-size:12px}.quick-actions button span{margin-left:14px;color:#aa8a57}.home-quote{text-align:center;margin-top:64px;font:italic 16px Georgia,serif;color:#7c8791}.home-quote small{display:block;margin-top:10px;font:10px Inter,sans-serif;letter-spacing:.16em;color:#ae8c5c}.watermark{position:absolute;right:3%;bottom:3%;font-size:min(29vw,360px);line-height:1;color:#d9d5c936;pointer-events:none}.conversation{display:flex;flex-direction:column;gap:28px;padding-top:30px}.thread{width:100%}.turn{margin-bottom:30px}.user{display:flex;justify-content:flex-end}.user-bubble{max-width:75%;padding:12px 17px;background:#e9eff3;border:1px solid #dce5ea;border-radius:14px 14px 3px 14px}.user-bubble p{margin:0 0 5px;white-space:pre-wrap}.user-bubble small{color:#66788c}.assistant-turn{padding:20px;background:#fffdfa;border:1px solid #e5e6e6;border-radius:12px;box-shadow:0 8px 28px #17324f09}.turn-label{margin:0 0 15px;color:#a28154;font-size:11px;font-weight:700;letter-spacing:.1em}.conversation .composer-region{width:100%;margin-top:auto;position:sticky;bottom:0;padding:12px 0 0;background:linear-gradient(transparent,#f8f7f3 14px)}.error{color:#9f4037;font-size:13px}.auth-screen{display:grid;place-items:center;min-height:100vh;background:#112a46;padding:24px}.auth-card{display:grid;gap:13px;width:min(420px,100%);padding:40px;background:#fffdfa;border-top:3px solid #c4a474;border-radius:10px;box-shadow:0 25px 70px #06172e55;color:#17324f}.auth-brand{font:normal 35px Georgia,serif;letter-spacing:.15em}.auth-card small{letter-spacing:.2em;color:#a38358}.auth-card h1{font:normal 28px Georgia,serif;margin:12px 0 0}.auth-card p{line-height:1.5}.auth-card label{display:grid;gap:6px;font-size:12px}.auth-card input{padding:10px;border:1px solid #ced7e0;border-radius:5px}.auth-card button{padding:12px;border:0;border-radius:5px;background:#17324f;color:#fff;cursor:pointer}.account-backdrop{position:fixed;inset:0;z-index:1000;display:grid;place-items:center;background:#0b1d2db8}.account-dialog{position:relative;width:min(400px,90%);padding:30px;background:#fff;border-radius:10px}.account-dialog button{position:absolute;right:18px;top:14px;border:0;background:none;font-size:24px}.account-dialog h2{font:normal 27px Georgia,serif}.mobile-menu,.mobile-overlay{display:none}button:focus-visible,textarea:focus-visible,input:focus-visible{outline:2px solid #b68a3a;outline-offset:2px}@media(max-width:1100px){.sidebar{flex-basis:250px}.workspace{padding-left:22px;padding-right:22px}.topbar{padding:0 22px}}@media(max-width:780px){.sidebar{position:fixed;z-index:30;transform:translateX(-100%);width:280px;transition:transform .2s}.sidebar.open{transform:none}.mobile-menu{display:block;border:0;background:none;font-size:21px}.mobile-overlay{display:block;position:fixed;inset:0;z-index:29;border:0;background:#0b1d2d88}.workspace{padding-top:40px}.topbar-copy{font-size:9px}.quick-actions{flex-direction:column}}
.mike-app{--myke-navy:#112a46;--myke-navy-soft:#233c59;--myke-paper:#f8f7f3;--myke-gold:#b89a68;--myke-line:#dfe3e5;--myke-muted:#69798a;--myke-shadow:0 18px 45px #142e4d16}
.sidebar{flex-basis:310px;padding:32px 21px;background:radial-gradient(circle at 90% 0%,#1c3856 0%,transparent 42%),linear-gradient(165deg,#142f4d,#0c213a 88%)}
.brand{padding-bottom:32px}.new-chat{padding:15px 17px;border-radius:11px;box-shadow:0 7px 20px #06182a26;transition:background .18s,transform .18s}.new-chat:hover{background:white;transform:translateY(-1px)}
.tool-wrap{position:relative}.tool-card{min-height:68px;transition:background .18s,border-color .18s}.tool-card:hover,.tool-card:focus-visible,.tool-card.active{background:var(--myke-navy-soft);border-color:#8d826b}.mini-card button svg{vertical-align:middle;margin-left:4px}.notification-icon{display:grid;place-items:center;color:#53677a}
.mini-card{position:fixed;z-index:120;width:min(320px,calc(100vw - 24px));max-height:calc(100vh - 24px);overflow-y:auto;margin:0;padding:20px 22px;background:#fffdf9;border:1px solid #e0d2bb;border-left:3px solid var(--myke-gold,#b89a68);border-radius:12px;color:#17324f;box-shadow:var(--myke-shadow,0 18px 45px #142e4d16);font-size:13px;animation:discover .18s ease-out}.mini-card p{margin:8px 0}.mini-card strong{font:normal 22px Georgia,serif}.mini-card .mini-category{color:#96754c}.mini-purpose{color:#66788c}.mini-card button:not(.mini-close){font-weight:700;color:#275780}.mini-card .mini-close{color:#52657b}@keyframes discover{from{opacity:0;transform:translateX(-5px)}to{opacity:1;transform:translateX(0)}}
.workspace{background:radial-gradient(circle at 50% 24%,#fffdfb 0%,transparent 55%)}.home{padding-top:12px}.kicker{display:flex;align-items:center;justify-content:center;gap:16px}.kicker::before,.kicker::after{content:'';display:block;width:48px;height:1px;background:#c9b997}.home h1{margin-top:26px}.intro{font-size:15px}.composer-region{margin-top:44px}.composer{border-radius:18px;box-shadow:var(--myke-shadow);padding:21px 23px 13px}.composer textarea{min-height:84px;max-height:220px;resize:none;overflow-y:auto}.composer:focus-within{border-color:#bba77f}.send{background:#23567f;border-radius:10px;transition:background .18s}.send:not(:disabled):hover{background:#173d61}.mic{display:grid;place-items:center;width:37px;height:37px;border-radius:10px;font-size:19px}.mic:hover{background:#f0f4f7}.mic.recording{color:#aa4339;background:#fbecea}.voice-timer{font-size:12px;color:#92423c;font-weight:700;font-variant-numeric:tabular-nums}.voice-message{font-size:12px;color:#42684d;margin:10px 5px}
.quick-actions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:28px}.quick-actions button{display:flex;align-items:flex-start;gap:12px;min-width:0;min-height:106px;padding:18px;text-align:left;border-radius:12px;box-shadow:0 8px 23px #142e4d09;transition:transform .18s,border-color .18s,box-shadow .18s}.quick-actions button:hover{transform:translateY(-2px);border-color:#c9b997;box-shadow:0 14px 28px #142e4d13}.quick-icon{font-size:22px;color:#a27f4e}.quick-copy{flex:1}.quick-copy strong,.quick-copy small{display:block}.quick-copy strong{font-size:12px;text-transform:uppercase;letter-spacing:.05em}.quick-copy small{margin-top:9px;color:#69798a;font-size:11px;line-height:1.5}.quick-actions button .quick-arrow{margin:0;color:#a27f4e}.home-quote{margin-top:54px}
@media(max-width:1280px){.sidebar{flex-basis:274px}.workspace{padding-left:24px;padding-right:24px}.quick-actions button{padding:14px;gap:8px}}
@media(max-width:900px){.sidebar{position:fixed;z-index:30;transform:translateX(-100%);width:285px;transition:transform .2s}.sidebar.open{transform:none}.mobile-menu{display:block;border:0;background:none;font-size:21px}.mobile-overlay{display:block;position:fixed;inset:0;z-index:29;border:0;background:#0b1d2d88}.quick-actions{grid-template-columns:1fr}.quick-actions button{min-height:75px}}
@media(max-width:550px){.workspace{padding:38px 16px 28px}.topbar{padding:0 15px}.topbar-copy{font-size:8px}.composer{padding:14px}.selector>button{font-size:11px;padding:7px}.home h1{font-size:40px}.subtitle{font-size:19px}.quick-actions button{min-height:70px}.home-quote{margin-top:36px}}
.mike-app{--home-sidebar-width:256px;--home-content-max:820px;--home-topbar-height:62px;--home-hero-title:clamp(44px,3.5vw,49px)}
.sidebar{flex:0 0 var(--home-sidebar-width);padding:24px 17px}
.brand{gap:11px;padding:2px 6px 21px}.brand-rule{height:33px}.brand strong{font-size:24px}.brand small{font-size:8.5px}
.new-chat{padding:11px 14px}.new-chat span{font-size:18px}.side-label{margin:27px 8px 11px}
.tool-nav{gap:4px}.tool-card{min-height:58px;padding:8px 7px}.tool-icon{width:30px;min-width:30px;height:30px;font-size:20px}.tool-copy strong{font-size:15px}.tool-copy small{font-size:11px}
.history{margin-top:18px;padding:14px 8px}.sidebar-profile{padding:12px 6px}.avatar{width:31px;height:31px}
.topbar{height:var(--home-topbar-height);padding:0 28px}.top-actions{gap:12px}.search-shortcut{font-size:22px}
.workspace{min-height:calc(100vh - var(--home-topbar-height));padding:52px 28px 28px}
.home,.composer-region,.thread{max-width:var(--home-content-max)}.home{padding-top:0}.kicker{font-size:10px}.home h1{font-size:var(--home-hero-title);line-height:1.08;margin:20px 0 9px}.subtitle{font-size:20px}.intro{font-size:14px;margin-top:13px;max-width:540px}
.composer-region{margin-top:32px}.composer{padding:16px 18px 10px}.composer textarea{min-height:70px;font-size:14.5px}.composer-bottom{padding-top:9px}
.mic{display:grid;place-items:center;flex:none;width:40px;height:40px;border:0;border-radius:50%;background:#edf0f3;color:#102b4c;transition:background .18s,box-shadow .18s,color .18s}.mic:hover:not(:disabled){background:#e1e7ec;box-shadow:0 2px 9px #102b4c18}.mic:disabled{opacity:.48;cursor:not-allowed}.mic.recording{background:#fbecea;color:#aa4339}.mic-icon{display:block;width:22px;height:22px}.mic-stop{display:block;width:12px;height:12px;border-radius:2px;background:currentColor}
.quick-actions{gap:11px;margin-top:20px}.quick-actions button{min-height:88px;padding:14px;gap:10px}.quick-icon{font-size:20px}.quick-copy strong{font-size:11.5px}.quick-copy small{margin-top:6px}.home-quote{margin-top:42px}
@media(max-width:900px){.sidebar{width:280px}.workspace{padding:40px 22px 28px}.quick-actions{grid-template-columns:1fr}}
@media(max-width:550px){.workspace{padding:38px 16px 28px}.topbar{padding:0 15px}.home h1{font-size:40px}.subtitle{font-size:19px}.composer{padding:14px}.quick-actions button{min-height:70px}}
.thread.search-thread{max-width:min(1220px,100%)}
.thread.case-thread{max-width:min(1240px,100%)}
.thread.court-thread{max-width:min(1240px,100%)}
.workspace.search-workspace{padding-top:40px}
.search-workspace .composer-region{max-width:min(1120px,100%);margin-top:24px}
.search-workspace .composer{padding:14px 18px 10px}
.search-workspace .composer textarea{min-height:64px}
.composer-filters{position:relative;flex:none}
.composer-filter-toggle{display:inline-flex;align-items:center;gap:7px;min-height:33px;padding:6px 10px;border:1px solid #d5dee6;border-radius:7px;background:#f8fafb;color:#244762;font:650 11px Inter,system-ui,sans-serif;transition:background .18s,border-color .18s}
.composer-filter-toggle svg{width:15px;height:15px;flex:none}
.composer-filter-toggle:hover,.composer-filter-toggle[aria-expanded="true"]{background:#edf3f7;border-color:#b9cbd9}
.composer-filter-toggle.active{color:#17375e;border-color:#b9cbd9}
.composer-filter-toggle:focus-visible{outline:2px solid #b68a3a;outline-offset:2px}
.filter-indicator{width:6px;height:6px;border-radius:50%;background:#b08a4c}
.composer-filter-panel{position:absolute;z-index:25;left:0;bottom:calc(100% + 8px);width:min(276px,calc(100vw - 32px));max-height:calc(100vh - 24px);overflow-y:auto;box-shadow:0 12px 28px #17324f1b;border-radius:10px}
.composer-filter-panel.below{bottom:auto;top:calc(100% + 8px)}
.composer-filter-panel.align-right{left:auto;right:0}
@media(max-width:560px){.composer-filter-panel{left:auto;right:0}}
.auth-links{display:flex;justify-content:space-between;gap:12px;margin-top:14px}
.auth-links button{border:0;background:none;color:#355c7b;font:600 12px Inter,system-ui,sans-serif;text-decoration:underline;cursor:pointer;padding:6px 0}
.auth-links button:focus-visible{outline:2px solid #b68a3a;outline-offset:2px;border-radius:3px}
.saved-case{display:grid;grid-template-columns:minmax(0,1fr) 28px 28px;align-items:center;gap:3px;margin:6px 0}
.saved-case-open{display:grid;min-width:0;gap:4px;text-align:left;padding:8px;border:1px solid #ffffff16;border-radius:7px;background:#ffffff08;color:#f7f5ef;cursor:pointer}
.saved-case-open strong{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px;font-weight:600}
.saved-case-open small{color:#c0c7cc;font-size:9px}
.saved-case-runs{display:grid;gap:4px;padding:0 2px 5px 10px}
.saved-case-runs a{display:grid;gap:3px;padding:7px 8px;border-left:2px solid #c4a474;color:#eee9db;text-decoration:none;font-size:10px}
.saved-case-runs a:hover{background:#ffffff0e}
.saved-case-runs a small,.saved-case-runs p{margin:0;color:#c0c7cc;font-size:9px}
.saved-case>button:not(.saved-case-open){height:28px;border:1px solid #ffffff20;border-radius:6px;background:#ffffff08;color:#eee9db;cursor:pointer}
.saved-case>button:hover{background:#ffffff18}
.saved-case button:focus-visible{outline:2px solid #d3bd93;outline-offset:2px}
.case-side-label{margin-top:30px}
.workspace-nav{display:grid;gap:5px}
.workspace-nav-link{display:flex;align-items:center;gap:11px;padding:11px 10px;border:1px solid transparent;border-radius:7px;color:#f7f5ef;text-decoration:none;font-size:13px}
.workspace-nav-link>span:first-child{display:grid;place-items:center;width:27px;height:27px;border:1px solid #a8946f;border-radius:6px;color:#ddc497;font-size:17px}
.workspace-nav-link small{margin-left:auto;color:#c8d0d7;font-size:10px}
.workspace-nav-link:hover,.workspace-nav-link.active{border-color:#9b845d;background:#233c59}
.workspace-nav-link:focus-visible{outline:2px solid #d3bd93;outline-offset:2px}
.sidebar-profile{width:100%;border:0;background:transparent;color:#f7f5ef;text-align:left;cursor:pointer;font:inherit}
.sidebar-profile:hover{background:#ffffff09}
.sidebar-profile:focus-visible{outline:2px solid #d3bd93;outline-offset:2px}
.account-name{max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px}
.workspace:has(.cases-page),.workspace:has(.case-detail),.workspace:has(.account-page){padding:42px clamp(22px,4vw,54px);overflow:visible}
.workspace-content{min-width:0}
@media(max-width:780px){.workspace:has(.cases-page),.workspace:has(.case-detail),.workspace:has(.account-page){padding:30px 20px}.account-name{display:none}}
@media(max-width:560px){.workspace:has(.cases-page),.workspace:has(.case-detail),.workspace:has(.account-page){padding:24px 15px}.case-side-label{margin-top:22px}}
</style>
