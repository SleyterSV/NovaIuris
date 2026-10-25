<template>
  <main class="strategy-editorial" aria-labelledby="strategy-title">
    <header class="strategy-header">
      <div>
        <p class="strategy-eyebrow"><span aria-hidden="true"></span> MYKE · NOVACASE</p>
        <h2 id="strategy-title">Estrategia jurídica</h2>
        <p class="strategy-subtitle">Plan de actuación elaborado a partir de los hechos, la evidencia, los riesgos y las fuentes jurídicas analizadas en el caso.</p>
      </div>
      <span v-if="analyzed" class="strategy-status"><span aria-hidden="true"></span>Estrategia analizada</span>
    </header>

    <section v-if="executiveItems.length" class="strategy-overview" aria-label="Síntesis estratégica">
      <article v-if="strategySummary.main" class="overview-item strategy-main-card">
        <span>{{ strategySummary.main.label }}</span>
        <MarkdownRenderer citation-numbers-only :content="strategySummary.main.value" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" />
      </article>
      <div class="strategy-sidecards">
        <article v-if="strategySummary.objective" class="overview-item strategy-context-card objective-card">
          <span>{{ strategySummary.objective.label }}</span>
          <MarkdownRenderer citation-numbers-only :content="strategySummary.objective.value" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" />
        </article>
        <article v-if="strategySummary.condition" class="overview-item strategy-context-card key-condition-card">
          <span>{{ strategySummary.condition.label }}</span>
          <MarkdownRenderer citation-numbers-only :content="strategySummary.condition.value" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" />
        </article>
      </div>
    </section>

    <section v-if="objective" class="strategy-section objective-section" aria-labelledby="objective-title">
      <header class="section-heading"><p class="section-kicker">OBJETIVO DEL CASO</p><h3 id="objective-title">Objetivo jurídico</h3></header>
      <div class="objective-copy"><p class="field-label">Pretensión principal</p><MarkdownRenderer citation-numbers-only :content="objective" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /></div>
    </section>

    <section v-if="mainLine || strategyFoundations.length" class="strategy-section main-strategy" aria-labelledby="main-strategy-title">
      <header class="section-heading"><p class="section-kicker">LÍNEA DE ACTUACIÓN</p><h3 id="main-strategy-title">Estrategia principal</h3></header>
      <div v-if="mainLine" class="main-line"><p class="field-label">Pretensión y vía propuestas</p><MarkdownRenderer citation-numbers-only :content="mainLine" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /></div>
      <div v-if="strategyFoundations.length" class="foundation-list">
        <header class="foundation-heading"><p class="section-kicker">SUSTENTO JURÍDICO Y FÁCTICO</p><h4>Fundamentos de la estrategia</h4></header>
        <article v-for="(item,index) in strategyFoundations" :key="item.key" class="foundation-row">
          <span class="editorial-number" aria-hidden="true">{{ number(index + 1) }}</span>
          <div><h4 v-if="item.title">{{ item.title }}</h4><MarkdownRenderer citation-numbers-only v-if="item.body" :content="item.body" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" />
            <section v-if="item.legalBasis.length" class="foundation-detail"><h5>Fundamento jurídico</h5><MarkdownRenderer citation-numbers-only v-for="(text, basisIndex) in item.legalBasis" :key="`${item.key}-basis-${basisIndex}`" :content="text" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /></section>
            <section v-if="item.facts.length" class="foundation-detail"><h5>Hechos relacionados</h5><ul><li v-for="(fact,factIndex) in item.facts" :key="`${item.key}-fact-${factIndex}`"><MarkdownRenderer citation-numbers-only :content="fact" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /></li></ul></section>
            <div v-if="item.sources.length" class="source-list"><h5>Fuentes jurídicas</h5><ul><li v-for="source in item.sources" :key="source.source_id"><button v-if="citationLabel(source)" type="button" class="source-label novacase-citation-badge" :aria-label="`Ver fuente ${citationLabel(source).slice(1, -1)}`" @click="selectSource(source)">{{ citationLabel(source).slice(1, -1) }}</button><span v-else class="source-label">{{ sourceHumanLabel(source) }}</span><span v-if="citationLabel(source)" class="source-detail">{{ sourceHumanLabel(source) }}</span><button type="button" class="source-open" :aria-label="`Ver fuente ${citationLabel(source)?.replace(/[\[\]]/g, '') || sourceHumanLabel(source)}`" @click="selectSource(source)">Ver fuente <span aria-hidden="true">↗</span></button></li></ul></div>
          </div>
        </article>
      </div>
    </section>

    <section v-if="pendingItems.length" class="strategy-section" aria-labelledby="pending-title">
      <header class="section-heading"><p class="section-kicker">ANTES DE DEFINIR LA ACTUACIÓN</p><h3 id="pending-title">Información clave pendiente</h3><p>Documentación y elementos que deben incorporarse antes de consolidar la estrategia procesal.</p></header>
      <div class="editorial-list"><article v-for="(item,index) in pendingItems" :key="item.key" class="editorial-row"><span class="editorial-number" aria-hidden="true">{{ number(index + 1) }}</span><div><h4 v-if="item.title">{{ item.title }}</h4><MarkdownRenderer citation-numbers-only :content="item.body" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /></div></article></div>
    </section>

    <section v-if="opposingItems.length" class="strategy-section" aria-labelledby="opposing-title">
      <header class="section-heading"><p class="section-kicker">LECTURA ADVERSARIAL</p><h3 id="opposing-title">Objeciones previsibles</h3><p>Principales argumentos que podrían ser planteados contra la pretensión.</p></header>
      <ol class="editorial-list"><li v-for="(item,index) in opposingItems" :key="item.key" class="editorial-row"><span class="editorial-number" aria-hidden="true">{{ number(index + 1) }}</span><div><h4 v-if="item.title">{{ item.title }}</h4><MarkdownRenderer citation-numbers-only :content="item.body" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /><section v-if="item.response" class="strategic-response"><h5>Respuesta estratégica</h5><MarkdownRenderer citation-numbers-only :content="item.response" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /></section></div></li></ol>
    </section>

    <section v-if="priorityEvidence.length" class="strategy-section" aria-labelledby="evidence-title">
      <header class="section-heading"><p class="section-kicker">SUSTENTO PROBATORIO</p><h3 id="evidence-title">Evidencia prioritaria</h3><p>Elementos probatorios que pueden fortalecer o condicionar la estrategia propuesta.</p></header>
      <ol class="editorial-list"><li v-for="(item,index) in priorityEvidence" :key="item.key" class="editorial-row"><span class="editorial-number" aria-hidden="true">{{ number(index + 1) }}</span><div><h4 v-if="item.title">{{ item.title }}</h4><p v-if="item.relevance" class="field-label">Relevancia</p><MarkdownRenderer citation-numbers-only v-if="item.relevance" :content="item.relevance" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /><p v-if="item.status" class="evidence-status"><strong>Estado</strong> {{ item.status }}</p><MarkdownRenderer citation-numbers-only v-if="item.body" :content="item.body" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /><div v-if="item.sources.length" class="inline-source-actions"><button v-for="source in item.sources" :key="source.source_id" type="button" class="source-open" :aria-label="`Ver fuente ${citationLabel(source)?.replace(/[\[\]]/g, '') || sourceHumanLabel(source)}`" @click="selectSource(source)">{{ citationLabel(source) || sourceHumanLabel(source) }} · Ver fuente ↗</button></div></div></li></ol>
    </section>

    <section v-if="actionGroups.length" class="strategy-section" aria-labelledby="actions-title">
      <header class="section-heading"><p class="section-kicker">SECUENCIA DE PREPARACIÓN</p><h3 id="actions-title">Plan de actuación</h3><p>Acciones necesarias para preparar y ejecutar la estrategia jurídica.</p></header>
      <section v-for="group in actionGroups" :key="group.key" class="action-group"><h4 v-if="group.title">{{ group.title }}</h4><ol class="editorial-list"><li v-for="(item,index) in group.items" :key="item.key" class="editorial-row"><span class="editorial-number" aria-hidden="true">{{ number(index + 1) }}</span><div><MarkdownRenderer citation-numbers-only :content="item.body" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /></div></li></ol></section>
    </section>

    <section v-if="strategicRisks.length" class="strategy-section risk-section" aria-labelledby="risks-title">
      <header class="section-heading"><p class="section-kicker">CONTINGENCIAS DE EJECUCIÓN</p><h3 id="risks-title">Riesgos que condicionan la estrategia</h3><p>Aspectos que requieren preparación o mitigación dentro de la línea propuesta.</p></header>
      <ol class="editorial-list"><li v-for="(item,index) in strategicRisks" :key="item.key" class="editorial-row"><span class="editorial-number" aria-hidden="true">{{ number(index + 1) }}</span><div><h4 v-if="item.title">{{ item.title }}</h4><MarkdownRenderer citation-numbers-only :content="item.body" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /><section v-if="item.mitigation" class="strategic-response"><h5>Medida de mitigación</h5><MarkdownRenderer citation-numbers-only :content="item.mitigation" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /></section></div></li></ol>
    </section>

    <section v-if="strategicConclusion" class="strategy-conclusion" aria-labelledby="conclusion-title">
      <p class="section-kicker">SÍNTESIS ESTRATÉGICA</p><h3 id="conclusion-title">Conclusión estratégica</h3>
      <p v-if="diagnosis" class="field-label">Diagnóstico</p><MarkdownRenderer citation-numbers-only v-if="diagnosis" :content="diagnosis" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" />
      <p v-if="strategicConclusion.conditions.length" class="field-label">Condiciones para ejecutarla</p><ul v-if="strategicConclusion.conditions.length"><li v-for="(item,index) in strategicConclusion.conditions" :key="`condition-${index}`"><MarkdownRenderer citation-numbers-only :content="item" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /></li></ul>
      <div v-if="strategicConclusion.alternative" class="conclusion-alternative"><p class="field-label">Alternativa procesal</p><MarkdownRenderer citation-numbers-only :content="strategicConclusion.alternative" :citations="citations" :sources="safeSources" :case-id="caseId" @select-citation="openCitation" /></div>
    </section>

    <p v-if="!hasStrategyData" class="strategy-empty" role="status">No se identificó información suficiente para formular una estrategia.</p>
    <p v-if="hasStrategyData" class="strategy-disclaimer">La estrategia constituye una herramienta de apoyo al análisis jurídico y debe evaluarse considerando las circunstancias específicas del caso y el criterio profesional.</p>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import { presentableText, relatedFactTexts, verifiedArgumentSources, sourceHumanLabel, argumentCitationForSource } from '@/utils/novacasePresentation.js'
