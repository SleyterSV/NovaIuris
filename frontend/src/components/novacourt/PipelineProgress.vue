<template>
  <section class="pipeline" aria-label="Progreso real del análisis judicial">
    <span class="eyebrow">NOVACOURT · PROCESAMIENTO</span><h2>{{ current || 'Preparando expediente' }}</h2>
    <p>{{ progress }}% · Los estados reflejan hitos completados por el backend.</p>
    <ol><li v-for="stage in stages" :key="stage.id" :class="stage.status"><strong>{{ stage.label }}</strong><span>{{ stage.status }}</span></li></ol>
  </section>
</template>
<script setup>
defineProps({ progress: {type:Number, default:0}, current: {type:String, default:''}, stages: {type:Array, default:()=>[]} })
</script>
<style scoped>
.pipeline{padding:32px;border:1px solid #d9e0e8;background:#fffdf9;color:#17375e}.eyebrow{color:#b08a4c;font-size:.72rem;font-weight:700;letter-spacing:.12em}.pipeline h2{font-family:Georgia,serif;margin:8px 0}.pipeline p{color:#647487}.pipeline ol{list-style:none;margin:24px 0 0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:#d9e0e8}.pipeline li{background:white;padding:12px;display:flex;justify-content:space-between;gap:8px}.pipeline .running{border-left:3px solid #b08a4c}.pipeline .completed span{color:#2f7d62}.pipeline .failed span{color:#9b3a3a}@media(max-width:600px){.pipeline ol{grid-template-columns:1fr}}
</style>
