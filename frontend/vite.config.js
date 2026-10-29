import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { assertSafePublicEnvironment } from './src/config/publicEnv.js'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  assertSafePublicEnvironment(loadEnv(mode, process.cwd(), ''))

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@locales': path.resolve(__dirname, '../locales')
      }
    },
    server: {
      port: 3000,
      open: true,
      proxy: {
        '/api': {
          target: 'http://localhost:5001',
          changeOrigin: true,
          secure: false
        }
      }
    }
  }
})
