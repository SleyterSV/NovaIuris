<template>
  <div class="mike-app">

    <!-- =========================================================
         SIDEBAR
    ========================================================== -->
    <aside
      class="sidebar"
      :class="{ 'sidebar-open': mobileSidebarOpen }"
    >
      <!-- Marca -->
      <div class="sidebar-top">
        <button
          class="brand"
          type="button"
          aria-label="Ir al inicio de MIKE"
          @click="goMikeHome"
        >
          <span class="brand-line"></span>

          <span class="brand-copy">
            <strong>MIKE</strong>
            <small>LEGAL INTELLIGENCE</small>
          </span>
        </button>

        <button
          class="mobile-close"
          type="button"
          aria-label="Cerrar menú"
          @click="mobileSidebarOpen = false"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M5 5l14 14M19 5 5 19" />
          </svg>
        </button>
      </div>


      <!-- =======================================================
           HERRAMIENTAS
      ======================================================== -->
      <nav
        class="tools-nav"
        aria-label="Herramientas de MIKE"
      >
        <div
          v-for="tool in tools"
          :key="tool.id"
          class="tool-card-wrap"
        >

          <div class="tool-row">

            <!-- Acceso principal -->
            <button
              type="button"
              class="tool-button"
              @click="navigate(tool.route)"
            >
              <span class="tool-icon">

                <!-- NovaSearch -->
                <svg
                  v-if="tool.icon === 'search'"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle cx="10.5" cy="10.5" r="6.5" />
                  <path d="m15.5 15.5 5 5" />
                </svg>

                <!-- NovaCase -->
                <svg
                  v-else-if="tool.icon === 'case'"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path d="M6 3h9l4 4v14H6z" />
                  <path d="M15 3v5h5" />
                  <path d="M9 12h7M9 16h7" />
                </svg>

                <!-- NovaCourt -->
                <svg
                  v-else
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path d="M12 3v18" />
                  <path d="M5 7h14" />
                  <path d="m5 7-3 6h6L5 7Z" />
                  <path d="m19 7-3 6h6l-3-6Z" />
                  <path d="M7 21h10" />
                </svg>

              </span>

              <span class="tool-copy">
                <strong>{{ tool.name }}</strong>
                <small>{{ tool.description }}</small>
              </span>

              <svg
                class="tool-arrow"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M9 6l6 6-6 6" />
              </svg>
            </button>


            <!-- Eslabón -->
            <button
              type="button"
              class="tool-info-trigger"
              :aria-label="`Conocer más sobre ${tool.name}`"
              :title="`Conocer ${tool.name}`"
              @click="openToolInfo(tool)"
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M10.5 13.5a4.5 4.5 0 0 0 6.36 0l2.1-2.1a4.5 4.5 0 0 0-6.36-6.36l-1.2 1.2"
                />
                <path
                  d="M13.5 10.5a4.5 4.5 0 0 0-6.36 0l-2.1 2.1a4.5 4.5 0 1 0 6.36 6.36l1.2-1.2"
                />
              </svg>
            </button>

          </div>


          <!-- ===================================================
               MINI CARD AL PASAR EL MOUSE
          ==================================================== -->
          <aside
            class="tool-hover-card"
            role="tooltip"
          >
            <div class="hover-card-top">
              <span class="hover-category">
                {{ tool.category }}
              </span>

              <span class="hover-number">
                {{ tool.number }}
              </span>
            </div>

            <h3>
              {{ tool.name }}
            </h3>

            <p>
              {{ tool.shortInfo }}
            </p>

            <button
              type="button"
              class="hover-more"
              @click="openToolInfo(tool)"
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M10.5 13.5a4.5 4.5 0 0 0 6.36 0l2.1-2.1a4.5 4.5 0 0 0-6.36-6.36l-1.2 1.2"
                />
                <path
                  d="M13.5 10.5a4.5 4.5 0 0 0-6.36 0l-2.1 2.1a4.5 4.5 0 1 0 6.36 6.36l1.2-1.2"
                />
              </svg>

              <span>
                Conocer la herramienta
              </span>
            </button>
          </aside>

        </div>
      </nav>


      <div class="sidebar-divider"></div>


      <!-- =======================================================
           CHATS RECIENTES
      ======================================================== -->
      <section class="history-section">

        <div class="history-heading">
          <strong>Chats recientes</strong>

          <button type="button">
            Ver todos
          </button>
        </div>

        <div class="history-list">
          <button
            v-for="chat in recentChats"
            :key="chat.title"
            type="button"
            class="history-item"
          >
            <svg
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M5 5h14v10H9l-4 4z" />
              <path d="M9 10h.01M12 10h.01M15 10h.01" />
            </svg>

            <span>
              <strong>{{ chat.title }}</strong>
              <small>{{ chat.date }}</small>
            </span>
          </button>
        </div>

      </section>


      <!-- Nuevo chat -->
      <button
        class="new-chat"
        type="button"
        @click="newChat"
      >
        <span>＋</span>
        Nuevo chat
      </button>


      <!-- =======================================================
           PERFIL
      ======================================================== -->
      <div class="profile">

        <div class="avatar">
          ES
        </div>

        <div class="profile-copy">
          <strong>Edwin Saldaña</strong>
          <small>MIKE Legal Intelligence</small>
        </div>

        <button
          class="settings-button"
          type="button"
          aria-label="Configuración"
        >
          <svg
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="3" />

            <path
              d="M12 2v3M12 19v3M4.9 4.9 7 7M17 17l2.1 2.1M2 12h3M19 12h3M4.9 19.1 7 17M17 7l2.1-2.1"
            />
          </svg>
        </button>

      </div>

    </aside>


    <!-- Overlay móvil -->
    <button
      v-if="mobileSidebarOpen"
      class="sidebar-overlay"
      type="button"
      aria-label="Cerrar menú"
      @click="mobileSidebarOpen = false"
    ></button>


    <!-- =========================================================
         ÁREA PRINCIPAL
    ========================================================== -->
    <main class="main-area">

      <!-- =======================================================
           TOPBAR
      ======================================================== -->
      <header class="topbar">

        <button
          class="mobile-menu"
          type="button"
          aria-label="Abrir menú"
          @click="mobileSidebarOpen = true"
        >
          <svg viewBox="0 0 24 24">
            <path d="M4 7h16M4 12h16M4 17h16" />
          </svg>
        </button>

        <span class="topbar-copy">
          EL DERECHO, POTENCIADO POR IA
        </span>


        <div class="topbar-actions">

          <button
            type="button"
            aria-label="Buscar"
          >
            <svg viewBox="0 0 24 24">
              <circle
                cx="10.5"
                cy="10.5"
                r="6.5"
              />

              <path d="m15.5 15.5 5 5" />
            </svg>
          </button>


          <div class="topbar-separator"></div>


          <div class="top-avatar">
            ES
          </div>

        </div>

      </header>


      <!-- =======================================================
           WORKSPACE
      ======================================================== -->
      <section class="workspace">

        <div class="workspace-decoration">
          <span></span>

          <p>
            ANALIZA · INVESTIGA · ARGUMENTA
          </p>
        </div>


        <div class="assistant-content">

          <!-- Bienvenida -->
          <div class="welcome">

            <p class="welcome-kicker">
              LEGAL INTELLIGENCE
            </p>

            <h1>
              Hola, soy
              <span>MIKE</span>
            </h1>

            <h2>
              Tu asistente jurídico inteligente
            </h2>

            <p class="welcome-description">
              Investiga el derecho, analiza expedientes y explora
              escenarios jurídicos desde un mismo entorno.
            </p>

          </div>


          <!-- ===================================================
               COMPOSER
          ==================================================== -->
          <form
            class="composer"
            @submit.prevent="handleSubmit"
          >

            <button
              class="composer-plus"
              type="button"
              aria-label="Adjuntar archivo"
            >
              +
            </button>

            <textarea
              ref="composerInput"
              v-model="message"
              rows="1"
              placeholder="Escribe tu consulta jurídica aquí..."
              @keydown.enter.exact.prevent="handleSubmit"
            ></textarea>

            <button
              class="composer-mic"
              type="button"
              aria-label="Entrada por voz"
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <rect
                  x="9"
                  y="3"
                  width="6"
                  height="11"
                  rx="3"
                />

                <path
                  d="M6 11a6 6 0 0 0 12 0M12 17v4M9 21h6"
                />
              </svg>
            </button>

            <button
              class="composer-send"
              type="submit"
              aria-label="Enviar consulta"
            >
              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="m3 11 18-8-8 18-2-8-8-2Z"
                />

                <path d="m11 13 10-10" />
              </svg>
            </button>

          </form>


          <!-- ===================================================
               ACCIONES RÁPIDAS
          ==================================================== -->
          <div class="quick-actions">

            <button
              type="button"
              @click="navigate('/novasearch')"
            >
              <span>
                Buscar jurisprudencia
              </span>

              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M9 6l6 6-6 6" />
              </svg>
            </button>


            <button
              type="button"
              @click="navigate('/novacase')"
            >
              <span>
                Analizar un expediente
              </span>

              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M9 6l6 6-6 6" />
              </svg>
            </button>


            <button
              type="button"
              @click="navigate('/novacourt')"
            >
              <span>
                Simular una audiencia
              </span>

              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="M9 6l6 6-6 6" />
              </svg>
            </button>

          </div>


          <!-- Mensaje inferior -->
          <div class="bottom-message">

            <div class="quote-mark">
              “
            </div>

            <p>
              La mejor estrategia comienza
              <br />
              con mejor información.
            </p>

            <span>
              MIKE · LEGAL INTELLIGENCE
            </span>

          </div>

        </div>


        <!-- Marca de agua -->
        <div class="watermark">
          <svg
            viewBox="0 0 200 240"
            aria-hidden="true"
          >
            <path d="M100 22v172" />
            <path d="M48 58h104" />
            <path d="m48 58-30 55h60L48 58Z" />
            <path d="m152 58-30 55h60l-30-55Z" />
            <path d="M62 194h76" />
            <path d="M76 214h48" />
          </svg>
        </div>

      </section>

    </main>


    <!-- =========================================================
         MODAL DE INFORMACIÓN
    ========================================================== -->
    <Teleport to="body">

      <Transition name="tool-modal">

        <div
          v-if="selectedTool"
          class="tool-modal-overlay"
          @click.self="closeToolInfo"
        >

          <section
            class="tool-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="tool-modal-title"
          >

            <!-- Cerrar -->
            <button
              type="button"
              class="tool-modal-close"
              aria-label="Cerrar información"
              @click="closeToolInfo"
            >
              <svg viewBox="0 0 24 24">
                <path d="M5 5l14 14M19 5 5 19" />
              </svg>
            </button>


            <!-- Encabezado -->
            <div class="tool-modal-header">

              <div class="tool-modal-icon">

                <svg
                  v-if="selectedTool.icon === 'search'"
                  viewBox="0 0 24 24"
                >
                  <circle
                    cx="10.5"
                    cy="10.5"
                    r="6.5"
                  />

                  <path d="m15.5 15.5 5 5" />
                </svg>


                <svg
                  v-else-if="selectedTool.icon === 'case'"
                  viewBox="0 0 24 24"
                >
                  <path d="M6 3h9l4 4v14H6z" />
                  <path d="M15 3v5h5" />
                  <path d="M9 12h7M9 16h7" />
                </svg>


                <svg
                  v-else
                  viewBox="0 0 24 24"
                >
                  <path d="M12 3v18" />
                  <path d="M5 7h14" />
                  <path d="m5 7-3 6h6L5 7Z" />
                  <path d="m19 7-3 6h6l-3-6Z" />
                  <path d="M7 21h10" />
                </svg>

              </div>


              <div class="tool-modal-heading">

                <span>
                  {{ selectedTool.category }}
                </span>

                <h2 id="tool-modal-title">
                  {{ selectedTool.name }}
                </h2>

                <p>
                  {{ selectedTool.description }}
                </p>

              </div>

            </div>


            <div class="tool-modal-rule"></div>


            <!-- Contenido -->
            <div class="tool-modal-content">

              <section class="tool-modal-about">

                <span class="modal-section-label">
                  QUÉ HACE
                </span>

                <p>
                  {{ selectedTool.longInfo }}
                </p>

              </section>


              <section class="tool-modal-capabilities">

                <span class="modal-section-label">
                  CAPACIDADES PRINCIPALES
                </span>

                <div class="capabilities-list">

                  <div
                    v-for="capability in selectedTool.capabilities"
                    :key="capability"
                    class="capability-item"
                  >
                    <span class="capability-dot"></span>

                    <p>
                      {{ capability }}
                    </p>
                  </div>

                </div>

              </section>

            </div>


            <!-- Footer -->
            <footer class="tool-modal-footer">

              <p>
                Integrado dentro del ecosistema de inteligencia jurídica MIKE.
              </p>

              <button
                type="button"
                class="tool-modal-open"
                @click="navigate(selectedTool.route)"
              >
                <span>
                  Abrir {{ selectedTool.name }}
                </span>

                <svg viewBox="0 0 24 24">
                  <path d="M5 12h14" />
                  <path d="m13 6 6 6-6 6" />
                </svg>
              </button>

            </footer>

          </section>

        </div>

      </Transition>

    </Teleport>

  </div>
