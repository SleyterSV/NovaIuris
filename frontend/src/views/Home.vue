<template>
  <div class="nova-home">

    <!-- =========================================================
         NAVBAR
    ========================================================== -->
    <header class="navbar">
      <div class="navbar-inner">

        <button
          type="button"
          class="brand"
          aria-label="Ir al inicio"
          @click="scrollToSection('inicio')"
        >
          <span class="brand-name">NOVA IURIS</span>
          <span class="brand-rule"></span>
        </button>

        <nav class="desktop-nav" aria-label="Navegación principal">
          <button type="button" @click="scrollToSection('inicio')">
            Inicio
          </button>

          <button type="button" @click="scrollToSection('plataforma')">
            Plataforma
          </button>

          <button type="button" @click="scrollToSection('como-funciona')">
            Cómo funciona
          </button>

          <button type="button" @click="scrollToSection('tecnologia')">
            Tecnología
          </button>
        </nav>

        <button
          type="button"
          class="navbar-cta"
          @click="openPlatformModal"
        >
          <span>Ingresar a la plataforma</span>
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M5 12h13" />
            <path d="m13 6 6 6-6 6" />
          </svg>
        </button>

        <button
          type="button"
          class="mobile-menu-button"
          :aria-expanded="mobileMenuOpen"
          aria-label="Abrir menú"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <span></span>
          <span></span>
        </button>

      </div>

      <div
        v-if="mobileMenuOpen"
        class="mobile-menu"
      >
        <button
          type="button"
          @click="mobileNavigate('inicio')"
        >
          Inicio
        </button>

        <button
          type="button"
          @click="mobileNavigate('plataforma')"
        >
          Plataforma
        </button>

        <button
          type="button"
          @click="mobileNavigate('como-funciona')"
        >
          Cómo funciona
        </button>

        <button
          type="button"
          @click="mobileNavigate('tecnologia')"
        >
          Tecnología
        </button>

        <button
          type="button"
          class="mobile-platform-button"
          @click="openPlatformModal"
        >
          Ingresar a la plataforma
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M5 12h13" />
            <path d="m13 6 6 6-6 6" />
          </svg>
        </button>
      </div>
    </header>


    <main>

      <!-- =======================================================
           HERO
      ======================================================== -->
      <section
        id="inicio"
        class="hero-section"
      >
        <div class="hero-background"></div>

        <div class="container hero-container">

          <div class="hero-copy">

            <div class="hero-eyebrow">
              <span class="eyebrow-dot"></span>

              <span>
                LEGAL INTELLIGENCE
              </span>

              <i></i>

              <span>
                AI-POWERED ANALYSIS
              </span>

              <i></i>

              <span>
                MULTI-AGENT SYSTEMS
              </span>
            </div>

            <div class="hero-line"></div>

            <h1>
              La nueva inteligencia
              <br />
              para el análisis y la
              <br />
              estrategia jurídica.
            </h1>

            <p class="hero-description">
              Nova Iuris integra inteligencia artificial, búsqueda jurídica
              inteligente y simulación multiagente para ayudar a profesionales
              e instituciones a analizar información jurídica, explorar
              escenarios y tomar decisiones con mayor respaldo.
            </p>

            <div class="hero-actions">

              <button
                type="button"
                class="button button-primary"
                @click="openPlatformModal"
              >
                <span>Ingresar a la plataforma</span>

                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M5 12h13" />
                  <path d="m13 6 6 6-6 6" />
                </svg>
              </button>

              <button
                type="button"
                class="button button-secondary"
                @click="scrollToSection('plataforma')"
              >
                Conocer la plataforma
              </button>

            </div>

            <div class="hero-meta">
              <span>01</span>

              <span class="hero-meta-line"></span>

              <span>
                UNA INFRAESTRUCTURA DE INTELIGENCIA
                PARA EL TRABAJO JURÍDICO
              </span>
            </div>

          </div>


          <!-- ===================================================
               HERO IMAGE
          ==================================================== -->
          <div class="hero-visual">

            <div class="hero-image-wrapper">

              <img
                src="/nova-hero.png"
                alt="Nova Iuris — inteligencia jurídica"
                class="hero-image"
                @error="handleImageError"
              />

              <div
                v-if="imageError"
                class="hero-image-fallback"
              >
                <div class="fallback-symbol">
                  <svg viewBox="0 0 100 100" aria-hidden="true">
                    <path d="M50 18v58" />
                    <path d="M27 34h46" />
                    <path d="M27 34 16 55h22L27 34Z" />
                    <path d="M73 34 62 55h22L73 34Z" />
                    <path d="M30 76h40" />
                    <path d="M38 84h24" />
                  </svg>
                </div>

                <span>NOVA IURIS</span>
              </div>

            </div>

          </div>

        </div>
      </section>


      <!-- =======================================================
           PLATAFORMA
      ======================================================== -->
      <section
        id="plataforma"
        class="platform-section"
      >
        <div class="container">

          <div class="section-heading section-heading-dark">

            <span class="section-kicker">
              PLATAFORMA NOVA IURIS
            </span>

            <h2>
              Una nueva capa de inteligencia
              <br />
              para el trabajo jurídico.
            </h2>

            <p>
              Tres sistemas especializados trabajan dentro de una misma
              infraestructura para investigar información, estructurar casos
              y explorar escenarios jurídicos.
            </p>

          </div>


          <div class="tools-grid">

            <!-- =================================================
                 NOVA SEARCH
            ================================================== -->
            <article
              class="tool-card"
              tabindex="0"
              role="button"
              aria-label="Abrir NovaSearch"
              @click="goToTool('/novasearch')"
              @keydown.enter="goToTool('/novasearch')"
            >

              <div class="tool-header">

                <div class="tool-icon">
                  <svg viewBox="0 0 48 48" aria-hidden="true">
                    <circle
                      cx="21"
                      cy="21"
                      r="10"
                    />
                    <path
                      d="m29 29 10 10"
                    />
                  </svg>
                </div>

                <span class="tool-number">
                  01
                </span>

              </div>

              <div class="tool-body">

                <span class="tool-label">
                  NOVA SEARCH
                </span>

                <h3>
                  Investigación jurídica
                  inteligente
                </h3>

                <p>
                  Explora legislación, jurisprudencia y conocimiento jurídico
                  mediante recuperación contextual e inteligencia artificial.
                </p>

              </div>

              <div class="tool-footer">

                <span>
                  Explorar herramienta
                </span>

                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path d="M4 12h15" />
                  <path d="m13 6 6 6-6 6" />
                </svg>

              </div>

            </article>


            <!-- =================================================
                 NOVA CASE
            ================================================== -->
            <article
              class="tool-card"
              tabindex="0"
              role="button"
              aria-label="Abrir NovaCase"
              @click="goToTool('/novacase')"
              @keydown.enter="goToTool('/novacase')"
            >

              <div class="tool-header">

                <div class="tool-icon">
                  <svg viewBox="0 0 48 48" aria-hidden="true">
                    <rect
                      x="13"
                      y="10"
                      width="22"
                      height="28"
                      rx="2"
                    />
                    <path d="M18 17h12" />
                    <path d="M18 23h12" />
                    <path d="M18 29h8" />
                    <path d="M19 10v-3h10v3" />
                  </svg>
                </div>

                <span class="tool-number">
                  02
                </span>

              </div>

              <div class="tool-body">

                <span class="tool-label">
                  NOVA CASE
                </span>

                <h3>
                  Inteligencia para casos
                  jurídicos
                </h3>

                <p>
                  Organiza hechos, evidencia, argumentos y relaciones
                  relevantes para construir una visión estructurada del caso.
                </p>

              </div>

              <div class="tool-footer">

                <span>
                  Analizar un caso
                </span>

                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path d="M4 12h15" />
                  <path d="m13 6 6 6-6 6" />
                </svg>

              </div>

            </article>


            <!-- =================================================
                 NOVA COURT
            ================================================== -->
            <article
              class="tool-card tool-card-featured"
              tabindex="0"
              role="button"
              aria-label="Abrir NovaCourt"
              @click="goToTool('/novacourt')"
              @keydown.enter="goToTool('/novacourt')"
            >

              <span class="featured-tag">
                TECNOLOGÍA CENTRAL
              </span>

              <div class="tool-header">

                <div class="tool-icon">
                  <svg viewBox="0 0 48 48" aria-hidden="true">
                    <path d="M24 8v28" />
                    <path d="M12 15h24" />
                    <path d="M12 15 5 29h14l-7-14Z" />
                    <path d="M36 15 29 29h14l-7-14Z" />
                    <path d="M15 36h18" />
                    <path d="M19 40h10" />
                  </svg>
                </div>

                <span class="tool-number">
                  03
                </span>

              </div>

              <div class="tool-body">

                <span class="tool-label">
                  NOVA COURT
                </span>

                <h3>
                  Tribunal multiagente
                  inteligente
                </h3>

                <p>
                  Explora posiciones, argumentos y dinámicas jurídicas mediante
                  agentes especializados y simulación de escenarios.
                </p>

              </div>

              <div class="tool-footer">

                <span>
                  Iniciar simulación
                </span>

                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path d="M4 12h15" />
                  <path d="m13 6 6 6-6 6" />
                </svg>

              </div>

            </article>

          </div>

        </div>
      </section>


      <!-- =======================================================
           CÓMO FUNCIONA
      ======================================================== -->
      <section
        id="como-funciona"
        class="process-section"
      >
        <div class="container">

          <div class="process-top">

            <div class="section-heading section-heading-light">

              <span class="section-kicker">
                CÓMO FUNCIONA
              </span>

              <h2>
                De la información
                <br />
                al análisis estratégico.
              </h2>

            </div>

            <p class="process-intro">
              Nova Iuris conecta investigación, recuperación de conocimiento,
              análisis asistido por IA y exploración de escenarios dentro
              de un mismo flujo de trabajo.
            </p>

          </div>


          <div class="process-grid">

            <!-- 01 -->
            <article class="process-card">

              <div class="process-card-top">
                <span>01</span>

                <div class="process-icon">
                  <svg viewBox="0 0 48 48" aria-hidden="true">
                    <circle
                      cx="20"
                      cy="20"
                      r="10"
                    />
                    <path d="m28 28 11 11" />
                  </svg>
                </div>
              </div>

              <h3>
                Consulta
              </h3>

              <p>
                El usuario plantea una pregunta, analiza un documento
                o introduce un escenario jurídico.
              </p>

            </article>


            <!-- 02 -->
            <article class="process-card">

              <div class="process-card-top">
                <span>02</span>

                <div class="process-icon">
                  <svg viewBox="0 0 48 48" aria-hidden="true">
                    <rect
                      x="10"
                      y="11"
                      width="28"
                      height="8"
                      rx="2"
                    />
                    <rect
                      x="10"
                      y="21"
                      width="28"
                      height="8"
                      rx="2"
                    />
                    <rect
                      x="10"
                      y="31"
                      width="28"
                      height="6"
                      rx="2"
                    />
                  </svg>
                </div>
              </div>

              <h3>
                Recuperación
              </h3>

              <p>
                El sistema recupera y relaciona información jurídica
                relevante mediante búsqueda contextual.
              </p>

            </article>


            <!-- 03 -->
            <article class="process-card">

              <div class="process-card-top">
                <span>03</span>

                <div class="process-icon">
                  <svg viewBox="0 0 48 48" aria-hidden="true">
                    <path d="M10 34h28" />
                    <path d="M14 29V20" />
                    <path d="M24 29V13" />
                    <path d="M34 29V17" />
                    <circle cx="14" cy="18" r="2" />
                    <circle cx="24" cy="11" r="2" />
                    <circle cx="34" cy="15" r="2" />
                  </svg>
                </div>
              </div>

              <h3>
                Análisis
              </h3>

              <p>
                La plataforma ayuda a estructurar argumentos, evidencia,
                criterios y relaciones relevantes.
              </p>

            </article>


            <!-- 04 -->
            <article class="process-card">

              <div class="process-card-top">
                <span>04</span>

                <div class="process-icon">
                  <svg viewBox="0 0 48 48" aria-hidden="true">
                    <circle
                      cx="24"
                      cy="24"
                      r="14"
                    />
                    <path d="M24 10v14l9 8" />
                    <path d="M24 24 15 17" />
                  </svg>
                </div>
              </div>

              <h3>
                Simulación
              </h3>

              <p>
                Nova Court permite explorar diferentes perspectivas,
                posiciones y escenarios jurídicos.
              </p>

            </article>

          </div>

        </div>
      </section>


      <!-- =======================================================
           TECNOLOGÍA
      ======================================================== -->
      <section
        id="tecnologia"
        class="technology-section"
      >
        <div class="container">

          <div class="section-heading">

            <span class="section-kicker">
              TECNOLOGÍA
            </span>

            <h2>
              Arquitectura diseñada para el
              <br />
              razonamiento jurídico complejo.
            </h2>

            <p>
              Nova Iuris combina diferentes capas tecnológicas para construir
              experiencias de inteligencia jurídica más profundas,
              contextuales y orientadas al análisis.
            </p>

          </div>


          <div class="technology-grid">

            <!-- 01 -->
            <article class="technology-card">

              <div class="technology-icon">
                <svg viewBox="0 0 48 48" aria-hidden="true">
                  <circle
                    cx="20"
                    cy="20"
                    r="10"
                  />
                  <path d="m28 28 11 11" />
                </svg>
              </div>

              <div class="technology-content">

                <span>
                  01
                </span>

                <h3>
                  Recuperación inteligente
                </h3>

                <p>
                  Sistemas de búsqueda contextual para recuperar
                  información jurídica relevante.
                </p>

              </div>

            </article>


            <!-- 02 -->
            <article class="technology-card">

              <div class="technology-icon">
                <svg viewBox="0 0 48 48" aria-hidden="true">
                  <path d="m24 8 14 7-14 7-14-7 14-7Z" />
                  <path d="m10 24 14 7 14-7" />
                  <path d="m10 31 14 7 14-7" />
                </svg>
              </div>

              <div class="technology-content">

                <span>
                  02
                </span>

                <h3>
                  Arquitectura RAG
                </h3>

                <p>
                  Integración de modelos de inteligencia artificial
                  con bases de conocimiento especializadas.
                </p>

              </div>

            </article>


            <!-- 03 -->
            <article class="technology-card">

              <div class="technology-icon">
                <svg viewBox="0 0 48 48" aria-hidden="true">
                  <path d="M24 7v34" />
                  <path d="M17 14h14" />
                  <path d="M13 21h22" />
                  <path d="M17 28h14" />
                  <path d="M13 35h22" />
                  <circle cx="24" cy="7" r="2" />
                  <circle cx="24" cy="41" r="2" />
                </svg>
              </div>

              <div class="technology-content">

                <span>
                  03
                </span>

                <h3>
                  Inteligencia artificial aplicada
                </h3>

                <p>
                  Modelos orientados al análisis, síntesis y estructuración
                  de información jurídica.
                </p>

              </div>

            </article>


            <!-- 04 -->
            <article class="technology-card">

              <div class="technology-icon">
                <svg viewBox="0 0 48 48" aria-hidden="true">
                  <circle cx="24" cy="10" r="4" />
                  <circle cx="10" cy="34" r="4" />
                  <circle cx="38" cy="34" r="4" />
                  <path d="M24 14v9" />
                  <path d="M24 23 10 30" />
                  <path d="M24 23 38 30" />
                </svg>
              </div>

              <div class="technology-content">

                <span>
                  04
                </span>

                <h3>
                  Sistemas multiagente
                </h3>

                <p>
                  Arquitecturas capaces de representar diferentes
                  perspectivas y explorar escenarios complejos.
                </p>

              </div>

            </article>

          </div>

        </div>
      </section>


      <!-- =======================================================
           VISIÓN
      ======================================================== -->
      <section class="vision-section">

        <div class="container">

          <div class="vision-content">

            <span class="section-kicker">
              NOVA IURIS
            </span>

            <div class="vision-rule"></div>

            <h2>
              Estamos construyendo el futuro de la
              <br />
              inteligencia jurídica.
            </h2>

            <p>
              Nuestra visión es desarrollar herramientas que permitan a
              profesionales e instituciones interactuar con el conocimiento
              jurídico de una forma más inteligente, contextual y estratégica.
            </p>

            <div class="vision-values">

              <div>
                <span></span>
                <strong>Más contexto.</strong>
              </div>

              <div>
                <span></span>
                <strong>Mejor análisis.</strong>
              </div>

              <div>
                <span></span>
                <strong>Nuevas posibilidades.</strong>
              </div>

            </div>

          </div>

        </div>

      </section>


      <!-- =======================================================
           FINAL CTA
      ======================================================== -->
      <section class="final-section">

        <div class="container">

          <div class="final-content">

            <span class="section-kicker">
              NOVA IURIS
            </span>

            <h2>
              Explora una nueva forma
              <br />
              de trabajar con el derecho.
            </h2>

            <p>
              Investiga información jurídica, estructura casos y explora
              escenarios mediante inteligencia artificial.
            </p>

            <button
              type="button"
              class="button button-primary final-button"
              @click="openPlatformModal"
            >
              <span>Comenzar ahora</span>

              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 12h13" />
                <path d="m13 6 6 6-6 6" />
              </svg>
            </button>

          </div>

        </div>

      </section>

    </main>


    <!-- =========================================================
         FOOTER
    ========================================================== -->
    <footer class="footer">

      <div class="container">

        <div class="footer-top">

          <div class="footer-brand">

            <div class="footer-logo">
              NOVA IURIS
            </div>

            <span class="footer-brand-rule"></span>

            <p>
              Inteligencia jurídica para el análisis,
              la estrategia y la simulación.
            </p>

          </div>

          <div class="footer-links">

            <button
              type="button"
              @click="scrollToSection('inicio')"
            >
              Inicio
            </button>

            <button
              type="button"
              @click="scrollToSection('plataforma')"
            >
              Plataforma
            </button>

            <button
              type="button"
              @click="scrollToSection('como-funciona')"
            >
              Cómo funciona
            </button>

            <button
              type="button"
              @click="scrollToSection('tecnologia')"
            >
              Tecnología
            </button>

          </div>

        </div>


        <div class="footer-bottom">

          <span>
            © {{ currentYear }} Nova Iuris.
            Todos los derechos reservados.
          </span>

          <span>
            LEGAL INTELLIGENCE · AI ANALYSIS · MULTI-AGENT SYSTEMS
          </span>

        </div>

      </div>

    </footer>


    <!-- =========================================================
         PLATFORM MODAL
    ========================================================== -->
    <Teleport to="body">

      <Transition name="modal">

        <div
          v-if="platformModalOpen"
          class="modal-overlay"
          @click.self="closePlatformModal"
        >

          <div
            class="platform-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="platform-modal-title"
          >

            <button
              type="button"
              class="modal-close"
              aria-label="Cerrar"
              @click="closePlatformModal"
            >
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 5l14 14" />
                <path d="m19 5-14 14" />
              </svg>
            </button>


            <div class="modal-heading">

              <span class="section-kicker">
                NOVA IURIS PLATFORM
              </span>

              <h2 id="platform-modal-title">
                Selecciona una herramienta
              </h2>

              <p>
                Accede directamente al sistema especializado
                que necesitas.
              </p>

            </div>


            <div class="modal-tools">

              <!-- NOVA SEARCH -->
              <button
                type="button"
                class="modal-tool"
                @click="goToTool('/novasearch')"
              >

                <div class="modal-tool-icon">
                  <svg viewBox="0 0 48 48" aria-hidden="true">
                    <circle
                      cx="21"
                      cy="21"
                      r="10"
                    />
                    <path d="m29 29 10 10" />
                  </svg>
                </div>

                <div class="modal-tool-info">

                  <span>
                    NOVA SEARCH
                  </span>

                  <strong>
                    Investigación jurídica inteligente
                  </strong>

                  <small>
                    Búsqueda, legislación y jurisprudencia
                  </small>

                </div>

                <div class="modal-tool-arrow">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 12h15" />
                    <path d="m13 6 6 6-6 6" />
                  </svg>
                </div>

              </button>


              <!-- NOVA CASE -->
              <button
                type="button"
                class="modal-tool"
                @click="goToTool('/novacase')"
              >

                <div class="modal-tool-icon">
                  <svg viewBox="0 0 48 48" aria-hidden="true">
                    <rect
                      x="13"
                      y="10"
                      width="22"
                      height="28"
                      rx="2"
                    />
                    <path d="M18 17h12" />
                    <path d="M18 23h12" />
                    <path d="M18 29h8" />
                    <path d="M19 10v-3h10v3" />
                  </svg>
                </div>

                <div class="modal-tool-info">

                  <span>
                    NOVA CASE
                  </span>

                  <strong>
                    Inteligencia para casos jurídicos
                  </strong>

                  <small>
                    Hechos, evidencia y estrategia
                  </small>

                </div>

                <div class="modal-tool-arrow">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 12h15" />
                    <path d="m13 6 6 6-6 6" />
                  </svg>
                </div>

              </button>


              <!-- NOVA COURT -->
              <button
                type="button"
                class="modal-tool"
                @click="goToTool('/novacourt')"
              >

                <div class="modal-tool-icon">
                  <svg viewBox="0 0 48 48" aria-hidden="true">
                    <path d="M24 8v28" />
                    <path d="M12 15h24" />
                    <path d="M12 15 5 29h14l-7-14Z" />
                    <path d="M36 15 29 29h14l-7-14Z" />
                    <path d="M15 36h18" />
                    <path d="M19 40h10" />
                  </svg>
                </div>

                <div class="modal-tool-info">

                  <span>
                    NOVA COURT
                  </span>

                  <strong>
                    Tribunal multiagente inteligente
                  </strong>

                  <small>
                    Simulación y escenarios jurídicos
                  </small>

                </div>

                <div class="modal-tool-arrow">
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M4 12h15" />
                    <path d="m13 6 6 6-6 6" />
                  </svg>
                </div>

              </button>

            </div>


            <div class="modal-note">
              Selecciona una herramienta para continuar.
            </div>

          </div>

        </div>

      </Transition>

    </Teleport>

  </div>
