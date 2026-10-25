<template>
  <main class="court-decision" aria-labelledby="decision-title">
    <header class="decision-header">
      <div>
        <p class="decision-eyebrow"><span aria-hidden="true"></span> MYKE · NOVACOURT</p>
        <h2 id="decision-title">Decisión simulada</h2>
        <p>Evaluación razonada del escenario jurídico a partir de los hechos, argumentos, evidencia y fuentes verificadas del caso.</p>
      </div>
      <span v-if="simulation.status === 'ready'" class="decision-badge"><span aria-hidden="true">✓</span> Simulación completada</span>
    </header>

    <p class="decision-notice"><span aria-hidden="true">ⓘ</span> Simulación jurídica. No constituye una resolución judicial real ni sustituye la evaluación profesional.</p>
    <p v-if="simulation.status !== 'ready'" class="decision-state" role="status">{{ simulation.message || 'Decisión simulada no disponible.' }}</p>

    <template v-else>
      <section v-if="outcomeSummary" class="outcome-panel" aria-labelledby="outcome-title">
        <div><p class="section-kicker">RESULTADO DE LA SIMULACIÓN</p><h3 id="outcome-title">Resultado simulado</h3></div>
        <MarkdownRenderer :content="outcomeSummary" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
        <div v-if="conditionText" class="outcome-condition"><strong>Condición relevante</strong><MarkdownRenderer :content="conditionText" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></div>
      </section>

      <section v-if="sections.controversy.length" class="decision-section controversy-section" aria-labelledby="controversy-title">
        <header class="section-heading"><p class="section-kicker">CONTROVERSIA JURÍDICA</p><h3 id="controversy-title">Cuestión central sometida a evaluación</h3></header>
        <MarkdownRenderer v-for="(text,index) in sections.controversy" :key="`controversy-${index}`" :content="text" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
      </section>

      <section v-if="positions.length" class="positions-section" aria-labelledby="positions-considered-title">
        <header class="section-heading"><p class="section-kicker">CONTEXTO DE LA DECISIÓN</p><h3 id="positions-considered-title">Posiciones consideradas</h3></header>
        <div class="position-cards"><article v-for="position in positions" :key="position.key" :class="`position-${position.key}`"><p>{{ position.label }}</p><MarkdownRenderer :content="position.content" :citations="position.citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></article></div>
      </section>

      <section v-if="factItems.length" class="decision-section facts-section" aria-labelledby="facts-title">
        <header class="section-heading"><p class="section-kicker">HECHOS Y ANTECEDENTES</p><h3 id="facts-title">Hechos relevantes para la decisión</h3></header>
        <ol class="fact-list"><li v-for="(text,index) in factItems" :key="`fact-${index}`"><span aria-hidden="true">{{ number(index + 1) }}</span><MarkdownRenderer :content="text" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></li></ol>
      </section>

      <section v-if="sections.evidence.length" class="decision-section evidence-section" aria-labelledby="evidence-title">
        <header class="section-heading"><p class="section-kicker">VALORACIÓN PROBATORIA</p><h3 id="evidence-title">Documentación del caso y fuentes jurídicas</h3></header>
        <div class="evidence-copy"><MarkdownRenderer v-for="(text,index) in sections.evidence" :key="`evidence-${index}`" :content="text" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></div>
      </section>

      <section v-if="sections.grounds.length" class="decision-section grounds-section" aria-labelledby="grounds-title">
        <header class="section-heading"><p class="section-kicker">MARCO APLICABLE</p><h3 id="grounds-title">Fundamentos jurídicos</h3></header>
        <ol class="editorial-list"><li v-for="(item,index) in sections.grounds" :key="`ground-${index}`"><span aria-hidden="true">{{ number(index + 1) }}</span><div><h4 v-if="item.title">{{ item.title }}</h4><MarkdownRenderer :content="item.content" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></div></li></ol>
      </section>

      <section v-if="sections.reasoning.length" class="decision-section reasoning-section" aria-labelledby="reasoning-title">
        <header class="section-heading"><p class="section-kicker">ANÁLISIS DEL ESCENARIO</p><h3 id="reasoning-title">Razonamiento de la decisión</h3></header>
        <MarkdownRenderer v-for="(text,index) in sections.reasoning" :key="`reasoning-${index}`" :content="text" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
      </section>

      <section v-if="sections.limitations.length" class="limitations-panel" aria-labelledby="limitations-title">
        <header class="section-heading"><p class="section-kicker">ALCANCE DE LA EVALUACIÓN</p><h3 id="limitations-title">Condicionantes de la decisión</h3><p>El resultado simulado debe interpretarse considerando las siguientes limitaciones probatorias y procesales.</p></header>
        <ul><li v-for="(text,index) in sections.limitations" :key="`limitation-${index}`"><MarkdownRenderer :content="text" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></li></ul>
      </section>

      <section v-if="finalDecision.length" class="final-decision" aria-labelledby="final-decision-title">
        <p class="section-kicker">SÍNTESIS CONCLUSIVA</p><h3 id="final-decision-title">Decisión simulada</h3>
        <MarkdownRenderer v-for="(text,index) in finalDecision" :key="`decision-${index}`" :content="text" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
      </section>

      <section v-if="sections.recommendations.length" class="decision-section recommendations-section" aria-labelledby="recommendations-title">
        <header class="section-heading"><p class="section-kicker">ACTUACIONES POSTERIORES</p><h3 id="recommendations-title">Actuaciones recomendadas</h3></header>
        <ol class="fact-list"><li v-for="(text,index) in sections.recommendations" :key="`recommendation-${index}`"><span aria-hidden="true">{{ number(index + 1) }}</span><MarkdownRenderer :content="text" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></li></ol>
      </section>

      <section v-if="sourceGroups.private.length || sourceGroups.public.length" class="sources-section" aria-labelledby="decision-sources-title">
        <header class="section-heading"><p class="section-kicker">TRAZABILIDAD</p><h3 id="decision-sources-title">Fuentes utilizadas</h3></header>
        <div v-if="sourceGroups.private.length" class="source-group"><h4>Documentos del caso</h4><ul><li v-for="source in sourceGroups.private" :key="source.source_id"><span v-if="citationFor(source)" class="novacase-citation-badge">{{ citationFor(source).label.slice(1,-1) }}</span><span class="source-copy"><strong>{{ sourceTitle(source) }}</strong><small>{{ sourceDetails(source) }}</small></span><button type="button" @click="selectSource(source)">Ver documento <span aria-hidden="true">↗</span></button></li></ul></div>
        <div v-if="sourceGroups.public.length" class="source-group"><h4>Fuentes jurídicas consideradas</h4><p class="legal-source-note">Las fuentes jurídicas sustentan la interpretación normativa y no constituyen prueba de los hechos del caso.</p><ul><li v-for="source in sourceGroups.public" :key="source.source_id"><span v-if="citationFor(source)" class="novacase-citation-badge">{{ citationFor(source).label.slice(1,-1) }}</span><span class="source-copy"><strong>{{ sourceTitle(source) }}</strong><small>{{ sourceDetails(source) }}</small></span><button type="button" @click="selectSource(source)">Ver fuente <span aria-hidden="true">↗</span></button></li></ul></div>
      </section>
      <p v-if="!hasDecisionContent" class="decision-state" role="status">No se recibió contenido suficiente para mostrar la decisión simulada.</p>
    </template>

    <SourceModal :source="selectedSource" :case-id="caseId" @close="selectedSource = null" />
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import SourceModal from '@/components/common/SourceModal.vue'
import { argumentCitationForSource, presentableText } from '@/utils/novacasePresentation.js'
import { normalizeSources, resolveCitations } from '@/utils/sourceContract.js'

