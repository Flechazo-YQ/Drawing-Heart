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
    host: '0.0.0.0', // 允许从任何IP访问
    port: 5173,
    allowedHosts: [
      "huixintongxue.com",
      "www.huixintongxue.com",
      "api.huixintongxue.com",
      "4v22948452.eicp.vip",
      "1075oj69wr205.vicp.fun",
      'hkg1.efrp.399339.xyz',
      'localhost',
      '127.0.0.1',
      '101.132.253.65',  // 添加服务器IP
      '192.168.2.10',    // 添加您的局域网IP
      '*.cpolar.top',
      '*.r15.cpolar.top',
      '218e05ad.r15.cpolar.top'
    ],
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          // 添加CORS头
          proxy.on('proxyRes', (proxyRes, req, res) => {
            proxyRes.headers['Access-Control-Allow-Origin'] = '*';
            proxyRes.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS';
            proxyRes.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization';
          });
        }
      },
      '/uploads': {
        target: process.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false
      },
      '/socket.io': {
        target: process.env.VITE_API_BASE_URL?.replace('http', 'ws') || 'ws://127.0.0.1:5000',
        ws: true,
        changeOrigin: true
      }
    }
  }
})
