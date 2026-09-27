export function normalizeApiBase(value = '') {
  return String(value).trim().replace(/\/+$/, '').replace(/(?:\/api)+$/, '')
}
