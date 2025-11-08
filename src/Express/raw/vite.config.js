import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // 监听 0.0.0.0，允许外网访问
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true
  },
  preview: {
    host: true // 预览同样对外可访问
  }
})


