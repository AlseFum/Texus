import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 说明：
// - 不设置 base（默认为 '/'），构建后的 index.html 将引用 /assets/*
// - 后端已提供 GET /assets/{path} 的静态资源服务
// - 构建产物输出到默认 dist/，后端会从 dist/index.html 读取并注入 /*!insert*/

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist',
    emptyOutDir: true
  }
})

