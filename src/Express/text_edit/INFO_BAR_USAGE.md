# 信息提示栏使用说明

## 功能概述

在文本编辑器顶部添加了一个动态信息提示栏，用于向用户显示各种状态信息和提示。

## 功能特性

- ✅ 支持多种提示类型（info、warning、error、success、empty）
- ✅ 自动配色（不同类型有不同的背景色和图标）
- ✅ 可关闭提示（点击 × 按钮）
- ✅ 自动消失（可设置持续时间）
- ✅ 平滑动画（滑入滑出效果）
- ✅ 响应式设计（移动端适配）

## 提示类型

### 1. info（信息）
- 颜色：蓝色
- 图标：ℹ️
- 用途：一般信息提示

### 2. warning（警告）
- 颜色：橙色
- 图标：⚠️
- 用途：警告提示

### 3. error（错误）
- 颜色：红色
- 图标：❌
- 用途：错误提示

### 4. success（成功）
- 颜色：绿色
- 图标：✓
- 用途：成功提示

### 5. empty（空白）
- 颜色：紫色
- 图标：📝
- 用途：空文档提示

## 使用方法

### 方法 1：在 Vue 组件内部使用

在 App.vue 的 `<script setup>` 中可以直接调用 `showInfo()` 函数：

```javascript
// 显示信息提示（3秒后自动消失）
showInfo('文档类型: markdown', 'info', true, 3000)

// 显示警告（5秒后自动消失）
showInfo('文件较大，保存可能需要时间', 'warning', true, 5000)

// 显示错误（不自动消失）
showInfo('加载失败: 网络错误', 'error', true, 0)

// 显示成功（3秒后自动消失）
showInfo('保存成功！', 'success', true, 3000)

// 显示空文档提示（5秒后自动消失）
showInfo('当前文档为空，开始编辑吧 📝', 'empty', true, 5000)
```

### 方法 2：从外部 JavaScript 调用

信息提示功能已暴露到 `window` 对象，可以从任何地方调用：

```javascript
// 在浏览器控制台或其他脚本中
window.showEditorInfo('这是一条测试消息', 'info', true, 3000)
```

### 方法 3：从后端传递信息

后端可以在 API 响应中包含提示信息，前端自动显示：

```python
# Python 后端示例
return {
    "content": "文档内容...",
    "mime": "markdown",
    "info": {
        "message": "这是一个 Markdown 文档",
        "type": "info",
        "duration": 3000
    }
}
```

然后在 `loadNote()` 函数中处理：

```javascript
if (result.info) {
  showInfo(
    result.info.message, 
    result.info.type || 'info', 
    true, 
    result.info.duration || 3000
  )
}
```

## 函数签名

```javascript
showInfo(message, type = 'info', dismissible = true, duration = 0)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `message` | string | - | 要显示的消息内容（必需） |
| `type` | string | 'info' | 提示类型：'info', 'warning', 'error', 'success', 'empty' |
| `dismissible` | boolean | true | 是否可以手动关闭 |
| `duration` | number | 0 | 自动消失时间（毫秒），0 表示不自动消失 |

## 使用场景示例

### 1. 空文档提示

```javascript
if (!content.value || content.value.trim() === '') {
  showInfo('当前文档为空，开始编辑吧 📝', 'empty', true, 5000)
}
```

### 2. MIME 类型提示

```javascript
if (mimeType && mimeType !== 'text') {
  showInfo(`文档类型: ${mimeType}`, 'info', true, 3000)
}
```

### 3. 加载失败提示

```javascript
catch (error) {
  showInfo(`加载失败: ${error.message}`, 'error', true, 5000)
}
```

### 4. 只读模式提示

```javascript
if (isReadOnly) {
  showInfo('当前文档为只读模式', 'warning', false, 0)
}
```

### 5. 保存成功提示

```javascript
if (saveResult.success) {
  showInfo('文档已保存 ✓', 'success', true, 2000)
}
```

### 6. 文件大小警告

```javascript
if (fileSize > 1024 * 1024) {
  showInfo('文件较大（>1MB），操作可能较慢', 'warning', true, 5000)
}
```

### 7. 协作提示

```javascript
if (hasOtherUsers) {
  showInfo('有 3 位用户正在同时编辑此文档', 'info', true, 0)
}
```

## 手动关闭提示

用户可以点击提示栏右侧的 × 按钮关闭提示（前提是 `dismissible` 设置为 `true`）。

也可以通过代码手动关闭：

```javascript
dismissInfo()
```

## 样式定制

如果需要自定义样式，可以修改 `App.vue` 中的 `.info-bar` 相关样式：

```css
/* 自定义信息栏高度 */
.info-bar {
  padding: 12px 15px; /* 增加内边距 */
}

/* 自定义颜色 */
.info-bar.info {
  background-color: #your-color;
  color: #your-text-color;
}
```

## 注意事项

1. **同时只显示一条提示**：新的提示会替换旧的提示
2. **自动清理**：组件销毁时会自动清理定时器
3. **性能友好**：使用 CSS 动画，性能良好
4. **移动端适配**：在小屏幕设备上自动调整大小和间距

## 开发建议

1. **保持简洁**：提示消息应该简短明了
2. **使用合适的类型**：根据实际情况选择正确的提示类型
3. **设置合理的持续时间**：
   - 一般信息：3-5秒
   - 警告：5-8秒
   - 错误：不自动消失或 8-10秒
   - 成功：2-3秒
4. **避免过度使用**：不要在用户操作时频繁弹出提示

## 测试

在浏览器控制台中测试：

```javascript
// 测试所有类型
window.showEditorInfo('这是信息提示', 'info', true, 3000)
window.showEditorInfo('这是警告提示', 'warning', true, 3000)
window.showEditorInfo('这是错误提示', 'error', true, 3000)
window.showEditorInfo('这是成功提示', 'success', true, 3000)
window.showEditorInfo('这是空文档提示', 'empty', true, 3000)
```