</template>


<script setup>
import {
  ref,
  computed,
  onMounted,
  onBeforeUnmount
} from 'vue'

import { useRouter } from 'vue-router'


/* =========================================================
   ROUTER
========================================================= */

const router = useRouter()


/* =========================================================
   STATE
========================================================= */

const platformModalOpen = ref(false)
const mobileMenuOpen = ref(false)
const imageError = ref(false)


/* =========================================================
   YEAR
========================================================= */

const currentYear = computed(() => {
  return new Date().getFullYear()
})


/* =========================================================
   IMAGE ERROR
========================================================= */

const handleImageError = () => {
  imageError.value = true
}


/* =========================================================
   MODAL
========================================================= */

const openPlatformModal = () => {
  mobileMenuOpen.value = false
  platformModalOpen.value = true

  document.body.style.overflow = 'hidden'
}


const closePlatformModal = () => {
  platformModalOpen.value = false
  document.body.style.overflow = ''
}


/* =========================================================
   TOOL NAVIGATION
========================================================= */

/*
  RUTAS DEL ECOSISTEMA NOVA IURIS

  NovaSearch -> /novasearch
  NovaCase   -> /novacase
  NovaCourt  -> /novacourt

  Se utiliza router.push para mantener
  la navegación dentro de la aplicación Vue.
*/

