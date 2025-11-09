<template>
  <div class="note-container">
    <!-- 头部 -->
    <header class="note-header">
      <h1 class="note-title">{{ noteTitle }}</h1>
    </header>

    <!-- 信息提示栏 -->
    <Transition name="info-slide">
      <div v-if="infoMessage" class="info-bar" :class="infoType">
        <span class="info-icon">{{ getInfoIcon(infoType) }}</span>
        <span class="info-text">{{ infoMessage }}</span>
        <button v-if="infoDismissible" @click="dismissInfo" class="info-close" aria-label="关闭提示">
          ×
        </button>
      </div>
    </Transition>

    <!-- 编辑器 -->
    <main class="note-editor">
      <textarea
        v-model="content"
        class="note-textarea"
        @keydown="handleKeyDown"
      ></textarea>
    </main>

    <!-- 底部工具栏 -->
    <footer class="note-footer">
      <div class="footer-left">
        <span class="word-count">{{ wordCount }} 字符</span>
        <span v-if="saveStatus" class="save-status" :class="{ 
          'saving': isSaving, 
          'success': saveStatus === '保存成功', 
          'error': saveStatus === '保存失败' 
        }">
          {{ saveStatus }}
        </span>
      </div>
      <div class="footer-right">
        <button @click="saveNote" class="btn btn-primary" :disabled="isSaving">
          {{ isSaving ? '保存中...' : '保存 (Ctrl+S)' }}
        </button>
        <button @click="clearNote" class="btn btn-secondary">
          清空
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 响应式数据
const content = ref(inlineContent)
const isSaving = ref(false)
const saveStatus = ref('')

// 信息提示栏数据
const infoMessage = ref('')
const infoType = ref('info') // 'info', 'warning', 'error', 'success'
const infoDismissible = ref(true)
let infoTimeout = null

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

// 信息提示栏方法
const showInfo = (message, type = 'info', dismissible = true, duration = 0) => {
  infoMessage.value = message
  infoType.value = type
  infoDismissible.value = dismissible
  
  // 清除之前的定时器
  if (infoTimeout) {
    clearTimeout(infoTimeout)
    infoTimeout = null
  }
  
  // 如果设置了持续时间，自动关闭
  if (duration > 0) {
    infoTimeout = setTimeout(() => {
      dismissInfo()
    }, duration)
  }
}

const dismissInfo = () => {
  infoMessage.value = ''
  if (infoTimeout) {
    clearTimeout(infoTimeout)
    infoTimeout = null
  }
}

const getInfoIcon = (type) => {
  const icons = {
    'info': 'ℹ️',
    'warning': '⚠️',
    'error': '❌',
    'success': '✓',
    'empty': '📝'
  }
  return icons[type] || icons.info
}

// 暴露给外部使用（可以通过 window 访问）
if (typeof window !== 'undefined') {
  window.showEditorInfo = showInfo
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
    let mimeType = ""
    
    if (result && typeof result === 'object') {
      // 优先使用content字段，然后text字段
      text = result.content || result.text || ""
      mimeType = result.mime || result.mimeType || ""
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
    
    // 显示信息提示
    if (!text || text.trim() === '') {
      showInfo('当前文档为空，开始编辑吧 📝', 'empty', true, 5000)
    } else if (mimeType && mimeType !== 'text') {
      showInfo(`文档类型: ${mimeType}`, 'info', true, 3000)
    }
    
  } catch (error) {
    console.error('加载文本文件失败:', error)
    content.value = ""
    showInfo(`加载失败: ${error.message}`, 'error', true, 5000)
  }
}

