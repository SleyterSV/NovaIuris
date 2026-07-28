<template>
  <router-view />
</template>

<script setup>
// Enrutador principal de Vue
</script>

<style>
/* Importar fuente profesional */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset global */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #0A192F; /* Azul oscuro institucional */
  background-color: #F4F7F9;
}

/* Estilo de barra de desplazamiento profesional */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #F4F7F9;
}

::-webkit-scrollbar-thumb {
  background: #0A192F;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #D4AF37; /* Dorado al pasar el mouse */
}

button {
  font-family: inherit;
}
</style>