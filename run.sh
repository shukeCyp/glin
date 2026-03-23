#!/usr/bin/env bash
set -euo pipefail

# 编译前端
(
  cd frontend
  npm run build
)

# 激活虚拟环境并以调试模式启动
source .venv/bin/activate
export GLIN_DEV_UI=1
uv run main.py
