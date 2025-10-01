<template>
  <div class="note-container">
    <!-- 头部 -->
    <header class="note-header">
      <h1 class="note-title">{{ noteTitle }}</h1>
    </header>

    <!-- 编辑器 -->
    <main class="note-editor">
      <textarea
        v-model="content"
        class="note-textarea"
      ></textarea>
    </main>

    <!-- 底部工具栏 -->
    <footer class="note-footer">
      <div class="footer-left">
        <span class="word-count">{{ wordCount }} 字符</span>
      </div>
      <div class="footer-right">
        <button @click="saveNote" class="btn btn-primary">
          保存
        </button>
        <button @click="clearNote" class="btn btn-secondary">
          清空
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 响应式数据
const content = ref(inlineContent)

// 计算属性
const noteTitle = computed(() => {
  const rawId = getCurrentNoteId()
  try {
    return decodeURIComponent(rawId)
  } catch {
    // 如果解码失败，返回原始值
    return rawId
  }
})

const wordCount = computed(() => {
  return content.value.length
})

// 方法
const getCurrentNoteId = () => {
  const path = window.location.pathname
  const parts = path.split('/')
  return parts[parts.length - 1] || 'default'
}

const loadNote = async () => {
  console.log("Loading note", getCurrentNoteId())
  try {
    const noteObj = await fetch(`/api/${getCurrentNoteId()}?op=get`).then(res => res.json())
    console.log("Got noteObj", noteObj)
    // 确保从对象中提取 text 字段，并且是字符串
    let text = ""
    if (typeof noteObj === 'object' && noteObj !== null && 'text' in noteObj) {
      // 从对象中提取 text 字段
      text = noteObj.text || ""
    } else if (typeof noteObj === 'string') {
      // 如果直接是字符串
      text = noteObj
    } else {
      // 其他情况转为字符串
      text = String(noteObj || "")
    }
    
    // 确保 text 是字符串
    text = String(text)
    
    // 尝试解码，防止多重编码（只在文本看起来被编码时才解码）
    if (text.includes('%')) {
      try {
        content.value = decodeURIComponent(text)
      } catch {
        // 如果解码失败，使用原始文本
        content.value = text
      }
    } else {
      // 没有编码标记，直接使用
      content.value = text
    }
  } catch (error) {
    console.warn('加载笔记失败:', error)
    content.value = ""
  }
}

const saveNote = async () => {
  try {
    const noteId = getCurrentNoteId()
    const encodedContent = encodeURIComponent(content.value)
    const response = await fetch(`/api/${noteId}?op=set&content=${encodedContent}`)
    const result = await response.json()
    
    if (result.success) {
      console.log('保存成功，时间:', result.data.lastSaveTime)
    } else {
      console.error('保存失败:', result.message)
    }
  } catch (error) {
    console.error('保存笔记失败:', error)
  }
}

const clearNote = () => {
  if (confirm('确定要清空笔记内容吗？')) {
    content.value = ''
  }
}

// 生命周期
onMounted(() => {
  loadNote()
})
</script>
