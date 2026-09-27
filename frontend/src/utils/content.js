const labelFor = key => String(key)
  .replace(/([a-z])([A-Z])/g, '$1 $2')
  .replace(/[_-]+/g, ' ')
  .replace(/^./, character => character.toUpperCase())

export function normalizeRenderableContent(value, depth = 0, seen = new WeakSet()) {
  if (value === null || value === undefined) return ''
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)

  if (Array.isArray(value)) {
    if (seen.has(value)) return ''
    seen.add(value)
    return value
      .map(item => normalizeRenderableContent(item, depth + 1, seen))
      .filter(Boolean)
      .map(item => `${'  '.repeat(depth)}- ${item}`)
      .join('\n')
  }

  if (typeof value !== 'object' || seen.has(value)) return ''
  seen.add(value)

  return Object.entries(value)
    .map(([key, item]) => {
      const rendered = normalizeRenderableContent(item, depth + 1, seen)
      return rendered ? `**${labelFor(key)}**\n${rendered}` : ''
    })
    .filter(Boolean)
    .join('\n\n')
}

export function hasRenderableContent(value) {
  return Boolean(normalizeRenderableContent(value).trim())
}
