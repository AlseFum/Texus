# 通知栏使用说明

text_edit 网页现在支持在文本框上方显示可关闭的通知栏，用于向用户提示重要信息。

## 功能特性

- ✅ 显示在文本框上方
- ✅ 可关闭（可配置）
- ✅ 支持自动关闭（可配置时长）
- ✅ 支持多种类型样式
- ✅ 平滑的动画效果
- ✅ 响应式设计（支持移动端）

## 通知类型

通知栏支持 5 种不同的类型，每种类型有不同的颜色和图标：

| 类型 | 图标 | 颜色 | 用途 |
|------|------|------|------|
| `info` | ℹ️ | 蓝色 | 一般信息提示 |
| `warning` | ⚠️ | 橙色 | 警告信息 |
| `error` | ❌ | 红色 | 错误信息 |
| `success` | ✓ | 绿色 | 成功信息 |
| `empty` | 📝 | 紫色 | 空文档提示 |

## 后端注入方式

### 方法 1: 通过 Payload 配置（推荐）

在 Port 层返回 `FinalVis` 时，在 payload 中添加通知栏配置：

```python
from Common.base import FinalVis

# 基本用法
return FinalVis.of("text", payload={
    "text": "文档内容",
    "infoMessage": "这是一条提示信息",
    "infoType": "info",
    "infoDismissible": True,
    "infoDuration": 5000  # 5秒后自动关闭
})

# 示例 1: 显示警告信息（不自动关闭）
return FinalVis.of("text", payload={
    "text": "文档内容",
    "infoMessage": "请注意：此文档正在被其他用户编辑",
    "infoType": "warning",
    "infoDismissible": True,
    "infoDuration": 0  # 0 表示不自动关闭
})

# 示例 2: 显示成功信息（3秒后自动关闭）
return FinalVis.of("text", payload={
    "text": "文档内容",
    "infoMessage": "文档已成功导入！",
    "infoType": "success",
    "infoDismissible": True,
    "infoDuration": 3000
})

# 示例 3: 显示错误信息（不可关闭，直到用户修复问题）
return FinalVis.of("text", payload={
    "text": "文档内容",
    "infoMessage": "文档格式有误，请检查后重试",
    "infoType": "error",
    "infoDismissible": False,  # 不可关闭
    "infoDuration": 0
})
```

### 方法 2: 直接在渲染器中注入（高级用法）

如果需要自定义渲染器，可以直接在 HTML 模板注入点设置变量：

```python
from Express import get_template, HTMLResponse

html = get_template("text_edit")

# 构建注入的 JavaScript
js_inject = f'''var inlineContent="{escaped_content}";
var infoBarMessage="欢迎使用文本编辑器！";
var infoBarType="success";
var infoBarDismissible=true;
var infoBarDuration=3000;'''

return HTMLResponse(content=html.replace("/*!insert*/", js_inject))
```

## Payload 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `infoMessage` | string | `""` | 通知消息内容（空字符串则不显示通知栏） |
| `infoType` | string | `"info"` | 通知类型：`info`、`warning`、`error`、`success`、`empty` |
| `infoDismissible` | boolean | `true` | 是否显示关闭按钮，允许用户手动关闭 |
| `infoDuration` | number | `0` | 自动关闭时间（毫秒），0 表示不自动关闭 |

## 实际应用场景

### 场景 1: 文档为空时的提示

```python
# 在 Port/Text.py 中
def getByWeb(pack) -> FinalVis:
    text_file = Text.get_data(pack.entry or pack.path)
    text_content = text_file.value.get("text", "")
    
    payload = {"text": text_content}
    
    # 如果文档为空，显示提示
    if not text_content or text_content.strip() == "":
        payload.update({
            "infoMessage": "当前文档为空，开始编辑吧 📝",
            "infoType": "empty",
            "infoDismissible": True,
            "infoDuration": 5000
        })
    
    return FinalVis.of("text", payload=payload)
```

### 场景 2: 文档类型提示

```python
def getByWeb(pack) -> FinalVis:
    text_file = Text.get_data(pack.entry or pack.path)
    text_content = text_file.value.get("text", "")
    
    payload = {"text": text_content}
    
    # 根据文档类型显示不同提示
    if pack.suffix == "md":
        payload.update({
            "infoMessage": "Markdown 文档 - 支持 Markdown 语法",
            "infoType": "info",
            "infoDismissible": True,
            "infoDuration": 3000
        })
    elif pack.suffix == "py":
        payload.update({
            "infoMessage": "Python 脚本 - 记得保持代码缩进",
            "infoType": "info",
            "infoDismissible": True,
            "infoDuration": 3000
        })
    
    return FinalVis.of("text", payload=payload)
```

### 场景 3: 权限警告

```python
def getByWeb(pack) -> FinalVis:
    text_file = Text.get_data(pack.entry or pack.path)
    text_content = text_file.value.get("text", "")
    
    payload = {"text": text_content}
    
    # 检查是否有编辑权限
    if not check_edit_permission(pack.user):
        payload.update({
            "infoMessage": "⚠️ 您只有只读权限，无法保存修改",
            "infoType": "warning",
            "infoDismissible": False,  # 不可关闭，持续提醒
            "infoDuration": 0
        })
    
    return FinalVis.of("text", payload=payload)
```

### 场景 4: 临时通知（快速消失）

```python
def getByWeb(pack) -> FinalVis:
    text_file = Text.get_data(pack.entry or pack.path)
    text_content = text_file.value.get("text", "")
    
    payload = {
        "text": text_content,
        "infoMessage": "文档加载成功！",
        "infoType": "success",
        "infoDismissible": True,
        "infoDuration": 2000  # 2秒后自动消失
    }
    
    return FinalVis.of("text", payload=payload)
```

## 前端调用方式

除了后端注入，前端也可以通过 JavaScript 调用通知栏：

```javascript
// 在浏览器控制台或前端代码中调用
window.showEditorInfo('这是一条消息', 'info', true, 3000)

// 参数说明：
// 1. message: 消息内容（string）
// 2. type: 类型（string: 'info'/'warning'/'error'/'success'/'empty'）
// 3. dismissible: 是否可关闭（boolean）
// 4. duration: 自动关闭时间，单位毫秒（number，0表示不自动关闭）
```

## 样式定制

通知栏的样式已经内置在 `App.vue` 中，包括：
- 响应式设计（适配移动端）
- 平滑的进入动画
- Hover 效果
- 不同类型的配色方案

如需自定义样式，可以修改 `src/App.vue` 中的 `.info-bar` 相关样式。

## 注意事项

1. **消息内容会被自动转义**：特殊字符（如引号、换行符等）会被正确处理
2. **空消息不显示**：如果 `infoMessage` 为空字符串，通知栏不会显示
3. **自动关闭与手动关闭**：设置了 `infoDuration` 后仍可手动关闭（如果 `infoDismissible` 为 true）
4. **多次调用会覆盖**：新的通知会替换旧的通知（包括清除旧的自动关闭定时器）

## 开发构建

修改前端代码后需要重新构建：

```bash
cd src/Express/text_edit
npm install  # 首次运行
npm run build  # 构建生产版本
```

构建后的文件会输出到 `dist/` 目录，Express 会自动使用最新的构建版本。

