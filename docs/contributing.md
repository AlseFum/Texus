# 贡献指南

感谢您对 Texus 项目的关注！我们欢迎任何形式的贡献。

## 开发环境设置

1. **克隆仓库**:
   ```bash
   git clone <repository-url>
   cd texus
   ```

2. **创建虚拟环境**:
   ```bash
   uv venv
   ```

3. **安装依赖**:
   ```bash
   uv sync
   ```

4. **运行开发服务器**:
   ```bash
   uv run uvicorn --app-dir src app:app --reload --host 0.0.0.0 --port 7123
   ```

## 代码规范

- **Python 风格**: 遵循 PEP 8
- **类型提示**: 使用类型注解
- **文档字符串**: 为所有公共函数和类添加文档字符串
- **注释**: 解释复杂的逻辑

## 提交规范

提交信息应遵循以下格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**:
```
feat(Port): 添加新的 Gen Port 功能

实现了基于模板的内容生成器，支持随机选择和嵌套结构。

Closes #123
```

## 添加新的 Port

1. **创建 Port 类**:
   ```python
   from Common.base import FinalVis
   from .Text import Text
   
   class MyPort(Text):
       @staticmethod
       def access(pack) -> FinalVis:
           # 处理逻辑
           return FinalVis.of("text", result)
   ```

2. **注册到分发系统**:
   在 `src/Port/__init__.py` 中的 `dispatch()` 函数添加：
   ```python
   elif which == "myport":
       return MyPort
   ```

3. **编写文档**:
   - 在 `src/Port/README.md` 中添加说明
   - 在 `src/Port/Meta.py` 中添加帮助文档

## 添加新的 Express 渲染器

Express 模块支持通过插件机制添加新的渲染器，无需修改核心代码。

### 方法 1: 创建插件文件

在 `src/Express/` 目录下创建新的 Python 文件（如 `my_renderer.py`）：

```python
from Express import extract_str, HTMLResponse, get_template

def registry():
    """插件注册函数"""
    def render_my_type(v):
        # 提取内容
        content = extract_str(v)
        
        # 获取 payload（可选配置）
        payload = getattr(v, "payload", None)
        
        # 处理渲染逻辑
        html = get_template("my_renderer")  # 或自定义 HTML
        
        # 注入数据
        js_inject = f'var myData="{content}";'
        return HTMLResponse(content=html.replace("/*!insert*/", js_inject))
    
    return {
        "suffix": ["mytype"],  # 支持的文件类型
        "lambda": render_my_type
    }
```

### 方法 2: 前端 UI 组件开发

如果需要自定义 UI 界面：

1. **创建前端项目**:
   ```bash
   cd src/Express
   mkdir my_ui
   cd my_ui
   npm init -y
   npm install vue@next vite @vitejs/plugin-vue
   ```

2. **开发界面**:
   - 在 `src/` 目录创建 Vue 组件
   - 配置 `vite.config.js`
   - 确保构建输出到 `dist/` 目录

3. **构建生产版本**:
   ```bash
   npm run build
   ```

4. **在渲染器中引用**:
   ```python
   html = get_template("my_ui")
   ```

详细信息请参考 [Express 模块文档](../src/Express/README.md)。

## 前端开发指南

### 文本编辑器开发

文本编辑器位于 `src/Express/text_edit/`，基于 Vue 3 开发。

#### 开发环境设置

```bash
cd src/Express/text_edit
npm install
npm run dev
```

#### 项目结构

```
text_edit/
├── src/
│   ├── App.vue         # 主组件
│   ├── main.js         # 入口文件
│   └── style.css       # 全局样式
├── dist/               # 构建输出
├── index.html          # HTML 模板
├── package.json        # 依赖配置
└── vite.config.js      # Vite 配置
```

#### 构建生产版本

```bash
npm run build
```

构建后的文件会输出到 `dist/` 目录，自动被后端加载。

#### 添加新功能

1. **修改 Vue 组件** (`src/App.vue`)
2. **测试功能** (`npm run dev`)
3. **构建生产版本** (`npm run build`)
4. **重启后端服务器**查看效果

#### 样式规范

- 遵循现有的设计风格
- 使用响应式设计
- 支持移动端访问
- 保持界面简洁

### 通知栏功能

如需在渲染器中使用通知栏功能，通过 payload 传递配置：

```python
return FinalVis.of("text", payload={
    "text": "内容",
    "infoMessage": "提示信息",
    "infoType": "info",  # info/warning/error/success/empty
    "infoDismissible": True,
    "infoDuration": 5000  # 毫秒
})
```

详见 [Payload 使用方法](../src/Express/README.md#payload-使用方法)。

## 测试

运行测试（如果有）:

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_port.py
```

## Pull Request 流程

1. **创建分支**:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **提交更改**:
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

3. **推送分支**:
   ```bash
   git push origin feature/my-feature
   ```

4. **创建 Pull Request**:
   - 在 GitHub 上创建 PR
   - 描述更改内容和原因
   - 等待代码审查

## 问题报告

报告问题时请包含：

- **问题描述**: 清晰描述问题
- **复现步骤**: 如何重现问题
- **预期行为**: 应该发生什么
- **实际行为**: 实际发生了什么
- **环境信息**: Python 版本、操作系统等

## 许可

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。

## 贡献者

感谢所有为项目做出贡献的人！

