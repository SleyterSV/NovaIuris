import test from 'node:test'
import assert from 'node:assert/strict'
import { assertSafePublicEnvironment } from '../src/config/publicEnv.js'

test('public Vite environment accepts only public integration settings', () => {
  assert.doesNotThrow(() => assertSafePublicEnvironment({
    VITE_API_BASE_URL: 'https://api.example.test',
    VITE_SUPABASE_URL: 'https://project.supabase.co',
    VITE_SUPABASE_PUBLISHABLE_KEY: 'public-placeholder'
  }))
})

test('public Vite environment rejects server secret variable names', () => {
  for (const name of [
    'VITE_SUPABASE_SERVICE_ROLE_KEY',
    'VITE_SUPABASE_SECRET_KEY',
    'VITE_OPENAI_API_KEY',
    'VITE_ZEP_API_KEY',
    'VITE_SMTP_PASSWORD',
    'VITE_DATABASE_URL'
  ]) {
    assert.throws(() => assertSafePublicEnvironment({ [name]: 'placeholder' }), /Private variables/)
  }
})
