<template>
  <div class="results-container">
    <div class="header-actions">
      <h2 class="title">Evaluación y Veredicto</h2>
      <div class="action-buttons">
        <button class="btn-download" @click="downloadReport" :disabled="isDownloading">
          {{ isDownloading ? '⏳ Generando...' : '📄 Descargar Informe' }}
        </button>
        <button class="btn-secondary" @click="$emit('new-simulation')">← Nuevo Caso</button>
      </div>
    </div>

    <!-- Pestañas de Navegación -->
    <div class="tabs">
      <button :class="{ active: activeTab === 'debate' }" @click="activeTab = 'debate'">Debate Legal</button>
      <button :class="{ active: activeTab === 'base' }" @click="activeTab = 'base'">Base Jurídica</button>
      <button :class="{ active: activeTab === 'metricas' }" @click="activeTab = 'metricas'">Evaluación Inteligente 📊</button>
    </div>

    <div class="tab-content">
      <!-- PESTAÑA 1: DEBATE Y VEREDICTO -->
      <div v-if="activeTab === 'debate'" class="debate-grid">
        <div class="agent-card fiscal">
          <h3>👨‍⚖️ Postura de Fiscalía / Demandante</h3>
          <p class="agent-text">{{ results.fiscal }}</p>
        </div>
        <div class="agent-card defensa">
          <h3>🛡️ Estrategia de Defensa</h3>
          <p class="agent-text">{{ results.defensa }}</p>
        </div>
        <div class="agent-card juez full-width">
          <h3>⚖️ Resolución del Juez</h3>
          <p class="agent-text">{{ results.juez }}</p>
        </div>
      </div>

      <!-- PESTAÑA 2: BASE JURÍDICA -->
      <div v-if="activeTab === 'base'" class="base-legal-card">
        <h3>Normativa y Jurisprudencia Aplicada (RAG)</h3>
        <pre class="legal-text">{{ results.base_legal }}</pre>
      </div>

      <!-- PESTAÑA 3: MÉTRICAS Y GRÁFICOS -->
      <div v-if="activeTab === 'metricas'" class="metrics-grid">
        <div class="metric-box">
          <h4>Probabilidad de Éxito</h4>
          <div class="bar-row">
            <span>Demandante</span>
            <div class="bar-bg"><div class="bar-fill blue" :style="{ width: results.metricas.probabilidad_exito_demandante + '%' }"></div></div>
            <span>{{ results.metricas.probabilidad_exito_demandante }}%</span>
          </div>
          <div class="bar-row">
            <span>Demandado</span>
            <div class="bar-bg"><div class="bar-fill gray" :style="{ width: results.metricas.probabilidad_exito_demandado + '%' }"></div></div>
            <span>{{ results.metricas.probabilidad_exito_demandado }}%</span>
          </div>
        </div>

        <div class="metric-box">
          <h4>Evaluación de Calidad</h4>
          <div class="bar-row">
            <span>Arg. Fiscal</span>
            <div class="bar-bg"><div class="bar-fill gold" :style="{ width: results.metricas.calidad_argumentativa_fiscal + '%' }"></div></div>
            <span>{{ results.metricas.calidad_argumentativa_fiscal }}/100</span>
          </div>
          <div class="bar-row">
            <span>Arg. Defensa</span>
            <div class="bar-bg"><div class="bar-fill gold" :style="{ width: results.metricas.calidad_argumentativa_defensa + '%' }"></div></div>
            <span>{{ results.metricas.calidad_argumentativa_defensa }}/100</span>
          </div>
          <div class="bar-row">
            <span>Solidez Prob.</span>
            <div class="bar-bg"><div class="bar-fill green" :style="{ width: results.metricas.solidez_probatoria + '%' }"></div></div>
            <span>{{ results.metricas.solidez_probatoria }}/100</span>
          </div>
        </div>

        <div class="metric-box warning-box">
          <h4>Riesgo Procesal</h4>
          <div class="risk-circle">
            <span class="risk-number">{{ results.metricas.riesgo_procesal }}%</span>
          </div>
          <p class="risk-desc">Nivel de incertidumbre procesal y posibles contradicciones identificadas en la estrategia.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  results: Object
});

