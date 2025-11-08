import { createApp } from 'vue'
import App from './App.vue'

const bootstrap = () => {
  const initial = (typeof window !== 'undefined' && typeof window.__RAW_TEXT__ !== 'undefined')
    ? String(window.__RAW_TEXT__)
    : ''
  const initialTitle = (typeof window !== 'undefined' && typeof window.__RAW_TITLE__ !== 'undefined')
    ? String(window.__RAW_TITLE__)
    : ''
  const app = createApp(App, { text: initial, title: initialTitle })
  app.mount('#app')
}

bootstrap()