</template>


<script setup>
import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref
} from 'vue'

import { useRouter } from 'vue-router'


const router = useRouter()


/* =========================================================
   STATE
========================================================= */

const message = ref('')

const composerInput = ref(null)

const mobileSidebarOpen = ref(false)

const selectedTool = ref(null)


/* =========================================================
   HERRAMIENTAS
========================================================= */

const tools = [
  {
    id: 'search',
    number: '01',
    name: 'NovaSearch',
    category: 'INVESTIGACIÓN JURÍDICA',

    description:
      'Busca normativa y jurisprudencia',

    shortInfo:
      'Investiga normas, jurisprudencia y criterios jurídicos relevantes desde una única consulta.',

    longInfo:
      'NovaSearch es el motor de investigación jurídica de MIKE. Permite formular consultas en lenguaje natural y recuperar información jurídica relacionada para facilitar la revisión de normativa, jurisprudencia y otros criterios relevantes para el análisis del asunto.',

    capabilities: [
      'Búsqueda jurídica mediante lenguaje natural.',
      'Recuperación contextual de normativa y jurisprudencia.',
      'Identificación de información relevante para sustentar el análisis.',
      'Acceso estructurado a las fuentes jurídicas recuperadas.'
    ],

    route: '/novasearch',
    icon: 'search'
  },

  {
    id: 'case',
    number: '02',
    name: 'NovaCase',
    category: 'ANÁLISIS JURÍDICO',

    description:
      'Analiza y estructura casos',

    shortInfo:
      'Transforma los hechos de un expediente en un análisis organizado de evidencia, riesgos y estrategia.',

    longInfo:
      'NovaCase es el entorno de análisis de casos de MIKE. Organiza la información proporcionada por el usuario para estructurar hechos, cuestiones jurídicas, evidencia, argumentos, riesgos y posibles líneas de estrategia dentro de una visión integrada del caso.',

    capabilities: [
      'Estructuración de hechos y problemas jurídicos.',
      'Análisis organizado de evidencia y argumentos.',
      'Identificación de riesgos y contraargumentos.',
      'Construcción de una visión estratégica del caso.'
    ],

    route: '/novacase',
    icon: 'case'
  },

  {
    id: 'court',
    number: '03',
    name: 'NovaCourt',
    category: 'SIMULACIÓN JURÍDICA',

    description:
      'Simula escenarios jurídicos',

    shortInfo:
      'Contrasta posiciones jurídicas y explora cómo podría desarrollarse un escenario de controversia.',

    longInfo:
      'NovaCourt es el entorno de simulación jurídica de MIKE. Permite explorar un caso desde diferentes posiciones mediante agentes especializados, contrastar teorías y argumentos y obtener una proyección orientativa del escenario jurídico analizado.',

    capabilities: [
      'Contraste estructurado de posiciones jurídicas.',
      'Simulación multiagente de argumentos contrapuestos.',
      'Valoración de fortalezas y riesgos de cada posición.',
      'Proyección orientativa del escenario analizado.'
    ],

    route: '/novacourt',
    icon: 'court'
  }
]


