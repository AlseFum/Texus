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

// 检查是否需要从服务器请求数据
const useRequest = typeof window !== 'undefined' && window.inlineContent === undefined

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
  console.log("Loading text file", getCurrentNoteId())
  try {
    const response = await fetch(`/api/${getCurrentNoteId()}?op=get`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    console.log("API Response:", result)
    
    // 处理新的API响应格式
    let text = ""
    if (result && typeof result === 'object') {
      // 优先使用content字段，然后text字段
      text = result.content || result.text || ""
    } else if (typeof result === 'string') {
      text = result
    } else {
      text = String(result || "")
    }
    
    // 确保文本是字符串并处理编码
    text = String(text)
    
    // 处理URL编码的内容
    if (text.includes('%')) {
      try {
        text = decodeURIComponent(text)
      } catch (e) {
        console.warn('URL解码失败:', e)
      }
    }
    
    content.value = text
    
  } catch (error) {
    console.error('加载文本文件失败:', error)
    content.value = ""
    // 可以在这里显示错误提示
  }
}

const saveNote = async () => {
  try {
    const fileId = getCurrentNoteId()
    const encodedContent = encodeURIComponent(content.value)
    
    const response = await fetch(`/api/${fileId}?op=set&content=不是${encodedContent}`, {
      method: 'GET', // 后端使用GET方法处理set操作
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    console.log('Save response:', result)
    
    if (result.success) {
      console.log('保存成功，时间:', result.data.lastSaveTime)
      // 保存成功的反馈
    } else {
      console.error('保存失败:', result.message)
      // 保存失败的反馈
      alert(`保存失败: ${result.message}`)
    }
  } catch (error) {
    console.error('保存文本文件失败:', error)
    alert('保存失败，请检查网络连接')
  }
}

const clearNote = () => {
  if (confirm('确定要清空文本内容吗？')) {
    content.value = ''
  }
}

// 生命周期
onMounted(() => {
  // 只有当useRequest为true时才从服务器加载note
  if (useRequest) {
    loadNote()
  }
})
</script>
