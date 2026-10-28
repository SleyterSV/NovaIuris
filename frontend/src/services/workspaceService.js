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
