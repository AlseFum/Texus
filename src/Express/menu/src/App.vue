<template>
  <div class="container">
    <div class="card">
      <h1 class="title">{{ schema.title || entry || 'menu' }}</h1>
      <p class="desc">根据 PUB 表前缀 <span class="key">{{ entry }}</span> 自动生成的配置表单。</p>

      <form @submit.prevent="onSubmit">
        <div class="row two">
          <div v-for="f in schema.fields" :key="f.name" class="field">
            <label class="label">{{ f.name }}
              <span class="hint">（{{ f.type }}）</span>
            </label>

            <template v-if="f.type === 'boolean'">
              <label class="checkbox">
                <input type="checkbox" v-model="form[f.name]" />
                <span>启用</span>
              </label>
            </template>

            <template v-else-if="f.type === 'number'">
              <input type="number" v-model.number="form[f.name]" />
            </template>

            <template v-else>
              <input type="text" v-model.trim="form[f.name]" />
            </template>

            <div class="hint">键：<span class="key">{{ f.key }}</span></div>
          </div>
        </div>

        <div class="btns">
          <button type="submit">保存并应用</button>
          <button type="button" class="ghost" @click="reload">刷新</button>
        </div>
      </form>

      <div class="toast" v-if="message">{{ message }}</div>
      <div class="toast error" v-if="error">{{ error }}</div>

      <details class="list">
        <summary>当前提交内容（调试）</summary>
        <pre>{{ form }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'

const props = defineProps({ entry: { type: String, default: '' } })

const entry = props.entry
const schema = reactive({ title: '', fields: [] })
let form = reactive({})
const message = ref('')
const error = ref('')

const reload = async () => {
  message.value = ''
  error.value = ''
  try {
    const res = await fetch(`/api/${encodeURIComponent(entry)}.menu`)
    const json = await res.json()
    const data = json && json.value ? json.value : json
    schema.title = data.title || entry
    schema.fields = Array.isArray(data.fields) ? data.fields : []
    const next = {}
    for (const f of schema.fields) {
      if (f.type === 'boolean') next[f.name] = !!f.value
      else if (f.type === 'number') next[f.name] = (typeof f.value === 'number') ? f.value : Number(f.value || 0)
      else next[f.name] = (f.value ?? '').toString()
    }
    form = reactive(next)
  } catch (e) {
    error.value = '加载表单失败'
  }
}

const onSubmit = async () => {
  message.value = ''
  error.value = ''
  try {
    const params = new URLSearchParams()
    params.set('op', 'apply')
    for (const [k, v] of Object.entries(form)) {
      params.set(k, String(v))
    }
    const url = `/api/${encodeURIComponent(entry)}.menu?` + params.toString()
    const res = await fetch(url, { method: 'POST' })
    const json = await res.json()
    const data = json && json.value ? json.value : json
    if (data && data.success) {
      message.value = '已保存：' + (data.updated || []).join(', ')
    } else {
      error.value = '保存失败'
    }
  } catch (e) {
    error.value = '提交失败'
  }
}

onMounted(reload)
</script>

<style>
:root { color-scheme: light dark; }
html, body { height: 100%; }
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", Arial, "Noto Sans", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; color: #111; background: #fafafa; }
.container { max-width: 840px; margin: 0 auto; padding: 24px; }
.card { background: #fff; border: 1px solid #eaeaea; border-radius: 12px; padding: 20px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.title { margin: 0 0 16px; font-size: 20px; font-weight: 700; color: #222; }
.desc { margin: 0 0 24px; color: #666; font-size: 14px; }
form { display: grid; gap: 16px; }
.field { display: grid; gap: 6px; }
.label { font-size: 13px; color: #444; font-weight: 600; }
.hint { font-size: 12px; color: #888; }
input[type="text"], input[type="number"], textarea, select {
  width: 100%; box-sizing: border-box; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; background: #fff; color: #222; outline: none;
}
input[type="checkbox"] { width: 16px; height: 16px; }
textarea { min-height: 88px; resize: vertical; }
.row { display: grid; grid-template-columns: 1fr; gap: 16px; }
@media (min-width: 720px) { .row.two { grid-template-columns: 1fr 1fr; } }
.btns { display: flex; gap: 12px; margin-top: 8px; }
button { padding: 10px 14px; border-radius: 8px; border: 1px solid #ddd; background: #111; color: #fff; cursor: pointer; }
button.ghost { background: #fff; color: #111; }
.toast { margin-top: 12px; font-size: 13px; color: #0a7a0a; }
.error { color: #b00020; }
.list { margin-top: 12px; color: #999; font-size: 12px; }
.key { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
.checkbox { display:flex; align-items:center; gap:8px; }
</style>