const goToTool = async (path) => {

  closePlatformModal()

  try {

    await router.push(path)

  } catch (error) {

    console.error(
      `[Nova Iuris] Error al navegar hacia ${path}:`,
      error
    )

  }
}


/* =========================================================
   SCROLL
========================================================= */

const scrollToSection = (sectionId) => {

  mobileMenuOpen.value = false

  const section = document.getElementById(sectionId)

  if (!section) {
    return
  }

  section.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  })
}


/* =========================================================
   MOBILE NAVIGATION
========================================================= */

const mobileNavigate = (sectionId) => {

  mobileMenuOpen.value = false

  requestAnimationFrame(() => {
    scrollToSection(sectionId)
  })
}


/* =========================================================
   ESC
========================================================= */

const handleKeydown = (event) => {

  if (event.key === 'Escape') {

    if (platformModalOpen.value) {
      closePlatformModal()
    }

    mobileMenuOpen.value = false
  }
}


/* =========================================================
   LIFECYCLE
========================================================= */

onMounted(() => {

  window.addEventListener(
    'keydown',
    handleKeydown
  )

})


onBeforeUnmount(() => {

  window.removeEventListener(
    'keydown',
    handleKeydown
  )

  document.body.style.overflow = ''

})
</script>


<style scoped>
@import url(
  'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@400;500;600&display=swap'
);


