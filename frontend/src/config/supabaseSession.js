import { reactive } from 'vue'
import { createClient } from '@supabase/supabase-js'
import { setAccessToken } from './authSession.js'

const env = import.meta.env || {}
const url = env.VITE_SUPABASE_URL
const key = env.VITE_SUPABASE_PUBLISHABLE_KEY
export const authRequired = Boolean(url && key) || Boolean(env.PROD)
export const authConfigured = Boolean(url && key)
export const authState = reactive({ loading:authRequired, user:null, error:'' })
let client = null
let subscription = null

export async function startAuth(providedClient = null) {
  if (!authRequired && !providedClient) { authState.loading = false; return }
  if (!authConfigured && !providedClient) {
    authState.error = 'Configura VITE_SUPABASE_URL y VITE_SUPABASE_PUBLISHABLE_KEY para iniciar sesión.'
    authState.loading = false
    return
  }
  if (subscription) return
  client = providedClient || createClient(url, key)
  const listener = client.auth.onAuthStateChange((_event, session) => {
    setAccessToken(session?.access_token || null)
    authState.user = session?.user || null
    authState.loading = false
  })
  subscription = listener.data.subscription
  try {
    const { data, error } = await client.auth.getSession()
    if (error) throw error
    setAccessToken(data.session?.access_token || null)
    authState.user = data.session?.user || null
  } catch {
    setAccessToken(null)
    authState.user = null
    authState.error = 'No fue posible comprobar la sesión. Inténtalo de nuevo.'
  } finally { authState.loading = false }
}

export async function signIn(email, password) {
  if (!client) return 'La autenticación no está configurada.'
  const { error } = await client.auth.signInWithPassword({ email, password })
  return error ? 'No fue posible iniciar sesión. Revisa tus credenciales.' : ''
}

export async function signOut() {
  // Clear private data immediately, even if the provider request fails.
  setAccessToken(null)
  authState.user = null
  if (client) await client.auth.signOut({ scope:'local' })
}

export function stopAuth() {
  subscription?.unsubscribe()
  subscription = null
  client = null
  setAccessToken(null)
  authState.user = null
}
