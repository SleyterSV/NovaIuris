import assert from 'node:assert/strict'
import test from 'node:test'
import {
  caseDocumentStatus, caseRunStatus, caseToolName, documentLibraryState,
  formatCaseActivityDate, formatDocumentSize, formatDocumentType, isPersistedCaseDocument
} from '../src/utils/caseActivityPresentation.js'
import { downloadCaseDocument, listCaseDocuments } from '../src/services/documentService.js'
import { setAccessToken } from '../src/config/authSession.js'

test('history presents persisted tools and supported task states in product language', () => {
  assert.equal(caseToolName('case'), 'NovaCase')
  assert.equal(caseToolName('court'), 'NovaCourt')
  assert.equal(caseToolName('search'), 'NovaSearch')
  assert.equal(caseRunStatus('queued'), 'Pendiente')
  assert.equal(caseRunStatus('processing'), 'Analizando')
  assert.equal(caseRunStatus('completed'), 'Completado')
  assert.equal(caseRunStatus('partial'), 'Completado parcialmente')
  assert.equal(caseRunStatus('failed'), 'No completado')
  assert.equal(caseRunStatus('cancelled'), 'Cancelado')
  assert.equal(caseRunStatus('timeout'), 'Tiempo agotado')
  assert.equal(caseRunStatus('interrupted'), 'Interrumpido')
  assert.equal(caseRunStatus('internal-provider-stack'), 'Estado no disponible')
})

test('document library exposes only persisted case_documents and translates processing state', () => {
  for (const status of ['uploaded', 'processing', 'ready', 'failed']) {
    assert.equal(documentLibraryState({ processing_status:status }), status)
    assert.equal(isPersistedCaseDocument({ document_id:'document-id', processing_status:status }), true)
  }
  assert.equal(isPersistedCaseDocument({ document_id:'legacy-index-only', status:'ready' }), false)
  assert.equal(documentLibraryState({ status:'ready' }), 'ready')
  assert.equal(caseDocumentStatus('uploaded'), 'Subido')
  assert.equal(caseDocumentStatus('processing'), 'Procesando')
  assert.equal(caseDocumentStatus('ready'), 'Disponible')
  assert.equal(caseDocumentStatus('failed'), 'Error')
  assert.equal(caseDocumentStatus('unknown-internal-value'), 'Estado no disponible')
})

test('document metadata formatting handles persisted sizes and missing timestamps safely', () => {
  assert.equal(formatDocumentSize(2048), '2 KB')
  assert.equal(formatDocumentSize(2 * 1024 * 1024), '2.0 MB')
  assert.equal(formatDocumentSize(undefined), 'Tamaño no disponible')
  assert.equal(formatDocumentType({ mime_type:'application/pdf', filename:'escrito' }), 'PDF')
  assert.equal(formatDocumentType({ filename:'contrato.docx' }), 'DOCX')
  assert.equal(formatDocumentType({ mime_type:'text/plain' }), 'TXT')
  assert.equal(formatCaseActivityDate('not-a-date'), 'Fecha no disponible')
  assert.match(formatCaseActivityDate('2026-10-26T10:00:00Z'), /2026/)
})

test('case library reads documents from the authenticated case-scoped API', async () => {
  const originalFetch = globalThis.fetch
  setAccessToken('test-user-session')
  globalThis.fetch = async (url, options) => {
    assert.equal(options.headers.Authorization, 'Bearer test-user-session')
    if (String(url).endsWith('/CASE%2FA/documents')) {
      assert.match(String(url), /\/api\/cases\/CASE%2FA\/documents$/)
    } else assert.match(String(url), /\/api\/cases\/CASE-B\/documents$/)
    return Response.json({ success:true, case_id:'CASE/A', documents:[{ document_id:'doc-a', processing_status:'ready' }] })
  }
  try {
    const documents = await listCaseDocuments('CASE/A')
    assert.equal(documents[0].document_id, 'doc-a')
    await assert.rejects(listCaseDocuments('CASE-B'), /corpus/i)
  } finally {
    globalThis.fetch = originalFetch
    setAccessToken(null)
  }
})

test('private document download uses the authorized case/document endpoint and rejects unavailable files safely', async () => {
  const originals = { fetch:globalThis.fetch, document:globalThis.document,
    createObjectURL:URL.createObjectURL, revokeObjectURL:URL.revokeObjectURL }
  const clicks = []
  globalThis.document = {
    createElement:() => ({ click() { clicks.push({ href:this.href, download:this.download }) }, remove() {} }),
    body:{ append() {} }
  }
  URL.createObjectURL = () => 'blob:case-document'
  URL.revokeObjectURL = () => {}
  setAccessToken('test-user-session')
  globalThis.fetch = async (url, options) => {
    assert.match(String(url), /\/api\/cases\/CASE-A\/documents\/DOC-A\/file$/)
    assert.equal(options.headers.Authorization, 'Bearer test-user-session')
    assert.equal(options.cache, 'no-store')
    return new Response(new Blob(['private file bytes']), { status:200 })
  }
  try {
    await downloadCaseDocument('CASE-A', { document_id:'DOC-A', filename:'contrato.pdf' })
    assert.deepEqual(clicks, [{ href:'blob:case-document', download:'contrato.pdf' }])
    globalThis.fetch = async () => Response.json({ success:false, error:{ message:'No se encontró el documento.' } }, { status:404 })
    await assert.rejects(downloadCaseDocument('CASE-A', 'DOC-A'), /No se encontró el documento/i)
  } finally {
    globalThis.fetch = originals.fetch
    globalThis.document = originals.document
    URL.createObjectURL = originals.createObjectURL
    URL.revokeObjectURL = originals.revokeObjectURL
    setAccessToken(null)
  }
})