/* =========================================================
   HISTORIAL VISUAL
========================================================= */

const recentChats = [
  {
    title: 'Recurso de apelación',
    date: 'Reciente'
  },

  {
    title: 'Despido laboral',
    date: 'Reciente'
  },

  {
    title: 'Contrato de compraventa',
    date: 'Reciente'
  },

  {
    title: 'Análisis de jurisprudencia',
    date: 'Reciente'
  }
]


/* =========================================================
   NAVEGACIÓN
========================================================= */

const navigate = async (path) => {

  closeToolInfo()

  mobileSidebarOpen.value = false

  await router.push(path)
}


const goMikeHome = async () => {

  await router.push('/mike')
}


/* =========================================================
   MODAL DE HERRAMIENTAS
========================================================= */

const openToolInfo = (tool) => {

  selectedTool.value = tool

  document.body.style.overflow = 'hidden'
}


const closeToolInfo = () => {

  selectedTool.value = null

  document.body.style.overflow = ''
}


/* =========================================================
   NUEVO CHAT
========================================================= */

const newChat = async () => {

  message.value = ''

  await nextTick()

  composerInput.value?.focus()
}


/* =========================================================
   ENVÍO TEMPORAL
========================================================= */

const handleSubmit = async () => {

  const query = message.value.trim()

  if (!query) {

    composerInput.value?.focus()

    return
  }

  /*
    En esta etapa MIKE todavía no clasifica
    automáticamente la intención.

    Conservamos temporalmente NovaSearch
    como destino por defecto.
  */

  await router.push({

    path: '/novasearch',

    query: {
      q: query
    }

  })
}