/* =========================================================
   DESIGN SYSTEM
========================================================= */

.nova-home {

  --white: #ffffff;
  --off-white: #f7f9fc;

  --navy-950: #050d19;
  --navy-900: #071321;
  --navy-850: #0a1727;
  --navy-800: #0d1c30;
  --navy-700: #12253d;

  --blue-700: #124c8f;
  --blue-600: #1764b5;
  --blue-500: #2678ce;
  --blue-300: #77b3ec;
  --blue-100: #dcecff;

  --gold: #caa968;
  --gold-light: #dec68f;

  --text-dark: #0b1b30;
  --text-muted: #66768b;

  --text-light: #eef4fb;
  --text-light-muted: #aebed0;

  --border: #dbe3ed;
  --border-dark: rgba(255,255,255,.12);

  --shadow-soft:
    0 15px 45px rgba(8, 25, 48, .08);

  --shadow-card:
    0 22px 55px rgba(3, 15, 31, .20);

  min-height: 100vh;

  background: var(--white);

  color: var(--text-dark);

  font-family:
    'DM Sans',
    sans-serif;

  overflow-x: hidden;
}


.nova-home *,
.nova-home *::before,
.nova-home *::after {
  box-sizing: border-box;
}


.nova-home button {
  font: inherit;
}


/* =========================================================
   GLOBAL CONTAINER
========================================================= */

.container {
  width: min(
    calc(100% - 120px),
    1240px
  );

  margin: 0 auto;
}


/* =========================================================
   NAVBAR
========================================================= */

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 500;
  background:
    rgba(5, 13, 25, .96);
  border-bottom:
    1px solid rgba(255,255,255,.09);
  backdrop-filter:
    blur(18px);
}


.navbar-inner {
  width: min(
    calc(100% - 120px),
    1240px
  );

  min-height: 72px;

  margin: 0 auto;

  display: flex;
  align-items: center;

  gap: 32px;
}


.brand {
  display: inline-flex;
  align-items: center;

  gap: 13px;

  border: none;
  background: transparent;

  color: white;

  padding: 0;

  cursor: pointer;
}


.brand-name {
  font-size: 18px;

  font-weight: 600;

  letter-spacing:
    4px;
}


.brand-rule {
  width: 27px;
  height: 1px;

  background:
    var(--gold);
}


.desktop-nav {
  display: flex;
  align-items: center;

  gap: 34px;

  margin-left: auto;
}


.desktop-nav button {
  position: relative;

  border: none;
  background: transparent;

  color:
    #aeb9c8;

  font-size: 14px;

  padding: 9px 0;

  cursor: pointer;

  transition:
    color .2s ease;
}


.desktop-nav button::after {
  content: '';

  position: absolute;

  left: 0;
  bottom: 0;

  width: 0;
  height: 1px;

  background:
    var(--gold);

  transition:
    width .2s ease;
}


.desktop-nav button:hover {
  color: white;
}


.desktop-nav button:hover::after {
  width: 100%;
}


.navbar-cta {
  min-height: 44px;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  gap: 12px;

  padding: 0 20px;

  border:
    1px solid
    rgba(202,169,104,.65);

  background:
    transparent;

  color:
    var(--gold-light);

  cursor: pointer;

  transition:
    background .22s ease,
    color .22s ease,
    border-color .22s ease;
}


.navbar-cta svg {
  width: 17px;
  height: 17px;

  fill: none;
  stroke: currentColor;
  stroke-width: 1.5;

  transition:
    transform .22s ease;
}


.navbar-cta:hover {
  background:
    var(--gold);

  border-color:
    var(--gold);

  color:
    var(--navy-950);
}


