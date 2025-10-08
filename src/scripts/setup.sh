#!/bin/bash

# 开发环境初始化脚本

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== NoteServer 开发环境初始化 ===${NC}"

# 检查 uv
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}正在安装 uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # 刷新环境变量
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}uv 安装失败，请手动安装${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ uv 已安装${NC}"

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    uv venv
fi

# 同步依赖
echo -e "${YELLOW}同步依赖...${NC}"
uv sync

# 创建必要的目录
mkdir -p logs
mkdir -p data

echo -e "${GREEN}=== 初始化完成 ===${NC}"
echo -e "运行 ${YELLOW}bash src/scripts/start.sh${NC} 启动服务器"

