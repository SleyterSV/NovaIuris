import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { prepareCaseExport, downloadCasePdf, downloadCaseDocx, downloadCourtPdf, downloadCourtDocx } from '../src/services/caseExport.js'
import { reportForReading, reportUsedSources } from '../src/utils/caseReportPresentation.js'

test('Case export sends only server-owned identifiers', async () => {
  const calls = []
  const result = await prepareCaseExport('CASE-A', 'TASK-A', async (path, options) => {
    calls.push({ path, options })
    return { success: true }
  })
  assert.equal(result.success, true)
  assert.equal(calls[0].path, '/export/prepare')
  assert.deepEqual(JSON.parse(calls[0].options.body),
    { case_id: 'CASE-A', task_id: 'TASK-A', tool: 'case' })
  assert.throws(() => prepareCaseExport('', 'TASK-A'), /incompleta/)
})

test('Case refresh recovers an explicit scoped task and report print verifies it', async () => {
  const root = new URL('../src/views/', import.meta.url)
  const mike = await readFile(new URL('MikeView.vue', root), 'utf8')
  const caseView = await readFile(new URL('NovaCaseView.vue', root), 'utf8')
  const report = await readFile(new URL('../components/novacase/ReportView.vue', root), 'utf8')
  assert.match(mike, /const path = tool === 'court' \? '\/novacourt\/results' : '\/tasks'/)
  assert.match(mike, /requestJson\(`\$\{path\}\/\$\{encodeURIComponent\(taskId\)\}\?case_id=/)
  assert.match(mike, /existingTaskId:taskId/)
  assert.match(caseView, /:task-id="completedTaskId"/)
  assert.match(report, /await prepareCaseExport\(props.caseId, props.taskId\)/)
  assert.match(report, /await prepareCaseExport\(props.caseId, props.taskId\)/)
  assert.match(report, /No fue posible preparar el informe para imprimir/)
  const legacy = await readFile(new URL('../components/Step4Report.vue', root), 'utf8')
  assert.match(legacy, /class="export-pdf-btn" type="button" disabled/)
})

test('Case UI distinguishes explicit cancellation from component cleanup', async () => {
  const caseView = await readFile(new URL('../src/views/NovaCaseView.vue', import.meta.url), 'utf8')
  assert.match(caseView, /class="cancel-analysis" @click="controller\?\.abort\('user'\)"/)
  assert.match(caseView, /onBeforeUnmount\(\(\) => controller\?\.abort\('detach'\)\)/)
})

test('PDF download sends only scoped identifiers and expects a PDF response', async () => {
  const calls = []
  const pdf = new Blob(['%PDF-1.7'], { type:'application/pdf' })
  const result = await downloadCasePdf('CASE-A', 'TASK-A', async (url, options) => {
    calls.push({ url, options })
    return { ok:true, headers:new Headers({ 'Content-Type':'application/pdf' }), blob:async () => pdf }
  })
  assert.equal(result, pdf)
  assert.match(calls[0].url, /\/export\/pdf$/)
  assert.deepEqual(JSON.parse(calls[0].options.body), { case_id:'CASE-A', task_id:'TASK-A', tool:'case' })
  await assert.rejects(() => downloadCasePdf('', 'TASK-A'), /incompleta/)
})

test('DOCX uses the same scoped identity and validates the file response', async () => {
  const docx = new Blob(['PK-document'],
    { type:'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
  const calls=[]
  const result=await downloadCaseDocx('CASE-A','TASK-A',async (url,options)=>{
    calls.push({url,options})
    return {ok:true,headers:new Headers({'Content-Type':docx.type}),blob:async()=>docx}
  })
  assert.equal(result,docx)
  assert.match(calls[0].url,/\/export\/docx$/)
  assert.deepEqual(JSON.parse(calls[0].options.body),
    {case_id:'CASE-A',task_id:'TASK-A',tool:'case'})
  await assert.rejects(()=>downloadCaseDocx('','TASK-A'),/incompleta/)
})

test('NovaCourt PDF and DOCX send only persisted task identity', async () => {
  const calls = []
  for (const [download, format, mime, bytes] of [
    [downloadCourtPdf, 'pdf', 'application/pdf', '%PDF-1.7'],
    [downloadCourtDocx, 'docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'PK-office']
  ]) {
    const file = new Blob([bytes], { type:mime })
    const result = await download('CASE-COURT', 'TASK-COURT', async (url, options) => {
      calls.push({ url, options })
      return { ok:true, headers:new Headers({ 'Content-Type':mime }), blob:async () => file }
    })
    assert.equal(result, file)
    assert.match(calls.at(-1).url, new RegExp(`/export/court/${format}$`))
    assert.deepEqual(JSON.parse(calls.at(-1).options.body),
      { case_id:'CASE-COURT', task_id:'TASK-COURT', tool:'court' })
    assert.doesNotMatch(calls.at(-1).options.body, /report|result|html|markdown|content/i)
  }
})

test('NovaCourt report exposes copy, print and real file actions without client report payload', async () => {
  const report = await readFile(new URL('../src/components/novacourt/CourtReport.vue', import.meta.url), 'utf8')
  const view = await readFile(new URL('../src/views/NovaCourtView.vue', import.meta.url), 'utf8')
  assert.match(report, /Copiar informe/)
  assert.match(report, /@click="printReport"/)
  assert.match(report, /Descargar PDF/)
  assert.match(report, /Descargar DOCX/)
  assert.match(report, /Generando PDF/)
  assert.match(report, /Generando DOCX/)
  assert.match(report, /No fue posible generar el PDF/)
  assert.match(report, /No fue posible generar el DOCX/)
  assert.doesNotMatch(report, /PDF · próximamente|DOCX · próximamente/)
  assert.match(view, /:task-id="taskId"/)
  assert.match(report, /downloadCourtPdf\(props\.caseId, props\.taskId\)/)
  assert.match(report, /navigator\.clipboard\.writeText\(cleanReportText\(reportText\)\)/)
})

test('report presentation removes only duplicate source section and keeps canonical citations', () => {
  const report='# Informe\n## Objeto y alcance\nSe examina [1].\n## Fuentes\nDuplicado.\n'
  assert.equal(reportForReading(report),'## Objeto y alcance\nSe examina [1].')
  assert.deepEqual(reportUsedSources([{source_id:'A'}],[{source_id:'A'},{source_id:'B'}]),[{source_id:'A'}])
})