/* =========================================================
   KEYBOARD
========================================================= */

const handleGlobalKeydown = (event) => {

  if (
    event.key === 'Escape' &&
    selectedTool.value
  ) {

    closeToolInfo()
  }
}


/* =========================================================
   LIFECYCLE
========================================================= */

onMounted(() => {

  window.addEventListener(
    'keydown',
    handleGlobalKeydown
  )
})


onBeforeUnmount(() => {

  window.removeEventListener(
    'keydown',
    handleGlobalKeydown
  )

  document.body.style.overflow = ''
})
</script>


<style scoped>

/* =========================================================
   DESIGN SYSTEM
========================================================= */

.mike-app {

  --navy-950: #071321;
  --navy-900: #0a1a2c;
  --navy-850: #0d2136;

  --gold: #c5a15c;
  --gold-light: #dcc185;

  --blue: #275d92;
  --blue-light: #dfeaf5;

  --ink: #091a30;
  --muted: #6c7c90;

  --surface: #ffffff;
  --background: #f5f8fb;
  --border: #dce4ec;

  min-height: 100vh;

  display: flex;

  background:
    var(--background);

  color:
    var(--ink);

  font-family:
    Inter,
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
}


/* =========================================================
   SIDEBAR
========================================================= */

.sidebar {

  width: 310px;

  min-height: 100vh;

  flex:
    0 0 310px;

  display: flex;

  flex-direction:
    column;

  padding:
    28px 18px
    20px;

  background:
    linear-gradient(
      180deg,
      #081828 0%,
      #091b2e 100%
    );

  color:
    white;

  border-right:
    1px solid
    rgba(255,255,255,.08);

  z-index: 60;
}


.sidebar-top {

  display: flex;

  align-items:
    flex-start;

  justify-content:
    space-between;

  padding:
    0 8px
    25px;
}


.brand {

  display: flex;

  align-items:
    stretch;

  gap:
    16px;

  border:
    0;

  background:
    transparent;

  color:
    white;

  padding:
    0;

  cursor:
    pointer;

  text-align:
    left;
}


.brand-line {

  width:
    2px;

  background:
    var(--gold);

  opacity:
    .95;
}


.brand-copy {

  display:
    flex;

  flex-direction:
    column;

  gap:
    5px;
}


.brand-copy strong {

  font-family:
    Georgia,
    "Times New Roman",
    serif;

  font-size:
    35px;

  font-weight:
    500;

  letter-spacing:
    5px;

  line-height:
    1;
}


.brand-copy small {

  color:
    var(--gold-light);

  font-size:
    9px;

  font-weight:
    600;

  letter-spacing:
    3px;
}


.mobile-close {

  display:
    none;
}


/* =========================================================
   TOOLS
========================================================= */

.tools-nav {

  display:
    flex;

  flex-direction:
    column;

  gap:
    9px;
}


.tool-card-wrap {

  position:
    relative;

  width:
    100%;
}


.tool-row {

  display:
    grid;

  grid-template-columns:
    minmax(0, 1fr)
    38px;

  align-items:
    stretch;

  border:
    1px solid
    rgba(255,255,255,.13);

  border-radius:
    9px;

  background:
    rgba(255,255,255,.018);

  transition:
    background .18s ease,
    border-color .18s ease,
    box-shadow .18s ease;
}


.tool-row:hover {

  background:
    rgba(44,94,144,.13);

  border-color:
    rgba(111,163,213,.36);

  box-shadow:
    inset 2px 0 0
    rgba(197,161,92,.85);
}


.tool-button {

  min-height:
    76px;

  width:
    100%;

  display:
    grid;

  grid-template-columns:
    42px 1fr 18px;

  align-items:
    center;

  gap:
    10px;

  padding:
    12px 9px
    12px 14px;

  border:
    0;

  border-radius:
    9px 0 0 9px;

  background:
    transparent;

  color:
    white;

  cursor:
    pointer;

  text-align:
    left;
}


.tool-icon {

  width:
    39px;

  height:
    39px;

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;
}


.tool-icon svg {

  width:
    29px;

  height:
    29px;

  fill:
    none;

  stroke:
    #eef5fc;

  stroke-width:
    1.55;

  stroke-linecap:
    round;

  stroke-linejoin:
    round;
}


.tool-copy {

  min-width:
    0;

  display:
    flex;

  flex-direction:
    column;

  gap:
    3px;
}


.tool-copy strong {

  color:
    #ffffff;

  font-size:
    15px;

  font-weight:
    600;
}


.tool-copy small {

  color:
    #9fb2c8;

  font-size:
    11px;

  line-height:
    1.3;
}


