import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // 代理所有非静态资源请求到后端
      '^/(api|assets|health)/.*': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // 代理根路径下的其他请求（排除 Vite 自己的请求）
      '^/(?!src|node_modules|@vite|@id|@fs).*': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
