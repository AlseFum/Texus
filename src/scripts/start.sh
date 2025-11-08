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

# 端口占用检测函数（lsof + ss 双保险）
is_port_in_use() {
    local p=$1
    if lsof -Pi :$p -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    fi
    if ss -ltn 2>/dev/null | awk 'NR>1 {print $4}' | grep -qE "[:.]${p}(\s|$)"; then
        return 0
    fi
    return 1
}

# 自动选择可用端口（从 PORT 或 8000 开始，逐个 +1）
BASE_PORT=${PORT:-8000}
PORT=$BASE_PORT
MAX_TRIES=50
TRY=0
while is_port_in_use "$PORT"; do
    TRY=$((TRY+1))
    if [ "$TRY" -ge "$MAX_TRIES" ]; then
        echo -e "${RED}错误: 在 $BASE_PORT 起始范围内未找到可用端口（尝试 $MAX_TRIES 次）${NC}"
        exit 1
    fi
    PORT=$((PORT+1))
done
if [ "$PORT" != "$BASE_PORT" ]; then
    echo -e "${YELLOW}提示: 端口 $BASE_PORT 被占用，改用可用端口 $PORT${NC}"
else
    echo -e "${GREEN}✓ 使用端口 $PORT${NC}"
fi

# 如缺少前端构建产物且系统存在 npm，则自动构建 raw 前端
AUTO_BUILD_FRONTEND=${AUTO_BUILD_FRONTEND:-true}
RAW_DIST="src/Express/raw/dist/index.html"
if [ "$AUTO_BUILD_FRONTEND" = "true" ]; then
    if command -v npm >/dev/null 2>&1; then
        if [ ! -f "$RAW_DIST" ]; then
            echo -e "${YELLOW}检测到缺少 raw/dist，自动构建前端...${NC}"
            (cd src/Express/raw && npm install && npm run build) || echo -e "${YELLOW}raw 前端构建失败，继续启动后端${NC}"
        fi
    else
        echo -e "${YELLOW}缺少 npm，跳过前端构建${NC}"
    fi
fi

# 启动，若因端口占用失败则自动 +1 重试
ATTEMPT=0
while true; do
    uv run uvicorn --app-dir src app:app --reload --host 0.0.0.0 --port $PORT
    STATUS=$?
    if [ $STATUS -eq 0 ]; then
        exit 0
    fi
    # 仅在端口占用情况下重试
    if is_port_in_use "$PORT"; then
        ATTEMPT=$((ATTEMPT+1))
        if [ "$ATTEMPT" -ge "$MAX_TRIES" ]; then
            echo -e "${RED}错误: 连续 $MAX_TRIES 次端口冲突，停止重试${NC}"
            exit 1
        fi
        PORT=$((PORT+1))
        echo -e "${YELLOW}提示: 端口被占用，尝试改用端口 $PORT 重启...${NC}"
        continue
    fi
    # 其他错误直接退出
    exit $STATUS
done