.navbar-cta:hover svg {
  transform:
    translateX(3px);
}


.mobile-menu-button,
.mobile-menu {
  display: none;
}


/* =========================================================
   HERO
========================================================= */

.hero-section {
  position: relative;

  min-height: 690px;

  display: flex;
  align-items: center;

  overflow: hidden;

  background:
    var(--navy-900);

  color: white;
}


.hero-background {
  position: absolute;
  inset: 0;

  pointer-events: none;

  background:
    radial-gradient(
      circle at 75% 30%,
      rgba(30,100,180,.12),
      transparent 32%
    ),

    radial-gradient(
      circle at 20% 80%,
      rgba(14,76,139,.09),
      transparent 35%
    );
}


.hero-background::after {
  content: '';

  position: absolute;
  inset: 0;

  opacity: .14;

  background-image:
    linear-gradient(
      rgba(119,179,236,.08) 1px,
      transparent 1px
    ),
    linear-gradient(
      90deg,
      rgba(119,179,236,.08) 1px,
      transparent 1px
    );

  background-size:
    70px 70px;

  mask-image:
    linear-gradient(
      to bottom,
      black,
      transparent 78%
    );
}


.hero-container {
  position: relative;
  z-index: 2;

  display: grid;

  grid-template-columns:
    minmax(0, .98fr)
    minmax(0, 1.02fr);

  align-items: center;

  gap: 74px;

  padding-top: 76px;
  padding-bottom: 78px;
}


.hero-copy {
  max-width: 650px;
}


.hero-eyebrow {
  display: flex;
  align-items: center;
  flex-wrap: wrap;

  gap: 9px;

  color:
    var(--gold-light);

  font-family:
    'DM Mono',
    monospace;

  font-size: 9px;

  letter-spacing:
    1.45px;

  line-height: 1.7;
}


.eyebrow-dot {
  width: 7px;
  height: 7px;

  flex: 0 0 auto;

  border-radius: 50%;

  background:
    var(--gold);

  box-shadow:
    0 0 0 4px
    rgba(202,169,104,.09);
}


.hero-eyebrow i {
  width: 3px;
  height: 3px;

  border-radius: 50%;

  background:
    rgba(202,169,104,.6);
}


.hero-line {
  width: 64px;
  height: 1px;

  margin-top: 25px;
  margin-bottom: 35px;

  background:
    var(--gold);
}


.hero-copy h1 {
  margin: 0;

  color:
    #f5f2ec;

  font-family:
    'Playfair Display',
    serif;

  font-size:
    clamp(
      49px,
      5.1vw,
      76px
    );

  font-weight: 400;

  line-height:
    1.04;

  letter-spacing:
    -2.1px;
}


.hero-description {
  max-width: 620px;

  margin:
    30px 0 0;

  color:
    #afbed0;

  font-size:
    16px;

  line-height:
    1.8;
}


.hero-actions {
  display: flex;
  align-items: center;

  gap: 12px;

  flex-wrap: wrap;

  margin-top: 34px;
}


.button {
  min-height: 53px;

  display: inline-flex;
  align-items: center;
  justify-content: center;

  gap: 17px;

  padding:
    0 24px;

  border-radius: 0;

  cursor: pointer;

  font-size: 14px;

  font-weight: 600;

  transition:
    transform .22s ease,
    background .22s ease,
    border-color .22s ease,
    color .22s ease,
    box-shadow .22s ease;
}


.button svg {
  width: 18px;
  height: 18px;

  fill: none;
  stroke: currentColor;
  stroke-width: 1.5;

  transition:
    transform .22s ease;
}


.button:hover {
  transform:
    translateY(-2px);
}


.button:hover svg {
  transform:
    translateX(4px);
}


.button-primary {
  border:
    1px solid var(--gold);

  background:
    var(--gold);

  color:
    var(--navy-950);

  box-shadow:
    0 12px 30px
    rgba(0,0,0,.18);
}


.button-primary:hover {
  background:
    var(--gold-light);

  border-color:
    var(--gold-light);

  box-shadow:
    0 16px 35px
    rgba(0,0,0,.24);
}


.button-secondary {
  border:
    1px solid
    rgba(178,198,219,.28);

  background:
    transparent;

  color:
    #e8eff7;
}


.button-secondary:hover {
  border-color:
    rgba(119,179,236,.7);

  color:
    white;

  background:
    rgba(119,179,236,.06);
}


.hero-meta {
  display: flex;
  align-items: center;

  gap: 12px;

  margin-top: 43px;

  color:
    #7890a9;

  font-family:
    'DM Mono',
    monospace;

  font-size: 8px;

  letter-spacing:
    1.2px;
}


.hero-meta > span:first-child {
  color:
    var(--gold);
}


.hero-meta-line {
  width: 38px;
  height: 1px;

  background:
    rgba(202,169,104,.45);
}


/* =========================================================
   HERO IMAGE
========================================================= */

.hero-visual {
  display: flex;
  align-items: center;
  justify-content: center;
}


.hero-image-wrapper {
  position: relative;

  width: 100%;

  display: flex;
  align-items: center;
  justify-content: center;

  overflow: hidden;
}


.hero-image {
  display: block;

  width: 100%;
  height: auto;

  max-height: 510px;

  object-fit: contain;

  object-position: center;

  border: none;

  border-radius: 0;

  box-shadow: none;

  background: transparent;
}


.hero-image-fallback {
  width: 100%;
  min-height: 390px;

  display: flex;
  flex-direction: column;

  align-items: center;
  justify-content: center;

  gap: 20px;

  background:
    linear-gradient(
      145deg,
      #0a1829,
      #0e243d
    );

  color:
    var(--gold-light);

  font-family:
    'DM Mono',
    monospace;

  letter-spacing:
    4px;
}


.fallback-symbol svg {
  width: 150px;
  height: 150px;

  fill: none;

  stroke:
    currentColor;

  stroke-width: 1.2;
}


/* =========================================================
   SECTION HEADING
========================================================= */

.section-heading {
  max-width: 900px;
}


.section-kicker {
  display: inline-block;

  color:
    var(--gold);

  font-family:
    'DM Mono',
    monospace;

  font-size: 10px;

  font-weight: 500;

  letter-spacing:
    2.1px;
}


.section-heading h2 {
  margin:
    20px 0 0;

  font-family:
    'Playfair Display',
    serif;

  font-size:
    clamp(
      42px,
      4.5vw,
      64px
    );

  font-weight: 400;

  line-height:
    1.08;

  letter-spacing:
    -1.3px;
}


.section-heading p {
  max-width: 760px;

  margin:
    22px 0 0;

  font-size: 16px;

  line-height:
    1.78;
}


/* =========================================================
   PLATFORM
========================================================= */

.platform-section {
  padding:
    110px 0
    120px;

  background:
    var(--navy-800);

  color:
    white;
}


.section-heading-dark h2 {
  color:
    #f4f1eb;
}


.section-heading-dark p {
  color:
    #aebed0;
}


.tools-grid {
  display: grid;

  grid-template-columns:
    repeat(3, 1fr);

  gap: 18px;

  margin-top: 58px;
}


