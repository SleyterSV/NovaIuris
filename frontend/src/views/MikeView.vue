<script setup>
import { computed, defineAsyncComponent, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CaseDocumentUpload from '@/components/common/CaseDocumentUpload.vue'
import ToolDetailModal from '@/components/common/ToolDetailModal.vue'
import { createWorkspace, createTurn, normalizeTool, caseReuseContext } from '@/utils/mikeWorkspace.js'
import { authRequired, authState, signIn, signOut, startAuth } from '@/config/supabaseSession.js'

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
const email = ref(''), password = ref(''), loginBusy = ref(false)
const menuOpen = ref(false), selectorOpen = ref(false), infoTool = ref(null), detailTool = ref(null)
const running = ref({ search:false, case:false, court:false })
const activeTool = computed(() => workspace.value.activeTool)
const activeMeta = computed(() => tools[activeTool.value] || null)
const placeholder = computed(() => ({ search:'¿Qué necesitas investigar?', case:'Describe el caso o adjunta documentos', court:'Describe el caso o reutiliza un análisis existente' })[activeTool.value] || 'Escribe tu consulta jurídica aquí…')
const canSend = computed(() => !running.value[activeTool.value || 'search'] &&
  (draft.value.trim().length > 0 || (activeTool.value !== 'search' && selectedDocuments.value.length > 0)))
const userName = computed(() => authState.user?.user_metadata?.full_name || authState.user?.user_metadata?.name || authState.user?.email || 'Mi cuenta')
const initials = computed(() => userName.value.split(/[\s@]+/).filter(Boolean).slice(0,2).map(part => part[0].toUpperCase()).join(''))

watch(() => route.query.tool, value => { workspace.value.activeTool = normalizeTool(value) })
watch(() => authState.user, (user, previous) => { if (previous && !user) newConversation() })
onMounted(startAuth)

function selectTool(value, reveal = true) {
  const tool = normalizeTool(value)
  workspace.value.activeTool = tool
  infoTool.value = reveal ? tool : null
  selectorOpen.value = false
  mobileMenu.value = false
  error.value = ''
  router.replace({ path:'/', query:tool ? { tool } : {} })
  nextTick(() => composer.value?.focus())
}
function newConversation() {
  workspace.value = createWorkspace()
  selectedDocuments.value = []
  draft.value = ''
  error.value = ''
  running.value = { search:false, case:false, court:false }
  infoTool.value = null
  detailTool.value = null
  selectTool(null, false)
}
function addOperation(kind, text, context = {}) {
  const request = { id:crypto.randomUUID(), text, caseId:context.caseId || workspace.value.caseId,
    documentIds:[...(context.documentIds || selectedDocuments.value)], ...(context.reuse ? { reuse:context.reuse } : {}) }
  workspace.value.turns.push(createTurn('user',kind,text,{ caseId:request.caseId, documentIds:request.documentIds }))
  const assistant = createTurn('assistant',kind,'',{ caseId:request.caseId, documentIds:request.documentIds,
    resultRef:request.id, status:'running' })
  assistant.request = request
  workspace.value.turns.push(assistant)
  workspace.value.title = text.slice(0,64)
  workspace.value.documentIds = [...request.documentIds]
  running.value = { ...running.value, [kind]:true }
  nextTick(() => document.querySelector('.turn:last-child')?.scrollIntoView({ behavior:'smooth', block:'start' }))
}
function submit() {
  if (!canSend.value) return
  const kind = activeTool.value || 'search'
  if (!activeTool.value) selectTool(kind, false)
  const text = draft.value.trim()
  if (kind === 'search' && text.length < 5) { error.value = 'Describe con mayor detalle la consulta jurídica.'; return }
  error.value = ''
  addOperation(kind, text || 'Analiza los documentos jurídicos aportados para este caso.')
  draft.value = ''
}
function onComposerKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing && !event.repeat) { event.preventDefault(); submit() }
}
function onTaskState(turn, state) {
  if (!workspace.value.turns.includes(turn)) return
  turn.status = state.running ? 'running' : 'completed'
  if (state.taskId) {
    turn.task_id = state.taskId
    workspace.value[`${state.tool}TaskId`] = state.taskId
  }
  running.value = { ...running.value, [state.tool]:state.running }
}
function onCaseCompleted(turn, { result, taskId, caseText }) {
  if (!workspace.value.turns.includes(turn) || result?.case_id !== workspace.value.caseId) return
  turn.task_id = taskId
  workspace.value.caseTaskId = taskId
  workspace.value.caseReuse = caseReuseContext(result,taskId,caseText)
}
function reuseCase(context) {
  if (!context || context.caseId !== workspace.value.caseId || running.value.court) return
  workspace.value.caseReuse = context
  workspace.value.documentIds = [...context.documentIds]
  selectedDocuments.value = [...context.documentIds]
  selectTool('court',false)
  addOperation('court',context.caseText,{ caseId:context.caseId, documentIds:context.documentIds, reuse:context })
}
function chooseFiles() { uploader.value?.$el?.querySelector('input[type="file"]')?.click() }
async function login() {
  if (loginBusy.value) return
  loginBusy.value = true
  loginError.value = await signIn(email.value,password.value)
  password.value = ''
  loginBusy.value = false
}
async function logout() {
  menuOpen.value = false
  newConversation()
  try { await signOut() } catch { loginError.value = 'Se cerró la sesión local. Vuelve a iniciar sesión.' }
}
function openAbout() { menuOpen.value = false; router.push('/about') }
</script>

