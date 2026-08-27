import { ref, reactive } from 'vue'

export function useNovaCase() {
  // ==========================================
  // 1. ESTADO DE ENTRADA (Panel Izquierdo)
  // ==========================================
  const caseContext = ref('')
  const uploadedFiles = ref([])

  // ==========================================
  // 2. ESTADO DE PROCESAMIENTO (Panel Derecho)
  // ==========================================
  const isAnalyzing = ref(false)
  const currentPhase = ref('idle') // Fases: idle, reading, researching, drafting, completed
  const activeAgentAction = ref('') // Texto dinámico para mostrar qué hace la IA
  const analysisError = ref(null)

  // ==========================================
  // 3. RESULTADO ESTRUCTURADO (Entregable Final)
  // ==========================================
  const finalStrategy = ref(null)

  // ==========================================
  // 4. ACCIONES Y CONEXIÓN CON EL BACKEND
  // ==========================================

  /**
   * Manejo de archivos subidos por el usuario
   */
  const handleFileUpload = (files) => {
    // Aquí puedes agregar lógica para validar tamaño o tipo de archivo (PDF, DOCX)
    Array.from(files).forEach(file => {
      uploadedFiles.value.push(file)
    })
  }

  const removeFile = (index) => {
    uploadedFiles.value.splice(index, 1)
  }

  /**
   * Dispara el análisis profundo del caso a través de LangGraph
   */
  const generateStrategy = async () => {
    if (!caseContext.value.trim() && uploadedFiles.value.length === 0) {
      analysisError.value = "Por favor, ingresa los hechos del caso o sube al menos un documento."
      return
    }

    isAnalyzing.value = true
    analysisError.value = null
    finalStrategy.value = null

    // === SIMULACIÓN DE FASES DE LANGGRAPH (Backend orquestado) ===
    // En producción, esto se conectaría por WebSockets (Socket.io) o Server-Sent Events (SSE)
    // para recibir el status en tiempo real de tu backend en FastAPI.
    
    // Fase 1: Lectura de hechos
    currentPhase.value = 'reading'
    activeAgentAction.value = 'Agente Analista: Extrayendo hechos clave del contexto...'
    
    setTimeout(() => {
      // Fase 2: Búsqueda de leyes y jurisprudencia en Supabase
      currentPhase.value = 'researching'
      activeAgentAction.value = 'Agente Investigador: Cruzando datos con la base de jurisprudencia (Supabase)...'
      
      setTimeout(() => {
        // Fase 3: Redacción estructurada
        currentPhase.value = 'drafting'
        activeAgentAction.value = 'Agente Estratega: Estructurando la fundamentación jurídica...'
        
        setTimeout(() => {
          // Fase 4: Entrega del resultado
          currentPhase.value = 'completed'
          activeAgentAction.value = 'Estrategia completada exitosamente.'
          isAnalyzing.value = false
          
          // Estructura de datos Premium para el documento final
          finalStrategy.value = {
            resumenHechos: "El caso trata sobre la nulidad de un acto jurídico por falta de manifestación de voluntad, fundamentado en firmas supuestamente falsificadas en un documento privado.",
            fundamentacionLegal: [
              "Artículo 219, inciso 1 del Código Civil (Causales de Nulidad).",
              "Artículo 2001, inciso 1 del Código Civil (Plazo prescriptorio)."
            ],
            jurisprudenciaClave: [
              {
                titulo: "Casación N° 20221-2023",
                extracto: "La simulación absoluta requiere prueba indiciaria concurrente para desvirtuar la manifestación de voluntad."
              }
            ],
            estrategiaSugerida: "1. Solicitar pericia grafotécnica sobre el documento original. \n2. Interponer demanda de nulidad acumulando pretensión de indemnización por daños y perjuicios.",
            nivelViabilidad: 85 // Porcentaje para mostrar un gráfico circular bonito
          }
        }, 3000)
      }, 3000)
    }, 2000)
  }

  // ==========================================
  // 5. EXPORTAR PARA LA VISTA
  // ==========================================
  return {
    caseContext,
    uploadedFiles,
    isAnalyzing,
    currentPhase,
    activeAgentAction,
    analysisError,
    finalStrategy,
    handleFileUpload,
    removeFile,
    generateStrategy
  }
}