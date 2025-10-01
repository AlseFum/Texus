# NoteServer

使用 FastAPI 构建的轻量级内容存储和展示服务。

## 🎯 项目概述

NoteServer 是一个基于 FastAPI 的内容管理系统，支持通过 Web 界面和 API 接口访问和展示文本内容、笔记等。项目采用模块化设计，具备简单的访问控制和内容分发机制。

## ✨ 核心功能

- **内容管理**：存储和管理文本内容、笔记
- **Web 界面**：响应式设计的网页展示界面
- **RESTful API**：提供标准化的 API 接口
- **访问控制**：支持公开和私有内容的权限管理
- **模块化架构**：清晰的代码组织和可扩展设计
## TODO
应该改为Access，Database，Express三大模块（改名而已
## 🏗️ 项目架构

```
src/
├── server/          # Web 服务器模块
│   └── main.py      # FastAPI 应用和路由
├── database/        # 数据存储模块
│   ├── database.py  # 内存数据库
│   └── __init__.py  # 数据库接口
├── media/           # 内容分发模块
│   └── __init__.py  # 媒体类型处理器
├── web/             # Web 界面模块
│   ├── __init__.py  # HTML 渲染
│   └── raw.html     # 页面模板
└── protocol/        # 协议定义模块
    ├── Access.py    # 访问控制类型
    └── types.py     # 数据类型定义
```

### 模块说明

#### Server 模块
- 基于 FastAPI 的 Web 服务器
- 处理所有 HTTP 请求和路由
- 提供健康检查接口：`/health`
- 支持动态路径访问

#### Database 模块
- **公开数据库** (`pubdb`)：存储可公开访问的内容
- **隐藏数据库** (`hiddb`)：存储需要权限验证的内容
- 提供统一的数据访问接口
- 可替换不同的服务器形式

#### Media 模块
- 内容类型分发器
- 支持多种媒体类型处理：
  - `Note`：普通笔记内容
  - `Authen`：需要认证的内容
- 访问权限控制和内容提取

#### Web 模块
- HTML 模板渲染引擎
- 使用简单而高效的模板替换机制
- 使用多个子page操作

#### Protocol 模块
- 定义系统中的数据结构
- 访问者类型：User、Script、Agent
- 访问平台：Web、API
- 内容类型定义

#### Scripts 模块
- 用于系统配置

## 🚀 快速开始

### 环境要求
- Python >= 3.10
- FastAPI >= 0.115.0
- uvicorn >= 0.30.0

### 安装依赖
```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 启动服务
```bash
# 开发模式
uvicorn src.server.main:app --reload

# 生产模式
uvicorn src.server.main:app --host 0.0.0.0 --port 8000
```

### 访问服务
- 主页：http://localhost:8000/
- 健康检查：http://localhost:8000/health
- API 文档：http://localhost:8000/docs

## 💡 使用示例

### 访问内容
- `GET /` - 访问首页，显示欢迎信息
- `GET /a` - 访问内容 "234"
- `GET /danshi` - 访问内容 "oh wo ai ni"

### 工作流程
1. 用户访问任意路径（如 `/example`）
2. 服务器解析路径和请求参数
3. Media 模块根据内容类型分发请求
4. 执行访问权限检查
5. 从数据库提取相应内容
6. Web 模块渲染 HTML 页面并返回

## 🔧 配置说明

### 数据库配置
在 `src/database/database.py` 中配置内容：

```python
pubdb = {
    "": {"public": True, "pagetype": "text", "value": "欢迎访问首页"},
    "your-path": "your-content",
    # 添加更多内容...
}
```

### 模板自定义
修改 `src/web/raw.html` 来自定义页面样式和布局。

## 📝 开发说明

### 添加新的内容类型
1. 在 `src/media/__init__.py` 中创建新的 Media 类
2. 实现 `access()` 和 `extract()` 方法
3. 在 `dispatch()` 函数中添加路由逻辑

### 扩展数据库
- 当前使用内存数据库，可以轻松替换为 SQLite、PostgreSQL 等
- 只需修改 `src/database/` 模块中的实现

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目！

## 📄 许可证

MIT License

## 计划
写note，shell，authen认证，文件夹
写monaco port，还有展示用的网页
完善架构