const props = defineProps({ simulation: { type: Object, default: () => ({}) }, caseId: { type: String, default: null } })
const simulation = computed(() => props.simulation || {})
const selectedSource = ref(null)
const judge = computed(() => simulation.value.judge || {})
const judicialAnalysis = computed(() => simulation.value.judicial_analysis || {})
const decisionData = computed(() => simulation.value.decision || {})
const rawContent = computed(() => judicialAnalysis.value.content || judge.value.content || decisionData.value.content || '')
const sourcesAll = computed(() => normalizeSources(simulation.value.sources, props.caseId))
const citationCandidates = computed(() => {
  const sections = [judge.value, judicialAnalysis.value, decisionData.value]
  const explicit = sections.flatMap(section => Array.isArray(section?.citations) ? section.citations : [])
  return [...new Map((explicit.length ? explicit : (simulation.value.citations || [])).filter(item => item?.citation_id).map(item => [item.citation_id, item])).values()]
})
const citations = computed(() => resolveCitations(citationCandidates.value, sourcesAll.value, props.caseId).citations)
const sources = computed(() => {
  const ids = new Set(citations.value.map(item => item.source_id))
  return sourcesAll.value.filter(source => ids.has(source.source_id))
})
const sections = computed(() => parseDecision(rawContent.value))
const positions = computed(() => {
  const provided = sections.value.positions.flatMap(parsePositionLine)
  const claimant = provided.find(item => item.key === 'claimant')?.content || positionSummary(simulation.value.prosecutor)
  const defendant = provided.find(item => item.key === 'defendant')?.content || positionSummary(simulation.value.defense)
  return [
    { key: 'claimant', label: 'PARTE DEMANDANTE', content: claimant, citations: simulation.value.prosecutor?.citations || citations.value },
    { key: 'defendant', label: 'PARTE DEMANDADA', content: defendant, citations: simulation.value.defense?.citations || citations.value }
  ].filter(item => item.content)
})
const factItems = computed(() => sections.value.facts.flatMap(splitBlocks))
const finalDecision = computed(() => sections.value.conclusion.length
  ? sections.value.conclusion
  : rawContent.value && !Object.values(sections.value).some(items => items.length) ? [rawContent.value] : [])
