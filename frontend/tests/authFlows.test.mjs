import { test, afterEach } from 'node:test'
import assert from 'node:assert/strict'
import {
  authState, resendConfirmation, requestPasswordReset, signUp, signOut,
  startAuth, stopAuth, updatePassword
} from '../src/config/supabaseSession.js'
import { authHeaders } from '../src/config/authSession.js'
import { readFile } from 'node:fs/promises'

let calls = []
let authListener
let apiError = null
let session = null

function createAuthClient() {
  calls = []
  apiError = null
  session = null
  return { auth: {
    onAuthStateChange(callback) {
      authListener = callback
      return { data:{ subscription:{ unsubscribe() {} } } }
    },
    async getSession() { return { data:{ session }, error:null } },
    async signUp(payload) {
      calls.push(['signUp', payload])
      return { data:{ session:null, user:{ id:'user-test' } }, error:apiError }
    },
    async resend(payload) {
      calls.push(['resend', payload])
      return { data:{}, error:apiError }
    },
    async resetPasswordForEmail(email, options) {
      calls.push(['resetPasswordForEmail', email, options])
      return { data:{}, error:apiError }
    },
    async updateUser(payload) {
      calls.push(['updateUser', payload])
      return { data:{ user:{ id:'user-test' } }, error:apiError }
    },
    async signOut(options) {
      calls.push(['signOut', options])
      return { error:apiError }
    }
  } }
}

afterEach(() => {
  stopAuth()
  delete globalThis.window
  authState.error = ''
  authState.linkError = ''
  authState.recovery = false
  authState.passwordUpdated = false
})

test('signup confirmation, resend, and password reset use the allow-listed app origin', async () => {
  globalThis.window = { location:{ origin:'http://localhost:5173', search:'' } }
  await startAuth(createAuthClient())
  const signup = await signUp('Test User', 'test@example.test', 'SecurePass1')
  assert.equal(signup.confirmationRequired, true)
  assert.equal(calls.at(-1)[0], 'signUp')
  assert.equal(calls.at(-1)[1].options.emailRedirectTo, 'http://localhost:5173')

  assert.equal(await resendConfirmation('test@example.test'), '')
  assert.deepEqual(calls.at(-1), ['resend', {
    type:'signup', email:'test@example.test', options:{ emailRedirectTo:'http://localhost:5173' }
  }])

  assert.equal(await requestPasswordReset('test@example.test'), '')
  assert.deepEqual(calls.at(-1), ['resetPasswordForEmail', 'test@example.test', {
    redirectTo:'http://localhost:5173/?auth_action=reset'
  }])
})

test('resend and reset failures return sanitized messages', async () => {
  await startAuth(createAuthClient())
  apiError = { message:'internal SMTP credential rejected', status:429 }
  assert.match(await resendConfirmation('test@example.test'), /No fue posible reenviar/)
  assert.match(await requestPasswordReset('test@example.test'), /No fue posible iniciar la recuperación/)
  assert.doesNotMatch(await resendConfirmation('test@example.test'), /SMTP|credential|429/)
})

test('recovery event accepts password update only through the authenticated SDK session', async () => {
  const access = 'synthetic-access-token'
  const client = createAuthClient()
  session = { access_token:access, user:{ id:'user-test' } }
  await startAuth(client)
  assert.equal(authState.user.id, 'user-test')
  assert.deepEqual(authHeaders(), { Authorization:`Bearer ${access}` })

  authListener('PASSWORD_RECOVERY', session)
  assert.equal(authState.recovery, true)
  assert.equal(await updatePassword('NewSecurePass2'), '')
  assert.deepEqual(calls.at(-1), ['updateUser', { password:'NewSecurePass2' }])
  assert.equal(authState.recovery, false)
  assert.equal(authState.passwordUpdated, true)

  await signOut()
  assert.deepEqual(calls.at(-1), ['signOut', { scope:'local' }])
  assert.deepEqual(authHeaders(), {})
  assert.equal(authState.user, null)
})

test('expired callback errors are translated to safe guidance', async () => {
  globalThis.window = { location:{ origin:'http://localhost:5173', search:'?error=access_denied&error_code=otp_expired' } }
  await startAuth(createAuthClient())
  assert.match(authState.linkError, /venci[oó] o ya fue utilizado/)
  assert.doesNotMatch(authState.linkError, /otp_expired|access_denied/)
})

test('auth screen provides resend and password confirmation states', async () => {
  const source = await readFile(new URL('../src/views/MikeView.vue', import.meta.url), 'utf8')
  assert.match(source, /authMode === 'confirmation' \? 'Reenviar correo'/)
  assert.match(source, /Confirmar contraseña<input v-model="confirmPassword"/)
  assert.match(source, /authState\.passwordUpdated \? 'Contraseña actualizada'/)
  assert.match(source, /authState\.linkError" role="alert"/)
})
