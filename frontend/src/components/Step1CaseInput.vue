<template>
  <div class="input-container">
    <div class="content-wrapper" v-if="!loading">
      <h2 class="section-title">Configuración del Caso: {{ domainName }}</h2>
      
      <div class="form-grid">
        <div class="form-main">
          <div class="form-group">
            <label>Descripción de los Hechos</label>
            <textarea 
              v-model="casoText" 
              placeholder="Redacte los hechos del caso, pretensiones o pegue el texto principal aquí..."
              rows="6"
            ></textarea>
          </div>

          <div class="form-group">
            <label>Evidencia y Documentos Anexos (PDF, DOCX, TXT)</label>
            <div 
              class="upload-zone" 
              @click="triggerFileInput"
              @drop.prevent="handleDrop"
              @dragover.prevent
            >
              <!-- Añadido el atributo "multiple" -->
              <input type="file" ref="fileInput" @change="handleFileChange" hidden multiple accept=".pdf,.docx,.doc,.txt">
              
              <template v-if="selectedFiles.length === 0">
                <span class="upload-icon">📁</span>
                <p>Arrastre <strong>múltiples documentos</strong> aquí o haga clic para seleccionarlos.</p>
              </template>
              
              <template v-else>
                <div class="file-list" @click.stop>
                  <p class="file-count">✅ {{ selectedFiles.length }} archivo(s) listo(s) para análisis:</p>
                  <ul>
                    <li v-for="(file, index) in selectedFiles" :key="index">
                      <span class="filename">📄 {{ file.name }}</span>
                      <button class="btn-remove" @click="removeFile(index)">❌</button>
                    </li>
                  </ul>
                  <button class="btn-add-more" @click="triggerFileInput">+ Añadir más</button>
                </div>
              </template>
            </div>
          </div>
        </div>

        <div class="form-sidebar">
          <div class="settings-card">
            <h3>Parámetros de Simulación</h3>
            <div class="setting-item">
              <label>Agentes Involucrados</label>
              <select><option>Juez, Fiscal, Defensa</option></select>
            </div>
            <div class="setting-item">
              <label>Perfil del Juez</label>
              <select>
                <option>Estricto y Textualista</option>
                <option>Garantista</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div class="action-footer">
        <button class="btn-primary" @click="startSimulation" :disabled="!casoText && selectedFiles.length === 0">
          Procesar Expediente y Simular 🚀
        </button>
      </div>
    </div>

    <!-- Pantalla de Carga -->
    <div class="loading-wrapper" v-else>
      <div class="loader-spinner"></div>
      <h2 class="loader-title">Procesando Expediente Masivo</h2>
      <p class="loader-status">{{ currentLoadingText }}</p>
      <div class="progress-bar"><div class="progress-fill"></div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';

const props = defineProps({ domainName: String });
const emit = defineEmits(['simulation-complete']);

const casoText = ref('');
const selectedFiles = ref([]); // Ahora es un Array para múltiples archivos
const fileInput = ref(null);
const loading = ref(false);

const loadingSteps = [
  "Leyendo archivos adjuntos (PDFs/Word)...",
  "Recuperando normativa desde Supabase...",
  "Estructurando el expediente del caso...",
  "Generando estrategia del Fiscal/Demandante...",
  "Analizando vulnerabilidades (Defensa)...",
  "Deliberación final del Juez...",
  "Calculando métricas probabilísticas..."
];
const currentLoadingText = ref(loadingSteps[0]);
let stepInterval = null;

const triggerFileInput = () => fileInput.value.click();

const handleFileChange = (e) => {
  if (e.target.files.length > 0) {
    selectedFiles.value.push(...Array.from(e.target.files));
  }
};

const handleDrop = (e) => {
  if (e.dataTransfer.files.length > 0) {
    selectedFiles.value.push(...Array.from(e.dataTransfer.files));
  }
};

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1);
};

