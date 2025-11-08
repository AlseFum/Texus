<template>
  <div class="container">
    <div class="card">
      <h1 v-if="title" class="title">{{ title }}</h1>
      <div class="text">{{ text }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, onMounted } from 'vue'

const props = defineProps({
  text: { type: String, default: '' },
  title: { type: String, default: '' }
})
const text = props.text
const title = computed(() => props.title)

const applyTitle = (t) => {
  if (typeof document !== 'undefined') {
    document.title = t && String(t).trim() ? String(t) : ' - '
  }
}

onMounted(() => applyTitle(title.value))
watch(title, (t) => applyTitle(t))
</script>

<style>
:root {
  color-scheme: light dark;
}

html,
body {
  width: 100%;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", Arial, "Noto Sans", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  color: #111;
  background: #f4f4f4;
}

.container {

  margin: 8px;
}

.card {
  background: #fff;
  border: none;
  border-radius: 4px;
  padding: 16px;
  /* 分层阴影，增强立体感 */
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.04),
    0 2px 6px rgba(0, 0, 0, 0.06),
    0 8px 20px rgba(0, 0, 0, 0.08),
    0 18px 40px rgba(0, 0, 0, 0.10);
  min-height: calc(90vh - 40px); /* 扣除上下 8px padding */
  display: flex;
  flex-direction: column;
}

.title {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 700;
  color: #222;
}

.text {
  white-space: pre-wrap;
  word-break: break-word;
  color: #333;
  flex: 1;
  overflow: auto;
  padding: 8px 0;
  line-height: 1.6;
}
</style>