import { normalizeSource, normalizeSources } from '@/utils/sourceContract.js'

const props = defineProps({
  strategy: { type: Object, default: () => ({}) }, finalStrategy: { type: Object, default: () => ({}) },
  arguments: { type: Object, default: () => ({}) }, facts: { type: Array, default: () => [] },
  issues: { type: Array, default: () => [] }, evidence: { type: Object, default: () => ({}) },
  risks: { type: Object, default: () => ({}) }, counterArguments: { type: Object, default: () => ({}) },
  sources: { type: Array, default: () => [] }, citations: { type: Array, default: () => [] },
  caseId: { type: String, default: null }, analyzed: { type: Boolean, default: false }
})
const emit = defineEmits(['select-source'])
const safeSources = computed(() => normalizeSources(props.sources, props.caseId))

function list(value) { return Array.isArray(value) ? value : value == null || value === '' ? [] : [value] }
function clean(value) { return typeof value === 'string' ? presentableText(value).replace(/\s{2,}/g, ' ').trim() : '' }
function firstText(record, keys) {
  if (typeof record === 'string') return clean(record)
  if (!record || typeof record !== 'object' || Array.isArray(record)) return ''
  for (const key of keys) {
    const value = record[key]
    if (typeof value === 'string' && clean(value)) return clean(value)
    if (Array.isArray(value)) {
      const items = value.map(item => firstText(item, ['text','description','content','title','name'])).filter(Boolean)
      if (items.length) return items.join('\n\n')
    }
  }
  return ''
}
function titleOf(record, fallback = '') { return (typeof record === 'string' ? fallback : firstText(record, ['title','name','heading','document_title','display_title'])) || fallback }
function bodyOf(record) { return firstText(record, ['argument','principal_line','claim_strategy','risk','opposing_position','counterargument','objection','description','text','content','summary','what_it_supports','evidence','recommendation','action','query']) }
function keyOf(record, prefix, index, text) { return record?.argument_id || record?.risk_id || record?.evidence_id || `${prefix}-${index}-${text.slice(0,24)}` }
function numberedText(value, prefix) {
  return list(value).map((raw,index) => {
    const body = bodyOf(raw)
    if (!body || isTechnicalOnly(body)) return null
    const title = titleOf(raw)
    return { key:keyOf(raw,prefix,index,title || body), title, body, raw }
  }).filter(Boolean)
}
function isTechnicalOnly(value) { return /^(?:(?:ISSUE|SRC|FACT)-[a-f0-9]{12,}|[0-9a-f-]{36})$/i.test(value.trim()) }
function number(value) { return String(value).padStart(2,'0') }
function statusLabel(value) {
  const key=String(value || '').toLocaleLowerCase().trim()
  return ({supported:'Identificada', verified:'Verificada', available:'Disponible', alleged:'Pendiente de corroboración', missing:'Pendiente de incorporación', unavailable:'No disponible', recommended:'Recomendada', pending:'Pendiente de verificación', unknown:'No determinada', 'not identified':'No identificada', not_identified:'No identificada', 'pending verification':'Pendiente de verificación'})[key] || (/^[A-Z_ -]+$/.test(String(value || '')) ? '' : clean(value))
}
function categoryLabel(value) {
  const raw=clean(value)
  const key=raw.toLocaleLowerCase().replace(/[_-]+/g,' ').trim()
  const labels={documentation:'Documentación esencial',documents:'Documentación esencial',documental:'Documentación esencial',evidence:'Acreditación probatoria',evidentiary:'Acreditación probatoria',procedural:'Vía y plazos',deadlines:'Vía y plazos',strategy:'Preparación procesal'}
  if(labels[key]) return labels[key]
  const phase=key.match(/^phase\s+(\d+)$/)
  if(phase) return `Fase ${phase[1]}`
  if(/^(?:phase|category|group|objective|documentation|documents|evidence|procedural|strategy)\b/i.test(raw)) return ''
  return raw
}
function citationLabel(source) { return argumentCitationForSource(source,props.citations,safeSources.value,props.caseId)?.label || '' }
function sourceList(record) { return verifiedArgumentSources(record,safeSources.value,props.caseId,props.citations) }
function selectSource(value) { const source=normalizeSource(value,props.caseId); if(source) emit('select-source',source) }
function openCitation(citation) { const source=safeSources.value.find(item=>item.source_id===citation?.source_id); if(source) selectSource(source) }