<template>
  <div v-if="authState.loading" class="auth-screen" role="status"><div class="auth-card"><strong class="auth-brand">MYKE</strong><p>Comprobando sesión…</p></div></div>
  <div v-else-if="authRequired && !authState.user" class="auth-screen">
    <form class="auth-card" @submit.prevent="login"><strong class="auth-brand">MYKE</strong><small>LEGAL INTELLIGENCE</small><h1>Tu espacio jurídico</h1><p>Inicia sesión para continuar tu trabajo privado.</p><p v-if="authState.error" role="alert">{{ authState.error }}</p><template v-else><label>Correo electrónico<input v-model="email" type="email" required autocomplete="username"></label><label>Contraseña<input v-model="password" type="password" required autocomplete="current-password"></label><p v-if="loginError" role="alert">{{ loginError }}</p><button type="submit" :disabled="loginBusy">{{ loginBusy ? 'Ingresando…' : 'Ingresar' }}</button></template></form>
  </div>
  <div v-else class="mike-app">
    <aside class="sidebar" :class="{ open:mobileMenu }" aria-label="Navegación de MYKE">
      <button class="brand" type="button" @click="newConversation"><span class="brand-rule"></span><span><strong>MYKE</strong><small>LEGAL INTELLIGENCE</small></span></button>
      <button class="new-chat" type="button" @click="newConversation"><span aria-hidden="true">＋</span> Nuevo chat</button>
      <p class="side-label">HERRAMIENTAS</p>
      <nav class="tool-nav" aria-label="Herramientas de MYKE">
        <div v-for="(item,key) in tools" :key="key" class="tool-wrap">
          <button class="tool-card" :class="{ active:activeTool === key }" type="button" :aria-pressed="activeTool === key" @click="selectTool(key)">
            <span class="tool-icon" aria-hidden="true">{{ key === 'search' ? '⌕' : key === 'case' ? '▤' : '⚖' }}</span><span class="tool-copy"><strong>{{ item.name }}</strong><small>{{ item.description }}</small></span><span aria-hidden="true">›</span>
          </button>
          <div v-if="infoTool === key" class="mini-card"><p class="mini-category">{{ item.category }}</p><p>{{ item.short }}</p><button type="button" @click="detailTool = key">Conocer más →</button><button class="mini-close" type="button" :aria-label="`Ocultar información de ${item.name}`" @click="infoTool = null">×</button></div>
        </div>
      </nav>
      <section class="history"><h2>Chats recientes</h2><p>Sin conversaciones recientes</p></section>
      <div class="sidebar-profile"><span class="avatar">{{ initials || 'M' }}</span><span><strong>{{ userName }}</strong><small>MYKE Legal Intelligence</small></span></div>
    </aside>
    <button v-if="mobileMenu" class="mobile-overlay" type="button" aria-label="Cerrar menú" @click="mobileMenu = false"></button>
    <div class="main-area">
      <header class="topbar"><button class="mobile-menu" type="button" aria-label="Abrir menú" @click="mobileMenu = true">☰</button><span class="topbar-copy">EL DERECHO, POTENCIADO POR IA</span><div class="top-actions"><button class="search-shortcut" type="button" aria-label="Seleccionar Buscar" @click="selectTool('search')">⌕</button><div class="account"><button type="button" aria-haspopup="menu" :aria-expanded="menuOpen" @click="menuOpen = !menuOpen"><span class="avatar">{{ initials || 'M' }}</span>⌄</button><div v-if="menuOpen" class="account-menu" role="menu"><div class="account-identity"><strong>{{ userName }}</strong><small>{{ authState.user?.email }}</small></div><button type="button" role="menuitem" @click="menuOpen = false; detailTool = 'account'">Mi cuenta</button><button type="button" role="menuitem" @click="openAbout">Acerca de MYKE</button><hr><button type="button" role="menuitem" @click="logout">Cerrar sesión</button></div></div></div></header>
      <main class="workspace" :class="{ conversation:workspace.turns.length }">
        <div v-if="!workspace.turns.length" class="home"><p class="kicker">LEGAL INTELLIGENCE</p><h1>Hola, soy <span>MYKE</span></h1><p class="subtitle">Tu asistente jurídico inteligente</p><p class="intro">Investiga el derecho, analiza expedientes y explora escenarios jurídicos desde un mismo entorno.</p></div>
        <section v-else class="thread" aria-label="Conversación">
          <article v-for="turn in workspace.turns" :key="turn.id" class="turn" :class="turn.role">
            <div v-if="turn.role === 'user'" class="user-bubble"><p>{{ turn.text }}</p><small>{{ tools[turn.tool].label }}</small></div>
            <div v-else class="assistant-turn"><p class="turn-label">MYKE · {{ tools[turn.tool].label }}</p><component :is="panels[turn.tool]" embedded :request="turn.request" @task-state="onTaskState(turn,$event)" @case-completed="onCaseCompleted(turn,$event)" @reuse-case="reuseCase" /></div>
          </article>
        </section>
        <div class="composer-region">
          <form class="composer" @submit.prevent="submit"><textarea ref="composer" v-model="draft" rows="2" :placeholder="placeholder" aria-label="Consulta jurídica" @keydown="onComposerKeydown"></textarea><div class="composer-bottom"><button class="attach" type="button" :disabled="activeTool === 'search' || !activeTool" aria-label="Adjuntar documentos" title="Adjuntar documentos" @click="chooseFiles">＋</button><div class="selector"><button type="button" aria-haspopup="listbox" :aria-expanded="selectorOpen" @click="selectorOpen = !selectorOpen">{{ activeMeta?.label || 'Buscar' }} · {{ activeMeta?.name || 'NovaSearch' }} ▾</button><div v-if="selectorOpen" class="selector-menu" role="listbox" aria-label="Seleccionar herramienta"><button v-for="(item,key) in tools" :key="key" type="button" role="option" :aria-selected="activeTool === key" @click="selectTool(key)"><strong>{{ item.label }} · {{ item.name }}</strong><small>{{ item.description }}</small></button></div></div><span class="composer-spacer"></span><button type="button" class="mic" disabled title="Próximamente" aria-label="Entrada por voz próximamente">♩</button><button class="send" type="submit" :disabled="!canSend" aria-label="Enviar consulta">➤</button></div></form>
          <p v-if="error" class="error" role="alert">{{ error }}</p>
          <CaseDocumentUpload v-show="activeTool === 'case' || activeTool === 'court'" :key="workspace.id" ref="uploader" :case-id="workspace.caseId" :initial-document-ids="workspace.documentIds" :disabled="running.case || running.court" @update:document-ids="selectedDocuments = $event" />
          <div v-if="!workspace.turns.length" class="quick-actions"><button v-for="(item,key) in tools" :key="key" type="button" @click="selectTool(key)">{{ key === 'search' ? 'Buscar jurisprudencia' : key === 'case' ? 'Analizar un expediente' : 'Simular un caso' }} <span>→</span></button></div>
          <p v-if="!workspace.turns.length" class="home-quote">“La mejor estrategia comienza con mejor información.” <small>MYKE · LEGAL INTELLIGENCE</small></p>
        </div>
        <div class="watermark" aria-hidden="true">⚖</div>
      </main>
    </div>
    <ToolDetailModal v-if="detailTool && detailTool !== 'account'" :tool="tools[detailTool]" @close="detailTool = null" @use="selectTool(detailTool,false); detailTool = null" />
    <div v-if="detailTool === 'account'" class="account-backdrop" @click.self="detailTool = null"><section class="account-dialog" role="dialog" aria-modal="true" aria-labelledby="account-title"><button type="button" aria-label="Cerrar" @click="detailTool = null">×</button><h2 id="account-title">Mi cuenta</h2><p>{{ userName }}</p><p>{{ authState.user?.email }}</p></section></div>
  </div>