const activeTab = ref('debate');
const isDownloading = ref(false);

const downloadReport = async () => {
  isDownloading.value = true;
  try {
    const response = await fetch('http://127.0.0.1:5001/api/simulation/court/download-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(props.results)
    });

    if (!response.ok) throw new Error("Error del servidor al generar informe");

    // Lógica para descargar el archivo directamente en el navegador
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `LexSimulator_Expediente_${props.results.session_id || 'Legal'}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
  } catch (error) {
    alert("Hubo un problema al descargar el informe.");
    console.error(error);
  } finally {
    isDownloading.value = false;
  }
};
</script>

<style scoped>
.results-container { padding: 40px; }
.header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.title { font-size: 1.8rem; color: #0A192F; }

.action-buttons { display: flex; gap: 15px; }
.btn-secondary { background: white; border: 1px solid #CCC; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: 600; transition: 0.2s;}
.btn-secondary:hover { background: #F8F9FA; }

.btn-download { 
  background: #0A192F; color: white; border: 1px solid #0A192F; 
  padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: 600; transition: 0.3s;
}
.btn-download:hover:not(:disabled) { background: #D4AF37; border-color: #D4AF37; color: #0A192F; }
.btn-download:disabled { opacity: 0.7; cursor: not-allowed; }

.tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #EAEAEA; }
.tabs button { 
  background: transparent; border: none; padding: 12px 24px; font-size: 1rem; font-weight: 600; 
  color: #8892B0; cursor: pointer; border-bottom: 3px solid transparent; margin-bottom: -2px;
}
.tabs button.active { color: #0A192F; border-bottom: 3px solid #D4AF37; }

.debate-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.agent-card { background: white; padding: 25px; border-radius: 8px; border: 1px solid #EAEAEA; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
.agent-card h3 { font-size: 1.1rem; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #EEE; }
.agent-card.fiscal h3 { color: #B71C1C; }
.agent-card.defensa h3 { color: #0D47A1; }
.agent-card.juez h3 { color: #D4AF37; }
.full-width { grid-column: 1 / -1; background: #0A192F; color: white; }
.full-width .agent-text { color: #F8F9FA; }
.agent-text { font-size: 0.95rem; line-height: 1.7; white-space: pre-wrap; }

.base-legal-card { background: white; padding: 30px; border-radius: 8px; border: 1px solid #EAEAEA; }
.legal-text { font-family: monospace; font-size: 0.9rem; color: #333; white-space: pre-wrap; line-height: 1.6; background: #F8F9FA; padding: 20px; border-radius: 6px; }

.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
.metric-box { background: white; padding: 25px; border-radius: 8px; border: 1px solid #EAEAEA; }
.metric-box h4 { margin-bottom: 20px; color: #0A192F; font-size: 1.1rem; }

.bar-row { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; font-size: 0.9rem; font-weight: 600;}
.bar-row span:first-child { width: 90px; color: #555; }
.bar-bg { flex: 1; height: 10px; background: #EAEAEA; border-radius: 5px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 5px; transition: width 1s ease-in-out; }
.bar-fill.blue { background: #0D47A1; }
.bar-fill.gray { background: #8892B0; }
.bar-fill.gold { background: #D4AF37; }
.bar-fill.green { background: #4CAF50; }

.warning-box { text-align: center; background: #FFF8E1; border-color: #FFE082; }
.risk-circle { width: 100px; height: 100px; border: 6px solid #FF8F00; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; }
.risk-number { font-size: 1.8rem; font-weight: 800; color: #FF8F00; }
.risk-desc { font-size: 0.9rem; color: #795548; }
</style>