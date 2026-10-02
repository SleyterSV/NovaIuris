import { test } from 'node:test'
import assert from 'node:assert/strict'
import { setAccessToken, authHeaders, publicApiError } from '../src/config/authSession.js'

test('bearer token is added centrally and removed on sign out', () => {
  setAccessToken('synthetic-token')
  assert.deepEqual(authHeaders(), { Authorization: 'Bearer synthetic-token' })
  setAccessToken(null)
  assert.deepEqual(authHeaders(), {})
})

test('401 and 403 are distinct safe errors', () => {
  assert.match(publicApiError({ status: 401 }, { error: { message: 'internal' } }).message, /sesión/)
  assert.match(publicApiError({ status: 403 }, { error: { message: 'internal' } }).message, /permiso/)
  assert.match(publicApiError({ status: 429 }, { error: { message: 'internal' } }).message, /Demasiadas/)
  assert.doesNotMatch(publicApiError({ status: 503 }, { error: { message: 'internal host' } }).message, /internal/)
})
