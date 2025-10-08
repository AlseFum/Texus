#!/bin/bash

# 停止服务器脚本

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PORT=${1:-8000}

echo "正在停止端口 $PORT 上的服务..."

if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    lsof -ti:$PORT | xargs kill -9
    echo -e "${GREEN}✓ 服务已停止${NC}"
else
    echo -e "${RED}端口 $PORT 上没有运行的服务${NC}"
fi

