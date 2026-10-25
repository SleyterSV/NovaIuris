<template>
  <section class="pipeline" :class="{ 'is-complete': complete }" aria-label="Progreso del análisis judicial">
    <div class="pipeline-action"><slot name="action" /></div>
    <header class="pipeline-head">
      <div class="pipeline-intro">
        <span class="court-emblem" aria-hidden="true">⚖</span>
        <div class="pipeline-copy">
          <span class="eyebrow">NOVACOURT · PROCESAMIENTO JUDICIAL</span>
          <h2>{{ complete ? 'Análisis judicial completado' : restoring ? 'Recuperando la simulación existente' : 'NovaCourt está analizando el caso' }}</h2>
          <p>{{ complete ? 'La simulación y evaluación jurídica del caso han finalizado.' : 'El sistema está organizando los hechos, identificando los elementos jurídicos relevantes y simulando posibles escenarios judiciales con base en la normativa y jurisprudencia aplicable.' }}</p>
        </div>
      </div>
      <div class="pipeline-aside">
        <div class="progress-meter" role="progressbar" :aria-valuenow="percent" aria-valuemin="0" aria-valuemax="100" aria-label="Progreso general" :style="{ '--progress': `${percent}%` }">
          <div class="progress-center"><strong>{{ percent }}<small> %</small></strong><span>Progreso general</span></div>
        </div>
        <p class="progress-caption">{{ percent }} % completado</p>
      </div>
    </header>
    <div v-if="!complete" class="pipeline-stages">
      <div class="stage-heading"><span>ETAPAS DEL ANÁLISIS</span><p>El análisis avanza conforme se completan las etapas de la simulación.</p></div>
      <ol>
        <li v-for="stage in visibleStages" :key="stage.id" :class="stage.status">
          <span class="stage-mark" aria-hidden="true">{{ stage.status === 'completed' ? '✓' : stage.status === 'running' ? '•' : stage.status === 'failed' ? '!' : '' }}</span>
          <strong>{{ stage.label }}</strong><span class="stage-chip">{{ stageLabel(stage.status) }}</span>
        </li>
      </ol>
    </div>
    <p v-if="!complete" class="current-stage" role="status">{{ current || '\u00a0' }}</p>
    <div class="pipeline-warnings"><slot name="warnings" /></div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ progress: { type: Number, default: 0 }, current: { type: String, default: '' },
  stages: { type: Array, default: () => [] }, restoring: { type: Boolean, default: false }, complete: { type: Boolean, default: false } })
const percent = computed(() => Math.max(0, Math.min(100, Math.round(Number(props.progress) || 0))))
const milestones = [
  ['intake', 'Recepción'], ['facts', 'Hechos'], ['research', 'Investigación'],
  ['evidence', 'Evidencia'], ['risks', 'Riesgos'], ['counter_arguments', 'Contraargumentos'],
  ['final_strategy', 'Estrategia'], ['citations', 'Verificación de citas'],
  ['simulation', 'Simulación argumentativa']
]
const visibleStages = computed(() => {
  const byId = new Map(props.stages.map(stage => [stage.id, stage]))
  return milestones.map(([id, label]) => ({ id, label, status: byId.get(id)?.status || 'pending' }))
})
function stageLabel(status) {
  return { completed: 'Completado', running: 'En proceso', pending: 'Pendiente',
    skipped: 'No requerido', failed: 'Requiere atención' }[status] || 'Pendiente'
}
</script>

