# Express 模块

Express 模块负责管理数据的呈现形式，提供多种用户界面和渲染方式。目前主要提供网页形式的用户界面。

## 文件结构

```
Express/
├── __init__.py           # 主入口文件，提供渲染和包装功能
├── text_edit/            # 文本编辑器界面 (Vue.js)
│   ├── src/             # Vue 源码
│   ├── dist/            # 构建后的静态文件
│   └── package.json     # 前端依赖配置
└── README.md            # 本文档
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
from protocol.types import FinalVis

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
4. 在 `__init__.py` 中注册渲染函数

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

Express 模块设计为可扩展的，可以轻松添加新的渲染方式和 UI 组件：

1. **新的 MIME 类型** - 在 `mimes` 字典中注册
2. **新的 UI 组件** - 创建独立的前端应用
3. **自定义渲染器** - 实现特定的渲染逻辑
4. **主题系统** - 支持多种视觉主题