// One API origin for every frontend client. VITE_API_BASE_URL is canonical;
// VITE_API_URL remains accepted while existing deployments migrate.
import { normalizeApiBase } from './apiBase.js'
const environment = import.meta.env || {}
const configuredBaseUrl = normalizeApiBase(
  environment.VITE_API_BASE_URL || environment.VITE_API_URL ||
  (environment.DEV ? 'http://localhost:5001' : '')
)

// Older VITE_API_URL values often included /api. Normalize them once.
export const API_BASE_URL = configuredBaseUrl.replace(/\/api$/, '')
export const API_URL = `${API_BASE_URL}/api`

export function apiUrl(path = '') {
  return `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
}