.tool-card {
  position: relative;

  min-height: 420px;

  display: flex;
  flex-direction: column;

  padding:
    31px;

  border:
    1px solid
    rgba(255,255,255,.12);

  background:
    rgba(255,255,255,.035);

  cursor: pointer;

  outline: none;

  transition:
    transform .25s ease,
    background .25s ease,
    border-color .25s ease,
    box-shadow .25s ease;
}


.tool-card:hover,
.tool-card:focus-visible {
  transform:
    translateY(-6px);

  background:
    rgba(255,255,255,.065);

  border-color:
    rgba(119,179,236,.62);

  box-shadow:
    var(--shadow-card);
}


.tool-card-featured {
  border-color:
    rgba(202,169,104,.42);

  background:
    linear-gradient(
      145deg,
      rgba(202,169,104,.07),
      rgba(255,255,255,.035)
    );
}


.featured-tag {
  position: absolute;

  top: 0;
  right: 0;

  padding:
    8px 15px;

  background:
    var(--gold);

  color:
    var(--navy-950);

  font-family:
    'DM Mono',
    monospace;

  font-size: 8px;

  font-weight: 600;

  letter-spacing:
    1.4px;
}


.tool-header {
  display: flex;
  align-items: flex-start;

  justify-content: space-between;
}


.tool-icon {
  width: 58px;
  height: 58px;

  display: flex;
  align-items: center;
  justify-content: center;

  border:
    1px solid
    rgba(119,179,236,.42);

  background:
    rgba(119,179,236,.05);
}


.tool-icon svg {
  width: 29px;
  height: 29px;

  fill: none;

  stroke:
    #83baf0;

  stroke-width:
    1.45;

  stroke-linecap:
    round;

  stroke-linejoin:
    round;
}


.tool-number {
  color:
    rgba(205,220,235,.45);

  font-family:
    'DM Mono',
    monospace;

  font-size: 12px;
}


.tool-body {
  margin-top:
    35px;
}


.tool-label {
  display: block;

  margin-bottom:
    9px;

  color:
    #7eb5e9;

  font-family:
    'DM Mono',
    monospace;

  font-size: 9px;

  font-weight: 500;

  letter-spacing:
    1.8px;
}


.tool-body h3 {
  margin: 0;

  color:
    #f5f2ec;

  font-family:
    'Playfair Display',
    serif;

  font-size:
    29px;

  font-weight:
    400;

  line-height:
    1.16;
}


.tool-body p {
  margin:
    16px 0 0;

  color:
    #aebed0;

  font-size:
    14px;

  line-height:
    1.75;
}


.tool-footer {
  margin-top:
    auto;

  padding-top:
    22px;

  border-top:
    1px solid
    rgba(255,255,255,.10);

  display: flex;
  align-items: center;
  justify-content: space-between;

  color:
    #dce9f6;

  font-size:
    13px;

  font-weight:
    600;
}


.tool-footer svg {
  width: 21px;
  height: 21px;

  fill: none;

  stroke:
    var(--blue-300);

  stroke-width:
    1.5;

  transition:
    transform .22s ease;
}


.tool-card:hover .tool-footer svg,
.tool-card:focus-visible .tool-footer svg {
  transform:
    translateX(6px);
}


/* =========================================================
   PROCESS
========================================================= */

.process-section {
  padding:
    110px 0
    115px;

  background:
    var(--off-white);

  color:
    var(--text-dark);
}


.process-top {
  display: grid;

  grid-template-columns:
    1fr
    minmax(280px, .72fr);

  gap: 80px;

  align-items: end;
}


.section-heading-light h2 {
  color:
    var(--text-dark);
}


.process-intro {
  margin: 0;

  color:
    var(--text-muted);

  font-size:
    16px;

  line-height:
    1.8;
}


.process-grid {
  display: grid;

  grid-template-columns:
    repeat(4, 1fr);

  margin-top:
    58px;

  border-top:
    1px solid
    var(--border);

  border-left:
    1px solid
    var(--border);
}


.process-card {
  min-height:
    280px;

  padding:
    30px 27px;

  border-right:
    1px solid
    var(--border);

  border-bottom:
    1px solid
    var(--border);

  background:
    white;

  transition:
    background .22s ease;
}


.process-card:hover {
  background:
    #fbfcfe;
}


.process-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}


.process-card-top > span {
  color:
    var(--gold);

  font-family:
    'DM Mono',
    monospace;

  font-size:
    11px;
}


.process-icon {
  width: 45px;
  height: 45px;

  display: flex;
  align-items: center;
  justify-content: center;

  color:
    var(--blue-700);

  border:
    1px solid
    var(--blue-100);

  background:
    #f5f9ff;
}


.process-icon svg {
  width: 24px;
  height: 24px;

  fill: none;

  stroke:
    currentColor;

  stroke-width:
    1.35;

  stroke-linecap:
    round;

  stroke-linejoin:
    round;
}


.process-card h3 {
  margin:
    38px 0 0;

  color:
    var(--text-dark);

  font-family:
    'Playfair Display',
    serif;

  font-size:
    26px;

  font-weight:
    400;
}


.process-card p {
  margin:
    10px 0 0;

  color:
    var(--text-muted);

  font-size:
    14px;

  line-height:
    1.7;
}


/* =========================================================
   TECHNOLOGY
========================================================= */

.technology-section {
  padding:
    110px 0
    120px;

  background:
    white;
}


.technology-section
.section-heading
p {
  color:
    var(--text-muted);
}


.technology-grid {
  display: grid;

  grid-template-columns:
    repeat(2, 1fr);

  margin-top:
    56px;

  border-top:
    1px solid
    var(--border);

  border-left:
    1px solid
    var(--border);
}


.technology-card {
  min-height:
    205px;

  display: flex;
  align-items: flex-start;

  gap: 25px;

  padding:
    34px;

  border-right:
    1px solid
    var(--border);

  border-bottom:
    1px solid
    var(--border);

  transition:
    background .22s ease;
}


.technology-card:hover {
  background:
    #fafcff;
}


.technology-icon {
  width: 50px;
  height: 50px;

  flex: 0 0 auto;

  display: flex;
  align-items: center;
  justify-content: center;

  color:
    var(--blue-700);

  border:
    1px solid
    var(--blue-100);

  background:
    #f5f9ff;
}


.technology-icon svg {
  width: 27px;
  height: 27px;

  fill: none;

  stroke:
    currentColor;

  stroke-width:
    1.35;

  stroke-linecap:
    round;

  stroke-linejoin:
    round;
}


.technology-content > span {
  display: block;

  margin-bottom:
    7px;

  color:
    var(--gold);

  font-family:
    'DM Mono',
    monospace;

  font-size:
    9px;

  letter-spacing:
    1.4px;
}


.technology-content h3 {
  margin:
    0;

  color:
    var(--text-dark);

  font-family:
    'Playfair Display',
    serif;

  font-size:
    25px;

  font-weight:
    400;
}


.technology-content p {
  max-width:
    480px;

  margin:
    9px 0 0;

  color:
    var(--text-muted);

  font-size:
    14px;

  line-height:
    1.7;
}


/* =========================================================
   VISION
========================================================= */

.vision-section {
  padding:
    125px 0;

  background:
    var(--navy-900);

  color:
    white;

  text-align:
    center;
}


