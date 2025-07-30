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
  css: {
    // CSS代码分割优化
    devSourcemap: true
  },
  server: {
<<<<<<< HEAD
    host: true,
=======
    host: '0.0.0.0', // 允许从任何IP访问
    port: 5173,
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
    allowedHosts: [
      "4v22948452.eicp.vip",
      "1075oj69wr205.vicp.fun",
      'hkg1.efrp.399339.xyz',
      'localhost',
      '127.0.0.1',
      '101.132.253.65',  // 添加服务器IP
<<<<<<< HEAD
=======
      '192.168.2.10',    // 添加您的局域网IP
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
      '*.cpolar.top',
      '*.r15.cpolar.top',
      '218e05ad.r15.cpolar.top'
    ],
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
<<<<<<< HEAD
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/register': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/save': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
=======
        changeOrigin: true
>>>>>>> 7e7174f50028628ea41bb94a551956f5d3e33845
      },
      '/socket.io': {
        target: 'ws://127.0.0.1:5000',
        ws: true,
      }
    }
  }
})
