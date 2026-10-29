const PRIVATE_BROWSER_VARIABLE = /(?:SERVICE[_-]?ROLE|SECRET|PASSWORD|DATABASE|OPENAI|ZEP|SMTP|JWT|SUPABASE[_-]?KEY)/i

export function assertSafePublicEnvironment(environment) {
  const forbidden = Object.keys(environment || {}).filter((name) =>
    name.startsWith('VITE_') && PRIVATE_BROWSER_VARIABLE.test(name)
  )

  if (forbidden.length) {
    throw new Error(`Private variables cannot use the VITE_ prefix: ${forbidden.join(', ')}`)
  }
}