.vision-content {
  max-width:
    980px;

  margin:
    0 auto;
}


.vision-rule {
  width:
    62px;

  height:
    1px;

  margin:
    22px auto 32px;

  background:
    var(--gold);
}


.vision-content h2 {
  margin:
    0;

  color:
    #f5f2ec;

  font-family:
    'Playfair Display',
    serif;

  font-size:
    clamp(
      42px,
      4.8vw,
      65px
    );

  font-weight:
    400;

  line-height:
    1.08;

  letter-spacing:
    -1.2px;
}


.vision-content p {
  max-width:
    720px;

  margin:
    27px auto 0;

  color:
    #adbdcf;

  font-size:
    16px;

  line-height:
    1.8;
}


.vision-values {
  display: grid;

  grid-template-columns:
    repeat(3, 1fr);

  gap:
    24px;

  margin-top:
    57px;
}


.vision-values div {
  padding-top:
    19px;

  border-top:
    1px solid
    rgba(202,169,104,.38);
}


.vision-values span {
  display: none;
}


.vision-values strong {
  color:
    #e9eef4;

  font-family:
    'Playfair Display',
    serif;

  font-size:
    20px;

  font-weight:
    400;
}


/* =========================================================
   FINAL CTA
========================================================= */

.final-section {
  min-height:
    510px;

  display:
    flex;

  align-items:
    center;

  text-align:
    center;

  padding:
    105px 0;

  background:
    radial-gradient(
      circle at 50% 0%,
      rgba(23,100,181,.16),
      transparent 45%
    ),
    var(--navy-950);

  color:
    white;
}


.final-content {
  max-width:
    900px;

  margin:
    0 auto;
}


.final-content h2 {
  margin:
    22px 0 0;

  color:
    #f4f1eb;

  font-family:
    'Playfair Display',
    serif;

  font-size:
    clamp(
      45px,
      5vw,
      70px
    );

  font-weight:
    400;

  line-height:
    1.07;
}


.final-content p {
  max-width:
    650px;

  margin:
    23px auto 0;

  color:
    #aabacd;

  font-size:
    16px;

  line-height:
    1.75;
}


.final-button {
  margin-top:
    33px;
}


/* =========================================================
   FOOTER
========================================================= */

.footer {
  padding:
    60px 0 28px;

  background:
    #040b15;

  color:
    white;
}


.footer-top {
  display: flex;

  align-items:
    flex-start;

  justify-content:
    space-between;

  gap:
    40px;
}


.footer-logo {
  color:
    white;

  font-size:
    17px;

  font-weight:
    600;

  letter-spacing:
    4px;
}


.footer-brand-rule {
  display:
    block;

  width:
    28px;

  height:
    1px;

  margin-top:
    11px;

  background:
    var(--gold);
}


.footer-brand p {
  max-width:
    380px;

  margin:
    15px 0 0;

  color:
    #8497ad;

  font-size:
    13px;

  line-height:
    1.65;
}


.footer-links {
  display:
    flex;

  gap:
    30px;
}


.footer-links button {
  border:
    none;

  background:
    transparent;

  color:
    #93a6bb;

  padding:
    4px 0;

  font-size:
    13px;

  cursor:
    pointer;

  transition:
    color .2s ease;
}


.footer-links button:hover {
  color:
    white;
}


.footer-bottom {
  display:
    flex;

  align-items:
    center;

  justify-content:
    space-between;

  gap:
    25px;

  margin-top:
    48px;

  padding-top:
    22px;

  border-top:
    1px solid
    rgba(255,255,255,.08);

  color:
    #657991;

  font-family:
    'DM Mono',
    monospace;

  font-size:
    8px;

  letter-spacing:
    .7px;

  line-height:
    1.7;
}


/* =========================================================
   MODAL
========================================================= */

.modal-overlay {
  position:
    fixed;

  inset:
    0;

  z-index:
    9999;

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  padding:
    24px;

  background:
    rgba(2,10,20,.78);

  backdrop-filter:
    blur(14px);
}


.platform-modal {
  position:
    relative;

  width:
    min(100%, 790px);

  max-height:
    calc(100vh - 48px);

  overflow:
    auto;

  padding:
    48px;

  background:
    #f8fafc;

  border:
    1px solid
    #d3deea;

  box-shadow:
    0 40px 100px
    rgba(0,0,0,.32);
}


.modal-close {
  position:
    absolute;

  top:
    20px;

  right:
    21px;

  width:
    38px;

  height:
    38px;

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  border:
    none;

  background:
    transparent;

  color:
    #6b7b8f;

  cursor:
    pointer;
}


.modal-close:hover {
  color:
    var(--blue-700);
}


.modal-close svg {
  width:
    22px;

  height:
    22px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.4;
}


.modal-heading {
  max-width:
    600px;

  margin-bottom:
    31px;
}


.modal-heading h2 {
  margin:
    17px 0 0;

  color:
    var(--text-dark);

  font-family:
    'Playfair Display',
    serif;

  font-size:
    45px;

  font-weight:
    400;

  line-height:
    1.1;
}


.modal-heading p {
  margin:
    11px 0 0;

  color:
    var(--text-muted);

  font-size:
    14px;

  line-height:
    1.6;
}


.modal-tools {
  display:
    grid;

  gap:
    10px;
}


.modal-tool {
  width:
    100%;

  display:
    grid;

  grid-template-columns:
    58px 1fr 26px;

  align-items:
    center;

  gap:
    18px;

  padding:
    18px;

  border:
    1px solid
    var(--border);

  background:
    white;

  color:
    var(--text-dark);

  text-align:
    left;

  cursor:
    pointer;

  transition:
    transform .22s ease,
    border-color .22s ease,
    box-shadow .22s ease,
    background .22s ease;
}


.modal-tool:hover {
  transform:
    translateX(4px);

  border-color:
    #b5cbe1;

  box-shadow:
    var(--shadow-soft);

  background:
    #ffffff;
}


.modal-tool-icon {
  width:
    50px;

  height:
    50px;

  display:
    flex;

  align-items:
    center;

  justify-content:
    center;

  color:
    var(--blue-700);

  border:
    1px solid
    var(--blue-100);

  background:
    #f3f8fe;
}


.modal-tool-icon svg {
  width:
    27px;

  height:
    27px;

  fill:
    none;

  stroke:
    currentColor;

  stroke-width:
    1.4;

  stroke-linecap:
    round;

  stroke-linejoin:
    round;
}


.modal-tool-info span {
  display:
    block;

  margin-bottom:
    4px;

  color:
    var(--blue-600);

  font-family:
    'DM Mono',
    monospace;

  font-size:
    9px;

  letter-spacing:
    1.6px;
}


.modal-tool-info strong {
  display:
    block;

  color:
    var(--text-dark);

  font-family:
    'Playfair Display',
    serif;

  font-size:
    21px;

  font-weight:
    400;
}


.modal-tool-info small {
  display:
    block;

  margin-top:
    4px;

  color:
    var(--text-muted);

  font-size:
    12px;
}


.modal-tool-arrow {
  display:
    flex;

  align-items:
    center;

  justify-content:
    flex-end;
}