.tool-arrow {

  width:
    17px;

  height:
    17px;

  fill:
    none;

  stroke:
    #728aa1;

  stroke-width:
    1.7;

  transition:
    transform .18s ease,
    stroke .18s ease;
}


.tool-row:hover
.tool-arrow {

  transform:
    translateX(2px);

  stroke:
    #b7cbe0;
}


/* =========================================================
   TOOL INFO LINK
========================================================= */

.tool-info-trigger {

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  border:
    0;

  border-left:
    1px solid
    rgba(255,255,255,.08);

  border-radius:
    0 9px 9px 0;

  background:
    transparent;

  color:
    #718ba4;

  cursor:
    pointer;

  transition:
    color .18s ease,
    background .18s ease;
}


.tool-info-trigger:hover {

  color:
    var(--gold-light);

  background:
    rgba(255,255,255,.045);
}


.tool-info-trigger svg {

  width:
    16px;

  height:
    16px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.55;

  stroke-linecap:
    round;

  stroke-linejoin:
    round;
}


/* =========================================================
   HOVER TOOL CARD
========================================================= */

.tool-hover-card {

  position:
    absolute;

  left:
    calc(100% + 12px);

  top:
    50%;

  width:
    280px;

  padding:
    18px;

  border:
    1px solid
    rgba(153,183,211,.17);

  border-radius:
    10px;

  background:
    #10263b;

  color:
    white;

  box-shadow:
    0 24px 55px
    rgba(2,12,23,.28);

  opacity:
    0;

  visibility:
    hidden;

  pointer-events:
    none;

  transform:
    translate(
      7px,
      -50%
    );

  transition:
    opacity .17s ease,
    transform .17s ease,
    visibility .17s ease;

  z-index:
    120;
}


.tool-hover-card::before {

  content:
    '';

  position:
    absolute;

  top:
    0;

  left:
    -14px;

  width:
    14px;

  height:
    100%;
}


.tool-card-wrap:hover
.tool-hover-card {

  opacity:
    1;

  visibility:
    visible;

  pointer-events:
    auto;

  transform:
    translate(
      0,
      -50%
    );
}


.hover-card-top {

  display:
    flex;

  align-items:
    center;

  justify-content:
    space-between;

  margin-bottom:
    10px;
}


.hover-category {

  color:
    var(--gold-light);

  font-size:
    7px;

  font-weight:
    700;

  letter-spacing:
    1.6px;
}


.hover-number {

  color:
    #617b94;

  font-family:
    monospace;

  font-size:
    9px;
}


.tool-hover-card h3 {

  margin:
    0 0 8px;

  color:
    #ffffff;

  font-family:
    Georgia,
    "Times New Roman",
    serif;

  font-size:
    20px;

  font-weight:
    400;
}


.tool-hover-card p {

  margin:
    0;

  color:
    #b0c0d0;

  font-size:
    10.5px;

  line-height:
    1.68;
}


.hover-more {

  display:
    inline-flex;

  align-items:
    center;

  gap:
    7px;

  margin-top:
    15px;

  padding:
    0;

  border:
    0;

  background:
    transparent;

  color:
    var(--gold-light);

  font-size:
    9px;

  font-weight:
    600;

  cursor:
    pointer;
}


.hover-more svg {

  width:
    14px;

  height:
    14px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.55;

  stroke-linecap:
    round;

  stroke-linejoin:
    round;
}


.hover-more:hover span {

  text-decoration:
    underline;

  text-underline-offset:
    3px;
}


/* =========================================================
   SIDEBAR DIVIDER
========================================================= */

.sidebar-divider {

  height:
    1px;

  margin:
    27px 7px
    23px;

  background:
    rgba(255,255,255,.1);
}


/* =========================================================
   HISTORY
========================================================= */

.history-section {

  min-height:
    0;

  flex:
    1;
}


.history-heading {

  display:
    flex;

  align-items:
    center;

  justify-content:
    space-between;

  padding:
    0 7px
    13px;
}


.history-heading strong {

  font-size:
    13px;
}


.history-heading button {

  border:
    0;

  background:
    transparent;

  color:
    #9fb2c8;

  font-size:
    11px;

  cursor:
    pointer;
}


.history-list {

  display:
    flex;

  flex-direction:
    column;

  gap:
    3px;
}


.history-item {

  display:
    grid;

  grid-template-columns:
    28px 1fr;

  gap:
    7px;

  align-items:
    center;

  width:
    100%;

  padding:
    9px 8px;

  border:
    0;

  border-radius:
    6px;

  background:
    transparent;

  color:
    white;

  text-align:
    left;

  cursor:
    pointer;
}


.history-item:hover {

  background:
    rgba(255,255,255,.05);
}


.history-item svg {

  width:
    19px;

  height:
    19px;

  fill:
    none;

  stroke:
    #dfeaf5;

  stroke-width:
    1.4;
}


.history-item span {

  min-width:
    0;

  display:
    flex;

  flex-direction:
    column;

  gap:
    2px;
}


.history-item strong {

  overflow:
    hidden;

  font-size:
    12px;

  font-weight:
    500;

  white-space:
    nowrap;

  text-overflow:
    ellipsis;
}


.history-item small {

  color:
    #7e95ad;

  font-size:
    10px;
}


/* =========================================================
   NEW CHAT
========================================================= */

.new-chat {

  min-height:
    50px;

  margin-top:
    18px;

  border:
    1px solid
    var(--gold);

  border-radius:
    8px;

  background:
    transparent;

  color:
    var(--gold-light);

  font-size:
    13px;

  cursor:
    pointer;

  transition:
    background .18s ease,
    color .18s ease;
}


.new-chat:hover {

  background:
    var(--gold);

  color:
    var(--navy-950);
}


.new-chat span {

  margin-right:
    10px;

  font-size:
    18px;
}


