import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { prepareCaseExport } from '../src/services/caseExport.js'

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
  assert.match(mike, /requestJson\(`\/tasks\/\$\{encodeURIComponent\(taskId\)\}\?case_id=/)
  assert.match(mike, /existingTaskId:taskId/)
  assert.match(caseView, /:task-id="completedTaskId"/)
  assert.match(report, /await prepareCaseExport\(props.caseId, props.taskId\)/)
  assert.match(report, /TASK_NOT_READY/)
  assert.match(report, /EXPORT_NOT_AVAILABLE/)
  const legacy = await readFile(new URL('../components/Step4Report.vue', root), 'utf8')
  assert.match(legacy, /class="export-pdf-btn" type="button" disabled/)
})
