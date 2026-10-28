<script setup>
defineProps({ cases:{ type:Array, default:() => [] }, loading:Boolean, error:{ type:String, default:'' } })
defineEmits(['retry','new-analysis','open-case'])
function formatDate(value) {
  if (!value) return 'Sin actividad registrada'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'Sin actividad registrada' : new Intl.DateTimeFormat('es-PE', { dateStyle:'medium' }).format(date)
}
</script>

<template>
  <section class="cases-page" aria-labelledby="cases-title">
    <header class="page-heading">
      <div><p class="page-kicker">ESPACIO PERSONAL</p><h1 id="cases-title">Mis casos</h1><p>Expedientes y análisis guardados en tu espacio de trabajo.</p></div>
      <button class="primary-action" type="button" @click="$emit('new-analysis')">Nuevo análisis</button>
    </header>

    <div v-if="loading" class="case-grid" role="status" aria-label="Cargando casos">
      <div v-for="n in 3" :key="n" class="case-skeleton"><span></span><span></span><span></span></div>
    </div>
    <div v-else-if="error" class="cases-message cases-error" role="alert">
      <h2>No fue posible cargar tus casos</h2><p>{{ error }}</p><button type="button" @click="$emit('retry')">Reintentar</button>
    </div>
    <div v-else-if="cases.length === 0" class="cases-message cases-empty">
      <span class="empty-mark" aria-hidden="true">MYKE</span><h2>Aún no tienes casos</h2><p>Crea tu primer análisis para comenzar a organizar el trabajo jurídico.</p><button class="primary-action" type="button" @click="$emit('new-analysis')">Crear un análisis</button>
    </div>
    <ul v-else class="case-grid" aria-label="Casos guardados">
      <li v-for="item in cases" :key="item.id || item.case_id" class="case-card">
        <div class="case-card-top"><span class="case-status" :class="{ archived:item.status === 'archived' }">{{ item.status === 'archived' ? 'Archivado' : 'Activo' }}</span><span class="case-date">{{ formatDate(item.updated_at || item.created_at) }}</span></div>
        <h2>{{ item.title || 'Caso jurídico' }}</h2>
        <p v-if="item.description" class="case-description">{{ item.description }}</p>
        <dl class="case-meta"><div><dt>Creado</dt><dd>{{ formatDate(item.created_at) }}</dd></div><div><dt>Última actividad</dt><dd>{{ formatDate(item.updated_at || item.created_at) }}</dd></div></dl>
        <button class="case-open" type="button" @click="$emit('open-case', item)">Ver caso <span aria-hidden="true">→</span></button>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.cases-page{width:min(1120px,100%);margin:0 auto}.page-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;padding:12px 0 30px;border-bottom:1px solid #dfe4e7}.page-kicker{color:#9a7c50;font-size:10px;font-weight:700;letter-spacing:.16em}.page-heading h1{margin:9px 0 7px;font:normal clamp(32px,4vw,44px)/1.12 Georgia,serif;color:#15314e}.page-heading p:last-child{color:#64768a;font-size:14px}.primary-action,.case-open{border:0;border-radius:7px;background:#17324f;color:#fff;padding:12px 17px;font-weight:600;cursor:pointer}.primary-action:hover,.case-open:hover{background:#254866}.primary-action:focus-visible,.case-open:focus-visible,.cases-message button:focus-visible{outline:2px solid #b68a3a;outline-offset:3px}.case-grid{list-style:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,310px),1fr));gap:17px;margin:26px 0 0;padding:0}.case-card,.case-skeleton,.cases-message{border:1px solid #e0e5e8;border-radius:10px;background:#fffdfa}.case-card{display:flex;flex-direction:column;min-height:236px;padding:21px}.case-card-top{display:flex;align-items:center;justify-content:space-between;gap:12px}.case-status{border-radius:99px;background:#e9f2ed;color:#416b55;padding:5px 9px;font-size:10px;font-weight:700}.case-status.archived{background:#f1eee7;color:#776950}.case-date,.case-meta{color:#6b7b8b;font-size:11px}.case-card h2{margin:19px 0 8px;font:normal 22px/1.25 Georgia,serif;color:#17324f;overflow-wrap:anywhere}.case-description{margin:0;color:#617286;font-size:13px;line-height:1.55;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.case-meta{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:20px 0 19px}.case-meta div{min-width:0}.case-meta dt{color:#8a9299;font-size:10px}.case-meta dd{margin-top:4px;color:#42596e;font-weight:600}.case-open{display:flex;justify-content:space-between;align-items:center;margin-top:auto;text-align:left}.cases-message{max-width:650px;margin:54px auto;padding:44px 32px;text-align:center}.cases-message h2{font:normal 25px Georgia,serif;color:#17324f}.cases-message p{margin:10px auto 20px;max-width:440px;color:#68798a;line-height:1.6;font-size:14px}.cases-error{border-left:3px solid #a65248}.cases-message button:not(.primary-action){padding:10px 15px;border:1px solid #cbd4db;border-radius:6px;background:#fff;color:#17324f;cursor:pointer}.empty-mark{display:grid;place-items:center;width:58px;height:58px;margin:0 auto 17px;border-radius:50%;background:#f0eadf;color:#94744a;font:14px Georgia,serif;letter-spacing:.08em}.case-skeleton{height:236px;padding:24px;display:grid;align-content:start;gap:14px}.case-skeleton span{height:13px;border-radius:8px;background:linear-gradient(90deg,#edf0f2,#f8f7f3,#edf0f2);background-size:200% 100%;animation:shimmer 1.4s infinite}.case-skeleton span:nth-child(2){width:72%;height:28px;margin-top:17px}.case-skeleton span:nth-child(3){width:48%;margin-top:28px}@keyframes shimmer{to{background-position:-200% 0}}@media(max-width:650px){.page-heading{align-items:flex-start;flex-direction:column}.case-grid{grid-template-columns:1fr}.cases-message{margin:30px auto;padding:34px 22px}}
</style>
