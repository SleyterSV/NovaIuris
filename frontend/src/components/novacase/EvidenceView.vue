<template>
  <main class="evidence-editorial" aria-labelledby="evidence-title">
    <header class="evidence-header">
      <p class="evidence-eyebrow"><span aria-hidden="true"></span> NOVACASE · EVIDENCIA</p>
      <div class="evidence-title-row">
        <div>
          <h2 id="evidence-title">Análisis probatorio</h2>
          <p class="evidence-deck">Evaluación de los medios probatorios disponibles y de su relación con los hechos relevantes del caso.</p>
        </div>
        <span v-if="evidenceLevel" class="evidence-level"><span>Nivel general de evidencia</span><strong>{{ evidenceLevel }}</strong></span>
      </div>
    </header>

    <section class="evidence-context" aria-label="Síntesis probatoria">
      <h3>Evaluación probatoria</h3>
      <dl>
        <div><dt>Nivel general</dt><dd>{{ evidenceLevel || 'No identificado' }}</dd></div>
        <div><dt>Documentos aportados</dt><dd>{{ documentCount }}</dd></div>
        <div><dt>Hechos con respaldo documental</dt><dd>{{ supportedFacts.length }}</dd></div>
        <div><dt>Hechos pendientes de corroboración</dt><dd>{{ pendingFacts.length }}</dd></div>
        <div><dt>Fuentes jurídicas de apoyo</dt><dd>{{ legalSources.length }}</dd></div>
      </dl>
    </section>

    <div class="evidence-overview-grid">
      <section class="evidence-section documents-section" aria-labelledby="documents-title">
        <header class="section-heading">
          <p class="section-kicker">DOCUMENTACIÓN APORTADA</p>
          <h3 id="documents-title">Documentos del caso</h3>
        </header>
        <p v-if="documentGroups.length === 0 && !documentNarrative" class="section-empty">No se identificaron documentos incorporados al caso.</p>
        <div v-if="documentGroups.length === 0 && documentNarrative" class="document-narrative"><MarkdownRenderer :content="documentNarrative" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" /></div>
        <ol v-if="documentGroups.length" class="document-list">
          <li v-for="(group, index) in documentGroups" :key="group.key" class="document-row">
            <span class="row-number" aria-hidden="true">{{ number(index + 1) }}</span>
            <div class="document-content">
              <h4>{{ group.title }}</h4>
              <p class="document-meta">{{ documentTypeLabel(group) }} · {{ group.sources.length }} {{ group.sources.length === 1 ? 'página utilizada' : 'páginas utilizadas' }}</p>
              <p v-if="group.supports.length" class="document-note"><strong>Acredita:</strong> <span v-for="(item, supportIndex) in group.supports" :key="`support-${supportIndex}`"><MarkdownRenderer :content="item" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" /></span></p>
              <p v-if="group.limitations.length" class="document-note limitation-note"><strong>Limitaciones:</strong> <span v-for="(item, limitationIndex) in group.limitations" :key="`limit-${limitationIndex}`"><MarkdownRenderer :content="item" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" /></span></p>
              <ul class="document-pages">
                <li v-for="source in group.sources" :key="source.source_id">
                  <button type="button" class="source-action" :aria-label="`Ver documento${pageLabel(source) ? `, ${pageLabel(source)}` : ''}`" @click="selectSource(source)">
                    <span v-if="citationFor(source)" class="citation-badge">{{ citationFor(source).label }}</span>
                    <span>{{ pageActionLabel(source) }}</span><span aria-hidden="true">↗</span>
                  </button>
                </li>
              </ul>
            </div>
          </li>
        </ol>
        <div v-if="documentCount === 0" class="documents-empty" role="status">
          <p>Los hechos permanecen como alegaciones hasta contar con respaldo documental.</p>
          <button type="button" @click="$emit('add-documents')">Agregar documentos al caso</button>
        </div>
      </section>

      <section class="evidence-section other-evidence" aria-labelledby="other-evidence-title">
        <header class="section-heading">
          <p class="section-kicker">MEDIOS COMPLEMENTARIOS</p>
          <h3 id="other-evidence-title">Otros medios probatorios</h3>
        </header>
        <ul v-if="hasOtherEvidence" class="other-evidence-list">
          <li v-for="item in otherEvidence" :key="item.key">
            <span>{{ item.label }}</span>
            <MarkdownRenderer v-if="item.content" :content="item.content" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" />
            <strong v-else>No identificado</strong>
          </li>
        </ul>
        <p v-else class="section-empty">No se identificaron testimonios, peritajes ni evidencia digital en la información aportada.</p>
      </section>
    </div>

    <section v-if="supportedFacts.length" class="evidence-section fact-section" aria-labelledby="supported-facts-title">
      <header class="section-heading">
        <p class="section-kicker">HECHOS RESPALDADOS</p>
        <h3 id="supported-facts-title">Hechos acreditados documentalmente</h3>
        <p>Hechos respaldados por los documentos incorporados al caso.</p>
      </header>
      <ol class="fact-list">
        <li v-for="(fact, index) in supportedFacts" :key="fact.fact_id || `supported-${index}`">
          <span class="row-number" aria-hidden="true">{{ number(index + 1) }}</span>
          <div><MarkdownRenderer :content="safeText(fact.text)" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" />
            <div v-if="factSourceList(fact).length" class="fact-sources"><span>Fuente:</span>
              <button v-for="source in factSourceList(fact)" :key="source.source_id" type="button" class="source-action" :aria-label="`Ver fuente${citationFor(source) ? ` ${citationFor(source).label.slice(1,-1)}` : ''}: ${humanSourceLabel(source)}`" @click="selectSource(source)">
                <span v-if="citationFor(source)" class="citation-badge">{{ citationFor(source).label }}</span>{{ humanSourceLabel(source) }} <span aria-hidden="true">↗</span>
              </button>
            </div>
          </div>
        </li>
      </ol>
    </section>

    <section v-if="pendingFacts.length" class="evidence-section fact-section alleged-section" aria-labelledby="pending-facts-title">
      <header class="section-heading">
        <p class="section-kicker">RELATO PENDIENTE DE RESPALDO</p>
        <h3 id="pending-facts-title">Hechos pendientes de corroboración</h3>
        <p>Elementos provenientes del relato del caso que aún requieren respaldo documental.</p>
      </header>
      <ol class="fact-list">
        <li v-for="(fact, index) in pendingFacts" :key="fact.fact_id || `pending-${index}`">
          <span class="row-number" aria-hidden="true">{{ number(index + 1) }}</span>
          <div><MarkdownRenderer :content="safeText(fact.text)" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" />
            <span class="pending-label">Pendiente de corroboración</span>
          </div>
        </li>
      </ol>
    </section>

    <section v-if="legalSourceGroups.length" class="evidence-section legal-support" aria-labelledby="legal-support-title">
      <header class="section-heading">
        <p class="section-kicker">AUTORIDAD JURÍDICA</p>
        <h3 id="legal-support-title">Fuentes jurídicas de apoyo</h3>
        <p>Las siguientes fuentes sustentan el análisis jurídico, pero no constituyen prueba de los hechos del caso.</p>
      </header>
      <ol class="legal-source-list">
        <li v-for="group in legalSourceGroups" :key="group.key">
          <div class="legal-source-heading"><h4>{{ group.title }}</h4><p v-if="group.court">{{ group.court }}</p></div>
          <p v-if="group.units.length" class="legal-locators"><span>Unidades relevantes</span>{{ group.units.join(' · ') }}</p>
          <ul class="unit-actions"><li v-for="source in group.sources" :key="source.source_id">
            <button type="button" class="source-action" :aria-label="`Ver fuente: ${sourceUnitActionLabel(source)}`" @click="selectSource(source)">
              <span v-if="citationFor(source)" class="citation-badge">{{ citationFor(source).label }}</span>{{ sourceUnitActionLabel(source) }}<span aria-hidden="true">↗</span>
            </button>
          </li></ul>
        </li>
      </ol>
    </section>

    <section v-if="conclusionText || strengths.length || limitations.length" class="evidence-section conclusion-section" aria-labelledby="evidence-conclusion-title">
      <header class="section-heading"><p class="section-kicker">SÍNTESIS EJECUTIVA</p><h3 id="evidence-conclusion-title">Conclusión probatoria</h3></header>
      <p v-if="evidenceLevel" class="conclusion-level"><span>Nivel de evidencia</span><strong>{{ evidenceLevel }}</strong></p>
      <MarkdownRenderer v-if="conclusionText" :content="conclusionText" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" />
      <div v-if="strengths.length" class="conclusion-points"><h4>Fortalezas</h4><ul><li v-for="(item,index) in strengths" :key="`strength-${index}`"><MarkdownRenderer :content="item" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" /></li></ul></div>
      <div v-if="limitations.length" class="conclusion-points"><h4>Limitaciones</h4><ul><li v-for="(item,index) in limitations" :key="`limitation-${index}`"><MarkdownRenderer :content="item" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" /></li></ul></div>
    </section>

    <section v-if="issueEvidence.length" class="evidence-section issue-evidence" aria-labelledby="issue-evidence-title">
      <header class="section-heading"><p class="section-kicker">ANÁLISIS POR CUESTIÓN</p><h3 id="issue-evidence-title">Evidencia vinculada a las cuestiones jurídicas</h3></header>
      <ol class="issue-evidence-list">
        <li v-for="(item, index) in issueEvidence" :key="item.key">
          <span class="row-number" aria-hidden="true">{{ number(index + 1) }}</span>
          <article>
            <h4>{{ item.title }}</h4>
            <section v-if="item.issue"><h5>Cuestión jurídica</h5><MarkdownRenderer :content="item.issue" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" /></section>
            <section v-if="item.description"><h5>Evidencia disponible</h5><MarkdownRenderer :content="item.description" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" /></section>
            <section v-if="item.probativeValue"><h5>Valor probatorio</h5><MarkdownRenderer :content="item.probativeValue" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" /></section>
            <section v-if="item.limitations"><h5>Limitaciones</h5><MarkdownRenderer :content="item.limitations" :citations="citations" :sources="normalizedSources" :case-id="caseId" @select-citation="openCitation" /></section>
            <div v-if="item.sources.length" class="linked-sources"><h5>Fuentes</h5>
              <button v-for="source in item.sources" :key="source.source_id" type="button" class="source-action" :aria-label="`Ver fuente${citationFor(source) ? ` ${citationFor(source).label.slice(1,-1)}` : ''}: ${humanSourceLabel(source)}`" @click="selectSource(source)">
                <span v-if="citationFor(source)" class="citation-badge">{{ citationFor(source).label }}</span>{{ humanSourceLabel(source) }}<span aria-hidden="true">↗</span>
              </button>
            </div>
          </article>
        </li>
      </ol>
    </section>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import { evidenceAvailability, presentableText, sourceHumanLabel, sourceUnitLabel, argumentCitationForSource } from '@/utils/novacasePresentation.js'