/* =========================================================
   PROFILE
========================================================= */

.profile {

  display:
    grid;

  grid-template-columns:
    41px 1fr 32px;

  align-items:
    center;

  gap:
    10px;

  margin-top:
    19px;

  padding:
    20px 5px
    2px;

  border-top:
    1px solid
    rgba(255,255,255,.1);
}


.avatar,
.top-avatar {

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  border-radius:
    50%;

  background:
    #213f61;

  color:
    white;

  font-family:
    Georgia,
    serif;
}


.avatar {

  width:
    41px;

  height:
    41px;
}


.profile-copy {

  min-width:
    0;

  display:
    flex;

  flex-direction:
    column;

  gap:
    2px;
}


.profile-copy strong {

  font-size:
    12px;
}


.profile-copy small {

  overflow:
    hidden;

  color:
    #8ea3ba;

  font-size:
    9px;

  white-space:
    nowrap;

  text-overflow:
    ellipsis;
}


.settings-button {

  border:
    0;

  background:
    transparent;

  color:
    #c7d5e3;

  cursor:
    pointer;
}


.settings-button svg {

  width:
    20px;

  height:
    20px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.4;
}


/* =========================================================
   MAIN AREA
========================================================= */

.main-area {

  min-width:
    0;

  flex:
    1;

  min-height:
    100vh;

  display:
    flex;

  flex-direction:
    column;
}


/* =========================================================
   TOPBAR
========================================================= */

.topbar {

  min-height:
    70px;

  flex:
    0 0 70px;

  display:
    flex;

  align-items:
    center;

  gap:
    20px;

  padding:
    0 35px;

  background:
    rgba(255,255,255,.96);

  border-bottom:
    1px solid
    var(--border);
}


.topbar-copy {

  color:
    #314f70;

  font-size:
    10px;

  font-weight:
    600;

  letter-spacing:
    2.5px;
}


.topbar-actions {

  margin-left:
    auto;

  display:
    flex;

  align-items:
    center;

  gap:
    18px;
}


.topbar-actions button {

  width:
    36px;

  height:
    36px;

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  border:
    0;

  background:
    transparent;

  color:
    var(--ink);

  cursor:
    pointer;
}


.topbar-actions svg {

  width:
    24px;

  height:
    24px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.7;
}


.topbar-separator {

  width:
    1px;

  height:
    27px;

  background:
    var(--border);
}


.top-avatar {

  width:
    42px;

  height:
    42px;
}


.mobile-menu {

  display:
    none;
}


/* =========================================================
   WORKSPACE
========================================================= */

.workspace {

  position:
    relative;

  flex:
    1;

  overflow:
    hidden;

  background:
    linear-gradient(
      180deg,
      #fbfdff 0%,
      #f4f8fc 100%
    );
}


.workspace-decoration {

  position:
    absolute;

  top:
    30px;

  right:
    42px;

  display:
    flex;

  align-items:
    center;

  gap:
    14px;

  color:
    #9a7841;

  font-size:
    9px;

  font-weight:
    600;

  letter-spacing:
    2px;
}


.workspace-decoration span {

  width:
    58px;

  height:
    1px;

  background:
    var(--gold);
}


.assistant-content {

  position:
    relative;

  z-index:
    4;

  width:
    min(
      calc(100% - 80px),
      880px
    );

  min-height:
    calc(100vh - 70px);

  margin:
    0 auto;

  display:
    flex;

  flex-direction:
    column;

  align-items:
    center;

  padding:
    clamp(100px, 14vh, 155px)
    0
    34px;
}


/* =========================================================
   WELCOME
========================================================= */

.welcome {

  text-align:
    center;
}


.welcome-kicker {

  margin-bottom:
    17px;

  color:
    var(--gold);

  font-size:
    9px;

  font-weight:
    700;

  letter-spacing:
    3px;
}


.welcome h1 {

  margin:
    0;

  font-family:
    Georgia,
    "Times New Roman",
    serif;

  font-size:
    clamp(
      45px,
      5vw,
      68px
    );

  font-weight:
    400;

  line-height:
    1;
}


.welcome h1 span {

  color:
    #b88d3d;
}


.welcome h2 {

  margin:
    13px 0 0;

  color:
    #315579;

  font-size:
    clamp(
      20px,
      2vw,
      27px
    );

  font-weight:
    400;
}


.welcome-description {

  max-width:
    570px;

  margin:
    17px auto
    0;

  color:
    var(--muted);

  font-size:
    13px;

  line-height:
    1.7;
}


/* =========================================================
   COMPOSER
========================================================= */

.composer {

  width:
    100%;

  min-height:
    76px;

  display:
    grid;

  grid-template-columns:
    46px 1fr
    44px 54px;

  align-items:
    center;

  gap:
    6px;

  margin-top:
    38px;

  padding:
    8px 10px;

  background:
    white;

  border:
    1px solid
    #d7e0ea;

  border-radius:
    18px;

  box-shadow:
    0 16px 42px
    rgba(20,45,76,.08);
}


.composer textarea {

  width:
    100%;

  max-height:
    120px;

  resize:
    none;

  border:
    0;

  outline:
    0;

  background:
    transparent;

  color:
    var(--ink);

  font:
    inherit;

  font-size:
    15px;

  line-height:
    1.4;
}


.composer textarea::placeholder {

  color:
    #93a3b6;
}


.composer-plus {

  width:
    40px;

  height:
    40px;

  border:
    1px solid
    #d4dee8;

  border-radius:
    50%;

  background:
    white;

  color:
    #173a5d;

  font-size:
    25px;

  cursor:
    pointer;
}


.composer-mic {

  width:
    40px;

  height:
    40px;

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  border:
    0;

  background:
    transparent;

  color:
    #214d78;

  cursor:
    pointer;
}


