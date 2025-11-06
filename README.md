# Texus

**Runnable Notepad** - 一个功能强大的可执行记事本系统，支持文本处理、脚本执行、内容生成和定时任务管理。

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![CI](https://github.com/<your-org>/texus/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/texus/actions)

## 目录

- [特性](#特性)
- [文档](#文档)
- [快速开始](#快速开始)

## 特性

### 🚀 核心功能

- **文本处理 (Text Port)**: 完整的文本读写和 API 访问功能
- **脚本执行 (Py Port)**: 安全的 Python 脚本执行环境，支持数据库操作
- **内容生成 (Gen Port)**: 基于模板的随机内容生成器
- **Meta 脚本 (Meta Port)**: 数据转换和处理脚本
- **定时任务 (Timer Port)**: 定时任务管理和随机脚本执行

### 💾 数据管理

- **轻量级数据库**: 键值存储系统，支持多表管理
- **自动备份**: 定期备份系统，支持恢复功能
- **MIME 类型管理**: 自动识别和关联文件类型

### 🎨 用户界面

- **Web 界面**: 基于 Vue.js 的现代化文本编辑器
- **API 接口**: 完整的 RESTful API 支持
- **静态资源**: 自动扫描和提供静态资源

### 🔧 技术特点

- **模块化架构**: 基于 Port 系统的灵活扩展机制
- **安全执行**: 受限的脚本执行环境
- **异步处理**: 基于 FastAPI 的高性能异步框架
- **智能缓存**: 自动缓存解析结果，提高性能

## 文档

详细的文档请查看 [docs](docs/) 目录：

- 📚 [快速开始](docs/quick-start.md) - 安装和启动指南
- 🎯 [入门指南](docs/getting-started.md) - 基本概念和第一个示例
- 📖 [教程](docs/tutorial.md) - 完整的使用教程
- 🔌 [API 文档](docs/api.md) - 完整的 API 参考
- 🤝 [贡献指南](docs/contributing.md) - 如何参与项目开发

## 快速开始

### 前置要求

- Python 3.10 或更高版本
- [uv](https://github.com/astral-sh/uv) - Python 包管理器

### 安装和启动

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone <repository-url>
cd texus

# 安装依赖并启动开发服务器（uv 脚本）
uv sync
uv run dev
```

服务器默认在 `http://localhost:8000` 启动（uv run dev）。

#### 前端（menu）构建

```bash
cd src/Express/menu
npm install
npm run build
```

构建产物将输出到 `src/Express/menu/dist/`，后端会自动提供 `/assets/*` 静态资源并渲染 `.menu` 页面。

详细说明请查看 [快速开始指南](docs/quick-start.md)。

---

**作者**: Alsefum  
**版本**: 1.0.0  
**许可证**: MIT
