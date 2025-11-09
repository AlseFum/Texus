# Express 模块

Express 模块负责管理数据的呈现形式，提供多种用户界面和渲染方式。目前主要提供网页形式的用户界面。现已支持插件机制，可按需扩展新的渲染器与 UI。

## 目录

- [文件结构](#文件结构)
- [核心功能](#核心功能)
  - [1. 渲染系统](#1-渲染系统)
  - [2. 内容提取](#2-内容提取)
  - [3. 模板系统](#3-模板系统)
- [Payload 使用方法](#payload-使用方法)
  - [1. Text/Note Payload](#1-textnote-payload)
  - [2. Raw Payload](#2-raw-payload)
  - [3. 通知栏配置](#3-通知栏配置)
- [用户界面组件](#用户界面组件)
  - [1. Text Edit (文本编辑器)](#1-text-edit-文本编辑器)
- [使用示例](#使用示例)
- [模板自定义](#模板自定义)
- [开发指南](#开发指南)
- [样式指南](#样式指南)
- [注意事项](#注意事项)
- [扩展](#扩展)
- [插件机制](#插件机制新增)

## 文件结构

```
Express/
├── __init__.py             # 主入口，提供渲染包装与插件注册加载
├── text_edit/              # 文本编辑器界面 (Vue.js)
│   ├── src/               # Vue 源码
│   ├── dist/              # 构建后的静态文件
│   └── package.json       # 前端依赖配置
└── README.md              # 本文档
```

## 核心功能

### 1. 渲染系统

Express 模块提供统一的渲染接口，支持多种 MIME 类型的呈现：

#### 支持的 MIME 类型

- **`raw`** - 原始文本显示
- **`text`** - 文本编辑器界面
- **`note`** - 记事本界面（与 text 相同）

#### 主要函数

```python
from Express import wrap, useRaw, useNote

# 包装渲染对象
rendered = wrap(renderee_object)

# 直接使用原始渲染
raw_html = useRaw(content)

# 使用记事本渲染
note_html = useNote(content)
```

### 2. 内容提取

`extract_str()` 函数用于从各种对象中提取字符串内容：

```python
from Express import extract_str

# 支持多种对象类型
content = extract_str(renderee_object)
```

提取优先级：
1. `to_raw()` 方法
2. `value` 属性
3. 字符串转换

### 3. 模板系统

#### 获取模板

```python
from Express import get_template

# 获取指定模板
html = get_template("text_edit")
```

#### 默认模板

当找不到指定模板时，使用 `RAW_HTML_TEMPLATE` 作为后备：

- 响应式设计
- 现代化 UI 风格
- 支持中文显示
- 简洁的卡片布局

## Payload 使用方法

Express 支持通过 `payload` 字典传递额外的配置参数，控制渲染行为和界面显示。

### 1. Text/Note Payload

文本编辑器支持通过 payload 传递文本内容和通知栏配置。

#### 基本使用

```python
from Common.base import FinalVis

# 简单文本渲染
content = FinalVis.of("text", "Hello World")

# 使用 payload 传递配置
vis = FinalVis.of("text", payload={
    "text": "这是文本内容",
    "infoMessage": "欢迎使用文本编辑器",
    "infoType": "info",
    "infoDismissible": True,
    "infoDuration": 5000
})
```

#### Payload 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | string | 否 | - | 文本内容（如果不指定，使用 `extract_str()` 提取） |
| `infoMessage` | string | 否 | - | 通知栏消息内容 |
| `infoType` | string | 否 | `"info"` | 通知类型：`info`/`warning`/`error`/`success`/`empty` |
| `infoDismissible` | boolean | 否 | `True` | 是否可关闭通知栏 |
| `infoDuration` | integer | 否 | `3000` | 自动关闭时间（毫秒，0表示不自动关闭） |

#### 完整示例

```python
from Common.base import FinalVis
from Express import wrap

# 创建带通知栏的文本对象
vis = FinalVis.of("text", payload={
    "text": """
# 项目说明

这是一个示例项目。

## 功能特性
- 支持 Markdown
- 自动保存
- 快捷键支持
    """,
    "infoMessage": "⚠️ 此文档为只读模式",
    "infoType": "warning",
    "infoDismissible": True,
    "infoDuration": 0  # 不自动关闭
})

# 渲染为 HTML 响应
html_response = wrap(vis)
```

### 2. Raw Payload

原始渲染器提供最基础的文本显示，payload 结构较为简单。

#### 基本使用

```python
from Common.base import FinalVis

# 简单原始文本
content = FinalVis.of("raw", "纯文本内容")

# 使用 payload
vis = FinalVis.of("raw", payload={
    "text": "这是原始文本"
})
```

#### Payload 字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `text` | string | 否 | - | 文本内容 |

### 3. 通知栏配置

文本编辑器支持在页面加载时显示通知栏，用于提示用户重要信息。

#### 通知类型

通知栏支持 5 种类型，每种类型有不同的颜色主题：

| 类型 | 颜色 | 适用场景 |
|------|------|----------|
| `info` | 蓝色 | 一般信息提示 |
| `warning` | 橙色 | 警告信息 |
| `error` | 红色 | 错误提示 |
| `success` | 绿色 | 成功提示 |
| `empty` | 紫色 | 空文档提示 |

#### 动画效果

通知栏支持平滑的进入和离开动画：
- 进入时：高度从 0 展开，同时淡入
- 离开时：高度收缩到 0，同时淡出
- 动画时长：300ms

#### 使用示例

```python
# 信息提示
vis = FinalVis.of("text", payload={
    "text": "配置文件内容",
    "infoMessage": "💡 提示：修改后需要重启服务",
    "infoType": "info",
    "infoDuration": 5000
})

# 警告提示
vis = FinalVis.of("text", payload={
    "text": "系统配置",
    "infoMessage": "⚠️ 警告：此配置会影响系统稳定性",
    "infoType": "warning",
    "infoDismissible": True,
    "infoDuration": 0  # 不自动关闭
})

# 错误提示
vis = FinalVis.of("text", payload={
    "text": "错误日志",
    "infoMessage": "❌ 文件加载失败，显示为空内容",
    "infoType": "error",
    "infoDuration": 8000
})

# 成功提示
vis = FinalVis.of("text", payload={
    "text": "已保存的内容",
    "infoMessage": "✓ 文件已成功保存",
    "infoType": "success",
    "infoDuration": 3000
})

# 空文档提示
vis = FinalVis.of("text", payload={
    "text": "",
    "infoMessage": "📝 当前文档为空，开始编辑吧",
    "infoType": "empty",
    "infoDuration": 5000
})
```

#### 高级用法：动态通知

```python
def render_file_with_status(filepath, status="success"):
    """根据文件状态显示不同的通知"""
    
    # 读取文件内容
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception as e:
        content = ""
        status = "error"
    
    # 根据状态配置通知
    notifications = {
        "success": {
            "message": "✓ 文件加载成功",
            "type": "success",
            "duration": 3000
        },
        "error": {
            "message": f"❌ 文件加载失败: {str(e)}",
            "type": "error",
            "duration": 0
        },
        "empty": {
            "message": "📝 文件为空",
            "type": "empty",
            "duration": 5000
        }
    }
    
    notification = notifications.get(status, notifications["success"])
    
    return FinalVis.of("text", payload={
        "text": content,
        "infoMessage": notification["message"],
        "infoType": notification["type"],
        "infoDismissible": True,
        "infoDuration": notification["duration"]
    })
```

## 用户界面组件

### 1. Text Edit (文本编辑器)

基于 Vue.js 3 构建的现代化文本编辑器。

#### 特性

- **实时编辑** - 支持实时文本编辑
- **自动保存** - 自动保存编辑内容
- **响应式设计** - 适配各种屏幕尺寸
- **快捷键支持** - 支持常用编辑快捷键
- **语法高亮** - 支持多种编程语言语法高亮

#### 开发

```bash
cd text_edit/
npm install
npm run dev      # 开发模式
npm run build    # 构建生产版本
```

#### 技术栈

- **Vue 3** - 前端框架
- **Vite** - 构建工具
- **现代 CSS** - 样式系统


## 使用示例

### 1. 基本渲染

```python
from Express import wrap
from Common.base import FinalVis

# 创建渲染对象
content = FinalVis.of("text", "Hello World")

# 包装为 HTML 响应
html_response = wrap(content)
```

### 2. 自定义渲染

```python
from Express import useNote, extract_str

# 直接使用记事本渲染
my_content = "This is my content"
html = useNote(my_content)
```

### 3. 内容提取

```python
from Express import extract_str

# 从复杂对象中提取文本
class MyObject:
    def __init__(self, value):
        self.value = value

obj = MyObject("Hello")
text = extract_str(obj)  # "Hello"
```

## 模板自定义

### 1. 添加新的 MIME 类型

```python
from Express import mimes

def myCustomRenderer(content):
    # 自定义渲染逻辑
    return HTMLResponse(content="<h1>Custom Render</h1>")

# 注册新的 MIME 类型
mimes["custom"] = myCustomRenderer
```

### 2. 创建新的 UI 组件

1. 在 `Express/` 目录下创建新的子目录
2. 开发前端应用（Vue/React/原生等）
3. 构建到 `dist/` 目录
4. 在 `__init__.py` 或插件中注册渲染函数

## 开发指南

### 1. 前端开发

每个 UI 组件都是独立的前端应用：

```bash
# 创建新的 UI 组件
mkdir Express/my_new_ui
cd Express/my_new_ui

# 初始化前端项目
npm init -y
npm install vue@next vite @vitejs/plugin-vue

# 开发
npm run dev
```

### 2. 构建部署

```bash
# 构建生产版本
npm run build

# 确保 dist/ 目录包含构建后的文件
```

### 3. 集成到 Express

在 `__init__.py` 中添加新的渲染函数：

```python
def useMyNewUI(v):
    html = get_template("my_new_ui")
    content = extract_str(v)
    # 处理内容...
    return HTMLResponse(content=html)
```

## 样式指南

### 1. 设计原则

- **简洁性** - 保持界面简洁明了
- **一致性** - 统一的视觉风格
- **响应式** - 适配各种设备
- **可访问性** - 支持键盘导航和屏幕阅读器

### 2. 颜色方案

```css
/* 主色调 */
--primary-color: #007bff;
--secondary-color: #6c757d;

/* 背景色 */
--bg-primary: #fafafa;
--bg-card: #ffffff;

/* 文字颜色 */
--text-primary: #111;
--text-secondary: #333;
```

### 3. 布局规范

- 最大宽度：720px
- 内边距：24px
- 卡片圆角：12px
- 阴影：轻微阴影效果

## 注意事项

1. **构建文件** - 确保所有 UI 组件都有构建后的 `dist/` 目录
2. **编码格式** - 所有模板文件使用 UTF-8 编码
3. **错误处理** - 模板加载失败时使用默认模板
4. **性能优化** - 静态资源应该被适当压缩和优化
5. **浏览器兼容** - 确保支持主流浏览器

## 扩展

Express 模块设计为可扩展的，可以通过“插件机制”轻松添加新的渲染方式和 UI 组件：

1. **新的 MIME 类型** - 使用注册表 `register_renderer()` 或插件的 `register()` 注册
2. **新的 UI 组件** - 创建独立的前端应用并在渲染器中引用其模板
3. **自定义渲染器** - 实现特定的渲染逻辑并注册到特定 MIME
4. **主题系统** - 支持多种视觉主题

## 插件机制（新增）

### 1. 插件能做什么
- 注册新的 MIME 渲染器（如 `markdown`、`chart`、`diagram` 等）
- 使用自身的模板、静态资源渲染内容
- 不需要修改核心 `Express/__init__.py`

### 2. 插件放哪
- 项目内置：直接把插件 Python 文件放到 `Express/` 根目录（除 `__init__.py` 之外的 `*.py` 都会被自动当作插件）
- 外部模块：编写独立 Python 包，在运行时通过环境变量加载

### 3. 插件接口（新版）
插件文件需导出一个 `registry()` 函数，返回一个字典：
- 必填字段 `offix`：声明占用的 mime 名称（字符串）
- 渲染函数字段（二选一）：`lambda` 或 `handler` 或 `render`，为可调用对象，入参为 `Renderee`，返回 HTML 字符串或 `HTMLResponse`

在 `Express/my_markdown.py`：

```python
from Express import extract_str, HTMLResponse, get_template

def registry():
    def render_markdown(v):
        text = extract_str(v)
        # 这里省略 markdown 转 HTML 的实现，可引入第三方库
        html = get_template("my_markdown")  # 或自定义模板路径
        return html.replace("/*!insert*/", f'text = {text!r};')  # 返回字符串亦可
    return {
        "offix": "markdown",
        "lambda": render_markdown  # 或使用 "handler"/"render" 作为键名
    }

```

旧版仍然支持（兼容）：

```python
def register(registry):
    registry.register_mime("markdown", lambda v: HTMLResponse(content="..."))
```

对应的前端资源（可选，用于模板）：
```
Express/my_markdown/dist/index.html
```

### 4. 如何加载插件
- 自动加载：`Express/` 根目录下的每个 `*.py` 文件（排除 `__init__.py`）若导出 `registry()` 或 `register(registry)` 会在启动时自动加载
- 环境变量加载外部插件：
  - 设置 `EXPRESS_PLUGINS="pkg1,pkg2.subpkg"`，系统会尝试导入这些模块并调用其 `registry()` 或 `register(registry)`

### 5. 运行时注册（非插件）
你也可以在任意地方动态注册：

```python
from Express import register_renderer
register_renderer("custom", my_renderer)
```