.composer-mic svg {

  width:
    23px;

  height:
    23px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.5;
}


.composer-send {

  width:
    48px;

  height:
    48px;

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  border:
    0;

  border-radius:
    50%;

  background:
    #0c2947;

  color:
    white;

  cursor:
    pointer;

  transition:
    transform .18s ease,
    background .18s ease;
}


.composer-send:hover {

  transform:
    translateY(-2px);

  background:
    #173f68;
}


.composer-send svg {

  width:
    21px;

  height:
    21px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.6;
}


/* =========================================================
   QUICK ACTIONS
========================================================= */

.quick-actions {

  width:
    100%;

  display:
    grid;

  grid-template-columns:
    repeat(3, 1fr);

  gap:
    10px;

  margin-top:
    19px;
}


.quick-actions button {

  min-height:
    43px;

  display:
    flex;

  align-items:
    center;

  justify-content:
    space-between;

  gap:
    8px;

  padding:
    0 15px;

  border:
    1px solid
    #e0e6ed;

  border-radius:
    20px;

  background:
    rgba(255,255,255,.72);

  color:
    #294867;

  font-size:
    11px;

  cursor:
    pointer;

  transition:
    background .18s ease,
    border-color .18s ease,
    transform .18s ease;
}


.quick-actions button:hover {

  transform:
    translateY(-1px);

  background:
    white;

  border-color:
    #aabed1;
}


.quick-actions svg {

  width:
    16px;

  height:
    16px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.7;
}


/* =========================================================
   BOTTOM MESSAGE
========================================================= */

.bottom-message {

  margin-top:
    auto;

  align-self:
    flex-start;

  padding-top:
    70px;

  color:
    #173653;
}


.quote-mark {

  height:
    18px;

  color:
    var(--gold);

  font-family:
    Georgia,
    serif;

  font-size:
    35px;
}


.bottom-message p {

  margin:
    0;

  font-family:
    Georgia,
    serif;

  font-size:
    20px;

  font-style:
    italic;

  line-height:
    1.3;
}


.bottom-message span {

  display:
    block;

  margin-top:
    14px;

  color:
    #a27d40;

  font-size:
    8px;

  font-weight:
    700;

  letter-spacing:
    2px;
}


/* =========================================================
   WATERMARK
========================================================= */

.watermark {

  position:
    absolute;

  right:
    4%;

  bottom:
    -35px;

  width:
    240px;

  opacity:
    .042;

  color:
    #173b60;

  pointer-events:
    none;
}


.watermark svg {

  width:
    100%;

  height:
    auto;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    2;
}


/* =========================================================
   MODAL OVERLAY
========================================================= */

.tool-modal-overlay {

  position:
    fixed;

  inset:
    0;

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  padding:
    28px;

  background:
    rgba(5,15,26,.60);

  backdrop-filter:
    blur(6px);

  z-index:
    1000;
}


/* =========================================================
   MODAL
========================================================= */

.tool-modal {

  position:
    relative;

  width:
    min(
      720px,
      100%
    );

  overflow:
    hidden;

  border:
    1px solid
    #dce3ea;

  border-radius:
    14px;

  background:
    #ffffff;

  color:
    #10243b;

  box-shadow:
    0 35px 100px
    rgba(2,13,27,.26);
}


.tool-modal::before {

  content:
    '';

  position:
    absolute;

  top:
    0;

  left:
    0;

  width:
    100%;

  height:
    3px;

  background:
    linear-gradient(
      90deg,
      var(--gold),
      #264f77 55%,
      transparent
    );
}


/* =========================================================
   MODAL CLOSE
========================================================= */

.tool-modal-close {

  position:
    absolute;

  top:
    18px;

  right:
    18px;

  width:
    35px;

  height:
    35px;

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  border:
    1px solid
    #e1e6eb;

  border-radius:
    8px;

  background:
    #f8fafc;

  color:
    #53677b;

  cursor:
    pointer;

  z-index:
    2;

  transition:
    background .18s ease,
    color .18s ease;
}


.tool-modal-close:hover {

  background:
    #edf2f6;

  color:
    #142f4a;
}


.tool-modal-close svg {

  width:
    16px;

  height:
    16px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.6;
}


/* =========================================================
   MODAL HEADER
========================================================= */

.tool-modal-header {

  display:
    grid;

  grid-template-columns:
    58px 1fr;

  align-items:
    center;

  gap:
    19px;

  padding:
    34px 70px
    25px 34px;
}


.tool-modal-icon {

  width:
    58px;

  height:
    58px;

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  border:
    1px solid
    #d9e2ea;

  border-radius:
    11px;

  background:
    #f5f8fb;

  color:
    #234d74;
}


.tool-modal-icon svg {

  width:
    29px;

  height:
    29px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.45;

  stroke-linecap:
    round;

  stroke-linejoin:
    round;
}


.tool-modal-heading > span {

  display:
    block;

  margin-bottom:
    6px;

  color:
    #aa8445;

  font-size:
    8px;

  font-weight:
    700;

  letter-spacing:
    1.8px;
}


.tool-modal-heading h2 {

  margin:
    0;

  color:
    #102940;

  font-family:
    Georgia,
    "Times New Roman",
    serif;

  font-size:
    30px;

  font-weight:
    400;
}


.tool-modal-heading p {

  margin:
    5px 0 0;

  color:
    #728296;

  font-size:
    11px;
}


.tool-modal-rule {

  height:
    1px;

  margin:
    0 34px;

  background:
    #e7ebef;
}


/* =========================================================
   MODAL CONTENT
========================================================= */

.tool-modal-content {

  display:
    grid;

  grid-template-columns:
    1.06fr .94fr;

  gap:
    40px;

  padding:
    29px 34px
    31px;
}