const finalPlan = computed(() => props.finalStrategy || {})
const objective = computed(() => firstText(finalPlan.value,['objective']) || firstText(props.strategy,['objective','claim']) || firstText(props.issues?.[0],['objective','pretension_principal']))
const mainLine = computed(() => firstText(finalPlan.value,['principal_line','claim_strategy','strategy']) || firstText(props.strategy,['strategy','claim_strategy']))
const pendingItems = computed(() => numberedText(finalPlan.value.missing_information?.length ? finalPlan.value.missing_information : props.strategy.missing_information,'pending'))
const opposingItems = computed(() => numberedText(finalPlan.value.opposing_positions?.length ? finalPlan.value.opposing_positions : props.counterArguments.main_counterarguments,'opposing').map(item => ({...item,response:firstText(item.raw,['response','reply','answer'])})))
const priorityEvidence = computed(() => list(finalPlan.value.priority_evidence?.length ? finalPlan.value.priority_evidence : [...list(props.evidence.recommended_documents),...list(props.evidence.recommended_evidence)]).map((raw,index)=>{
  const title=titleOf(raw)
  const body=firstText(raw,['description','text','content','evidence'])
  const relevance=firstText(raw,['relevance','why_important','what_it_supports','probative_value'])
  if(!title && !body && !relevance) return null
  return {key:keyOf(raw,'priority-evidence',index,title || body || relevance),title,body,relevance,
    status:statusLabel(firstText(raw,['status','availability','state'])),sources:sourceList(raw)}
}).filter(Boolean))
const actionGroups = computed(() => {
  const inputs=[...list(finalPlan.value.recommended_actions),...list(props.strategy.recommended_actions || props.strategy.actions)]
  const seen=new Set(), groups=new Map()
  inputs.forEach((raw,index)=>{
    const body=bodyOf(raw), identity=body.toLocaleLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim()
    if(!body || isTechnicalOnly(body) || seen.has(identity)) return
    seen.add(identity)
    const title=categoryLabel(typeof raw === 'object' && raw !== null ? firstText(raw,['phase','category','group','objective']) : '')
    const key=title || 'actions'
    if(!groups.has(key)) groups.set(key,{key,title,items:[]})
    groups.get(key).items.push({key:`action-${index}`,body})
  })
  return [...groups.values()]
})
const strategicRisks = computed(() => numberedText(finalPlan.value.risks_to_mitigate?.length ? finalPlan.value.risks_to_mitigate : [...list(props.risks.critical_risks),...list(props.risks.procedural_risks)],'strategic-risk').slice(0,5).map(item=>({...item,mitigation:firstText(item.raw,['mitigation','recommendation','recommended_action'])})))
const strategyFoundations = computed(() => numberedText(finalPlan.value.supporting_arguments?.length ? finalPlan.value.supporting_arguments : props.arguments.main_arguments,'foundation').map(item=>{
  const record=item.raw || {}
  const legalBasis=list(record.legal_basis || record.foundation || record.legal_foundation).map(value=>bodyOf(value) || clean(value)).filter(Boolean)
  const facts=relatedFactTexts(record,props.facts).map(clean).filter(Boolean)
  return {...item,body:firstText(record,['argument','text','content','description']),legalBasis,facts,sources:sourceList(record)}
}).filter(item=>item.body || item.title || item.legalBasis.length || item.facts.length || item.sources.length))
const executiveItems = computed(() => [
  {label:'Objetivo',value:objective.value},
  {label:'Vía principal propuesta',value:mainLine.value},
  {label:'Condición clave',value:pendingItems.value[0]?.body}
].filter(item=>item.value))
const strategySummary = computed(() => ({
  main: executiveItems.value.find(item=>item.label==='Vía principal propuesta'),
  objective: executiveItems.value.find(item=>item.label==='Objetivo'),
  condition: executiveItems.value.find(item=>item.label==='Condición clave')
}))
const explicitConclusion = computed(()=>firstText(finalPlan.value,['strategic_conclusion','conclusion','summary']) || firstText(props.strategy,['strategic_conclusion','conclusion']))
const diagnosis = computed(()=>explicitConclusion.value || (objective.value && mainLine.value
  ? `La línea propuesta se orienta al objetivo jurídico identificado. ${pendingItems.value.length ? 'Su preparación queda sujeta a completar la información pendiente identificada.' : ''}`.trim()
  : ''))
