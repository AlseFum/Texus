# 快速开始

## 前置要求

- Python 3.10 或更高版本
- [uv](https://github.com/astral-sh/uv) - Python 包管理器

## 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 克隆项目

```bash
git clone <repository-url>
cd texus
```

## 启动服务器

使用提供的启动脚本：

```bash
chmod +x start.sh
./start.sh
```

或手动启动：

```bash
# 创建虚拟环境
uv venv

# 同步依赖
uv sync

# 启动服务器
uv run uvicorn --app-dir src app:app --reload --host 0.0.0.0 --port 7123
```

服务器将在 `http://localhost:7123` 启动。

## 下一步

- 阅读 [入门指南](getting-started.md) 了解基本概念
- 查看 [教程](tutorial.md) 学习如何使用各项功能
- 参考 [API 文档](api.md) 了解完整的 API 接口

