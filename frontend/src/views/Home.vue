<template>
  <div class="landing-container">
    <!-- Navbar Institucional Fija y Protegida -->
    <nav class="navbar">
      <div class="nav-brand">NOVA IURIS</div>
      <div class="nav-links">
        <a href="#inicio" class="nav-item">INICIO</a>
        <a href="#plataforma" class="nav-item">PLATAFORMA</a>
        <!-- Enlace a NovaSearch integrado en el menú -->
        <router-link to="/buscar" class="nav-item">NOVASEARCH</router-link>
        <a href="#tecnologia" class="nav-item">TECNOLOGÍA</a>
        <a href="#nosotros" class="nav-item">NOSOTROS</a>
        <a href="#contacto" class="nav-item">CONTACTO</a>
        <span class="version-text">v2.0 Enterprise</span>
      </div>
    </nav>

    <!-- Hero Section -->
    <header id="inicio" class="hero-section">
      <div class="hero-content">
        <!-- Logo integrado desde public/icon.png -->
        <img src="/icon.png" alt="Balanza Nova Iuris" class="hero-logo" />
        
        <!-- Título con color forzado (!important) para evitar que se pierda por estilos globales -->
        <h1 class="hero-title">Tribunal Multiagente <span class="gold-accent">Inteligente</span></h1>
        
        <div class="badge-tech">IA JURÍDICA AVANZADA</div>
        
        <p class="hero-subtitle">
          Análisis probabilístico y simulación de escenarios legales del sistema normativo peruano. <br>
          Anticípese a los resultados judiciales con estrategias validadas por Inteligencia Artificial.
        </p>

        <!-- Botones de Acción (Hero Actions) -->
        <div class="hero-actions">
          <button class="cta-btn">SOLICITAR DEMOSTRACIÓN</button>
          
          <!-- Nuevo Botón de NovaSearch (Estilo Outline Premium) -->
          <router-link to="/buscar" class="cta-btn-outline">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            PROBAR NOVASEARCH
          </router-link>
        </div>
      </div>
    </header>

    <!-- Dominios Jurídicos Section -->
    <section id="plataforma" class="domains-section">
      <div class="section-header">
        <h2 class="section-title">Módulos de Especialidad Jurídica</h2>
        <div class="divider"></div>
        <p class="section-subtitle">Seleccione la rama del Derecho correspondiente para acceder a la base normativa, jurisprudencia y agentes especializados.</p>
      </div>

      <!-- Flexbox para que las 5 tarjetas queden perfectamente centradas -->
      <div class="domains-grid">
        <div 
          v-for="(domain, index) in domains" 
          :key="index" 
          class="domain-card"
        >
          <div class="card-header">
            <span class="card-icon">{{ domain.icon }}</span>
            <h3 class="card-title">{{ domain.name }}</h3>
          </div>
          <p class="card-description">{{ domain.description }}</p>
          <div class="card-meta">
            <span class="meta-icon">⚖️</span>
            <span class="meta-text">{{ domain.normativeCount }} corpus normativo</span>
          </div>
          <button class="select-btn" @click="selectDomain(domain)">
            ACCEDER AL MÓDULO
          </button>
        </div>
      </div>
    </section>

    <!-- Footer Profesional -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-brand">NOVA IURIS</div>
        <p class="footer-rights">&copy; 2026 Nova Iuris Enterprise. Todos los derechos reservados.</p>
        <p class="footer-credits">Designed & Engineered by <span class="gold-accent">Sleyter Saldaña</span></p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Configuración de los Dominios Jurídicos