const saveNote = async () => {
  if (isSaving.value) return // 防止重复保存
  
  try {
    isSaving.value = true
    saveStatus.value = '保存中...'
    
    const fileId = getCurrentNoteId()
    const encodedContent = encodeURIComponent(content.value)
    
    const response = await fetch(`/api/${fileId}?op=set&content=${encodedContent}`, {
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
      saveStatus.value = '保存成功'
      // 3秒后清除状态
      setTimeout(() => {
        saveStatus.value = ''
      }, 3000)
    } else {
      console.error('保存失败:', result.message)
      saveStatus.value = '保存失败'
      setTimeout(() => {
        saveStatus.value = ''
      }, 3000)
    }
  } catch (error) {
    console.error('保存文本文件失败:', error)
    saveStatus.value = '保存失败'
    setTimeout(() => {
      saveStatus.value = ''
    }, 3000)
  } finally {
    isSaving.value = false
  }
}

const clearNote = () => {
  if (confirm('确定要清空文本内容吗？')) {
    content.value = ''
  }
}

// 处理键盘快捷键
const handleKeyDown = (event) => {
  const textarea = event.target
  const INDENT = '    ' // 4 个空格
  
  // Ctrl+S 保存
  if (event.ctrlKey && event.key === 's') {
    event.preventDefault()
    saveNote()
    return
  }
  
  // Tab 键处理
  if (event.key === 'Tab') {
    event.preventDefault() // 阻止默认的焦点切换行为
    
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    
    if (event.shiftKey) {
      // Shift+Tab: 减少缩进，确保空格数是 4 的倍数
      if (start === end) {
        // 没有选中文本，减少当前行的缩进
        const lineStart = content.value.lastIndexOf('\n', start - 1) + 1
        const lineEnd = content.value.indexOf('\n', start)
        const fullLine = content.value.substring(lineStart, lineEnd === -1 ? content.value.length : lineEnd)
        
        // 计算行首的空格数
        const leadingSpaces = fullLine.match(/^[ \t]*/)[0]
        let spaceCount = 0
        for (const char of leadingSpaces) {
          spaceCount += char === '\t' ? 4 : 1
        }
        
        if (spaceCount > 0) {
          // 减少到下一个 4 的倍数
          const newSpaceCount = Math.max(0, Math.floor((spaceCount - 1) / 4) * 4)
          const newIndent = ' '.repeat(newSpaceCount)
          const lineContent = fullLine.substring(leadingSpaces.length)
          
          const beforeLine = content.value.substring(0, lineStart)
          const afterLine = content.value.substring(lineEnd === -1 ? content.value.length : lineEnd)
          
          content.value = beforeLine + newIndent + lineContent + afterLine
          
          // 更新光标位置
          const cursorOffset = start - lineStart - leadingSpaces.length
          setTimeout(() => {
            textarea.selectionStart = textarea.selectionEnd = lineStart + newSpaceCount + Math.max(0, cursorOffset)
          }, 0)
        }
      } else {
        // 有选中文本，减少所有选中行的缩进
        const beforeSelection = content.value.substring(0, start)
        const afterSelection = content.value.substring(end)
        
        // 找到选中区域的起始行
        const selectionStart = beforeSelection.lastIndexOf('\n') + 1
        const selectionEnd = end
        
        // 获取选中区域的文本
        const textToProcess = content.value.substring(selectionStart, selectionEnd)
        
        // 对每一行减少缩进
        const lines = textToProcess.split('\n')
        const processedLines = lines.map(line => {
          const leadingSpaces = line.match(/^[ \t]*/)[0]
          let spaceCount = 0
          for (const char of leadingSpaces) {
            spaceCount += char === '\t' ? 4 : 1
          }
          
          if (spaceCount > 0) {
            const newSpaceCount = Math.max(0, Math.floor((spaceCount - 1) / 4) * 4)
            const newIndent = ' '.repeat(newSpaceCount)
            return newIndent + line.substring(leadingSpaces.length)
          }
          return line
        })
        
        const newText = processedLines.join('\n')
        const lengthDiff = textToProcess.length - newText.length
        
        content.value = content.value.substring(0, selectionStart) + newText + afterSelection
        
        // 更新选择区域
        setTimeout(() => {
          textarea.selectionStart = Math.max(selectionStart, start - Math.min(4, lengthDiff))
          textarea.selectionEnd = end - lengthDiff
        }, 0)
      }
    } else {
      // Tab: 增加缩进，对齐到 4 的倍数
      if (start === end) {
        // 没有选中文本，对齐到下一个 4 的倍数
        const lineStart = content.value.lastIndexOf('\n', start - 1) + 1
        const lineEnd = content.value.indexOf('\n', start)
        const fullLine = content.value.substring(lineStart, lineEnd === -1 ? content.value.length : lineEnd)
        
        // 计算行首的空格数
        const leadingSpaces = fullLine.match(/^[ \t]*/)[0]
        let spaceCount = 0
        for (const char of leadingSpaces) {
          spaceCount += char === '\t' ? 4 : 1
        }
        
        // 增加到下一个 4 的倍数
        const newSpaceCount = Math.ceil((spaceCount + 1) / 4) * 4
        const newIndent = ' '.repeat(newSpaceCount)
        const lineContent = fullLine.substring(leadingSpaces.length)
        
        const beforeLine = content.value.substring(0, lineStart)
        const afterLine = content.value.substring(lineEnd === -1 ? content.value.length : lineEnd)
        
        content.value = beforeLine + newIndent + lineContent + afterLine
        
        // 更新光标位置
        const cursorOffset = start - lineStart - leadingSpaces.length
        setTimeout(() => {
          textarea.selectionStart = textarea.selectionEnd = lineStart + newSpaceCount + Math.max(0, cursorOffset)
        }, 0)
      } else {
        // 有选中文本，为所有选中行增加缩进到 4 的倍数
        const beforeSelection = content.value.substring(0, start)
        const afterSelection = content.value.substring(end)
        
        // 找到选中区域的起始行
        const selectionStart = beforeSelection.lastIndexOf('\n') + 1
        const selectionEnd = end
        
        // 获取选中区域的文本
        const textToProcess = content.value.substring(selectionStart, selectionEnd)
        
        // 对每一行增加缩进
        const lines = textToProcess.split('\n')
        const processedLines = lines.map(line => {
          const leadingSpaces = line.match(/^[ \t]*/)[0]
          let spaceCount = 0
          for (const char of leadingSpaces) {
            spaceCount += char === '\t' ? 4 : 1
          }
          
          // 增加到下一个 4 的倍数
          const newSpaceCount = Math.ceil((spaceCount + 1) / 4) * 4
          const newIndent = ' '.repeat(newSpaceCount)
          return newIndent + line.substring(leadingSpaces.length)
        })
        
        const newText = processedLines.join('\n')
        const lengthDiff = newText.length - textToProcess.length
        
        content.value = content.value.substring(0, selectionStart) + newText + afterSelection
        
        // 更新选择区域
        setTimeout(() => {
          textarea.selectionStart = start + (start === selectionStart ? 4 : 0)
          textarea.selectionEnd = end + lengthDiff
        }, 0)
      }
    }
  }
}

// 全局键盘事件处理
const handleGlobalKeyDown = (event) => {
  // Ctrl+S 保存
  if (event.ctrlKey && event.key === 's') {
    event.preventDefault()
    saveNote()
  }
}

// 生命周期
onMounted(() => {
  // 检查是否有注入的通知栏信息
  if (typeof window !== 'undefined' && window.infoBarMessage) {
    const message = window.infoBarMessage || ''
    const type = window.infoBarType || 'info'
    const dismissible = window.infoBarDismissible !== false
    const duration = window.infoBarDuration || 0
    
    if (message) {
      showInfo(message, type, dismissible, duration)
    }
  }
  
  // 只有当useRequest为true时才从服务器加载note
  if (useRequest) {
    loadNote()
  }
  
  // 添加全局键盘事件监听
  document.addEventListener('keydown', handleGlobalKeyDown)
})

// 清理事件监听器
onUnmounted(() => {
  document.removeEventListener('keydown', handleGlobalKeyDown)
})
</script>

<style scoped>
/* 信息提示栏样式 */
.info-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  border-bottom: 1px solid transparent;
  font-size: 14px;
  pointer-events: auto;
  overflow: hidden;
}

