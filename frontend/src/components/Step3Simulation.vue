<template>
  <div class="novacourt-panel">
    <!-- Top Control Bar: Fases del Juicio -->
    <header class="court-header glass-panel">
      <div class="phase-stepper">
        <div class="step" :class="{ active: phase === 0 || phase === 1, completed: phase === 2 }">
          <span class="step-indicator">01</span>
          <span class="step-label">Apertura</span>
        </div>
        <div class="step-divider"></div>
        <div class="step" :class="{ active: phase === 1 && allActions.length > 5, completed: phase === 2 }">
          <span class="step-indicator">02</span>
          <span class="step-label">Debate y Refutación</span>
        </div>
        <div class="step-divider"></div>
        <div class="step" :class="{ active: phase === 2, completed: phase === 2 }">
          <span class="step-indicator">03</span>
          <span class="step-label">Veredicto</span>
        </div>
      </div>

      <div class="header-actions">
        <button 
          class="btn-premium"
          :disabled="phase !== 2 || isGeneratingReport"
          @click="handleNextStep"
        >
          <span v-if="isGeneratingReport" class="loading-spinner"></span>
          {{ isGeneratingReport ? 'Generando Resolución...' : 'Emitir Fallo Oficial ➔' }}
        </button>
      </div>
    </header>

    <div class="court-arena">
      <!-- Panel Izquierdo: Estado de los Agentes -->
      <aside class="agents-panel">
        <h3 class="panel-title">ESTADO DE IA</h3>
        
        <div class="agent-card" :class="{ processing: isStarting || (phase === 1 && allActions.length % 3 === 0) }">
          <div class="agent-avatar judge-aura">J</div>
          <div class="agent-details">
            <span class="agent-role">Juez</span>
            <span class="agent-status">{{ phase === 2 ? 'Fallo Emitido' : 'Analizando...' }}</span>
          </div>
        </div>

        <div class="agent-card" :class="{ processing: phase === 1 && allActions.length % 3 === 1 }">
          <div class="agent-avatar fiscal-aura">F</div>
          <div class="agent-details">
            <span class="agent-role">Fiscalía</span>
            <span class="agent-status">{{ phase === 0 ? 'Preparando' : 'Argumentando' }}</span>
          </div>
        </div>

        <div class="agent-card" :class="{ processing: phase === 1 && allActions.length % 3 === 2 }">
          <div class="agent-avatar defense-aura">D</div>
          <div class="agent-details">
            <span class="agent-role">Defensa</span>
            <span class="agent-status">{{ phase === 0 ? 'Preparando' : 'Buscando Jurisprudencia' }}</span>
          </div>
        </div>
      </aside>

      <!-- Panel Central: Transcripción del Debate -->
      <main class="transcript-panel glass-panel" ref="scrollContainer">
        <div class="transcript-header">
          <span class="live-indicator"><span class="dot"></span> TRANSCRIPCIÓN EN TIEMPO REAL</span>
          <span class="sim-id mono">ID: {{ simulationId || 'STANDBY' }}</span>
        </div>

        <div class="transcript-feed">
          <TransitionGroup name="fade-slide">
            <div 
              v-for="action in chronologicalActions" 
              :key="action._uniqueId || action.id" 
              class="speech-bubble-wrapper"
              :class="getAgentAlignment(action.agent_name)"
            >
              <div class="speech-bubble" :class="getAgentRoleClass(action.agent_name)">
                <div class="bubble-header">
                  <span class="speaker-name">{{ action.agent_name || 'Agente' }}</span>
                  <span class="speaker-time mono">{{ formatActionTime(action.timestamp) }}</span>
                </div>
                
                <div class="bubble-content">
                  <!-- Mapeo de la acción de LangGraph a diálogo legal -->
                  {{ action.action_args?.content || action.action_args?.quote_content || 'Buscando precedentes en la base de datos...' }}
                </div>

                <!-- Citas Jurisprudenciales (Si LangGraph usó SEARCH_POSTS o similar) -->
                <div v-if="action.action_type === 'SEARCH_POSTS' || action.action_args?.query" class="legal-citation">
                  <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                  Consultando: "{{ action.action_args?.query || 'Jurisprudencia vinculante' }}"
                </div>
              </div>
            </div>
          </TransitionGroup>

          <div v-if="allActions.length === 0" class="waiting-state">
            <div class="radar-spinner"></div>
            <p>Conectando con el Tribunal Digital...</p>
          </div>
        </div>
      </main>

      <!-- Panel Derecho: Logs y Métricas -->
      <aside class="metrics-panel">
        <div class="metrics-widget glass-panel">
          <h3 class="panel-title">MÉTRICAS (RONDAS: {{ runStatus.twitter_current_round || 0 }})</h3>
          <div class="metric-bar">
            <div class="metric-label">Solidez Legal</div>
            <div class="progress-track"><div class="progress-fill" :style="{ width: Math.min(allActions.length * 2, 100) + '%' }"></div></div>
          </div>
          <div class="metric-bar">
            <div class="metric-label">Citas Zep DB</div>
            <div class="progress-track"><div class="progress-fill" style="width: 75%; background: #2563EB;"></div></div>
          </div>
        </div>

        <div class="system-logs glass-panel">
          <h3 class="panel-title">TERMINAL DE EVENTOS</h3>
          <div class="log-content" ref="logContent">
            <div class="log-line" v-for="(log, idx) in systemLogs" :key="idx">
              <span class="log-time">[{{ log.time }}]</span>
              <span class="log-msg">{{ log.msg }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { startSimulation, stopSimulation, getRunStatus, getRunStatusDetail } from '../api/simulation'
import { generateReport } from '../api/report'

const props = defineProps({
  simulationId: String,
  maxRounds: Number,
  minutesPerRound: { type: Number, default: 30 },
  projectData: Object,
  graphData: Object,
  systemLogs: Array
})

const emit = defineEmits(['go-back', 'next-step', 'add-log', 'update-status'])
const router = useRouter()

const isGeneratingReport = ref(false)
const phase = ref(0)
const isStarting = ref(false)
const isStopping = ref(false)
const startError = ref(null)
const runStatus = ref({})
const allActions = ref([])
const actionIds = ref(new Set())
const scrollContainer = ref(null)
const logContent = ref(null)

const chronologicalActions = computed(() => allActions.value)

// Lógica de UI para los nuevos roles legales
const getAgentAlignment = (name) => {
  const lowerName = (name || '').toLowerCase()
  if (lowerName.includes('fiscal') || lowerName.includes('acusador')) return 'align-left'
  if (lowerName.includes('defensa') || lowerName.includes('abogado')) return 'align-right'
  return 'align-center' // Juez
}

const getAgentRoleClass = (name) => {
  const lowerName = (name || '').toLowerCase()
  if (lowerName.includes('fiscal')) return 'role-fiscal'
  if (lowerName.includes('defensa')) return 'role-defense'
  return 'role-judge'
}

const formatActionTime = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('es-PE', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

const addLog = (msg) => emit('add-log', msg)

const resetAllState = () => {
  phase.value = 0
  runStatus.value = {}
  allActions.value = []
  actionIds.value = new Set()
  startError.value = null
  isStarting.value = false
  isStopping.value = false
  stopPolling()
}

// ==== LA LÓGICA DE TU API SE MANTIENE INTACTA ====
const doStartSimulation = async () => {
  if (!props.simulationId) { addLog('Error: ID de simulación faltante'); return; }
  resetAllState()
  isStarting.value = true
  addLog('Iniciando Tribunal Digital Nova Iuris...')
  emit('update-status', 'processing')
  
  try {
    const params = { simulation_id: props.simulationId, platform: 'parallel', force: true, enable_graph_memory_update: true }
    if (props.maxRounds) params.max_rounds = props.maxRounds
    
    const res = await startSimulation(params)
    if (res.success && res.data) {
      addLog('Motor LangGraph inicializado. PID: ' + (res.data.process_pid || '-'))
      phase.value = 1
      runStatus.value = res.data
      startStatusPolling()
      startDetailPolling()
    } else {
      emit('update-status', 'error')
    }
  } catch (err) {
    addLog('Excepción al iniciar: ' + err.message)
    emit('update-status', 'error')
  } finally {
    isStarting.value = false
  }
}

let statusTimer = null
let detailTimer = null

const startStatusPolling = () => { statusTimer = setInterval(fetchRunStatus, 2000) }
const startDetailPolling = () => { detailTimer = setInterval(fetchRunStatusDetail, 3000) }
const stopPolling = () => { clearInterval(statusTimer); clearInterval(detailTimer); }

const fetchRunStatus = async () => {
  if (!props.simulationId) return
  try {
    const res = await getRunStatus(props.simulationId)
    if (res.success && res.data) {
      runStatus.value = res.data
      const isCompleted = res.data.runner_status === 'completed' || res.data.runner_status === 'stopped'
      if (isCompleted) {
        addLog('Debate concluido. Esperando resolución.')
        phase.value = 2
        stopPolling()
        emit('update-status', 'completed')
      }
    }
  } catch (err) { console.warn(err) }
}

const fetchRunStatusDetail = async () => {
  if (!props.simulationId) return
  try {
    const res = await getRunStatusDetail(props.simulationId)
    if (res.success && res.data) {
      const serverActions = res.data.all_actions || []
      serverActions.forEach(action => {
        const actionId = action.id || `${action.timestamp}-${action.platform}-${action.agent_id}-${action.action_type}`
        if (!actionIds.value.has(actionId)) {
          actionIds.value.add(actionId)
          allActions.value.push({ ...action, _uniqueId: actionId })
          
          // Auto-scroll en la transcripción
          nextTick(() => {
            if (scrollContainer.value) scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
          })
        }
      })
    }
  } catch (err) { console.warn(err) }
}

const handleNextStep = async () => {
  if (!props.simulationId || isGeneratingReport.value) return
  isGeneratingReport.value = true
  addLog('Estructurando fallo final y reporte táctico...')
  
  try {
    const res = await generateReport({ simulation_id: props.simulationId, force_regenerate: true })
    if (res.success && res.data) {
      router.push({ name: 'Report', params: { reportId: res.data.report_id } })
    } else {
      isGeneratingReport.value = false
    }
  } catch (err) {
    isGeneratingReport.value = false
  }
}

watch(() => props.systemLogs?.length, () => {
  nextTick(() => { if (logContent.value) logContent.value.scrollTop = logContent.value.scrollHeight })
})

onMounted(() => { if (props.simulationId) doStartSimulation() })
onUnmounted(() => { stopPolling() })
</script>

<style scoped>
/* ESTILOS PREMIUM DARK MODE - NOVA IURIS */
.novacourt-panel {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0B1120; /* Deep Midnight Blue */
  color: #F8FAFC;
  font-family: 'Inter', system-ui, sans-serif;
  overflow: hidden;
}

.mono { font-family: 'JetBrains Mono', monospace; }

.glass-panel {
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

/* TOP BAR */
.court-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  z-index: 10;
}

.phase-stepper {
  display: flex;
  align-items: center;
  gap: 16px;
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.4;
  transition: all 0.3s;
}

.step.active { opacity: 1; }
.step.completed { color: #cda34f; opacity: 1; } /* Dorado Nova Iuris */

.step-indicator {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  padding: 4px 8px;
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
}
.step.active .step-indicator { background: #2563EB; color: #000; }

.step-label { font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }
.step-divider { width: 40px; height: 1px; background: rgba(255,255,255,0.2); }

.btn-premium {
  background: #2563EB;
  color: #0B1120;
  border: none;
  padding: 10px 24px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-premium:hover:not(:disabled) { background: #dfb55d; box-shadow: 0 0 15px rgba(205, 163, 79, 0.4); }
.btn-premium:disabled { background: #334155; color: #94A3B8; cursor: not-allowed; }

/* MAIN ARENA */
.court-arena {
  display: grid;
  grid-template-columns: 260px 1fr 300px;
  gap: 24px;
  padding: 24px;
  height: calc(100vh - 80px);
}

.panel-title {
  font-size: 10px;
  font-weight: 700;
  color: #94A3B8;
  letter-spacing: 2px;
  margin-bottom: 16px;
}

/* LEFT PANEL: AGENTS */
.agents-panel { display: flex; flex-direction: column; gap: 16px; }

.agent-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  transition: all 0.3s;
}

.agent-card.processing {
  border-color: rgba(255,255,255,0.2);
  background: rgba(30, 41, 59, 0.8);
}

.agent-avatar {
  width: 40px; height: 40px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 16px;
}

/* Auras de los Agentes */
.agent-card.processing .judge-aura { box-shadow: 0 0 15px rgba(205, 163, 79, 0.5); background: rgba(205, 163, 79, 0.2); color: #cda34f; }
.agent-card.processing .fiscal-aura { box-shadow: 0 0 15px rgba(239, 68, 68, 0.5); background: rgba(239, 68, 68, 0.2); color: #EF4444; }
.agent-card.processing .defense-aura { box-shadow: 0 0 15px rgba(56, 189, 248, 0.5); background: rgba(56, 189, 248, 0.2); color: #38BDF8; }

.agent-role { display: block; font-size: 13px; font-weight: 600; color: #F8FAFC; }
.agent-status { display: block; font-size: 11px; color: #94A3B8; margin-top: 4px; }

/* CENTER PANEL: TRANSCRIPT */
.transcript-panel {
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.transcript-header {
  display: flex; justify-content: space-between;
  padding: 12px 24px;
  background: rgba(15, 23, 42, 0.6);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 10px; font-weight: 700; letter-spacing: 1px; color: #94A3B8;
}

.live-indicator { display: flex; align-items: center; gap: 8px; color: #10B981; }
.dot { width: 6px; height: 6px; background: #10B981; border-radius: 50%; animation: blink 1.5s infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

.transcript-feed {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.speech-bubble-wrapper { display: flex; width: 100%; }
.align-left { justify-content: flex-start; }
.align-right { justify-content: flex-end; }
.align-center { justify-content: center; width: 80%; margin: 0 auto; }

.speech-bubble {
  max-width: 80%;
  padding: 16px;
  border-radius: 8px;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255,255,255,0.05);
}

.role-fiscal { border-left: 3px solid #EF4444; }
.role-defense { border-right: 3px solid #38BDF8; }
.role-judge { border-top: 3px solid #cda34f; background: rgba(205, 163, 79, 0.05); text-align: center; }

.bubble-header { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 11px; color: #94A3B8; }
.speaker-name { font-weight: 700; color: #F8FAFC; text-transform: uppercase; letter-spacing: 1px; }

.bubble-content { font-size: 14px; line-height: 1.6; color: #E2E8F0; }

.legal-citation {
  margin-top: 12px; padding: 8px 12px;
  background: rgba(0,0,0,0.2); border-radius: 4px;
  font-size: 11px; color: #cda34f;
  display: flex; align-items: center; gap: 8px;
}

/* RIGHT PANEL: METRICS & LOGS */
.metrics-panel { display: flex; flex-direction: column; gap: 24px; }

.metrics-widget, .system-logs {
  padding: 16px; border-radius: 8px;
}

.metric-bar { margin-bottom: 12px; }
.metric-label { font-size: 11px; color: #94A3B8; margin-bottom: 6px; text-transform: uppercase; }
.progress-track { height: 4px; background: rgba(0,0,0,0.3); border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: #38BDF8; transition: width 0.5s ease; }

.system-logs { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.log-content { flex: 1; overflow-y: auto; font-size: 10px; color: #64748B; display: flex; flex-direction: column; gap: 4px; }
.log-line { display: flex; gap: 8px; }
.log-time { color: #475569; }

/* ANIMATIONS */
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.4s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(10px); }
.fade-slide-leave-to { opacity: 0; }

.waiting-state {
  margin: auto; display: flex; flex-direction: column; align-items: center; gap: 16px; color: #64748B; font-size: 11px; letter-spacing: 1px; text-transform: uppercase;
}
.radar-spinner { width: 40px; height: 40px; border: 1px solid rgba(255,255,255,0.1); border-radius: 50%; animation: pulse 2s infinite; }
@keyframes pulse { 0% { transform: scale(0.8); box-shadow: 0 0 0 0 rgba(205, 163, 79, 0.4); } 70% { transform: scale(1.2); box-shadow: 0 0 0 20px rgba(205, 163, 79, 0); } 100% { transform: scale(0.8); box-shadow: 0 0 0 0 rgba(205, 163, 79, 0); } }

/* SCROLLBARS */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
</style>