const domains = ref([
  {
    name: "Derecho Penal",
    icon: "I", 
    description: "Análisis dogmático en Derecho Penal, Procesal Penal, Criminalística, Medicina Legal y Psicología Forense.",
    normativeCount: "12,500+",
    route: "/process" 
  },
  {
    name: "Derecho Privado",
    icon: "II",
    description: "Resolución de conflictos en Derecho Civil, de Familia, Empresarial, Contratos, Sucesiones y Responsabilidad Civil.",
    normativeCount: "18,200+",
    route: "/process"
  },
  {
    name: "Derecho Público",
    icon: "III",
    description: "Asesoría estratégica en Derecho Administrativo, Tributario, Municipal y Contrataciones del Estado.",
    normativeCount: "15,800+",
    route: "/process"
  },
  {
    name: "Derecho Constitucional",
    icon: "IV",
    description: "Evaluación de Procesos Constitucionales, tutela de Derechos Fundamentales y análisis de Jurisprudencia vinculante.",
    normativeCount: "8,900+",
    route: "/process"
  },
  {
    name: "Derecho Económico y Social",
    icon: "V",
    description: "Regulación integral en materia de Derecho Laboral, Ambiental y normativas de Protección al Consumidor.",
    normativeCount: "10,300+",
    route: "/process"
  }
]);

const selectDomain = (domain) => {
  router.push({ name: 'Process', params: { projectId: 'new' }, query: { domain: domain.name } });
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap');

:root {
  --navy: #0A192F;
  --navy-dark: #060F1D;
  --gold: #D4AF37;
  --gold-light: rgba(212, 175, 55, 0.15);
  --white: #FFFFFF;
  --gray-bg: #F4F7F9;
  --gray-text: #4A5568;
  --gray-light: #E2E8F0;
}

.landing-container {
  background-color: var(--gray-bg);
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  padding-top: 80px;
}

/* NAVBAR */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 80px;
  background-color: #0A192F !important;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 5%;
  border-bottom: 1px solid rgba(212, 175, 55, 0.2);
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.nav-brand {
  font-family: 'Playfair Display', serif;
  font-weight: 700;
  letter-spacing: 3px;
  font-size: 1.4rem;
  color: #D4AF37 !important;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 30px;
}

.nav-item {
  color: #A0AABF !important;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 1px;
  transition: color 0.3s ease;
}

.nav-item:hover, .router-link-active.nav-item {
  color: #D4AF37 !important;
}

.version-text {
  color: #718096 !important;
  font-size: 0.8rem;
  padding-left: 20px;
  border-left: 1px solid #2D3748;
}

/* HERO SECTION */
.hero-section {
  background: radial-gradient(circle at center, #112240 0%, #0A192F 100%);
  padding: 80px 20px 120px;
  text-align: center;
  position: relative;
  border-bottom: 4px solid #D4AF37;
}

.hero-content {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-logo {
  width: 220px;
  height: auto;
  margin-bottom: 30px;
  filter: drop-shadow(0px 10px 20px rgba(0,0,0,0.4));
}

.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: 3.8rem;
  font-weight: 700;
  margin-bottom: 25px;
  line-height: 1.1;
  letter-spacing: -0.5px;
  color: #FFFFFF !important;
  text-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.gold-accent {
  color: #D4AF37 !important;
}

.badge-tech {
  display: inline-block;
  background-color: rgba(212, 175, 55, 0.08);
  color: #D4AF37 !important;
  padding: 8px 24px;
  border-radius: 30px;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 2px;
  border: 1px solid rgba(212, 175, 55, 0.5);
  margin-bottom: 35px;
  text-transform: uppercase;
}

.hero-subtitle {
  font-size: 1.15rem;
  color: #E2E8F0 !important;
  line-height: 1.7;
  max-width: 750px;
  margin-bottom: 50px;
  font-weight: 300;
}

/* HERO ACTIONS (Nuevos estilos para el contenedor de botones) */
.hero-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

.cta-btn {
  background: linear-gradient(135deg, #D4AF37 0%, #B5952F 100%);
  color: #0A192F !important;
  border: none;
  padding: 18px 45px;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 6px 20px rgba(212, 175, 55, 0.3);
}

.cta-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(212, 175, 55, 0.5);
}

.cta-btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  color: #D4AF37 !important;
  border: 2px solid #D4AF37;
  padding: 16px 35px;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  border-radius: 4px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.cta-btn-outline:hover {
  background: rgba(212, 175, 55, 0.1);
  box-shadow: 0 6px 20px rgba(212, 175, 55, 0.2);
  transform: translateY(-3px);
}

/* DOMAINS SECTION */
.domains-section {
  max-width: 1250px;
  margin: 0 auto;
  padding: 100px 20px 100px;
}

.section-header {
  text-align: center;
  margin-bottom: 70px;
}

.section-title {
  font-family: 'Playfair Display', serif;
  font-size: 2.8rem;
  color: #0A192F !important;
  margin-bottom: 15px;
  font-weight: 700;
}

.divider {
  width: 70px;
  height: 3px;
  background-color: #D4AF37;
  margin: 0 auto 25px;
}

.section-subtitle {
  color: #4A5568 !important;
  font-size: 1.15rem;
  max-width: 650px;
  margin: 0 auto;
  line-height: 1.6;
}

.domains-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 35px;
}

.domain-card {
  background: #FFFFFF;
  border-radius: 8px;
  padding: 40px 35px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 10px 25px rgba(10, 25, 47, 0.05);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  flex: 1 1 320px;
  max-width: 380px; 
}

.domain-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: #D4AF37;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.domain-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(10, 25, 47, 0.12);
  border-color: #D4AF37; 
}

.domain-card:hover::before {
  transform: scaleX(1);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
}

.card-icon {
    width: 58px;
    height: 58px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 15px;

    font-size: 1.65rem;

    background: #EFF6FF;

    color: #2563EB;

    border: 1px solid #DBEAFE;

    flex-shrink: 0;
}

.card-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.45rem;
  color: #0A192F !important;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.card-description {
  color: #4A5568 !important;
  line-height: 1.65;
  font-size: 0.95rem;
  margin-bottom: 30px;
  flex-grow: 1;
}

