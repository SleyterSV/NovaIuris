import { API_URL } from '../config/api.js'
import { authHeaders, publicApiError } from '../config/authSession.js'

export async function loadLegalUnitSource(unitId, documentId, { signal, fetchImpl = fetch } = {}) {
  const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  if (!uuid.test(String(unitId || '')) || !uuid.test(String(documentId || ''))) {
    throw new Error('La identidad de la unidad jurídica no es válida.')
  }
  const response = await fetchImpl(`${API_URL}/search/sources/${unitId}?document_id=${encodeURIComponent(documentId)}`, {
    method: 'GET', headers: authHeaders(), signal
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok || data.success !== true || !data.unit) {
    throw publicApiError(response, data)
  }
  return data.unit
}
