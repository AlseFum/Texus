#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== NoteServer 启动脚本 ===${NC}"

# 检查是否在项目根目录
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 检查 uv 是否安装
echo -e "${YELLOW}检查 uv...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${RED}错误: uv 未安装${NC}"
    echo "请访问 https://github.com/astral-sh/uv 安装 uv"
    echo "或运行: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo -e "${GREEN}✓ uv 已安装${NC}"

# 检查 Python 版本
echo -e "${YELLOW}检查 Python 版本...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.10"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}错误: 需要 Python >= $REQUIRED_VERSION, 当前版本: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 版本: $PYTHON_VERSION${NC}"

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}虚拟环境不存在，正在创建...${NC}"
    uv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 创建虚拟环境失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 虚拟环境已创建${NC}"
fi

# 同步依赖
echo -e "${YELLOW}同步依赖...${NC}"
uv sync
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 同步依赖失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 依赖已同步${NC}"

# 检查端口是否被占用
PORT=7123
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}警告: 端口 $PORT 已被占用${NC}"
    read -p "是否要杀死占用进程? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:$PORT | xargs kill -9
        echo -e "${GREEN}✓ 已清理端口 $PORT${NC}"
    else
        echo -e "${YELLOW}请手动处理端口占用或修改配置${NC}"
        exit 1
    fi
fi

uv run uvicorn --app-dir src server.main:app --reload --host 0.0.0.0 --port $PORT