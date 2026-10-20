<script setup>
import { computed } from 'vue'
const props = defineProps({ analysis: { type: Object, default: () => ({}) }, normalizedQuery: { type: String, default: '' } })
const hasAnalysis = computed(() => Boolean(props.analysis?.rama || props.analysis?.intent || props.analysis?.entities?.length))
</script>

<template>
  <section v-if="hasAnalysis" class="search-analysis" aria-labelledby="analysis-title">
    <header><h2 id="analysis-title">Interpretación jurídica</h2><p>Análisis de la naturaleza, intención y elementos jurídicamente relevantes de la consulta.</p></header>
    <div v-if="analysis.rama" class="branch"><span>Rama jurídica</span><strong>§ {{ analysis.rama }}</strong></div>
    <p v-if="analysis.intent" class="interpretation">{{ analysis.intent }}</p>
    <div v-if="analysis.entities?.length" class="concepts"><span>Conceptos relevantes</span><ul><li v-for="entity in analysis.entities" :key="entity">{{ entity }}</li></ul></div>
  </section>
</template>

<style scoped>
.search-analysis{border-top:1px solid #dce3e9;margin-top:58px;padding-top:38px;color:#24364b}.search-analysis h2{font:500 clamp(1.6rem,2.4vw,2.1rem)/1.2 Georgia,serif;color:#17375e;margin:0 0 9px}.search-analysis header p{margin:0;color:#667587;line-height:1.6}.branch{display:flex;align-items:center;gap:15px;flex-wrap:wrap;margin-top:26px}.branch span,.concepts>span{font-size:.72rem;color:#768494;font-weight:700;text-transform:uppercase;letter-spacing:.08em}.branch strong{border:1px solid #d7e1ea;background:#f2f5f8;border-radius:5px;padding:7px 12px;color:#315c97;font-size:.83rem}.interpretation,.query-summary{max-width:850px;line-height:1.7;margin:22px 0 0}.query-summary{color:#657485;font-size:.88rem}.concepts{margin-top:24px}.concepts ul{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0;margin:10px 0 0}.concepts li{border:1px solid #dce4eb;border-radius:5px;padding:5px 10px;font-size:.78rem;color:#315c97}
</style>