const startSimulation = async () => {
  if (!casoText.value && selectedFiles.value.length === 0) return;
  
  loading.value = true;
  let stepIndex = 0;
  
  stepInterval = setInterval(() => {
    if (stepIndex < loadingSteps.length - 1) {
      stepIndex++;
      currentLoadingText.value = loadingSteps[stepIndex];
    }
  }, 4000);

  const formData = new FormData();
  formData.append('caso', casoText.value);
  formData.append('dominio', props.domainName);
  
  // Añadimos TODOS los archivos iterando sobre el array
  selectedFiles.value.forEach(file => {
    formData.append('files', file); // El backend recibe 'files' como lista
  });

  try {
    const response = await fetch('http://127.0.0.1:5001/api/simulation/court/upload-and-simulate', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    
    if (data.success) {
      clearInterval(stepInterval);
      emit('simulation-complete', data.data);
    } else {
      alert("Error en el servidor: " + data.error);
      loading.value = false;
    }
  } catch (error) {
    alert("Error de conexión con el backend. Asegúrate de que Flask esté corriendo.");
    console.error(error);
    loading.value = false;
  } finally {
    clearInterval(stepInterval);
  }
};

onUnmounted(() => {
  if (stepInterval) clearInterval(stepInterval);
});
</script>

<style scoped>
.input-container { padding: 40px; height: 100%; }
.section-title { font-size: 1.8rem; color: #0A192F; margin-bottom: 30px; }

.form-grid { display: flex; gap: 30px; }
.form-main { flex: 2; }
.form-sidebar { flex: 1; }
.form-group { margin-bottom: 25px; }
label { display: block; font-weight: 600; color: #0A192F; margin-bottom: 10px; font-size: 0.95rem; }

textarea {
  width: 100%; padding: 15px; border: 1px solid #CCC; border-radius: 8px;
  font-family: inherit; font-size: 1rem; resize: vertical; background: white;
}

.upload-zone {
  border: 2px dashed #B0BEC5; background: #F8F9FA; padding: 20px;
  text-align: center; border-radius: 8px; cursor: pointer; transition: background 0.2s;
  min-height: 150px; display: flex; flex-direction: column; justify-content: center;
}
.upload-zone:hover { background: #E3F2FD; border-color: #4CAF50; }
.upload-icon { font-size: 2.5rem; display: block; margin-bottom: 10px; }

/* Lista de archivos */
.file-list { text-align: left; width: 100%; }
.file-count { font-weight: 600; color: #0A192F; margin-bottom: 10px; border-bottom: 1px solid #CCC; padding-bottom: 5px; }
.file-list ul { list-style: none; padding: 0; margin: 0 0 15px 0; max-height: 120px; overflow-y: auto; }
.file-list li { 
  display: flex; justify-content: space-between; align-items: center; 
  background: white; padding: 8px 12px; border: 1px solid #EEE; margin-bottom: 5px; border-radius: 4px;
}
.filename { font-size: 0.9rem; color: #555; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 80%; }
.btn-remove { background: none; border: none; cursor: pointer; font-size: 0.9rem; opacity: 0.6; }
.btn-remove:hover { opacity: 1; }
.btn-add-more { background: transparent; color: #0A192F; border: 1px solid #0A192F; padding: 6px 12px; border-radius: 4px; font-size: 0.85rem; cursor: pointer; font-weight: 600; }
.btn-add-more:hover { background: #EAEAEA; }

.settings-card {
  background: white; border-radius: 8px; padding: 25px; border: 1px solid #EAEAEA;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}
.settings-card h3 { font-size: 1.1rem; color: #0A192F; margin-bottom: 20px; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; }
.setting-item { margin-bottom: 15px; }
select { width: 100%; padding: 10px; border-radius: 6px; border: 1px solid #CCC; background: #F8F9FA; }

.action-footer { margin-top: 30px; text-align: right; }
.btn-primary {
  background: #0A192F; color: white; border: none; padding: 15px 30px;
  border-radius: 6px; font-size: 1.1rem; font-weight: 600; cursor: pointer; transition: 0.3s;
}
.btn-primary:hover:not(:disabled) { background: #D4AF37; color: #0A192F; }
.btn-primary:disabled { background: #CCC; cursor: not-allowed; }

.loading-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; text-align: center; }
.loader-spinner {
  width: 60px; height: 60px; border: 6px solid #EAEAEA; border-top: 6px solid #D4AF37;
  border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px;
}
.loader-title { font-size: 1.5rem; color: #0A192F; margin-bottom: 10px; }
.loader-status { color: #8892B0; font-size: 1.1rem; margin-bottom: 30px; font-weight: 500; }
.progress-bar { width: 100%; max-width: 500px; height: 8px; background: #EAEAEA; border-radius: 4px; overflow: hidden; }
.progress-fill { width: 30%; height: 100%; background: #D4AF37; animation: loadBar 30s linear forwards; }

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes loadBar { 0% { width: 5%; } 100% { width: 95%; } }
</style>