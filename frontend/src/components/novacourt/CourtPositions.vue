<template>
  <main class="court-positions" aria-labelledby="positions-title">
    <header class="positions-header">
      <div>
        <p class="positions-eyebrow"><span aria-hidden="true"></span> MYKE · NOVACOURT</p>
        <h2 id="positions-title">Posiciones de las partes</h2>
        <p>Contraste estructurado de las tesis, fundamentos, pruebas y vulnerabilidades de las partes dentro del escenario simulado.</p>
      </div>
      <span v-if="simulation.status === 'ready'" class="simulation-badge"><span aria-hidden="true">✓</span> Simulación completada</span>
    </header>

    <p class="simulation-notice"><span aria-hidden="true">ⓘ</span> Simulación jurídica. No constituye una resolución judicial real.</p>
    <p v-if="simulation.status !== 'ready'" class="positions-state" role="status">{{ simulation.message || 'Simulación no disponible. El análisis del caso permanece disponible.' }}</p>

    <template v-else>
      <section v-if="participants.length" class="position-summaries" aria-label="Síntesis comparativa de posiciones">
        <article v-for="party in participants" :key="party.key" class="position-summary" :class="`party-${party.key}`">
          <p class="party-label">{{ party.label }}</p>
          <h3>{{ party.key === 'claimant' ? 'Tesis de la parte demandante' : 'Tesis de la parte demandada' }}</h3>
          <p>{{ party.preview || 'No se proporcionó una síntesis de esta posición.' }}</p>
        </article>
      </section>

      <section v-for="party in participants" :key="`position-${party.key}`" class="party-section" :class="`party-section--${party.key}`" :aria-labelledby="`party-title-${party.key}`">
        <header class="party-heading"><span class="party-marker" aria-hidden="true">{{ party.key === 'claimant' ? 'D' : 'd' }}</span><div><p class="section-kicker">{{ party.label }}</p><h3 :id="`party-title-${party.key}`">{{ party.title }}</h3></div></header>

        <section v-if="party.sections.thesis.length" class="party-subsection thesis-section">
          <h4>Tesis principal</h4><MarkdownRenderer v-for="(text, index) in party.sections.thesis" :key="`${party.key}-thesis-${index}`" :content="text" :citations="party.citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
        </section>
        <section v-if="party.sections.facts.length" class="party-subsection">
          <h4>Hechos que sustentan esta posición</h4><ol class="position-fact-list"><li v-for="(text, index) in party.sections.facts" :key="`${party.key}-fact-${index}`"><span aria-hidden="true">{{ number(index + 1) }}</span><MarkdownRenderer :content="text" :citations="party.citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></li></ol>
        </section>
        <section v-if="party.sections.evidence.length" class="party-subsection">
          <h4>Evidencia disponible</h4><div class="party-prose"><MarkdownRenderer v-for="(text, index) in party.sections.evidence" :key="`${party.key}-evidence-${index}`" :content="text" :citations="party.citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></div>
        </section>
        <section v-if="party.sections.grounds.length" class="party-subsection">
          <h4>Fundamentos jurídicos</h4><ol class="grounds-list"><li v-for="(item, index) in party.sections.grounds" :key="`${party.key}-ground-${index}`"><span aria-hidden="true">{{ number(index + 1) }}</span><div><h5 v-if="item.title">{{ item.title }}</h5><MarkdownRenderer :content="item.content" :citations="party.citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></div></li></ol>
        </section>
        <section v-if="party.sections.recommended.length" class="party-subsection recommended-section">
          <h4>Evidencia que fortalecería esta posición</h4><ul class="simple-list"><li v-for="(text, index) in party.sections.recommended" :key="`${party.key}-recommended-${index}`"><MarkdownRenderer :content="text" :citations="party.citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></li></ul>
        </section>
        <section v-if="party.sections.vulnerabilities.length" class="party-subsection vulnerability-section">
          <h4>Vulnerabilidades de la posición</h4><ul class="simple-list"><li v-for="(text, index) in party.sections.vulnerabilities" :key="`${party.key}-vulnerability-${index}`"><MarkdownRenderer :content="text" :citations="party.citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></li></ul>
        </section>
        <section v-if="party.sections.conclusion.length" class="party-subsection conclusion-section">
          <h4>Conclusión de la posición</h4><MarkdownRenderer v-for="(text, index) in party.sections.conclusion" :key="`${party.key}-conclusion-${index}`" :content="text" :citations="party.citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
        </section>
        <section v-if="party.sections.other.length" class="party-subsection other-section">
          <h4>Desarrollo complementario</h4><MarkdownRenderer v-for="(text, index) in party.sections.other" :key="`${party.key}-other-${index}`" :content="text" :citations="party.citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" />
        </section>
      </section>

      <section v-if="comparisonRows.length" class="comparison-section" aria-labelledby="comparison-title">
        <header class="section-heading"><p class="section-kicker">LECTURA COMPARADA</p><h3 id="comparison-title">Contraste de posiciones</h3></header>
        <div class="comparison-table-wrap"><table><thead><tr><th scope="col">Aspecto</th><th scope="col">Demandante</th><th scope="col">Demandada</th></tr></thead><tbody><tr v-for="row in comparisonRows" :key="row.key"><th scope="row">{{ row.label }}</th><td><MarkdownRenderer :content="row.claimant" :citations="participants[0]?.citations || []" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></td><td><MarkdownRenderer :content="row.defendant" :citations="participants[1]?.citations || []" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></td></tr></tbody></table></div>
      </section>

      <section v-if="controversies.length" class="controversy-section" aria-labelledby="controversy-title">
        <header class="section-heading"><p class="section-kicker">CUESTIONES EN DEBATE</p><h3 id="controversy-title">Puntos centrales de controversia</h3></header>
        <ol class="position-fact-list"><li v-for="(item, index) in controversies" :key="`controversy-${index}`"><span aria-hidden="true">{{ number(index + 1) }}</span><MarkdownRenderer :content="item" :citations="citations" :sources="sources" :case-id="caseId" citation-numbers-only @select-citation="openCitation" /></li></ol>
      </section>

      <section v-if="sourceGroups.private.length || sourceGroups.public.length" class="sources-section" aria-labelledby="positions-sources-title">
        <header class="section-heading"><p class="section-kicker">RESPALDO DE LA SIMULACIÓN</p><h3 id="positions-sources-title">Fuentes utilizadas</h3></header>
        <div v-if="sourceGroups.private.length" class="source-group"><h4>Documentos del caso</h4><ul><li v-for="source in sourceGroups.private" :key="source.source_id"><span v-if="citationFor(source)" class="novacase-citation-badge">{{ citationFor(source).label.slice(1,-1) }}</span><span class="source-copy"><strong>{{ sourceTitle(source) }}</strong><small>{{ sourceDetails(source) }}</small></span><button type="button" @click="selectSource(source)">Ver documento <span aria-hidden="true">↗</span></button></li></ul></div>
        <div v-if="sourceGroups.public.length" class="source-group"><h4>Fuentes jurídicas</h4><ul><li v-for="source in sourceGroups.public" :key="source.source_id"><span v-if="citationFor(source)" class="novacase-citation-badge">{{ citationFor(source).label.slice(1,-1) }}</span><span class="source-copy"><strong>{{ sourceTitle(source) }}</strong><small>{{ sourceDetails(source) }}</small></span><button type="button" @click="selectSource(source)">Ver fuente <span aria-hidden="true">↗</span></button></li></ul></div>
      </section>
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
const rawSources = computed(() => normalizeSources(simulation.value.sources, props.caseId))
const citations = computed(() => {
  const sections = [simulation.value.prosecutor, simulation.value.defense]
  const sectionCitations = sections.flatMap(section => Array.isArray(section?.citations) ? section.citations : [])
  const candidates = sections.some(section => Array.isArray(section?.citations)) ? sectionCitations : (simulation.value.citations || [])
  return resolveCitations([...new Map(candidates.filter(item => item?.citation_id).map(item => [item.citation_id, item])).values()], rawSources.value, props.caseId).citations
})
const sources = computed(() => {
  const used = new Set(citations.value.map(item => item.source_id))
  return rawSources.value.filter(source => used.has(source.source_id))
})
const participantSpecs = [
  { key: 'claimant', source: 'prosecutor', label: 'PARTE DEMANDANTE', title: 'Parte demandante' },
  { key: 'defendant', source: 'defense', label: 'PARTE DEMANDADA', title: 'Parte demandada' }
]
const participants = computed(() => participantSpecs.map(spec => {
  const data = simulation.value[spec.source] || {}
  const partyCitations = Array.isArray(data.citations) ? resolveCitations(data.citations, rawSources.value, props.caseId).citations : citations.value
  const sections = parsePosition(data.content || '')
  const useExplicit = (key, fields) => {
    const value = fields.map(field => data[field]).find(value => value != null && value !== '')
    return value == null ? sections[key] : records(value).map(textOf).filter(Boolean)
  }
  const assembled = {
    thesis: useExplicit('thesis', ['thesis', 'main_thesis', 'position', 'argument']),
    facts: useExplicit('facts', ['facts', 'relevant_facts']),
    evidence: useExplicit('evidence', ['available_evidence', 'evidence']),
    grounds: useExplicit('grounds', ['legal_grounds', 'legal_basis']).map(parseGround),
    recommended: useExplicit('recommended', ['recommended_evidence', 'evidence_to_strengthen']),
    vulnerabilities: useExplicit('vulnerabilities', ['vulnerabilities', 'limitations', 'weaknesses']),
    conclusion: useExplicit('conclusion', ['conclusion', 'summary']),
    other: sections.other
  }
  return { ...spec, citations: partyCitations, sections: assembled, preview: preview(assembled.thesis[0] || textOf(data.content)) }
}).filter(party => party.sections.thesis.length || Object.values(party.sections).some(value => Array.isArray(value) && value.length)))
const comparisonRows = computed(() => {
  const left = participants.value[0], right = participants.value[1]
  if (!left || !right) return []
  const row = (key, label, claimant, defendant) => {
    const leftText = briefComparison(claimant), rightText = briefComparison(defendant)
    return leftText && rightText ? { key, label, claimant: leftText, defendant: rightText } : null
  }
  const allItems = party => [
    ...party.sections.grounds,
    ...party.sections.other.map(parseGround)
  ].filter(item => item.title && item.content)
  const topicRow = definition => {
    const claimant = allItems(left).find(item => definition.pattern.test(item.title))
    const defendant = allItems(right).find(item => definition.pattern.test(item.title))
    return row(definition.key, definition.label, claimant?.content, defendant?.content)
  }
  const legalGround = party => party.sections.grounds.find(item => briefComparison(item.content))?.content
  const evidence = party => party.sections.evidence.find(briefComparison)
  const vulnerability = party => party.sections.vulnerabilities.find(briefComparison)
  return [
    row('main-thesis', 'Tesis principal', left.sections.thesis[0], right.sections.thesis[0]),
    topicRow(comparisonDefinitions[0]),
    topicRow(comparisonDefinitions[1]),
    row('legal-ground', 'Fundamento jurídico principal', legalGround(left), legalGround(right)),
    row('main-evidence', 'Evidencia o respaldo principal', evidence(left), evidence(right)),
    row('main-vulnerability', 'Principal vulnerabilidad', vulnerability(left), vulnerability(right))
  ].filter(Boolean).slice(0, 6)
})
const controversies = computed(() => records(simulation.value.controversies || simulation.value.central_controversies || simulation.value.disputed_issues).map(textOf).filter(Boolean))
const sourceGroups = computed(() => ({
  private: sources.value.filter(source => ['case', 'private_case'].includes(source.source_scope)),
  public: sources.value.filter(source => source.source_scope === 'public_legal')
}))
const comparisonDefinitions = [
  { key: 'cas-nature', label: 'Naturaleza del vínculo / controversia central', pattern: /naturaleza|controversia central|v[ií]nculo/i },
  { key: 'nonrenewal', label: 'Motivación de la no renovación', pattern: /motivaci[oó]n.*no renovaci[oó]n|no renovaci[oó]n.*motivaci[oó]n/i }
]
function records(value) { return Array.isArray(value) ? value : value == null || value === '' ? [] : [value] }
function clean(value) { return typeof value === 'string' ? presentableText(value).replace(/\b(?:SRC|FACT|ISSUE)-[A-Z0-9_-]+\b/gi, '').replace(/\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, '').trim() : '' }
function textOf(value) {
  if (typeof value === 'string') return clean(value)
  if (value && typeof value === 'object') return clean(value.text || value.description || value.content || value.fact || value.evidence || value.title || value.name || '')
  return ''
}
function parseGround(value) {
  if (value && typeof value === 'object') return { title: clean(value.title || value.name || ''), content: textOf(value.text || value.description || value.content || value.argument || '') }
  const text = textOf(value)
  const lines = text.split(/\r?\n/).filter(Boolean)
  return lines.length > 1 ? { title: lines[0].replace(/^\s*#+\s*|\*\*/g, '').replace(/\*\*/g, '').replace(/:$/, ''), content: lines.slice(1).join('\n') } : { title: '', content: text }
}
const sectionDefinitions = [
  { key: 'thesis', pattern: /^(?:tesis(?: principal)?(?: de la parte (?:demandante|demandada))?|teor[ií]a de la defensa(?: de la parte demandada)?|pretensi[oó]n|posici[oó]n principal|argumento principal|principal thesis|main argument)$/i },
  { key: 'facts', pattern: /^(?:hechos(?: relevantes| que sustentan(?: esta posici[oó]n)?)?|facts(?: supporting.*)?|antecedentes f[aá]cticos)$/i },
  { key: 'evidence', pattern: /^(?:evidencia disponible|evidencia o respaldo principal|prueba(?: disponible)?|evidence(?: available)?|evidencia aportada)$/i },
  { key: 'grounds', pattern: /^(?:fundamentos? jur[ií]dicos?(?: principal)?|fundamento legal|legal grounds?|legal basis|argumentos? jur[ií]dicos?)$/i },
  { key: 'recommended', pattern: /^(?:prueba recomendada|evidencia recomendada|evidencia que fortalecer[ií]a(?: esta posici[oó]n)?|recommended evidence|evidence to strengthen)$/i },
  { key: 'vulnerabilities', pattern: /^(?:limitaciones|principal vulnerabilidad|vulnerabilidades?(?: de la posici[oó]n)?|weaknesses|limitations)$/i },
  { key: 'conclusion', pattern: /^(?:conclusi[oó]n(?: de la posici[oó]n)?|s[ií]ntesis|conclusion)$/i },
  { key: 'sources', pattern: /^(?:fuentes(?: utilizadas)?|sources(?: used)?)$/i }
]
function parsePosition(content) {
  const output = { thesis: [], facts: [], evidence: [], grounds: [], recommended: [], vulnerabilities: [], conclusion: [], other: [] }
  const allText = clean(content)
  if (!allText) return output
  let current = null, preamble = []
  for (const line of allText.split(/\r?\n/)) {
    const markdownHeading = line.match(/^\s*(#{1,5})\s+(.+?)\s*$/)
    const boldLabel = line.match(/^\s*\*\*([^*]+)\*\*\s*:?[ \t]*(.*)$/)
    const plainLabel = line.match(/^\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ][^:\n]{2,55}):\s*(.*)$/)
    const heading = markdownHeading ? [line, markdownHeading[2], ''] : (boldLabel || plainLabel)
    const label = heading?.[1]?.replace(/\*\*/g, '').replace(/[:：]\s*$/, '').trim()
    const section = label && sectionDefinitions.find(item => item.pattern.test(label))
    if (section?.key === 'sources') { current = null; continue }
    if (section) {
      current = section.key
      if (heading[2]?.trim()) output[current].push(heading[2].trim())
      continue
    }
    if (markdownHeading && (markdownHeading[1].length <= 2 || !current)) {
      current = 'other'
      output.other.push(line)
      continue
    }
    if (current) output[current].push(line)
    else preamble.push(line)
  }
  if (!output.thesis.length && preamble.join('\n').trim()) output.thesis.push(preamble.join('\n').trim())
  for (const key of Object.keys(output)) {
    const joined = output[key].map(text => text.trim()).filter(Boolean).join('\n')
    const blocks = ['grounds', 'other'].includes(key)
      ? joined.split(/\n(?=\s*(?:#{2,5}\s+|\*\*[^*]+\*\*))/)
      : joined.split(/\n\s*\n|\n(?=\s*(?:[-*•]|\d+[.)])\s+)/)
    output[key] = blocks.map(text => text.replace(/^\s*(?:[-*•]|\d+[.)])\s+/gm, '').trim()).filter(Boolean)
  }
  output.grounds = output.grounds.map(parseGround)
  return output
}
function preview(value) {
  const text = clean(value).replace(/^#{1,6}\s*/gm, '').replace(/\*\*/g, '').replace(/[*_`]/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/\[\d+\]/g, '').replace(/^\s*(?:[-*•]|\d+[.)])\s+/gm, '').replace(/\s+/g, ' ').trim()
  if (text.length <= 210) return text
  const cut = text.slice(0, 207).replace(/\s+\S*$/, '')
  return `${cut}…`
}
function briefComparison(value) {
  const text = textOf(value)
    .replace(/^\s*(?:tesis(?: principal)? de la parte demandante|tesis(?: principal)? de la parte demandada|teor[ií]a de la defensa de la parte demandada|teor[ií]a de la defensa|tesis principal|fundamento jur[ií]dico principal|evidencia o respaldo principal|principal vulnerabilidad)\s*[:：-]?\s*/i, '')
    .replace(/^\s*#{1,5}\s*[^\n]+\n?/gm, '')
    .replace(/^\s*\*\*[^*]+\*\*\s*[:：]?\s*$/gm, '')
    .replace(/^\s*(?:[-*•]|\d+[.)])\s+/gm, '')
    .trim()
  if (!text || /^(?:tesis(?: de la parte demandante| de la parte demandada)?|teor[ií]a de la defensa(?: de la parte demandada)?|fundamento jur[ií]dico principal|evidencia o respaldo principal|principal vulnerabilidad)\s*[:：]?$/i.test(text)) return ''
  if (text.length <= 280) return text
  return `${text.slice(0, 277).replace(/\s+\S*$/, '')}…`
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
.court-positions{--navy:#17375e;--muted:#667789;--line:#dce5ee;--gold:#a98551;display:grid;gap:26px;width:100%;min-width:0;color:#34485d}.positions-header{display:flex;align-items:flex-start;justify-content:space-between;gap:22px;padding-bottom:20px;border-bottom:1px solid var(--line)}.positions-header>div{max-width:900px;min-width:0}.positions-eyebrow,.section-kicker{display:flex;align-items:center;gap:8px;margin:0 0 9px;color:#92713c;font-size:.66rem;font-weight:750;letter-spacing:.12em}.positions-eyebrow span{width:20px;height:1px;background:#b08a4c}.positions-header h2{margin:0;color:var(--navy);font:600 clamp(1.7rem,2.5vw,2.15rem)/1.25 Georgia,'Times New Roman',serif}.positions-header>div>p:last-child{max-width:78ch;margin:8px 0 0;color:var(--muted);font-size:.91rem;line-height:1.65}.simulation-badge{display:inline-flex;align-items:center;gap:7px;flex:none;margin-top:4px;padding:7px 11px;border:1px solid #d9eade;border-radius:999px;background:#f1f8f3;color:#3b6d53;font-size:.72rem;font-weight:650}.simulation-notice{display:flex;align-items:center;gap:8px;margin:-10px 0 0;color:#768391;font-size:.74rem;line-height:1.5}.simulation-notice span{color:#a98551}.positions-state{margin:0;padding:14px 16px;border-left:2px solid var(--gold);background:#faf9f5;color:#637286;font-size:.87rem;line-height:1.6}
.position-summaries{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}.position-summary{min-width:0;padding:19px 21px;border:1px solid #dce5ee;border-radius:12px;background:#f5f8fb}.position-summary.party-defendant{border-color:#e8dfd1;background:#fbf8f2}.party-label{margin:0 0 7px;color:#55718a;font-size:.62rem;font-weight:750;letter-spacing:.11em}.party-defendant .party-label{color:#92764c}.position-summary h3{margin:0;color:var(--navy);font:600 1.08rem Georgia,'Times New Roman',serif}.position-summary>p:last-child{margin:8px 0 0;color:#506378;font-size:.86rem;line-height:1.65;overflow-wrap:break-word}.party-section{min-width:0;padding-top:23px;border-top:1px solid var(--line)}.party-heading{display:flex;align-items:center;gap:12px;margin-bottom:18px}.party-marker{display:grid;place-items:center;flex:none;width:34px;height:34px;border:1px solid #dce5ee;border-radius:10px;background:#edf3f8;color:#365d7c;font:700 1rem Georgia,serif}.party-section--defendant .party-marker{border-color:#e7ddce;background:#f5efe4;color:#8c7046}.party-heading .section-kicker{margin:0 0 4px}.party-heading h3{margin:0;color:var(--navy);font:600 1.28rem/1.3 Georgia,'Times New Roman',serif}.party-subsection{min-width:0;margin-left:46px;padding:17px 0;border-top:1px solid #e8edf1}.party-subsection h4,.source-group h4{margin:0 0 10px;color:#52697f;font-size:.69rem;font-weight:750;letter-spacing:.08em;text-transform:uppercase}.thesis-section{padding-top:4px;border-top:0}.party-prose,.party-subsection :deep(p){color:#405469;font-size:.89rem;line-height:1.72;overflow-wrap:break-word}.party-subsection :deep(p){margin:0 0 8px}.position-fact-list,.grounds-list,.simple-list{display:grid;margin:0;padding:0;list-style:none}.position-fact-list li,.grounds-list li{display:grid;grid-template-columns:30px minmax(0,1fr);gap:10px;padding:10px 0;border-top:1px solid #edf0f2}.position-fact-list li:first-child,.grounds-list li:first-child{border-top:0;padding-top:0}.position-fact-list li>span,.grounds-list li>span{color:var(--gold);font:600 .82rem Georgia,serif}.grounds-list li>div{min-width:0}.grounds-list h5{margin:0 0 5px;color:#334c64;font:600 .92rem Georgia,serif}.simple-list{gap:6px}.simple-list li{position:relative;padding-left:16px;color:#405469;font-size:.86rem;line-height:1.65}.simple-list li::before{position:absolute;left:0;top:.7em;width:5px;height:5px;border-radius:50%;background:#a98551;content:''}.recommended-section{padding-left:13px;border-left:2px solid #dce8df}.vulnerability-section{padding:13px 15px;border:1px solid #eadfcf;border-radius:9px;background:#fcf9f4}.vulnerability-section h4{color:#8b7048}.conclusion-section{margin-top:5px;padding:14px 16px;border-left:2px solid #b08a4c;background:#faf8f2}.other-section{color:#405469}
.section-heading{margin:0 0 13px}.section-heading .section-kicker{margin-bottom:6px}.section-heading h3{margin:0;color:var(--navy);font:600 1.23rem/1.35 Georgia,'Times New Roman',serif}.comparison-section,.controversy-section,.sources-section{min-width:0;padding-top:22px;border-top:1px solid var(--line)}.comparison-table-wrap{overflow-x:auto;border:1px solid #e1e8ee;border-radius:10px}.comparison-table-wrap table{width:100%;border-collapse:collapse}.comparison-table-wrap th,.comparison-table-wrap td{padding:12px 14px;border-bottom:1px solid #e7ecf0;text-align:left;vertical-align:top;font-size:.82rem;line-height:1.6}.comparison-table-wrap thead th{background:#f4f7f9;color:#465d72;font-size:.67rem;letter-spacing:.06em;text-transform:uppercase}.comparison-table-wrap tbody th{width:22%;color:#314c65;font-weight:650}.comparison-table-wrap tbody td{color:#526579}.source-group+.source-group{margin-top:20px}.source-group ul{display:grid;margin:0;padding:0;border-top:1px solid #e5ebf0;list-style:none}.source-group li{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:12px;padding:11px 5px;border-bottom:1px solid #e8edf1}.novacase-citation-badge{display:inline-flex;flex:none;align-items:center;justify-content:center;width:max-content;min-width:22px;height:22px;padding:0 6px;border:0;border-radius:6px;background:#102b4c;color:#fff;font-size:.72rem;font-weight:750;line-height:1;white-space:nowrap}.source-copy{display:grid;min-width:0;gap:3px}.source-copy strong{color:#314a62;font-size:.85rem;font-weight:650;overflow-wrap:anywhere}.source-copy small{color:#758495;font-size:.73rem}.source-group button{display:inline-flex;align-items:center;gap:5px;padding:5px 0;border:0;background:none;color:#315c83;font-size:.77rem;font-weight:650;white-space:nowrap;cursor:pointer}.source-group button:hover{text-decoration:underline;text-underline-offset:3px}.source-group button:focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:3px}
.court-positions :deep(.citation-inline){display:inline-flex;align-items:center;justify-content:center;vertical-align:baseline;min-width:22px;height:22px;padding:0 6px;border:0;border-radius:6px;background:#102b4c;color:#fff;font-size:.72rem;font-weight:750;line-height:1;white-space:nowrap;cursor:pointer}.court-positions :deep(.citation-inline:hover){background:#1d4168}.court-positions :deep(.citation-inline:focus-visible){outline:2px solid var(--gold);outline-offset:2px}.court-positions :deep(.novacase-citation-badge){width:auto;flex:0 0 auto}
@media(max-width:900px){.position-summaries{gap:12px}.party-subsection{margin-left:38px}.comparison-table-wrap th,.comparison-table-wrap td{padding:10px}}
@media(max-width:680px){.court-positions{gap:21px}.positions-header{flex-direction:column;gap:12px}.position-summaries{grid-template-columns:minmax(0,1fr)}.party-subsection{margin-left:0}.source-group li{grid-template-columns:auto minmax(0,1fr);gap:9px}.source-group button{grid-column:2;justify-self:start}.comparison-table-wrap table{min-width:620px}}
</style>
