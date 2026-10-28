export async function fetchOwnedCases(requestJson) {
  const response = await requestJson('/cases')
  if (!Array.isArray(response?.cases)) throw new Error('CASES_RESPONSE_INVALID')
  return response.cases
}

export async function fetchCaseActivity(requestJson, listDocuments, caseId) {
  const encodedCaseId = encodeURIComponent(caseId)
  const [history, documents] = await Promise.all([
    requestJson(`/cases/${encodedCaseId}/runs`),
    listDocuments(caseId)
  ])
  if (!Array.isArray(history?.runs) || !Array.isArray(documents)) throw new Error('CASE_ACTIVITY_RESPONSE_INVALID')
  return { runs:history.runs, documents }
}

export async function createOwnedCase(requestJson, input) {
  const title = typeof input?.title === 'string' ? input.title.trim() : ''
  const description = typeof input?.description === 'string' ? input.description.trim() : ''
  if (!title || title.length > 240 || description.length > 4000) throw new Error('CASE_INPUT_INVALID')
  const response = await requestJson('/cases', {
    method:'POST',
    body:JSON.stringify({ title, ...(description ? { description } : {}) })
  })
  if (!response?.case?.id) throw new Error('CASE_CREATE_RESPONSE_INVALID')
  return response.case
}

export async function updateOwnedCase(requestJson, caseId, patch) {
  if (!caseId || !patch || Object.keys(patch).some(key => !['title','status'].includes(key))) {
    throw new Error('CASE_UPDATE_INVALID')
  }
  const cleanPatch = { ...patch }
  if ('title' in cleanPatch) {
    if (typeof cleanPatch.title !== 'string') throw new Error('CASE_INPUT_INVALID')
    cleanPatch.title = cleanPatch.title.trim()
    if (!cleanPatch.title || cleanPatch.title.length > 240) throw new Error('CASE_INPUT_INVALID')
  }
  if ('status' in cleanPatch && !['active','archived'].includes(cleanPatch.status)) {
    throw new Error('CASE_INPUT_INVALID')
  }
  const response = await requestJson(`/cases/${encodeURIComponent(caseId)}`, {
    method:'PATCH', body:JSON.stringify(cleanPatch)
  })
  if (!response?.case?.id) throw new Error('CASE_UPDATE_RESPONSE_INVALID')
  return response.case
}

export function filterOwnedCases(cases, query = '', status = 'active') {
  const normalizedQuery = String(query).trim().toLocaleLowerCase('es')
  return (Array.isArray(cases) ? cases : []).filter(item => {
    const itemStatus = item.status === 'archived' ? 'archived' : 'active'
    return (status === 'all' || itemStatus === status) &&
      (!normalizedQuery || `${item.title || ''} ${item.description || ''}`.toLocaleLowerCase('es').includes(normalizedQuery))
  })
}

export function createCaseMutationRunner() {
  let pending = false
  return async action => {
    if (pending) throw new Error('CASE_MUTATION_PENDING')
    pending = true
    try { return await action() }
    finally { pending = false }
  }
}