.card-meta {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding-top: 20px;
  border-top: 1px solid #E2E8F0;
}

.meta-icon {
  font-size: 1.2rem;
  margin-right: 10px;
}

.meta-text {
  font-size: 0.85rem;
  color: #0A192F !important;
  font-weight: 700;
}

.select-btn {
  background-color: transparent;
  color: #0A192F !important;
  border: 2px solid #0A192F;
  padding: 14px 20px;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.domain-card:hover .select-btn {
  background-color: #0A192F !important;
  color: #FFFFFF !important;
  border-color: #0A192F;
}

/* FOOTER */
.footer {
  background-color: #060F1D;
  color: #FFFFFF;
  padding: 70px 20px 40px;
  text-align: center;
  border-top: 3px solid #D4AF37;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
}

.footer-brand {
  font-family: 'Playfair Display', serif;
  font-size: 1.6rem;
  color: #D4AF37;
  letter-spacing: 3px;
  margin-bottom: 20px;
  font-weight: 700;
}

.footer-rights {
  color: #A0AABF;
  font-size: 0.9rem;
  margin-bottom: 12px;
}

.footer-credits {
  color: #718096;
  font-size: 0.85rem;
  letter-spacing: 1px;
}

/* MEDIA QUERIES */
@media (max-width: 768px) {
  .navbar {
    position: static; 
    flex-direction: column;
    height: auto;
    padding: 20px;
  }
  .landing-container {
    padding-top: 0;
  }
  .nav-links {
    margin-top: 20px;
    flex-wrap: wrap;
    justify-content: center;
    gap: 15px;
  }
  .hero-title { 
    font-size: 2.5rem; 
  }
  .hero-logo {
    width: 170px;
  }
  .hero-actions {
    flex-direction: column;
    width: 100%;
    padding: 0 20px;
  }
  .cta-btn, .cta-btn-outline {
    width: 100%;
    justify-content: center;
  }
}
</style>