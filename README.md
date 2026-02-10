# Glin

pywebview + Vue (Vite) 桌面应用，带设备激活机制。

## 目录结构

```
Glin/
├── frontend/          # Vue 前端
├── static/            # 前端构建输出
├── data/              # SQLite 数据库 (glin.db)
├── logs/              # 日志文件
├── main.py            # 主程序入口
├── generate_code.py   # 激活码生成器（管理员用）
├── run.sh             # 启动脚本
└── requirements.txt   # Python 依赖
```

## 安装

```bash
cd frontend
npm install
cd ..

uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## 运行

```bash
./run.sh
```

## 激活流程

1. 用户启动应用，看到 **设备ID** 和 **挑战码**
2. 用户将 **设备ID** 发送给管理员
3. 管理员运行 `python generate_code.py <设备ID>` 生成激活码
4. 用户输入激活码完成激活

## 管理员：生成激活码

```bash
python generate_code.py <设备ID>
```

或交互式运行：

```bash
python generate_code.py
```
