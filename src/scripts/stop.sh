#!/bin/bash

# 停止服务器脚本

PORT=${1:-8000}

if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    lsof -ti:$PORT | xargs kill -9
fi