import { normalizeSource, normalizeSources } from '@/utils/sourceContract.js'

const props = defineProps({
  evidence: { type: Object, default: () => ({}) },
  analysis: { type: Object, default: () => ({}) },
  documentCount: { type: Number, default: 0 },
  factGroups: { type: Array, default: () => [] },
  facts: { type: Array, default: () => [] },
  issues: { type: Array, default: () => [] },
  evidenceLinks: { type: Array, default: () => [] },
  sources: { type: Array, default: () => [] },
  citations: { type: Array, default: () => [] },
  caseId: { type: String, default: null }
})
const emit = defineEmits(['add-documents', 'select-source'])

function safeText(value) {
  if (typeof value !== 'string') return ''
  return presentableText(value).replace(/Documento rotulado como\s+["'“]?ficticio["'”]?\s+en el entorno\s+QA\.?/gi, '').replace(/\(\s*\)|\[\s*\]/g, '').replace(/\s{2,}/g, ' ').trim()
}
function recordsList(value) {
  const items = Array.isArray(value) ? value : value == null || value === '' ? [] : [value]
  return items.map(displayContent).filter(Boolean)
}
function displayContent(value) {
  if (Array.isArray(value)) return value.map(displayContent).filter(Boolean).join('\n\n')
  if (value && typeof value === 'object') return displayContent(value.text || value.description || value.content || value.summary)
  if (typeof value === 'string') {
    const text = safeText(value).trim()
    const status = text.toLocaleLowerCase()
    const translated = ({ supported: 'Con respaldo documental', alleged: 'Pendiente de corroboración', verified: 'Acreditado', unknown: 'No identificado', not_identified: 'No identificado' })[status]
    if (translated) return translated
    return evidenceAvailability(text) === 'not_identified' ? '' : text
  }
  return ''
}
function firstValue(...values) { return values.find(value => typeof value === 'string' && value.trim()) || '' }
function number(value) { return String(value).padStart(2, '0') }
function selectSource(value) {
  const source = normalizeSource(value, props.caseId)
  if (source) emit('select-source', source)
}
function openCitation(citation) {
  const source = normalizedSources.value.find(item => item.source_id === citation?.source_id)
  if (source) selectSource(source)
}
function citationFor(source) {
  return argumentCitationForSource(source, props.citations, normalizedSources.value, props.caseId)
}
function pageLabel(source) {
  if (!source.page_start) return ''
  return source.page_end && source.page_end !== source.page_start
    ? `págs. ${source.page_start}–${source.page_end}` : `pág. ${source.page_start}`
}
function humanSourceTitle(source) {
  const title = safeText(source.display_title || source.title || 'Documento del caso')
  return title.replace(/^\s*\d+[_\s-]+/, '').replace(/\.[a-z0-9]{2,5}$/i, '').replace(/_+/g, ' ').replace(/\s{2,}/g, ' ').trim() || 'Documento del caso'
}
function documentTypeLabel(group) {
  const title = group.title.toLocaleLowerCase()
  if (title.includes('contrato')) return 'Documento contractual'
  if (title.includes('memorando') || title.includes('memorándum') || title.includes('memorandum')) return 'Comunicación administrativa'
  return 'Documento del caso'
}
function humanSourceLabel(source) { return safeText(sourceHumanLabel(source)) }
function pageActionLabel(source) { return ['case', 'private_case'].includes(source.source_scope) ? `Ver documento${pageLabel(source) ? ` · ${pageLabel(source)}` : ''}` : `Ver fuente${pageLabel(source) ? ` · ${pageLabel(source)}` : ''}` }
function sourceUnitActionLabel(source) { return [sourceUnitLabel(source) || 'Ver fuente', pageLabel(source)].filter(Boolean).join(' · ') }
function factSourceList(fact) {
  const ids = new Set(fact.source_ids || [])
  return normalizedSources.value.filter(source => ids.has(source.source_id) && ['case', 'private_case'].includes(source.source_scope))
}

const normalizedSources = computed(() => normalizeSources(props.sources, props.caseId))
const privateSources = computed(() => normalizedSources.value.filter(source => ['case', 'private_case'].includes(source.source_scope)))
const legalSources = computed(() => normalizedSources.value.filter(source => source.source_scope === 'public_legal'))
const evidenceLevel = computed(() => {
  const raw = firstValue(props.analysis?.nivel_evidencia, props.analysis?.evidence_level,
    props.analysis?.evidence_strength, props.evidence?.level, props.evidence?.evidence_level, props.evidence?.summary)
  const normalized = raw.toLocaleLowerCase().trim()
  if (['low', 'bajo', 'baja', 'limited', 'limitada'].includes(normalized)) return 'Baja'
  if (['medium', 'medio', 'media', 'moderate', 'moderada'].includes(normalized)) return 'Media'
  if (['high', 'alto', 'alta', 'strong', 'sólida'].includes(normalized)) return 'Alta'
  if (['critical', 'crítico', 'crítica'].includes(normalized)) return 'Crítica'
  if (['unknown', 'not identified', 'not_identified', 'desconocida', 'no identificado'].includes(normalized)) return 'No identificado'
  return ''
})
const supportedFacts = computed(() => props.factGroups.find(group => group.key === 'supported')?.facts || [])
const pendingFacts = computed(() => [
  ...(props.factGroups.find(group => group.key === 'alleged')?.facts || []),
  ...(props.factGroups.find(group => group.key === 'pending')?.facts || [])
])
const otherEvidence = computed(() => [
  { key: 'testimonies', label: 'Testimonios', content: displayContent(props.evidence.testimonies) },
  { key: 'expert', label: 'Peritajes', content: displayContent(props.evidence.expertReports) },
  { key: 'digital', label: 'Evidencia digital', content: displayContent(props.evidence.digitalEvidence) }
])
const hasOtherEvidence = computed(() => otherEvidence.value.some(item => item.content))
const documentNarrative = computed(() => props.documentCount > 0 ? displayContent(props.evidence.documents) : '')
const strengths = computed(() => recordsList(props.evidence.strengths))
const limitations = computed(() => [...recordsList(props.evidence.weaknesses), ...recordsList(props.evidence.missing_evidence)])
const conclusionText = computed(() => {
  const summary = displayContent(props.evidence.conclusion || props.analysis?.evidence_summary || props.evidence.summary)
  const levelValue = ['baja', 'low', 'media', 'medio', 'medium', 'alta', 'alto', 'high', 'crítica', 'crítico', 'critical', 'desconocida', 'unknown', 'no identificado', 'not identified', 'not_identified']
  return levelValue.includes(summary.toLocaleLowerCase().trim()) ? '' : summary
})
const documentGroups = computed(() => {
  const groups = new Map()
  for (const source of privateSources.value) {
    const title = humanSourceTitle(source)
    const key = source.document_id || source.metadata?.document_id || title
    if (!groups.has(key)) groups.set(key, { key, title, sources: [], supports: [], limitations: [] })
    const group = groups.get(key)
    group.sources.push(source)
    for (const link of props.evidenceLinks) {
      if (!(link.source_ids || []).includes(source.source_id)) continue
      const support = displayContent(link.what_it_supports || link.evidence_summary || link.text)
      const limitation = displayContent(link.limitations)
      if (support && !group.supports.includes(support)) group.supports.push(support)
      if (limitation && !group.limitations.includes(limitation)) group.limitations.push(limitation)
    }
  }
  return [...groups.values()].map(group => ({ ...group, sources: group.sources.sort((a, b) => (a.page_start || 0) - (b.page_start || 0)) }))
})
const legalSourceGroups = computed(() => {
  const groups = new Map()
  for (const source of legalSources.value) {
    const key = source.document_id || source.display_title || source.title
    if (!groups.has(key)) groups.set(key, { key, title: humanSourceTitle(source), court: safeText(source.court || source.issuer || source.entity || ''), sources: [], units: [] })
    const group = groups.get(key)
    group.sources.push(source)
    const unit = sourceUnitLabel(source)
    if (unit && !group.units.includes(unit)) group.units.push(unit)
  }
  return [...groups.values()]
})
const factsById = computed(() => new Map(props.facts.map(fact => [fact.fact_id, fact])))
const issuesById = computed(() => new Map(props.issues.map(issue => [issue.issue_id, issue])))
const issueEvidence = computed(() => props.evidenceLinks.map((link, index) => {
  const issue = issuesById.value.get(link.issue_id)
  const sourceIds = new Set(link.source_ids || [])
  const linkedSources = normalizedSources.value.filter(source => sourceIds.has(source.source_id))
  const facts = (link.fact_ids || []).map(id => factsById.value.get(id)).filter(fact => fact?.text)
  const description = displayContent(link.what_it_supports || link.evidence_summary || link.text)
  const limitations = displayContent(link.limitations)
  const probativeValue = displayContent(link.probative_value || link.value_assessment || link.assessment)
  const issueText = safeText(issue?.text || issue?.description || issue?.question || '')
  const title = safeText(link.title || issue?.title || '')
  const evidenceDescription = description || facts.map(fact => safeText(fact.text)).filter(Boolean).join('\n\n')
  return title || issueText || evidenceDescription || linkedSources.length
    ? { key: link.evidence_id || `${link.issue_id || 'evidence'}-${index}`, title: title || (issueText ? 'Cuestión jurídica relacionada' : 'Evidencia relacionada'), issue: issueText, description: evidenceDescription, probativeValue, limitations, sources: linkedSources }
    : null
}).filter(Boolean))
</script>

<style scoped>
.evidence-editorial{--evidence-navy:#17375e;--evidence-muted:#667789;--evidence-line:#dce5ee;--evidence-gold:#a98551;display:grid;gap:clamp(28px,3.5vw,48px);width:100%;max-width:1240px;min-width:0;margin:0 auto;color:#34485d}
.evidence-header{padding:2px 0 22px;border-bottom:1px solid var(--evidence-line)}
.evidence-eyebrow{display:flex;align-items:center;gap:9px;margin:0 0 10px;color:#8a6a37;font-size:.64rem;font-weight:750;letter-spacing:.12em}
.evidence-eyebrow span{width:22px;height:1px;background:#b08a4c}
.evidence-title-row{display:flex;align-items:flex-end;justify-content:space-between;gap:24px}
.evidence-title-row h2{margin:0;color:var(--evidence-navy);font:600 clamp(1.7rem,2.3vw,2.15rem)/1.24 Georgia,'Times New Roman',serif}
.evidence-deck{max-width:760px;margin:9px 0 0;color:var(--evidence-muted);font-size:.92rem;line-height:1.7}
.evidence-level{display:grid;gap:4px;flex:none;min-width:174px;padding:10px 14px;border:1px solid #e4e8e8;border-radius:8px;background:#fbfcfb}
.evidence-level span,.evidence-context dt{color:#788696;font-size:.68rem;font-weight:650}
.evidence-level strong{color:var(--evidence-navy);font:600 1.03rem Georgia,'Times New Roman',serif}
.evidence-context{padding:19px 22px 17px;border:1px solid #e0e6eb;border-radius:10px;background:#fff;box-shadow:0 5px 18px #17375e08}
.evidence-context h3{margin:0 0 13px;color:var(--evidence-navy);font:600 1.12rem Georgia,'Times New Roman',serif}
.evidence-context dl{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));margin:0;border-top:1px solid #e7ecf0}
.evidence-context dl>div{min-width:0;padding:12px 14px 0 0}
.evidence-context dl>div+div{padding-left:14px;border-left:1px solid #e7ecf0}
.evidence-context dt{margin:0 0 6px;line-height:1.45}
.evidence-context dd{margin:0;color:var(--evidence-navy);font:600 1.1rem Georgia,'Times New Roman',serif;line-height:1.25;overflow-wrap:normal}
.evidence-overview-grid{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(255px,.75fr);gap:36px;align-items:start}
.evidence-section{min-width:0;padding-top:22px;border-top:1px solid var(--evidence-line)}
.evidence-overview-grid>.evidence-section{padding-top:0;border-top:0}
.section-heading{margin:0 0 16px}
.section-kicker{margin:0 0 7px;color:#8a6a37;font-size:.61rem;font-weight:750;letter-spacing:.1em}
.section-heading h3{margin:0;color:var(--evidence-navy);font:600 1.34rem/1.32 Georgia,'Times New Roman',serif}
.section-heading>p:last-child:not(.section-kicker){max-width:780px;margin:7px 0 0;color:var(--evidence-muted);font-size:.84rem;line-height:1.65}
.section-empty,.document-narrative{margin:0;padding:14px 16px;border-left:2px solid #d4c29e;background:#faf9f5;color:#637286;font-size:.86rem;line-height:1.65}
.document-list,.fact-list,.legal-source-list,.unit-actions,.other-evidence-list,.issue-evidence-list,.document-pages{margin:0;padding:0;list-style:none}
.document-row,.fact-list>li,.issue-evidence-list>li{display:grid;grid-template-columns:38px minmax(0,1fr);gap:14px;min-width:0;padding:19px 0;border-bottom:1px solid #e7ecf0}
.document-row:first-child,.fact-list>li:first-child,.issue-evidence-list>li:first-child{padding-top:2px}
.row-number{padding-top:2px;color:#a17c43;font:600 .88rem Georgia,'Times New Roman',serif;letter-spacing:.03em}
.document-content,.fact-list>li>div,.issue-evidence-list article{min-width:0}
.document-content>h4,.legal-source-heading h4,.issue-evidence-list article>h4{margin:0;color:#263d55;font:600 1.05rem/1.45 Georgia,'Times New Roman',serif;overflow-wrap:break-word}
.document-meta{margin:5px 0 14px;color:#778594;font-size:.73rem;line-height:1.5}
.document-note{display:grid;grid-template-columns:minmax(86px,110px) minmax(0,1fr);gap:8px;margin:10px 0;color:#405469;font-size:.86rem;line-height:1.68}
.document-note strong{color:#637589;font-size:.72rem;font-weight:750;letter-spacing:.06em;text-transform:uppercase}
.document-note>span{min-width:0}
.document-note :deep(.markdown-body),.fact-list :deep(.markdown-body),.issue-evidence-list :deep(.markdown-body),.conclusion-section :deep(.markdown-body){color:#405469;font-size:.9rem;line-height:1.75}
.document-note :deep(p),.fact-list :deep(p),.issue-evidence-list :deep(p),.conclusion-section :deep(p){margin:0 0 8px}
.document-note :deep(p:last-child),.fact-list :deep(p:last-child),.issue-evidence-list :deep(p:last-child),.conclusion-section :deep(p:last-child){margin-bottom:0}
.limitation-note strong{color:#8b744f}
.document-pages{display:flex;flex-wrap:wrap;gap:5px 16px;margin-top:13px}
.document-pages li,.unit-actions li{margin:0;padding:0;list-style:none}
.source-action{display:inline-flex;align-items:center;gap:6px;max-width:100%;padding:5px 3px;border:0;border-radius:4px;background:transparent;color:#315c83;font:600 .77rem/1.45 system-ui,-apple-system,'Segoe UI',sans-serif;text-align:left;cursor:pointer;transition:background .16s,color .16s}
.source-action:hover{background:#edf3f7;color:#17375e}
.source-action:focus-visible{outline:2px solid var(--evidence-gold);outline-offset:2px}
.citation-badge{display:inline-block;flex:none;position:relative;top:-.04em;padding:.06em .34em;border:1px solid #d7e2ec;border-radius:4px;background:#f1f5f8;color:#1b496f;font-size:.88em;font-weight:750;line-height:1.3;white-space:nowrap}
.documents-empty{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-top:14px;padding:14px 16px;border:1px solid #e6eaf0;border-radius:8px;background:#fbfcfd}
.documents-empty p{margin:0;color:#667789;font-size:.84rem;line-height:1.6}
.documents-empty button{flex:none;padding:8px 11px;border:1px solid #c8d6e2;border-radius:6px;background:#fff;color:#244866;font:650 .76rem system-ui,sans-serif;cursor:pointer}
.documents-empty button:hover{background:#f1f5f8}.documents-empty button:focus-visible{outline:2px solid var(--evidence-gold);outline-offset:2px}
.other-evidence-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid #e7ecf0;border-bottom:1px solid #e7ecf0}
.other-evidence-list li{display:grid;align-content:start;gap:8px;min-width:0;padding:13px 12px 13px 0}
.other-evidence-list li+li{padding-left:14px;border-left:1px solid #e7ecf0}
.other-evidence-list li>span{color:#6c7b8b;font-size:.7rem;font-weight:700;letter-spacing:.04em}
.other-evidence-list li strong,.other-evidence-list :deep(.markdown-body){color:#344b62;font-size:.83rem;line-height:1.55}
.other-evidence-list :deep(p){margin:0}
.fact-list{border-top:1px solid #e7ecf0}
.fact-list>li{grid-template-columns:38px minmax(0,1fr)}
.fact-sources{display:flex;align-items:center;flex-wrap:wrap;gap:4px 8px;margin-top:9px}
.fact-sources>span{color:#788696;font-size:.75rem}
.pending-label{display:inline-flex;margin-top:8px;padding:4px 9px;border:1px solid #eadfc9;border-radius:999px;background:#fcfaf5;color:#80683d;font-size:.68rem;font-weight:650}
.legal-source-list{border-top:1px solid #e7ecf0}
.legal-source-list>li{padding:17px 0;border-bottom:1px solid #e7ecf0}
.legal-source-heading{display:flex;align-items:baseline;justify-content:space-between;gap:18px}
.legal-source-heading p{flex:none;margin:0;color:#718094;font-size:.78rem}
.legal-locators{display:flex;flex-wrap:wrap;gap:6px 16px;margin:9px 0 4px;color:#405469;font-size:.78rem;line-height:1.55}
.legal-locators span{color:#788696}
.unit-actions{display:flex;flex-wrap:wrap;gap:5px 12px;margin-top:5px}
.conclusion-section{padding:22px clamp(16px,2.1vw,26px);border:1px solid #e2e8e6;border-left:3px solid #95ad98;border-radius:8px;background:#fbfcfa}
.conclusion-section .section-heading{margin-bottom:12px}
.conclusion-level{display:flex;align-items:center;gap:10px;margin:10px 0 14px;color:#718094;font-size:.8rem}
.conclusion-level strong{padding:4px 9px;border:1px solid #d8e5da;border-radius:999px;background:#f4f8f4;color:#536d59;font-size:.76rem}
.conclusion-points{margin-top:16px}
.conclusion-points h4{margin:0 0 8px;color:#725f3f;font-size:.74rem;font-weight:750;letter-spacing:.07em;text-transform:uppercase}
.conclusion-points ul{display:grid;gap:7px;margin:0;padding-left:18px}
.conclusion-points li{color:#405469;font-size:.85rem;line-height:1.65}
.conclusion-points :deep(p){margin:0}
.issue-evidence-list{border-top:1px solid #e7ecf0}
.issue-evidence-list>li{grid-template-columns:38px minmax(0,1fr);padding:22px 0}
.issue-evidence-list article>h4{margin:0 0 15px;font-size:1.12rem}
.issue-evidence-list article>section{margin-top:13px}
.issue-evidence-list article h5{margin:0 0 5px;color:#778594;font-size:.69rem;font-weight:750;letter-spacing:.07em;text-transform:uppercase}
.linked-sources{display:flex;align-items:baseline;flex-wrap:wrap;gap:5px 14px;margin-top:12px;padding-top:9px;border-top:1px solid #e8edf2}
.linked-sources h5{margin:0;color:#778594;font-size:.69rem;font-weight:750;letter-spacing:.07em;text-transform:uppercase}
.linked-sources .source-action{margin-right:4px}
.evidence-editorial :deep(.citation-inline),.evidence-editorial :deep(.citation-link){display:inline;position:relative;top:-.07em;margin:0 .13em;padding:.08em .36em;border:1px solid #d7e2ec;border-radius:4px;background:#f1f5f8;color:#1b496f;font:700 .76em/1.2 system-ui,sans-serif;white-space:nowrap;cursor:pointer}
.evidence-editorial :deep(.citation-inline:hover),.evidence-editorial :deep(.citation-link:hover){background:#e3edf5;border-color:#b9cddb}
.evidence-editorial :deep(.citation-inline:focus-visible),.evidence-editorial :deep(.citation-link:focus-visible){outline:2px solid #315c97;outline-offset:2px}
@media(max-width:1080px){.evidence-context dl{grid-template-columns:repeat(3,minmax(0,1fr));row-gap:13px}.evidence-context dl>div:nth-child(4){padding-left:0;border-left:0}.evidence-overview-grid{grid-template-columns:minmax(0,1fr);gap:24px}}
@media(max-width:680px){.evidence-editorial{gap:22px}.evidence-title-row{flex-direction:column;gap:12px}.evidence-context dl{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:12px}.evidence-context dl>div:nth-child(odd){padding-left:0;border-left:0}.evidence-context dl>div:nth-child(4){padding-left:16px;border-left:1px solid #e6e9ed}.document-row,.fact-list>li,.issue-evidence-list>li{grid-template-columns:28px minmax(0,1fr);gap:9px}.legal-source-heading{align-items:flex-start;flex-direction:column;gap:3px}.other-evidence-list li{grid-template-columns:1fr;gap:4px}}
@media(max-width:420px){.evidence-context{padding:13px}.evidence-context dl{grid-template-columns:1fr}.evidence-context dl>div,.evidence-context dl>div:nth-child(4){padding:8px 0 0;border:0;border-top:1px solid #e6e9ed}.evidence-context dl>div:first-child{padding-top:0;border-top:0}.source-action{white-space:normal}}
</style>