const outcomeSummary = computed(() => brief(finalDecision.value[0] || decisionData.value.outcome || judicialAnalysis.value.outcome || judge.value.outcome || ''))
const conditionText = computed(() => brief(decisionData.value.condition || judicialAnalysis.value.condition || judge.value.condition || sections.value.condition[0] || ''))
const sourceGroups = computed(() => ({
  private: sources.value.filter(source => ['case', 'private_case'].includes(source.source_scope)),
  public: sources.value.filter(source => source.source_scope === 'public_legal')
}))
const hasDecisionContent = computed(() => Boolean(rawContent.value || outcomeSummary.value || positions.value.length || sources.value.length))
function clean(value) { return typeof value === 'string' ? presentableText(value).replace(/\b(?:SRC|FACT|ISSUE)-[A-Z0-9_-]+\b/gi, '').replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, '').trim() : '' }
function textOf(value) {
  if (typeof value === 'string') return clean(value)
  if (value && typeof value === 'object') return clean(value.text || value.description || value.content || value.title || value.name || '')
  return ''
}
function splitBlocks(value) {
  return textOf(value).split(/\n\s*\n|\n(?=\s*(?:[-*•]|\d+[.)])\s+)/).map(item => item.replace(/^\s*(?:[-*•]|\d+[.)])\s+/gm, '').trim()).filter(Boolean)
}
function parsePositionLine(value) {
  const line = textOf(value)
  const match = line.match(/^\s*(?:[-*•]\s*)?(demandante|parte actora|claimant|demandada|parte demandada|defensa|defendant)\s*:\s*([\s\S]+)$/i)
  if (!match) return []
  return [{ key: /demandante|actora|claimant/i.test(match[1]) ? 'claimant' : 'defendant', content: match[2].trim() }]
}
function positionSummary(participant) {
  const content = clean(participant?.thesis || participant?.main_thesis || participant?.content || '')
  if (!content) return ''
  const paragraphs = content.split(/\n\s*\n/)
  const thesisIndex = paragraphs.findIndex(value => /tesis|teor[ií]a|posici[oó]n/i.test(value) && /demandante|demandada|defensa|parte actora/i.test(value))
  const selected = thesisIndex >= 0 ? paragraphs[thesisIndex + 1] || paragraphs[thesisIndex] : paragraphs[0]
  return summarizePosition(selected.replace(/^\s*#{1,5}\s*/gm, '').replace(/^\s*(?:tesis|teor[ií]a de la defensa|posici[oó]n)[^\n]*\n/i, ''))
}
function normalizeHeading(value) { return clean(value).replace(/^\s*(?:[IVXLCDM]+|\d+)[.)]\s*/i, '').replace(/^\s*#+\s*/, '').replace(/\*\*/g, '').replace(/[:：]\s*$/, '').trim() }
const sectionMap = [
  ['controversy', /identificaci[oó]n de la controversia|controversia jur[ií]dica|cuesti[oó]n central/i],
  ['positions', /posiciones consideradas|posiciones de las partes/i],
  ['facts', /hechos relevantes|hechos acreditados|hechos probados|hechos alegados|antecedentes f[aá]cticos/i],
  ['evidence', /valoraci[oó]n (?:de la )?(?:prueba|evidencia)|valoraci[oó]n probatoria|evidencia y fuentes/i],
  ['grounds', /fundamentos? jur[ií]dicos|fundamentos? normativos|marco jur[ií]dico/i],
  ['reasoning', /razonamiento|an[aá]lisis jur[ií]dico|consideraciones/i],
  ['limitations', /l[ií]mites|limitaciones|condicionantes/i],
  ['conclusion', /decisi[oó]n simulada|decisi[oó]n final|conclusi[oó]n|fallo simulado/i],
  ['recommendations', /actuaciones? recomendadas|recomendaciones|acciones recomendadas/i],
  ['condition', /condici[oó]n relevante/i],
  ['sources', /fuentes utilizadas|fuentes jur[ií]dicas|sources/i]
]
function parseDecision(content) {
  const result = { controversy: [], positions: [], facts: [], evidence: [], grounds: [], reasoning: [], limitations: [], conclusion: [], recommendations: [], condition: [], sources: [] }
  const text = clean(content)
  if (!text) return result
  let current = null, preamble = []
  for (const line of text.split(/\r?\n/)) {
    const heading = line.match(/^\s*(?:#{1,5}\s+|\*\*)(.+?)(?:\*\*)?\s*[:：]?\s*$/)
    const key = heading && sectionMap.find(([, pattern]) => pattern.test(normalizeHeading(heading[1])))?.[0]
    if (key) { current = key; continue }
    if (line.trim() && /^\s*(?:[IVXLCDM]+|\d+)[.)]\s+/.test(line)) {
      const named = sectionMap.find(([, pattern]) => pattern.test(normalizeHeading(line)))?.[0]
      if (named) { current = named; continue }
    }
    if (current && current !== 'sources') result[current].push(line)
    else if (!current) preamble.push(line)
  }
  if (preamble.some(line => line.trim()) && !Object.values(result).some(items => items.length)) result.reasoning = preamble
  for (const key of Object.keys(result)) result[key] = splitBlocks(result[key].join('\n'))
  result.grounds = groupGrounds(result.grounds)
  return result
}
function groupGrounds(values) {
  const joined = values.join('\n')
  return joined.split(/(?=^\s*#{2,5}\s+)/gm).map(block => {
    const lines = block.split(/\r?\n/).filter(line => line.trim())
    const heading = lines[0]?.match(/^\s*#{2,5}\s+(.+?)\s*$/)
    return heading
      ? { title: normalizeHeading(heading[1]), content: lines.slice(1).join('\n') }
      : { title: '', content: block.trim() }
  }).filter(item => item.title || item.content)
}
function brief(value) {
  return textOf(value).replace(/^\s*(?:conclusi[oó]n|resultado simulado)\s*[:：-]?\s*/i, '').replace(/^\s*#{1,5}\s*/gm, '').replace(/\*\*/g, '').replace(/\s+/g, ' ').trim()
}
function summarizePosition(value, maxLength = 380) {
  const text = brief(value)
  const sentences = text.match(/[^.!?]+(?:[.!?]+|$)/g)?.map(sentence => sentence.trim()).filter(Boolean) || []
  let summary = ''
  for (const sentence of sentences) {
    const next = summary ? `${summary} ${sentence}` : sentence
    if (summary && next.length > maxLength) break
    summary = next
    if (summary.length >= maxLength) break
  }
  return summary || text
}
function number(value) { return String(value).padStart(2, '0') }
function citationFor(source) { return argumentCitationForSource(source, citations.value, sources.value, props.caseId) }
function sourceTitle(source) { return clean(source.display_title || source.title || 'Fuente del caso').replace(/^\d+[_\s-]+/, '').replace(/\.[a-z0-9]{2,5}$/i, '').replace(/_/g, ' ').trim() }
function sourceDetails(source) {
  const label = ['case', 'private_case'].includes(source.source_scope) ? 'Documento aportado' : (source.court || source.issuer || 'Fuente jurídica')
  const unit = source.unit_type === 'foundation' ? `Fundamento ${source.unit_number || ''}`.trim() : source.unit_type === 'article' ? `Artículo ${source.unit_number || ''}`.trim() : ''
  const pages = source.page_start ? `pág. ${source.page_start}${source.page_end && source.page_end !== source.page_start ? `–${source.page_end}` : ''}` : ''
  return [label, unit, pages].filter(Boolean).join(' · ')
}
function openCitation(citation) { selectedSource.value = sources.value.find(source => source.source_id === citation?.source_id) || null }
function selectSource(source) { selectedSource.value = source }
</script>

<style scoped>
.court-decision{--navy:#17375e;--muted:#667789;--line:#dce5ee;--gold:#a98551;display:grid;gap:25px;width:100%;min-width:0;color:#34485d}.decision-header{display:flex;align-items:flex-start;justify-content:space-between;gap:22px;padding-bottom:20px;border-bottom:1px solid var(--line)}.decision-header>div{max-width:900px;min-width:0}.decision-eyebrow,.section-kicker{display:flex;align-items:center;gap:8px;margin:0 0 9px;color:#92713c;font-size:.66rem;font-weight:750;letter-spacing:.12em}.decision-eyebrow span{width:20px;height:1px;background:#b08a4c}.decision-header h2{margin:0;color:var(--navy);font:600 clamp(1.7rem,2.5vw,2.15rem)/1.25 Georgia,'Times New Roman',serif}.decision-header>div>p:last-child{max-width:78ch;margin:8px 0 0;color:var(--muted);font-size:.91rem;line-height:1.65}.decision-badge{display:inline-flex;align-items:center;gap:7px;flex:none;margin-top:4px;padding:7px 11px;border:1px solid #d9eade;border-radius:999px;background:#f1f8f3;color:#3b6d53;font-size:.72rem;font-weight:650}.decision-notice{display:flex;align-items:center;gap:8px;margin:-10px 0 0;color:#768391;font-size:.74rem;line-height:1.5}.decision-notice span{color:var(--gold)}.decision-state{margin:0;padding:14px 16px;border-left:2px solid var(--gold);background:#faf9f5;color:#637286;font-size:.87rem;line-height:1.6}
.section-heading{margin:0 0 13px}.section-kicker{margin-bottom:6px;font-size:.61rem}.section-heading h3,.final-decision h3{margin:0;color:var(--navy);font:600 1.22rem/1.35 Georgia,'Times New Roman',serif}.section-heading>p:last-child:not(.section-kicker){max-width:76ch;margin:7px 0 0;color:var(--muted);font-size:.84rem;line-height:1.6}.decision-section,.positions-section,.sources-section{min-width:0;padding-top:21px;border-top:1px solid var(--line)}.decision-section :deep(.markdown-body),.outcome-panel :deep(.markdown-body),.final-decision :deep(.markdown-body){color:#405469;font-size:.88rem;line-height:1.72;overflow-wrap:break-word}.decision-section :deep(p),.outcome-panel :deep(p),.final-decision :deep(p){margin:0 0 9px}.outcome-panel{display:grid;gap:12px;min-width:0;padding:20px 22px;border:1px solid #e2e8ed;border-left:3px solid var(--gold);border-radius:11px;background:#fbfaf6}.outcome-panel>div:first-child h3{margin:0;color:var(--navy);font:600 1.15rem Georgia,'Times New Roman',serif}.outcome-condition{display:grid;grid-template-columns:minmax(125px,180px) minmax(0,1fr);gap:12px;padding-top:12px;border-top:1px solid #e9e3d7}.outcome-condition>strong{color:#80683d;font-size:.67rem;letter-spacing:.06em;text-transform:uppercase}.positions-section .section-heading{margin-bottom:13px}.position-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}.position-cards article{min-width:0;padding:15px 17px;border:1px solid #dce5ee;border-radius:10px;background:#f5f8fb}.position-cards .position-defendant{border-color:#e8dfd1;background:#fbf8f2}.position-cards article>p{margin:0 0 7px;color:#55718a;font-size:.62rem;font-weight:750;letter-spacing:.1em}.position-cards .position-defendant>p{color:#92764c}.position-cards :deep(.markdown-body){color:#405469;font-size:.84rem;line-height:1.62;overflow-wrap:break-word}.fact-list,.editorial-list{display:grid;margin:0;padding:0;border-top:1px solid #e7ecf0;list-style:none}.fact-list li,.editorial-list li{display:grid;grid-template-columns:32px minmax(0,1fr);gap:10px;padding:11px 0;border-bottom:1px solid #e7ecf0}.fact-list li>span,.editorial-list li>span{color:var(--gold);font:600 .84rem Georgia,serif}.fact-list :deep(.markdown-body),.editorial-list :deep(.markdown-body){color:#405469;font-size:.87rem;line-height:1.68;overflow-wrap:break-word}.editorial-list h4{margin:0 0 6px;color:#314b63;font:600 .97rem Georgia,serif}.limitations-panel{min-width:0;padding:18px 20px;border:1px solid #e9dfcc;border-left:3px solid #bc9b62;border-radius:10px;background:#fcfaf5}.limitations-panel ul{display:grid;gap:8px;margin:0;padding-left:18px;color:#5d5548;font-size:.86rem;line-height:1.65}.limitations-panel li::marker{color:#a98551}.final-decision{min-width:0;padding:20px 22px;border:1px solid #e8e2d6;border-top:3px solid #b08a4c;border-radius:10px;background:#fcfbf8}.final-decision h3{margin-bottom:12px;font-size:1.35rem}.recommendations-section{padding-bottom:2px}.source-group+.source-group{margin-top:20px}.source-group h4{margin:0 0 7px;color:#52697f;font-size:.69rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}.legal-source-note{margin:0 0 10px;color:#718092;font-size:.76rem;line-height:1.55}.source-group ul{display:grid;margin:0;padding:0;border-top:1px solid #e5ebf0;list-style:none}.source-group li{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:12px;padding:11px 5px;border-bottom:1px solid #e8edf1}.novacase-citation-badge{display:inline-flex;flex:none;align-items:center;justify-content:center;width:max-content;min-width:22px;height:22px;padding:0 6px;border:0;border-radius:6px;background:#102b4c;color:#fff;font-size:.72rem;font-weight:750;line-height:1;white-space:nowrap}.source-copy{display:grid;min-width:0;gap:3px}.source-copy strong{color:#314a62;font-size:.85rem;font-weight:650;overflow-wrap:anywhere}.source-copy small{color:#758495;font-size:.73rem}.source-group button{display:inline-flex;align-items:center;gap:5px;padding:5px 0;border:0;background:none;color:#315c83;font-size:.77rem;font-weight:650;white-space:nowrap;cursor:pointer}.source-group button:hover{text-decoration:underline;text-underline-offset:3px}.source-group button:focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:3px}.court-decision :deep(.citation-inline){display:inline-flex;align-items:center;justify-content:center;vertical-align:baseline;min-width:22px;height:22px;padding:0 6px;border:0;border-radius:6px;background:#102b4c;color:#fff;font-size:.72rem;font-weight:750;line-height:1;white-space:nowrap;cursor:pointer}.court-decision :deep(.citation-inline:hover){background:#1d4168}.court-decision :deep(.citation-inline:focus-visible){outline:2px solid var(--gold);outline-offset:2px}
@media(max-width:760px){.court-decision{gap:21px}.decision-header{flex-direction:column;gap:12px}.position-cards{grid-template-columns:minmax(0,1fr)}.outcome-condition{grid-template-columns:minmax(0,1fr);gap:5px}.fact-list li,.editorial-list li{grid-template-columns:26px minmax(0,1fr);gap:8px}.source-group li{grid-template-columns:auto minmax(0,1fr);gap:9px}.source-group button{grid-column:2;justify-self:start}}
</style>
