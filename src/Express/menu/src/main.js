import { createApp, reactive } from 'vue'
import App from './App.vue'

const bootstrap = () => {
  const entry = typeof window !== 'undefined' && typeof window.__ENTRY__ !== 'undefined'
    ? String(window.__ENTRY__)
    : ''
  const app = createApp(App, { entry })
  app.mount('#app')
}

bootstrap()

