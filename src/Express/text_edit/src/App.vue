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
        @keydown="handleKeyDown"
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

// 处理 Tab 键缩进
const handleKeyDown = (event) => {
  const textarea = event.target
  const INDENT = '    ' // 4 个空格
  
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

// 生命周期
onMounted(() => {
  // 只有当useRequest为true时才从服务器加载note
  if (useRequest) {
    loadNote()
  }
})
</script>
