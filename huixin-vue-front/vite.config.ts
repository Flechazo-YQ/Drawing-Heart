import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: true,
    allowedHosts: [
      "4v22948452.eicp.vip",
      "1075oj69wr205.vicp.fun",
      'hkg1.efrp.399339.xyz',
      'localhost',
      '127.0.0.1',
      '101.132.253.65',  // 添加服务器IP
      '*.cpolar.top',
      '*.r15.cpolar.top',
      '218e05ad.r15.cpolar.top'
    ],
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
