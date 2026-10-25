import assert from 'node:assert/strict'
import test from 'node:test'
import { readFile } from 'node:fs/promises'
import { createServer } from 'vite'
import { createSSRApp, h } from 'vue'
import { renderToString } from 'vue/server-renderer'

test('Court processing keeps one stable card with real progress and Spanish stage states', async () => {
  const server = await createServer({ server:{ middlewareMode:true, hmr:false, port:0 }, appType:'custom', logLevel:'error', optimizeDeps:{ noDiscovery:true, include:[] } })
  try {
    const component = (await server.ssrLoadModule('/src/components/novacourt/PipelineProgress.vue')).default
    const stages = [
      { id:'intake', label:'Recepción', status:'completed' },
      { id:'facts', label:'Hechos', status:'running' },
      { id:'research', label:'Investigación', status:'skipped' },
      { id:'evidence', label:'Evidencia', status:'failed' }
    ]
    const render = props => renderToString(createSSRApp({ render:() => h(component, props) }))
    const active = await render({ progress:80, current:'Se revisan los hechos.', stages })
    const finished = await render({ progress:100, stages, complete:true })
    assert.match(active,/NovaCourt está analizando el caso/)
    assert.match(active,/aria-valuenow="80"/)
    assert.match(active,/80 % completado/)
    assert.equal((active.match(/class="stage-mark"/g)||[]).length,9)
    for (const text of ['Recepción','Hechos','Investigación','Evidencia','Riesgos',
      'Contraargumentos','Estrategia','Verificación de citas','Simulación argumentativa',
      'Completado','En proceso','Pendiente','No requerido','Requiere atención']) assert.ok(active.includes(text),text)
    assert.doesNotMatch(active,/>\s*(?:completed|running|pending|skipped|failed)\s*</)
    assert.match(finished,/Análisis judicial completado/)
    assert.match(finished,/aria-valuenow="100"/)
    assert.equal((finished.match(/class="stage-mark"/g)||[]).length,9)
    const css = await readFile(new URL('../src/components/novacourt/PipelineProgress.vue',import.meta.url),'utf8')
    assert.match(css,/min-height:430px/)
    assert.match(css,/grid-template-columns:repeat\(9,minmax\(0,1fr\)\)/)
    const view = await readFile(new URL('../src/views/NovaCourtView.vue',import.meta.url),'utf8')
    assert.match(view,/:progress="novaCourt\.progress\.value"/)
    assert.match(view,/@click="novaCourt\.cancel"/)
    assert.match(view,/warning\.message/)
  } finally { await server.close() }
})