<style scoped>
.pipeline{position:relative;box-sizing:border-box;display:flex;flex-direction:column;gap:26px;width:100%;min-height:430px;padding:clamp(24px,3vw,38px);border:1px solid #dce5ed;border-radius:18px;background:linear-gradient(145deg,#fff 0%,#faf9f5 100%);box-shadow:0 12px 34px rgba(16,43,76,.055);color:#102b4c}.pipeline-action{position:absolute;top:20px;right:clamp(24px,3vw,38px);min-height:34px}
.pipeline-head{display:grid;grid-template-columns:minmax(0,1fr) 196px;gap:28px;min-height:178px;align-items:start}
.pipeline-intro{display:flex;align-items:flex-start;gap:18px;min-width:0;padding-top:8px}.court-emblem{display:grid;place-items:center;flex:none;width:56px;height:56px;border:1px solid #e7dcc9;border-radius:15px;background:#faf6ee;color:#997544;font:1.65rem Georgia,serif}
.pipeline-copy{min-width:0}.eyebrow,.stage-heading>span{color:#987544;font-size:.68rem;font-weight:750;letter-spacing:.11em}.pipeline h2{min-height:2.52em;margin:11px 0;color:#102b4c;font:600 clamp(1.55rem,2.2vw,2.05rem)/1.26 Georgia,'Times New Roman',serif;text-wrap:balance}.pipeline-copy>p{margin:0;color:#5d6c7e;font-size:.9rem;line-height:1.7}
.pipeline-aside{position:relative;display:grid;justify-items:center;gap:7px;min-height:178px;padding-top:30px}.progress-meter{display:grid;place-items:center;box-sizing:border-box;width:116px;height:116px;border-radius:50%;background:conic-gradient(#b08a4c var(--progress),#e5eaf0 0);box-shadow:0 3px 12px rgba(16,43,76,.06)}.progress-center{display:grid;place-content:center;justify-items:center;width:96px;height:96px;border-radius:50%;background:#fff;text-align:center}.progress-center strong{color:#102b4c;font:600 1.8rem/1.1 Georgia,serif}.progress-center small{font-size:.78rem}.progress-center span{margin-top:4px;color:#6d7d8e;font-size:.66rem;font-weight:650}.progress-caption{margin:0;color:#6d7d8e;font-size:.73rem;font-weight:600}
.pipeline-stages{min-width:0;padding-top:20px;border-top:1px solid #e5eaf0}.stage-heading{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:20px}.stage-heading p{margin:0;color:#718092;font-size:.76rem;line-height:1.5}.pipeline ol{display:flex;gap:8px;overflow-x:auto;overflow-y:hidden;scrollbar-width:thin;scrollbar-color:#c9d4df transparent;margin:0;padding:0 0 8px;list-style:none}.pipeline ol::-webkit-scrollbar{height:5px}.pipeline ol::-webkit-scrollbar-thumb{background:#c9d4df;border-radius:4px}.pipeline li{position:relative;display:flex;flex:1 0 128px;flex-direction:column;align-items:flex-start;gap:8px;min-width:128px;padding-top:7px}.pipeline li:not(:last-child)::after{content:'';position:absolute;top:20px;left:38px;right:-4px;height:1px;background:#dce4eb}
.stage-mark{z-index:1;display:grid;place-items:center;box-sizing:border-box;width:28px;height:28px;border:1px solid #dce4eb;border-radius:50%;background:#f1f4f6;color:#78899a;font-size:.85rem;font-weight:700}.pipeline li strong{min-height:34px;color:#43586f;font-size:.72rem;font-weight:650;line-height:1.4;overflow-wrap:break-word}.stage-chip{padding:4px 7px;border-radius:999px;background:#f0f3f6;color:#728194;font-size:.62rem;font-weight:650;white-space:nowrap}
.pipeline li.completed .stage-mark{border-color:#cce0d3;background:#eaf5ee;color:#3d8060}.pipeline li.completed .stage-chip{background:#eaf5ee;color:#3d8060}.pipeline li.running .stage-mark{border-color:#d9c39e;background:#b08a4c;color:#fff;box-shadow:0 0 0 4px #f8f2e9}.pipeline li.running strong{color:#102b4c}.pipeline li.running .stage-chip{background:#faf2e4;color:#876639}.pipeline li.skipped .stage-chip{background:#f2f3f5;color:#6f7c89}.pipeline li.failed .stage-mark{border-color:#eedbd5;background:#faf0ed;color:#9d574a}.pipeline li.failed .stage-chip{background:#faf0ed;color:#9d574a}
.current-stage{min-height:20px;margin:auto 0 0;color:#62758a;font-size:.77rem;line-height:1.45}.pipeline-warnings{display:grid;gap:8px}.pipeline-warnings:empty{display:none}
.pipeline.is-complete{min-height:0}.pipeline.is-complete .pipeline-head{min-height:178px}.pipeline.is-complete h2{min-height:0}
@media(max-width:720px){.pipeline{min-height:0;padding:24px;gap:24px}.pipeline-action{position:static;order:-1;align-self:flex-end}.pipeline-head{grid-template-columns:minmax(0,1fr);gap:18px;min-height:0}.pipeline.is-complete .pipeline-head{min-height:0}.pipeline-aside{display:flex;align-items:center;justify-content:flex-start;gap:18px;min-height:0;padding-top:0}.stage-heading{display:block}.stage-heading p{margin-top:6px}}
@media(max-width:480px){.pipeline{padding:20px}.pipeline-intro{gap:12px}.court-emblem{width:44px;height:44px;font-size:1.3rem}.pipeline h2{min-height:3.78em}.pipeline.is-complete h2{min-height:0}.pipeline-aside{flex-wrap:wrap}.progress-meter{width:94px;height:94px}.progress-center{width:77px;height:77px}.progress-center strong{font-size:1.45rem}}
@media(prefers-reduced-motion:reduce){.pipeline *{transition:none!important;animation:none!important}}
</style>
