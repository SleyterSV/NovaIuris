const RUN_TOOLS = { case:'NovaCase', court:'NovaCourt', search:'NovaSearch' }
const RUN_STATES = {
  queued:'Pendiente', pending:'Pendiente', processing:'Analizando',
  completed:'Completado', partial:'Completado parcialmente', failed:'No completado',
  cancelled:'Cancelado', timeout:'Tiempo agotado', interrupted:'Interrumpido'
}
const DOCUMENT_STATES = {
  uploaded:'Subido', processing:'Procesando', ready:'Disponible', failed:'Error'
}

export function caseToolName(tool) { return RUN_TOOLS[tool] || 'Análisis' }
export function caseRunStatus(status) { return RUN_STATES[status] || 'Estado no disponible' }
export function caseDocumentStatus(status) { return DOCUMENT_STATES[status] || 'Estado no disponible' }

export function formatCaseActivityDate(value) {
  const parsed = new Date(value)
  return value && !Number.isNaN(parsed.getTime())
    ? new Intl.DateTimeFormat('es-PE', { dateStyle:'medium', timeStyle:'short' }).format(parsed)
    : 'Fecha no disponible'
}

export function formatDocumentSize(value) {
  const size = Number(value)
  if (!Number.isFinite(size) || size < 0) return 'Tamaño no disponible'
  if (size < 1024 * 1024) return `${Math.max(1, Math.ceil(size / 1024))} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

export function formatDocumentType(document) {
  const mime = String(document?.mime_type || '').toLocaleLowerCase('en')
  const filename = String(document?.filename || document?.original_filename || document?.name || '')
  const extension = filename.split('.').pop()?.toLocaleLowerCase('en')
  if (mime === 'application/pdf' || extension === 'pdf') return 'PDF'
  if (mime === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || extension === 'docx') return 'DOCX'
  if (mime === 'text/plain' || extension === 'txt') return 'TXT'
  return 'Documento'
}

export function documentLibraryState(document) {
  const status = document?.processing_status || document?.status
  return DOCUMENT_STATES[status] ? status : 'unknown'
}

export function isPersistedCaseDocument(document) {
  return ['uploaded','processing','ready','failed'].includes(document?.processing_status)
}