.modal-tool-arrow svg {
  width:
    21px;

  height:
    21px;

  fill:
    none;

  stroke:
    var(--blue-600);

  stroke-width:
    1.5;

  transition:
    transform .22s ease;
}


.modal-tool:hover
.modal-tool-arrow svg {
  transform:
    translateX(4px);
}


.modal-note {
  margin-top:
    19px;

  color:
    #8392a4;

  font-family:
    'DM Mono',
    monospace;

  font-size:
    8px;

  letter-spacing:
    1px;
}


/* =========================================================
   MODAL TRANSITION
========================================================= */

.modal-enter-active,
.modal-leave-active {
  transition:
    opacity .25s ease;
}


.modal-enter-active
.platform-modal,
.modal-leave-active
.platform-modal {
  transition:
    opacity .25s ease,
    transform .25s ease;
}


.modal-enter-from,
.modal-leave-to {
  opacity:
    0;
}


.modal-enter-from
.platform-modal,
.modal-leave-to
.platform-modal {
  opacity:
    0;

  transform:
    translateY(18px)
    scale(.985);
}


/* =========================================================
   FOCUS
========================================================= */

button:focus-visible,
.tool-card:focus-visible {
  outline:
    2px solid
    rgba(38,120,206,.65);

  outline-offset:
    3px;
}


/* =========================================================
   TABLET
========================================================= */

@media (max-width: 1100px) {

  .container,
  .navbar-inner {
    width:
      min(
        calc(100% - 70px),
        1240px
      );
  }


  .hero-container {
    grid-template-columns:
      1fr;

    gap:
      45px;
  }


  .hero-copy {
    max-width:
      850px;
  }


  .hero-visual {
    max-width:
      850px;

    margin:
      0 auto;
  }


  .tools-grid {
    grid-template-columns:
      1fr;
  }


  .tool-card {
    min-height:
      340px;
  }


  .process-grid {
    grid-template-columns:
      repeat(2,1fr);
  }


  .process-top {
    grid-template-columns:
      1fr;
  }


  .process-intro {
    max-width:
      700px;
  }
}


/* =========================================================
   TABLET SMALL
========================================================= */

@media (max-width: 850px) {

  .navbar-inner {
    min-height:
      68px;
  }


  .desktop-nav,
  .navbar-cta {
    display:
      none;
  }


  .mobile-menu-button {
    margin-left:
      auto;

    width:
      42px;

    height:
      42px;

    display:
      flex;

    flex-direction:
      column;

    align-items:
      center;

    justify-content:
      center;

    gap:
      6px;

    border:
      1px solid
      rgba(255,255,255,.18);

    background:
      transparent;

    cursor:
      pointer;
  }


  .mobile-menu-button span {
    width:
      17px;

    height:
      1px;

    background:
      white;
  }


  .mobile-menu {
    display:
      flex;

    flex-direction:
      column;

    gap:
      4px;

    padding:
      13px 24px 20px;

    border-top:
      1px solid
      rgba(255,255,255,.07);

    background:
      #050d19;
  }


  .mobile-menu button {
    min-height:
      43px;

    border:
      none;

    background:
      transparent;

    color:
      #b4c0cf;

    text-align:
      left;

    cursor:
      pointer;

    font-size:
      14px;
  }


  .mobile-menu button:hover {
    color:
      white;
  }


  .mobile-platform-button {
    display:
      flex !important;

    align-items:
      center;

    justify-content:
      space-between;

    margin-top:
      8px;

    padding:
      0 14px;

    border:
      1px solid
      rgba(202,169,104,.55) !important;

    color:
      var(--gold-light) !important;
  }


  .mobile-platform-button svg {
    width:
      17px;

    height:
      17px;

    fill:
      none;

    stroke:
      currentColor;

    stroke-width:
      1.5;
  }


  .footer-top {
    flex-direction:
      column;
  }


  .footer-links {
    flex-wrap:
      wrap;
  }
}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 620px) {

  .container,
  .navbar-inner {
    width:
      calc(100% - 36px);
  }


  .brand-name {
    font-size:
      15px;

    letter-spacing:
      3.2px;
  }


  .brand-rule {
    width:
      20px;
  }


  .hero-section {
    min-height:
      auto;
  }


  .hero-container {
    padding-top:
      60px;

    padding-bottom:
      65px;
  }


  .hero-eyebrow {
    font-size:
      8px;

    letter-spacing:
      1px;
  }


  .hero-copy h1 {
    font-size:
      45px;

    letter-spacing:
      -1.2px;
  }


  .hero-description {
    font-size:
      15px;

    line-height:
      1.72;
  }


  .hero-actions {
    flex-direction:
      column;

    align-items:
      stretch;
  }


  .button {
    width:
      100%;
  }


  .hero-meta {
    line-height:
      1.6;
  }


  .hero-image {
    width:
      100%;

    max-height:
      310px;
  }


  .platform-section,
  .process-section,
  .technology-section {
    padding-top:
      80px;

    padding-bottom:
      85px;
  }


  .section-heading h2 {
    font-size:
      40px;

    letter-spacing:
      -.8px;
  }


  .tools-grid {
    margin-top:
      38px;
  }


  .tool-card {
    min-height:
      360px;

    padding:
      25px;
  }


  .tool-body h3 {
    font-size:
      27px;
  }


  .process-grid {
    grid-template-columns:
      1fr;
  }


  .process-card {
    min-height:
      230px;
  }


  .technology-grid {
    grid-template-columns:
      1fr;
  }


  .technology-card {
    min-height:
      auto;

    padding:
      26px;

    gap:
      18px;
  }


  .technology-content h3 {
    font-size:
      22px;
  }


  .vision-section {
    padding:
      90px 0;
  }


  .vision-content h2 {
    font-size:
      40px;
  }


  .vision-values {
    grid-template-columns:
      1fr;

    gap:
      20px;

    margin-top:
      42px;
  }


  .final-section {
    min-height:
      460px;

    padding:
      80px 0;
  }


  .final-content h2 {
    font-size:
      43px;
  }


  .platform-modal {
    max-height:
      calc(100vh - 28px);

    padding:
      38px 18px 22px;
  }


  .modal-heading h2 {
    font-size:
      35px;
  }


  .modal-tool {
    grid-template-columns:
      43px 1fr 19px;

    gap:
      11px;

    padding:
      13px;
  }


  .modal-tool-icon {
    width:
      40px;

    height:
      40px;
  }


  .modal-tool-icon svg {
    width:
      22px;

    height:
      22px;
  }


  .modal-tool-info strong {
    font-size:
      16px;
  }


  .modal-tool-info small {
    font-size:
      10px;
  }


  .modal-tool-arrow svg {
    width:
      17px;

    height:
      17px;
  }


  .footer {
    padding-top:
      45px;
  }


  .footer-links {
    gap:
      18px;
  }


  .footer-bottom {
    flex-direction:
      column;

    align-items:
      flex-start;

    gap:
      10px;
  }
}


/* =========================================================
   REDUCED MOTION
========================================================= */

@media (prefers-reduced-motion: reduce) {

  *,
  *::before,
  *::after {
    scroll-behavior:
      auto !important;

    transition-duration:
      .01ms !important;

    animation-duration:
      .01ms !important;
  }
}
</style>