.modal-section-label {

  display:
    block;

  margin-bottom:
    12px;

  color:
    #8a9aab;

  font-size:
    7.5px;

  font-weight:
    700;

  letter-spacing:
    1.7px;
}


.tool-modal-about > p {

  margin:
    0;

  color:
    #4e6276;

  font-size:
    11.5px;

  line-height:
    1.82;
}


.capabilities-list {

  display:
    flex;

  flex-direction:
    column;

  gap:
    11px;
}


.capability-item {

  display:
    grid;

  grid-template-columns:
    6px 1fr;

  gap:
    9px;

  align-items:
    start;
}


.capability-dot {

  width:
    5px;

  height:
    5px;

  margin-top:
    6px;

  border-radius:
    50%;

  background:
    var(--gold);
}


.capability-item p {

  margin:
    0;

  color:
    #526678;

  font-size:
    10.5px;

  line-height:
    1.55;
}


/* =========================================================
   MODAL FOOTER
========================================================= */

.tool-modal-footer {

  min-height:
    74px;

  display:
    flex;

  align-items:
    center;

  justify-content:
    space-between;

  gap:
    20px;

  padding:
    15px 34px;

  border-top:
    1px solid
    #e6ebef;

  background:
    #f8fafc;
}


.tool-modal-footer p {

  margin:
    0;

  color:
    #8a98a8;

  font-size:
    9px;
}


.tool-modal-open {

  min-height:
    41px;

  display:
    inline-flex;

  align-items:
    center;

  justify-content:
    center;

  gap:
    12px;

  padding:
    0 16px;

  border:
    0;

  border-radius:
    7px;

  background:
    #0b2947;

  color:
    white;

  font-size:
    10px;

  font-weight:
    600;

  cursor:
    pointer;

  transition:
    background .18s ease,
    transform .18s ease;
}


.tool-modal-open:hover {

  transform:
    translateY(-1px);

  background:
    #163f66;
}


.tool-modal-open svg {

  width:
    16px;

  height:
    16px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.6;
}


/* =========================================================
   MODAL ANIMATION
========================================================= */

.tool-modal-enter-active,
.tool-modal-leave-active {

  transition:
    opacity .18s ease;
}


.tool-modal-enter-active
.tool-modal,
.tool-modal-leave-active
.tool-modal {

  transition:
    opacity .18s ease,
    transform .18s ease;
}


.tool-modal-enter-from,
.tool-modal-leave-to {

  opacity:
    0;
}


.tool-modal-enter-from
.tool-modal,
.tool-modal-leave-to
.tool-modal {

  opacity:
    0;

  transform:
    translateY(8px)
    scale(.985);
}


/* =========================================================
   RESPONSIVE
========================================================= */

.sidebar-overlay {

  display:
    none;
}


@media (max-width: 1050px) {

  .sidebar {

    position:
      fixed;

    top:
      0;

    left:
      0;

    transform:
      translateX(-102%);

    transition:
      transform .25s ease;

    box-shadow:
      20px 0 50px
      rgba(0,0,0,.22);
  }


  .sidebar.sidebar-open {

    transform:
      translateX(0);
  }


  .sidebar-overlay {

    position:
      fixed;

    inset:
      0;

    z-index:
      50;

    display:
      block;

    border:
      0;

    background:
      rgba(3,13,24,.42);
  }


  .mobile-close {

    display:
      flex;

    width:
      32px;

    height:
      32px;

    align-items:
      center;

    justify-content:
      center;

    border:
      0;

    background:
      transparent;

    color:
      white;
  }


  .mobile-close svg {

    width:
      20px;

    height:
      20px;

    fill:
      none;

    stroke:
      currentColor;

    stroke-width:
      1.7;
  }


  .mobile-menu {

    display:
      flex;

    width:
      36px;

    height:
      36px;

    align-items:
      center;

    justify-content:
      center;

    border:
      0;

    background:
      transparent;

    color:
      var(--ink);
  }


  .mobile-menu svg {

    width:
      24px;

    height:
      24px;

    fill:
      none;

    stroke:
      currentColor;

    stroke-width:
      1.7;
  }


  .tool-hover-card {

    display:
      none;
  }

}


@media (max-width: 700px) {

  .topbar {

    padding:
      0 18px;
  }


  .topbar-copy {

    display:
      none;
  }


  .assistant-content {

    width:
      calc(100% - 28px);

    padding-top:
      80px;
  }


  .workspace-decoration {

    display:
      none;
  }


  .welcome h1 {

    font-size:
      43px;
  }


  .composer {

    grid-template-columns:
      42px 1fr
      40px 46px;

    min-height:
      68px;
  }


  .quick-actions {

    grid-template-columns:
      1fr;
  }


  .bottom-message {

    padding-top:
      50px;
  }


  .watermark {

    display:
      none;
  }


  .tool-modal-overlay {

    padding:
      14px;
  }


  .tool-modal-header {

    grid-template-columns:
      47px 1fr;

    padding:
      27px 55px
      21px 22px;
  }


  .tool-modal-icon {

    width:
      47px;

    height:
      47px;
  }


  .tool-modal-icon svg {

    width:
      24px;

    height:
      24px;
  }


  .tool-modal-heading h2 {

    font-size:
      25px;
  }


  .tool-modal-rule {

    margin:
      0 22px;
  }


  .tool-modal-content {

    grid-template-columns:
      1fr;

    gap:
      24px;

    padding:
      24px 22px;
  }


  .tool-modal-footer {

    align-items:
      stretch;

    flex-direction:
      column;

    padding:
      16px 22px;
  }


  .tool-modal-open {

    width:
      100%;
  }

}

</style>