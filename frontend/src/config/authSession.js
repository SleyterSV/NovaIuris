// In-memory Supabase access token. The sign-in integration supplies and refreshes it.
let accessToken = null

export function setAccessToken(token) {
  accessToken = typeof token === 'string' && token ? token : null
}

export function authHeaders() {
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {}
}

export function publicApiError(response, data) {
  const error = new Error(response.status === 401 ? 'Tu sesión expiró. Inicia sesión nuevamente.' :
    response.status === 403 ? 'No tienes permiso para acceder a este recurso.' :
    response.status === 429 ? 'Demasiadas solicitudes. Inténtalo más tarde.' :
    response.status >= 500 ? 'El servicio no está disponible en este momento.' :
    data?.error?.message || data?.message || 'No fue posible completar la solicitud.')
  error.status = response.status
  error.code = data?.error?.code
  return error
}