/* 信息栏进入和离开动画 */
.info-slide-enter-active,
.info-slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.info-slide-enter-from {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.info-slide-enter-to {
  opacity: 1;
  max-height: 200px;
  padding-top: 10px;
  padding-bottom: 10px;
}

.info-slide-leave-from {
  opacity: 1;
  max-height: 200px;
  padding-top: 10px;
  padding-bottom: 10px;
}

.info-slide-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.info-bar.info {
  background-color: #e3f2fd;
  color: #1565c0;
  border-bottom-color: #90caf9;
}

.info-bar.warning {
  background-color: #fff3e0;
  color: #e65100;
  border-bottom-color: #ffb74d;
}

.info-bar.error {
  background-color: #ffebee;
  color: #c62828;
  border-bottom-color: #ef5350;
}

.info-bar.success {
  background-color: #e8f5e9;
  color: #2e7d32;
  border-bottom-color: #66bb6a;
}

.info-bar.empty {
  background-color: #f3e5f5;
  color: #6a1b9a;
  border-bottom-color: #ba68c8;
}

.info-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.info-text {
  flex: 1;
  font-weight: 500;
}

.info-close {
  background: transparent;
  border: none;
  color: inherit;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
  opacity: 0.6;
  flex-shrink: 0;
}

.info-close:hover {
  opacity: 1;
  background-color: rgba(0, 0, 0, 0.1);
}

.info-close:active {
  transform: scale(0.9);
}

.save-status {
  margin-left: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.save-status.saving {
  background-color: #e3f2fd;
  color: #1976d2;
  animation: pulse 1.5s infinite;
}

.save-status.success {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.save-status.error {
  background-color: #ffebee;
  color: #c62828;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.footer-left {
  display: flex;
  align-items: center;
}

/* 响应式设计 - 移动端 */
@media (max-width: 768px) {
  .info-bar {
    padding: 8px 10px;
    font-size: 13px;
  }
  
  .info-icon {
    font-size: 16px;
  }
  
  .info-close {
    font-size: 20px;
    width: 20px;
    height: 20px;
  }
}
</style>
