import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createServer } from 'vite'
import { createSSRApp, h, reactive } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { createRouter, createMemoryHistory } from 'vue-router'
import { defaultSearchFilters, legalAreas } from '../src/utils/searchFilters.js'
import { useNovaSearch } from '../src/composables/useNovaSearch.js'

test('the composer shows Filters beside NovaSearch only, including before the first search', async () => {
  const server = await createServer({ server:{ middlewareMode:true, hmr:false, port:0 }, appType:'custom', logLevel:'error', optimizeDeps:{ noDiscovery:true, include:[] } })
  try {
    const component = (await server.ssrLoadModule('/src/views/MikeView.vue')).default
    for (const tool of ['search', 'case', 'court', null]) {
      const router = createRouter({ history:createMemoryHistory(), routes:[
        { path:'/', component }, { path:'/cases', component }, { path:'/cases/:caseId', component }, { path:'/account', component }
      ] })
      await router.push(tool ? `/?tool=${tool}` : '/')
      await router.isReady()
      const app = createSSRApp({ render:() => h(component) })
      app.use(router)
      const html = await renderToString(app)
      if (tool === 'search') {
        assert.match(html, /Buscar · NovaSearch/)
        assert.match(html, /class="composer-filters"/)
        assert.match(html, />Filtros/)
      } else assert.doesNotMatch(html, /class="composer-filters"|>Filtros/)
    }
  } finally { await server.close() }
})

test('composer and NovaSearch share the actual area and vigency filters', async () => {
  const filters = reactive(defaultSearchFilters())
  let state
  const html = await renderToString(createSSRApp({ setup() { state = useNovaSearch(filters); return () => h('span', state.filters.modulo) } }))
  assert.equal(state.filters, filters)
  assert.match(html, /Todos/)
  assert.ok(legalAreas.includes('Derecho Laboral'))
  Object.assign(filters, { modulo:'Derecho Laboral', solo_vigentes:false, vigencia_explicit:true })
  assert.deepEqual({ ...state.filters }, { modulo:'Derecho Laboral', solo_vigentes:false, vigencia_explicit:true })
})