</template>

<style scoped>
.mike-app{display:flex;min-height:100vh;background:#f8f7f3;color:#142f4d;font-family:Inter,system-ui,sans-serif}.sidebar{position:sticky;top:0;flex:0 0 286px;height:100vh;display:flex;flex-direction:column;padding:29px 19px;background:#112a46;color:#f7f5ef}.brand{display:flex;align-items:center;gap:13px;text-align:left;border:0;background:none;color:#fff;cursor:pointer;padding:2px 10px 26px}.brand-rule{height:39px;width:3px;background:#c4a474}.brand strong{display:block;font:normal 28px Georgia,serif;letter-spacing:.15em}.brand small{display:block;font-size:9px;letter-spacing:.2em;color:#d7c7a8}.new-chat{padding:13px 16px;background:#f8f7f3;border:1px solid #dccba9;border-radius:8px;color:#163554;text-align:left;font-weight:600;cursor:pointer}.new-chat span{font-size:20px;margin-right:7px}.side-label{margin:35px 11px 13px;color:#b9b9b0;font-size:10px;letter-spacing:.17em}.tool-nav{display:grid;gap:7px}.tool-card{display:flex;align-items:center;gap:10px;width:100%;text-align:left;padding:12px 9px;border:1px solid transparent;border-radius:8px;background:none;color:#f9f7f0;cursor:pointer}.tool-card:hover,.tool-card.active{border-color:#9b845d;background:#233c59}.tool-icon{display:grid;place-items:center;width:34px;min-width:34px;height:34px;border:1px solid #a8946f;border-radius:7px;color:#ddc497;font-size:23px}.tool-copy{flex:1;min-width:0}.tool-copy strong,.tool-copy small{display:block}.tool-copy strong{font:normal 16px Georgia,serif}.tool-copy small{margin-top:4px;color:#c2cbd3;font-size:11px;line-height:1.35}.mini-card{position:relative;margin:2px 4px 9px 45px;padding:11px 24px 12px 12px;border-left:2px solid #d4b57f;background:#1d3957;border-radius:0 7px 7px 0;font-size:11px;line-height:1.5;color:#e8ebee}.mini-card p{margin:5px 0}.mini-category{font-size:9px;letter-spacing:.1em;color:#ddc497}.mini-card button{border:0;background:none;color:#ecd1a1;cursor:pointer;padding:3px 0}.mini-card .mini-close{position:absolute;top:4px;right:8px;font-size:17px}.history{margin-top:25px;border-top:1px solid #42566b;padding:18px 10px}.history h2{font-size:12px;letter-spacing:.07em}.history p{font-size:12px;color:#aab9c9}.sidebar-profile{display:flex;align-items:center;gap:10px;margin-top:auto;padding:16px 8px;border-top:1px solid #42566b;min-width:0}.sidebar-profile>span:last-child{min-width:0}.sidebar-profile strong,.sidebar-profile small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.sidebar-profile strong{font-size:12px}.sidebar-profile small{font-size:10px;color:#aebbc8;margin-top:3px}.avatar{display:inline-grid;place-items:center;flex:none;width:34px;height:34px;border-radius:50%;background:#e9dbbd;color:#142f4d;font-size:11px;font-weight:700}.main-area{flex:1;min-width:0}.topbar{display:flex;justify-content:space-between;align-items:center;height:72px;padding:0 34px;border-bottom:1px solid #e4e5e4;background:#fffdfa}.topbar-copy{font-size:11px;letter-spacing:.16em;font-weight:700}.top-actions{display:flex;align-items:center;gap:16px}.top-actions button{border:0;background:none;color:#17324f;cursor:pointer}.search-shortcut{font-size:25px}.account{position:relative}.account>button{display:flex;align-items:center;gap:8px}.account-menu{position:absolute;z-index:20;right:0;top:43px;width:220px;padding:8px;background:#fff;border:1px solid #dce3e9;border-radius:10px;box-shadow:0 14px 30px #061c3022}.account-menu button{display:block;width:100%;padding:10px;text-align:left}.account-menu button:hover{background:#f2f5f7}.account-identity{padding:10px;font-size:12px;overflow-wrap:anywhere}.account-identity strong,.account-identity small{display:block}.account-menu hr{border:0;border-top:1px solid #e3e8ec}.workspace{position:relative;min-height:calc(100vh - 72px);padding:70px 32px 40px;overflow:hidden}.home,.composer-region,.thread{position:relative;z-index:1;max-width:890px;margin:auto}.home{text-align:center}.kicker{font-size:11px;letter-spacing:.2em;color:#a38358}.home h1{font:normal clamp(37px,4vw,59px) Georgia,serif;margin:18px 0 10px}.home h1 span{color:#9c7b4d}.subtitle{font:normal 23px Georgia,serif;margin:0}.intro{max-width:560px;margin:17px auto 0;color:#69798a;line-height:1.65;font-size:14px}.composer-region{margin-top:35px}.composer{padding:17px 18px 11px;border:1px solid #d9dfe4;border-radius:16px;background:#fff;box-shadow:0 12px 32px #142e4d12}.composer textarea{display:block;width:100%;min-height:72px;resize:vertical;border:0;outline:0;color:#17324f;background:none;font:15px/1.5 Inter,system-ui,sans-serif}.composer-bottom{display:flex;align-items:center;gap:9px;border-top:1px solid #edf0f2;padding-top:10px}.composer-bottom button{cursor:pointer}.attach,.mic{border:0;background:none;color:#4c6174;font-size:22px}.selector{position:relative}.selector>button{padding:8px 12px;border:1px solid #d5dee6;border-radius:7px;background:#f8fafb;color:#17324f;font-size:12px}.selector-menu{position:absolute;z-index:10;bottom:43px;left:0;width:290px;padding:6px;background:white;border:1px solid #d5dee6;border-radius:8px;box-shadow:0 12px 26px #102e4b28}.selector-menu button{display:block;width:100%;text-align:left;padding:10px;border:0;background:none;color:#17324f;border-radius:5px}.selector-menu button:hover{background:#f0f4f7}.selector-menu strong,.selector-menu small{display:block}.selector-menu small{font-size:11px;color:#64768a;margin-top:3px}.composer-spacer{flex:1}.send{width:37px;height:37px;border:0;border-radius:8px;background:#17324f;color:#fff}.send:disabled,.attach:disabled{opacity:.4;cursor:not-allowed}.mic:disabled{opacity:.45;cursor:not-allowed}.quick-actions{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:22px}.quick-actions button{padding:11px 14px;border:1px solid #e0e3e5;border-radius:8px;background:#fffdfa;color:#17324f;cursor:pointer;font-size:12px}.quick-actions button span{margin-left:14px;color:#aa8a57}.home-quote{text-align:center;margin-top:64px;font:italic 16px Georgia,serif;color:#7c8791}.home-quote small{display:block;margin-top:10px;font:10px Inter,sans-serif;letter-spacing:.16em;color:#ae8c5c}.watermark{position:absolute;right:3%;bottom:3%;font-size:min(29vw,360px);line-height:1;color:#d9d5c936;pointer-events:none}.conversation{display:flex;flex-direction:column;gap:28px;padding-top:30px}.thread{width:100%}.turn{margin-bottom:30px}.user{display:flex;justify-content:flex-end}.user-bubble{max-width:75%;padding:12px 17px;background:#e9eff3;border:1px solid #dce5ea;border-radius:14px 14px 3px 14px}.user-bubble p{margin:0 0 5px;white-space:pre-wrap}.user-bubble small{color:#66788c}.assistant-turn{padding:20px;background:#fffdfa;border:1px solid #e5e6e6;border-radius:12px;box-shadow:0 8px 28px #17324f09}.turn-label{margin:0 0 15px;color:#a28154;font-size:11px;font-weight:700;letter-spacing:.1em}.conversation .composer-region{width:100%;margin-top:auto;position:sticky;bottom:0;padding:12px 0 0;background:linear-gradient(transparent,#f8f7f3 14px)}.error{color:#9f4037;font-size:13px}.auth-screen{display:grid;place-items:center;min-height:100vh;background:#112a46;padding:24px}.auth-card{display:grid;gap:13px;width:min(420px,100%);padding:40px;background:#fffdfa;border-top:3px solid #c4a474;border-radius:10px;box-shadow:0 25px 70px #06172e55;color:#17324f}.auth-brand{font:normal 35px Georgia,serif;letter-spacing:.15em}.auth-card small{letter-spacing:.2em;color:#a38358}.auth-card h1{font:normal 28px Georgia,serif;margin:12px 0 0}.auth-card p{line-height:1.5}.auth-card label{display:grid;gap:6px;font-size:12px}.auth-card input{padding:10px;border:1px solid #ced7e0;border-radius:5px}.auth-card button{padding:12px;border:0;border-radius:5px;background:#17324f;color:#fff;cursor:pointer}.account-backdrop{position:fixed;inset:0;z-index:1000;display:grid;place-items:center;background:#0b1d2db8}.account-dialog{position:relative;width:min(400px,90%);padding:30px;background:#fff;border-radius:10px}.account-dialog button{position:absolute;right:18px;top:14px;border:0;background:none;font-size:24px}.account-dialog h2{font:normal 27px Georgia,serif}.mobile-menu,.mobile-overlay{display:none}button:focus-visible,textarea:focus-visible,input:focus-visible{outline:2px solid #b68a3a;outline-offset:2px}@media(max-width:1100px){.sidebar{flex-basis:250px}.workspace{padding-left:22px;padding-right:22px}.topbar{padding:0 22px}}@media(max-width:780px){.sidebar{position:fixed;z-index:30;transform:translateX(-100%);width:280px;transition:transform .2s}.sidebar.open{transform:none}.mobile-menu{display:block;border:0;background:none;font-size:21px}.mobile-overlay{display:block;position:fixed;inset:0;z-index:29;border:0;background:#0b1d2d88}.workspace{padding-top:40px}.topbar-copy{font-size:9px}.quick-actions{flex-direction:column}}
</style>
