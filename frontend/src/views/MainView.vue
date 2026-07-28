<template>
  <div class="main-view">
    <!-- Header Institucional -->
    <header class="app-header">
      <div class="header-left">
        <div class="brand" @click="router.push('/')">NOVA IURIS</div>
        <div class="domain-badge">{{ domainName }}</div>
      </div>

      <div class="header-right">
        <div class="workflow-step">
          <span class="step-num">Paso {{ currentStep }}/2</span>
          <span class="step-name">{{ currentStep === 1 ? 'Análisis y Configuración' : 'Resolución y Métricas' }}</span>
        </div>
      </div>
    </header>

    <!-- Área Principal -->
    <main class="content-area">
      <!-- Panel Izquierdo: Resumen del Expediente -->
      <div class="panel-wrapper left">
        <div class="dossier-panel">
          <div class="dossier-header">
            <h3>📑 Expediente Activo</h3>
            <span class="status-tag" :class="currentStep === 2 ? 'status-ready' : 'status-draft'">
              {{ currentStep === 2 ? 'CERRADO' : 'EN PREPARACIÓN' }}
            </span>
          </div>
          <div class="dossier-body">
            <p><strong>Módulo:</strong> {{ domainName }}</p>
            <p><strong>Motor RAG:</strong> Conectado a Supabase</p>
            <p><strong>Agentes Activos:</strong> Juez Supremo, Fiscal, Defensa</p>
            <div class="dossier-illustration" v-if="currentStep === 1">
              Esperando carga de hechos y documentos probatorios...
            </div>
            <div class="dossier-illustration success" v-else>
              Análisis Multiagente Completado Exitosamente.
            </div>
          </div>
        </div>
      </div>

      <!-- Panel Derecho: Dinámico (Formulario -> Resultados) -->
      <div class="panel-wrapper right">
        <!-- Paso 1: Ingreso del Caso -->
        <Step1CaseInput 
          v-if="currentStep === 1" 
          :domainName="domainName"
          @simulation-complete="handleSimulationComplete"
        />
        
        <!-- Paso 2: Resultados y Gráficos -->
        <Step2Results 
          v-else-if="currentStep === 2"
          :results="simulationResults"
          @new-simulation="resetSimulation"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// Importamos los nuevos componentes que crearemos en el siguiente paso
import Step1CaseInput from '../components/Step1CaseInput.vue';
import Step2Results from '../components/Step2Results.vue';

const route = useRoute();
const router = useRouter();

// Obtenemos el nombre del dominio desde la URL (Ej: "Derecho Penal")
const domainName = ref(route.query.domain || 'Dominio General');

const currentStep = ref(1);
const simulationResults = ref(null);

// Recibe los datos del backend y pasa al paso 2
const handleSimulationComplete = (data) => {
  simulationResults.value = data;
  currentStep.value = 2;
};

// Reinicia la interfaz para un nuevo caso
const resetSimulation = () => {
  simulationResults.value = null;
  currentStep.value = 1;
};
</script>

<style scoped>
.main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #F4F7F9;
  font-family: 'Inter', sans-serif;
}

.app-header {
  height: 70px;
  background: #0A192F;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  border-bottom: 2px solid #D4AF37;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.brand {
  font-weight: 800;
  font-size: 1.2rem;
  color: #D4AF37;
  cursor: pointer;
}

.domain-badge {
  background: rgba(255, 255, 255, 0.1);
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
}

.workflow-step {
  display: flex;
  gap: 10px;
  align-items: center;
}

.step-num {
  color: #D4AF37;
  font-weight: 700;
}

.content-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.panel-wrapper {
  height: 100%;
  overflow-y: auto;
}

.panel-wrapper.left {
  width: 30%;
  border-right: 1px solid #EAEAEA;
  background: #FFFFFF;
  padding: 30px;
}

.panel-wrapper.right {
  width: 70%;
  background: #F4F7F9;
}

.dossier-panel {
  border: 1px solid #EAEAEA;
  border-radius: 8px;
  overflow: hidden;
}

.dossier-header {
  background: #F8F9FA;
  padding: 15px 20px;
  border-bottom: 1px solid #EAEAEA;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dossier-header h3 {
  font-size: 1rem;
  color: #0A192F;
}

.status-tag {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 4px;
}
.status-draft { background: #FFF3CD; color: #856404; }
.status-ready { background: #D4EDDA; color: #155724; }

.dossier-body {
  padding: 20px;
  font-size: 0.9rem;
  color: #555;
  line-height: 1.8;
}

.dossier-illustration {
  margin-top: 30px;
  padding: 20px;
  background: #F4F7F9;
  border: 1px dashed #CCC;
  border-radius: 6px;
  text-align: center;
  color: #8892B0;
  font-size: 0.85rem;
}
.dossier-illustration.success {
  background: #E8F5E9;
  border-color: #4CAF50;
  color: #2E7D32;
  font-weight: 600;
}
</style>