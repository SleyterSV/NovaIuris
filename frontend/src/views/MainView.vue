<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="about">
    <header><button type="button" class="brand" @click="router.push('/')">MYKE <small>LEGAL INTELLIGENCE</small></button><button type="button" class="back" @click="router.push('/')">Volver al workspace →</button></header>
    <main>
      <p class="kicker">ACERCA DE MYKE</p>
      <h1>Un espacio de trabajo jurídico conectado</h1>
      <p class="lead">MYKE reúne investigación, análisis de expedientes y simulación jurídica en una conversación. Permite conservar el contexto y revisar las fuentes que sustentan cada resultado.</p>
      <section class="capabilities" aria-label="Capacidades">
        <article><span>01 / BUSCAR</span><h2>Investiga con NovaSearch</h2><p>Busca normativa y jurisprudencia disponible. Consulta respuestas, citas y fuentes verificables cuando existen.</p></article>
        <article><span>02 / ANALIZAR</span><h2>Estructura con NovaCase</h2><p>Analiza texto y documentos del caso. Organiza hechos, problemas jurídicos, evidencia, argumentos, riesgos y estrategia.</p></article>
        <article><span>03 / SIMULAR</span><h2>Contrasta con NovaCourt</h2><p>Explora posiciones contrapuestas y una decisión simulada razonada. Puede continuar un análisis previo sin repetirlo.</p></article>
      </section>
      <section class="detail"><div><p class="kicker">DOCUMENT INTELLIGENCE</p><h2>Documentos con contexto</h2><p>Los archivos PDF, DOCX y TXT se procesan dentro de un caso. Sus identificadores y ubicaciones permiten conservar la procedencia de los fragmentos utilizados.</p></div><div><p class="kicker">TRAZABILIDAD</p><h2>Fuentes, citas y grafo</h2><p>Las citas abren fichas de fuente con los datos disponibles, como documento, página, sección o URL oficial. Las relaciones verificables pueden mostrarse como cadenas de procedencia y en el grafo jurídico.</p></div></section>
      <section class="privacy"><h2>Un workspace privado</h2><p>La sesión protege el acceso al trabajo privado. Cada nueva conversación genera un contexto de caso propio para separar documentos y resultados. MYKE ofrece asistencia para el análisis; la revisión profesional de las fuentes y conclusiones sigue siendo necesaria.</p></section>
      <button type="button" class="cta" @click="router.push('/')">Abrir MYKE →</button>
    </main>
  </div>
</template>

<style scoped>
.about{min-height:100vh;background:#f8f7f3;color:#17324f;font-family:Inter,system-ui,sans-serif}.about header{display:flex;align-items:center;justify-content:space-between;padding:23px max(5vw,30px);background:#112a46;color:#fff}.brand{border:0;background:none;color:#fff;font:normal 27px Georgia,serif;letter-spacing:.15em;cursor:pointer}.brand small{display:block;font:9px Inter,sans-serif;letter-spacing:.2em;color:#d7c7a8}.back{border:0;background:none;color:#e4ca9b;cursor:pointer}.about main{max-width:1100px;margin:auto;padding:72px 30px 90px}.kicker,.capabilities span{font-size:11px;letter-spacing:.15em;color:#a17f4f;font-weight:700}.about h1{max-width:780px;font:normal clamp(36px,5vw,58px)/1.13 Georgia,serif;margin:16px 0 20px}.lead{max-width:790px;font-size:18px;line-height:1.7;color:#51657a}.capabilities{display:grid;grid-template-columns:repeat(3,1fr);gap:17px;margin:55px 0}.capabilities article,.detail>div,.privacy{padding:28px;background:#fffdf9;border:1px solid #e1e4e5;border-radius:10px}.about h2{font:normal 24px Georgia,serif;margin:12px 0}.about article p,.detail p,.privacy p{color:#586c7e;line-height:1.7;font-size:14px}.detail{display:grid;grid-template-columns:1fr 1fr;gap:17px}.privacy{margin:17px 0 30px}.cta{padding:14px 22px;border:0;border-radius:7px;background:#17324f;color:#fff;cursor:pointer}button:focus-visible{outline:2px solid #b68a3a;outline-offset:3px}@media(max-width:750px){.capabilities,.detail{grid-template-columns:1fr}.about main{padding-top:40px}}
</style>