const strategicConclusion = computed(()=>{
  const conditions=numberedText(finalPlan.value.execution_conditions || finalPlan.value.conditions || props.strategy.execution_conditions,'condition').map(item=>item.body)
  const alternative=firstText(finalPlan.value,['alternative_process','alternative_route']) || firstText(props.strategy,['alternative_strategy','alternative_route'])
  return diagnosis.value || conditions.length || alternative ? {conditions,alternative} : null
})
const hasStrategyData = computed(()=>Boolean(objective.value || mainLine.value || pendingItems.value.length || opposingItems.value.length || priorityEvidence.value.length || actionGroups.value.length || strategicRisks.value.length || strategyFoundations.value.length || strategicConclusion.value))
</script>

<style scoped>
.strategy-editorial{width:100%;max-width:1240px;min-width:0;margin:0 auto;display:grid;gap:clamp(36px,4vw,56px);color:#304357}
.strategy-header{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;padding-bottom:22px;border-bottom:1px solid #e2e8ef}
.strategy-eyebrow,.section-kicker{display:flex;align-items:center;gap:8px;margin:0 0 9px;color:#8a6a37;font-size:.62rem;font-weight:750;letter-spacing:.13em}
.strategy-eyebrow span{width:20px;height:1px;background:#b08a4c}
.strategy-header h2,.section-heading h3,.strategy-conclusion h3{margin:0;color:#17375e;font-family:Georgia,'Times New Roman',serif;font-weight:600}
.strategy-header h2{font-size:clamp(1.7rem,2.5vw,2.15rem);line-height:1.25}
.strategy-subtitle,.section-heading>p:last-child{max-width:840px;margin:8px 0 0;color:#69798a;font-size:.91rem;line-height:1.68}
.strategy-status{display:inline-flex;align-items:center;gap:8px;flex:none;padding:7px 11px;border:1px solid #dce7df;border-radius:999px;background:#f8fbf8;color:#55745d;font-size:.7rem;font-weight:650}
.strategy-status span{width:6px;height:6px;border-radius:50%;background:#72917a}
.strategy-overview{display:grid;grid-template-columns:minmax(0,2fr) minmax(280px,1fr);align-items:stretch;gap:18px}
.overview-item{min-width:0;padding:17px 19px;border:1px solid #e2e8ef;border-radius:8px;background:#fff}
.strategy-main-card{padding:22px 25px;border-left:3px solid #b08a4c;background:#fcfbf8}
.strategy-sidecards{display:grid;grid-template-rows:auto auto;align-content:start;gap:14px;min-width:0}
.strategy-context-card{padding:15px 17px;background:#fff}
.overview-item>span,.field-label{display:block;margin:0 0 7px;color:#8a6a37;font-size:.64rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}
.overview-item :deep(.markdown-body),.strategy-editorial :deep(.markdown-body){min-width:0;width:100%;color:#3d4e60;font-size:.91rem;line-height:1.75;word-break:normal;overflow-wrap:break-word}
.strategy-main-card :deep(.markdown-body){max-width:850px;font-size:.97rem;line-height:1.8}
.strategy-editorial :deep(.markdown-body p){margin:0 0 10px}.strategy-editorial :deep(.markdown-body p:last-child){margin-bottom:0}
.strategy-section{min-width:0}.section-heading{margin-bottom:18px}.section-heading h3,.strategy-conclusion h3{font-size:1.34rem;line-height:1.35}.section-heading>p:last-child{font-size:.84rem}
.objective-copy,.main-line{max-width:960px}.objective-copy{padding-left:17px;border-left:2px solid #b69a6a}.main-line{margin-bottom:24px;padding:18px 20px;border:1px solid #e4e9ed;border-left:3px solid #b08a4c;border-radius:8px;background:#fcfbf8}
.foundation-list,.editorial-list{margin:0;padding:0;list-style:none;border-top:1px solid #e4eaf0}.foundation-heading{padding:15px 0 4px}.foundation-heading .section-kicker{margin-bottom:5px}.foundation-heading h4{margin:0;color:#263d55;font:600 1rem/1.45 Georgia,'Times New Roman',serif}.foundation-row,.editorial-row{display:grid;grid-template-columns:38px minmax(0,1fr);gap:14px;min-width:0;padding:19px 0;border-bottom:1px solid #e4eaf0}
.editorial-number{padding-top:2px;color:#a17c43;font:600 .9rem Georgia,'Times New Roman',serif}.foundation-row>div,.editorial-row>div{min-width:0;max-width:960px}.foundation-row h4,.editorial-row h4,.action-group>h4{margin:0 0 8px;color:#263d55;font:600 1rem/1.45 Georgia,'Times New Roman',serif;overflow-wrap:break-word}
.foundation-detail,.source-list{margin-top:16px}.foundation-detail h5,.source-list h5,.strategic-response h5{margin:0 0 7px;color:#7d6845;font-size:.68rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}.foundation-detail ul,.strategy-conclusion ul{margin:0;padding-left:18px;color:#405469}.foundation-detail li,.strategy-conclusion li{padding:3px 0;line-height:1.65}
.source-list ul{margin:0;padding:0;list-style:none;border-top:1px solid #edf0f3}.source-list li{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:baseline;gap:4px 14px;padding:9px 0;border-bottom:1px solid #edf0f3}.source-label:not(.novacase-citation-badge){min-width:0;color:#315c83;font-size:.83rem;font-weight:650;overflow-wrap:break-word}.source-detail{grid-column:1;color:#7a8794;font-size:.75rem;line-height:1.5}.source-open{justify-self:end;padding:3px 5px;border:0;border-radius:4px;background:transparent;color:#315c83;font-family:inherit;font-size:.76rem;font-weight:600;line-height:1.5;white-space:nowrap;cursor:pointer}.source-open:hover{background:#edf3f7;color:#17375e}.source-open:focus-visible{outline:2px solid #b08a4c;outline-offset:2px}
.strategic-response{margin-top:15px;padding:12px 15px;border-left:2px solid #b69a6a;background:#faf8f2}.strategic-response h5{color:#806b49}.evidence-status{margin:10px 0 0;color:#607184;font-size:.83rem}.evidence-status strong{margin-right:7px;color:#718094;font-size:.68rem;letter-spacing:.06em;text-transform:uppercase}
.action-group+.action-group{margin-top:24px}.action-group>h4{color:#8a6a37;font-size:.7rem;letter-spacing:.08em;text-transform:uppercase}.action-group .editorial-row{padding-block:12px}
.risk-section .editorial-row{padding-block:15px}.strategy-conclusion{padding:22px clamp(18px,2.5vw,30px);border:1px solid #e6e1d7;border-left:3px solid #b08a4c;border-radius:8px;background:#fdfcf9}.strategy-conclusion h3{margin-bottom:17px}.strategy-conclusion ul{margin:0 0 15px}.conclusion-alternative{margin-top:14px;padding-top:12px;border-top:1px solid #e7e2d8}.strategy-disclaimer{margin:-22px 0 0;color:#758394;font-size:.75rem;line-height:1.6}.strategy-empty{margin:0;padding:14px 16px;border-left:2px solid #d4c29e;background:#faf9f5;color:#637286;font-size:.86rem;line-height:1.65}
@media(max-width:1359px){.strategy-overview{grid-template-columns:minmax(0,1fr)}.strategy-sidecards{grid-template-rows:auto auto}}
@media(max-width:680px){.strategy-editorial{gap:32px}.strategy-header{align-items:flex-start;flex-direction:column;gap:13px}.foundation-row,.editorial-row{grid-template-columns:30px minmax(0,1fr);gap:9px;padding:16px 0}.source-list li{grid-template-columns:minmax(0,1fr)}.source-open{justify-self:start}.main-line{padding:15px}.strategy-conclusion{padding:18px}}
</style>
