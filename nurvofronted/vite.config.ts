import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      // digiRunner WebSocket：/website/{siteName} → 容器 31080（見 WebSocketServer.java）
      '/website': {
        target: 'http://localhost:31080',
        changeOrigin: true,
        ws: true,
      },
      '/api': {
        target: 'http://localhost:31080',
        changeOrigin: true,
        ws: false,
      },
    },
  },
})
