# Glin — 万米霖带货神器

pywebview + Vue 3 (Vite) 桌面应用，集成多渠道图片生成（NanoBanana）和视频生成（VEO3 / Sora2），支持多渠道动态切换、设备激活机制、后台任务队列与自动重试，以及内置调试面板。

---

## 整体架构

```
┌──────────────────────────────────────────────────────────┐
│                   前端 (Vue 3 + Vite)                     │
│  App.vue → 侧边栏导航                                     │
│  ├── NanoBanana.vue   香蕉生图（多渠道）                   │
│  ├── GlinVeo.vue      VEO3 视频（荷塘渠道）                │
│  ├── VeoProduct.vue   VEO 带货                            │
│  ├── VeoQihao.vue     VEO 起号                            │
│  ├── VideoProduct.vue 视频带货（Sora2 队列）               │
│  ├── ImageGeneration  图片生成                            │
│  ├── ImageProcess     图片处理                            │
│  ├── Settings.vue     设置页面                            │
│  └── Debug.vue        调试面板（仅开发模式）               │
└────────────────────┬─────────────────────────────────────┘
                     │  window.pywebview.api.*
┌────────────────────▼─────────────────────────────────────┐
│                 app/api.py (pywebview JS API)             │
│  前后端唯一桥接层，所有 JS 调用均通过此类路由              │
└──┬──────────────┬──────────────┬────────────────┬────────┘
   │              │              │                │
┌──▼──┐     ┌────▼────┐   ┌─────▼──────┐  ┌─────▼──────┐
│ DB  │     │ 图片生成 │   │  视频生成   │  │  激活/设置  │
│(SQLite)│  │(NanoBanana)│ │(VEO/Sora2) │  │(activation)│
└─────┘     └─────────┘   └────────────┘  └────────────┘
```

### 通信模型

- **前端 → 后端**：`window.pywebview.api.方法名(参数)` 返回 Promise，后端同步/异步处理后返回 dict
- **后端 → 前端**：无主动推送，前端通过轮询（视频任务状态）或一次性调用获取结果
- **所有设置持久化**：SQLite `Settings` 表（key/value 结构），前端保存后立即生效，无需重启

---

## 目录结构

```
Glin/
├── main.py                    # 程序入口：初始化DB → 线程池 → 扫描器 → webview窗口
├── generate_code.py           # 激活码生成工具（管理员用）
├── run.sh                     # 开发启动脚本（含 GLIN_DEV_UI=1 调试模式）
├── requirements.txt           # Python 依赖
│
├── app/
│   ├── __init__.py            # 导出 Api 类和 logger
│   ├── api.py                 # pywebview JS API 桥接层（所有前后端交互入口）
│   ├── config.py              # 路径配置（BASE_DIR / DATA_DIR / LOGS_DIR / DB_PATH）
│   ├── constants.py           # 全局常量（ApiUrls / ModelProviders / SettingKeys）
│   ├── database.py            # SQLite CRUD（Settings + VideoTask 两张表）
│   ├── activation.py          # 设备ID生成 + 激活码校验
│   ├── logger.py              # 日志配置（按日期滚动，输出到 logs/）
│   ├── thread_pool.py         # 全局线程池（ThreadPoolExecutor，大小可配置）
│   ├── video_scanner.py       # 后台视频任务扫描器（5秒轮询 + 自动重试）
│   ├── debug_server.py        # 调试接口注册表
│   ├── debug.html             # 调试用静态页
│   │
│   └── services/
│       ├── media_generation.py    # 生成器注册表（MediaGenerationRegistry）
│       ├── nanobanana/            # NanoBanana 图片生成服务
│       │   ├── base.py            # NanoBananaBase 抽象基类 + NanoBananaResult
│       │   ├── yunwu.py           # 云雾渠道
│       │   ├── haotian.py         # 好田渠道
│       │   ├── xiaobanshou.py     # 小搬手渠道
│       │   └── glin.py            # 荷塘渠道（NanoBananaGlinCustom，自定义 Base URL）
│       ├── veo/                   # VEO3 视频生成服务
│       │   ├── base.py            # VeoBase 抽象基类 + VeoResult
│       │   ├── hetang.py          # 荷塘渠道（SSE 流式）
│       │   └── utils.py           # 视频下载工具函数
│       └── sora2/                 # Sora2 视频生成服务
│           ├── base.py            # Sora2Base 抽象基类 + Sora2Task + Sora2TaskStatus
│           ├── dayangyu.py        # 大洋鱼渠道
│           ├── yunwu.py           # 云雾渠道
│           ├── xiaobanshou.py     # 小搬手渠道
│           └── bandianwa.py       # 斑点蛙渠道
│
├── frontend/                  # Vue 3 + Vite 前端源码
│   └── src/
│       ├── App.vue            # 根组件：侧边栏导航 + 页面路由
│       ├── main.js            # Vue 入口
│       ├── style.css          # 全局主题 CSS 变量（多主题切换）
│       └── components/
│           ├── NanoBanana.vue # 香蕉生图页面
│           ├── GlinVeo.vue    # VEO3 视频生成页面
│           ├── VeoProduct.vue # VEO 带货工作流
│           ├── VeoQihao.vue   # VEO 起号工作流
│           ├── VideoProduct.vue   # 视频带货（Sora2 队列模式）
│           ├── VideoGeneration.vue # 视频批量生成
│           ├── ImageGeneration.vue # 图片批量生成
│           ├── ImageProcess.vue    # 图片处理（提示词 + 多渠道）
│           ├── Settings.vue   # 设置页面（主题 / 渠道 / API Key / 下载路径）
│           ├── Toast.vue      # 全局消息提示组件
│           └── Debug.vue      # 调试面板（仅 GLIN_DEV_UI=1 时可见）
│
├── static/                    # npm run build 输出目录（pywebview 加载此目录）
├── data/                      # SQLite 数据库文件（glin_v2.db）
└── logs/                      # 运行日志（按日期滚动）
```

---

## 启动流程

```
main.py
  │
  ├─ 1. init_db()              初始化 SQLite，写入默认 Base URL 配置
  ├─ 2. init_pool(size)        启动全局线程池（默认 10 线程，可在设置页调整）
  ├─ 3. start_scanner()        启动后台视频任务扫描器（daemon 线程）
  │      ├─ _resume_processing_tasks()  恢复上次未完成的视频任务
  │      └─ _scan_loop()               每 5 秒扫描 pending 任务并提交到线程池
  └─ 4. webview.create_window()  创建 pywebview 窗口，加载 static/index.html
```

---

## 核心模块说明

### `app/api.py` — 前后端桥接层

所有前端 JS 调用均通过 `window.pywebview.api.*` 映射到此类的方法。主要接口分组：

| 分组 | 方法 | 说明 |
|------|------|------|
| 激活 | `get_status()` `activate(code)` | 设备ID查询、激活码校验 |
| 设置 | `save_settings(dict)` `get_all_settings()` | 批量读写 SQLite Settings 表 |
| 图片处理 | `get_image_process_prompt()` `set_image_process_prompt()` | 图片处理提示词 |
| 图片生成 | `generate_image(...)` | 通过 MediaGenerationRegistry 路由到对应渠道 |
| 视频生成 | `generate_video(...)` | 通过 MediaGenerationRegistry 路由到对应渠道 |
| 视频任务 | `get_video_tasks()` `create_video_task()` `delete_video_task()` | VideoTask 队列管理 |
| 文件管理 | `select_folder()` `open_root_directory()` `open_download_directory()` | 文件夹操作 |
| 数据统计 | `get_data_status()` `get_download_status()` | 数据库/日志/下载文件大小 |
| 清理 | `clean_logs()` `clean_downloads()` | 日志和下载缓存清理 |
| 调试 | `debug_*_create()` `debug_*_query()` | 各渠道调试接口 |

### `app/database.py` — 数据持久化

两张表：

- **`Settings`**（key/value）：存储所有用户配置，包含 API Key、Base URL、主题、重试配置等
- **`VideoTask`**：视频批量生成任务队列，字段包括 `status`（pending/processing/completed/failed）、`remote_task_id`、`video_url`、`video_path`

启动时自动写入各渠道默认 Base URL（仅首次，不覆盖用户修改）：

| 渠道 | 默认 Base URL |
|------|---------------|
| 大洋鱼 (DYY) | `https://api.dyuapi.com` |
| 云雾 (YW) | `https://yunwu.ai` |
| 小搬手 (XBS) | `https://api.xintianwengai.com` |
| 好田 (HT) | `https://api.haoapi.top` |
| 斑点蛙 (BDW) | `https://api.hellobabygo.com` |
| 荷塘 | 无默认值（用户自行填写） |

### `app/services/media_generation.py` — 生成器注册表

`MediaGenerationRegistry` 统一管理所有图片/视频生成器，通过 `(platform, provider)` 二元组索引。

前端只需传入 `platform` 和 `provider`，后端自动路由到对应渠道的 `generate()` 方法，无需关心具体实现。

已注册的生成器：

| 类型 | platform | provider | 渠道 | 配置键 |
|------|----------|----------|------|--------|
| 图片 | nanobanana | yunwu | 云雾 | `yunwu_api_key` |
| 图片 | nanobanana | yunwu | 云雾 | `yunwu_api_key` + `yunwu_base_url` |
| 图片 | nanobanana | hetang | 荷塘 | `hetang_veo_api_key` + `hetang_veo_base_url` |
| 图片 | nanobanana | xiaobanshou | 小搬手 | `xiaobanshou_api_key` + `xiaobanshou_base_url` |
| 视频 | veo3 | hetang | 荷塘 VEO | `hetang_veo_api_key` + `hetang_veo_base_url` |
| 视频 | sora2 | dayangyu | 大洋鱼 | `dayangyu_api_key` + `dayangyu_base_url` |
| 视频 | sora2 | yunwu | 云雾 | `yunwu_api_key` + `yunwu_base_url` |
| 视频 | sora2 | xiaobanshou | 小搬手 | `xiaobanshou_api_key` + `xiaobanshou_base_url` |
| 视频 | sora2 | bandianwa | 斑点蛙 | `bandianwa_api_key` + `bandianwa_base_url` |

### `app/video_scanner.py` — 后台视频任务扫描器

Sora2 视频生成为异步任务模式（提交 → 轮询），扫描器在后台 daemon 线程中持续运行：

```
启动时:
  _resume_processing_tasks()  ── 恢复上次进程中断时的 processing 状态任务
       ├─ 有 remote_task_id → 直接进入轮询阶段
       └─ 无 remote_task_id → 重置为 pending 重新提交

运行时（每 5 秒）:
  扫描 pending 任务 → 逐个提交到线程池 → _process_task()
       ├─ 1. 获取 Sora2 服务实例（根据 sora2_model 设置选择渠道）
       ├─ 2. create_task() 提交到上游 API
       ├─ 3. 每 30 秒轮询一次，最多 60 次（共 30 分钟）
       ├─ 4. 完成 → 更新 DB status=completed，自动下载视频到本地
       └─ 5. 失败 → 根据 auto_retry 配置最多重试 N 次
```

视频下载策略（优先级）：
1. 若上游支持 `get_video_content()` API（大洋鱼渠道）→ 通过 API 下载原始数据
2. 否则 → 直接 HTTP GET `video_url` 流式下载

### `app/thread_pool.py` — 全局线程池

`ThreadPoolExecutor` 单例，大小默认 10，可在设置页配置（修改后重启生效）。视频任务扫描器和图片生成任务均通过 `submit_task()` 提交到此线程池异步执行。

### `app/activation.py` — 设备激活

- 设备ID：基于硬件信息生成唯一标识，存入 SQLite
- 激活码：管理员用 `generate_code.py` 对设备ID进行 HMAC 签名生成，客户端校验签名
- 激活状态持久化在 `Settings` 表中

---

## 图片生成：NanoBanana

统一抽象基类 `NanoBananaBase`，子类实现 `generate()` 方法，输出 `NanoBananaResult`（含 `image_data` base64、`mime_type`、`file_path` 本地路径）。

所有渠道均基于 OpenAI 兼容的 `POST /v1/chat/completions` SSE 流式接口，模型名称 `gemini-3.0-pro-image-{orientation}[-2k|-4k]`。

| 渠道 | 类名 | Base URL 默认值 | 所需配置 |
|------|------|----------------|---------|
| 云雾 (YW) | `NanoBananaYunwu` | `https://yunwu.ai` | `yunwu_api_key` |
| 好田 (HT) | `NanoBananaHaotian` | `https://api.haoapi.top` | `haotian_api_key` |
| 小搬手 (XBS) | `NanoBananaXiaobanshou` | `https://api.xintianwengai.com` | `xiaobanshou_api_key` |
| 荷塘 | `NanoBananaGlinCustom` | 用户自定义 | `hetang_veo_api_key` + `hetang_veo_base_url` |

支持参数：
- `aspect_ratio`：`9:16` / `16:9` / `1:1` / `4:3` / `3:4`
- `image_size`：`1K` / `2K` / `4K`
- `ref_images`：参考图列表（base64 + mime），支持图生图

---

## 视频生成：VEO3

统一基类 `VeoBase`，子类实现 `generate()` 方法，返回 `VeoResult`（含 `video_url`、`file_path`）。

荷塘渠道基于 OpenAI 兼容 SSE 流式接口，从响应中提取 `<video src='...'>` 标签获取视频链接。

| 渠道 | 所需配置 | 文生视频模型 | 图生视频模型 |
|------|---------|------------|------------|
| 荷塘 | `hetang_veo_api_key` + `hetang_veo_base_url` | `veo_3_1_t2v_fast_{portrait\|landscape}` | `veo_3_1_i2v_s_fast_{portrait_fl\|fl}` |

> 荷塘渠道的 VEO3 视频和 NanoBanana 图片生成共用同一套 Base URL 和 API Key。

---

## 视频生成：Sora2

统一基类 `Sora2Base`，分为"创建任务 `create_task()`"和"查询任务 `query_task()`"两阶段，支持文生视频与图生视频。

| 渠道 | 类名 | Base URL 默认值 | 所需配置 | 支持模型 |
|------|------|----------------|---------|---------|
| 大洋鱼 (DYY) | `Sora2Dayangyu` | `https://api.dyuapi.com` | `dayangyu_api_key` | `sora2-portrait` / `sora2-landscape` / `sora2-portrait-15s` / `sora2-landscape-15s` |
| 云雾 (YW) | `Sora2Yunwu` | `https://yunwu.ai` | `yunwu_api_key` | `sora-2` / `sora-2-all` |
| 小搬手 (XBS) | `Sora2Xiaobanshou` | `https://api.xintianwengai.com` | `xiaobanshou_api_key` | `sora-2-{orientation}-{duration}s` |
| 斑点蛙 (BDW) | `Sora2Bandianwa` | `https://api.hellobabygo.com` | `bandianwa_api_key` | `sora-2-{orientation}-{duration}s-guanzhuan` |

---

## 前端主题系统

主题通过 CSS 自定义属性（`--accent`、`--bg-card`、`--text-primary` 等）实现，`data-theme` attribute 挂载在 `<html>` 元素上。内置 7 套主题：暖奶油 / 暗夜玫瑰 / 森林 / 护眼 / 海洋蓝 / 午夜蓝 / 薰衣草，当前选中主题持久化到 SQLite。

---

## 调试面板

启动后在侧边栏点击「调试」进入，界面分三个标签页：

- **🍌 NanoBanana** — 选择图片渠道，填写 Prompt / 宽高比 / 清晰度，可上传参考图
- **🎬 VEO** — 选择视频渠道，填写 Prompt / 方向 / 时长，可上传参考图
- **🌊 Sora2** — 选择视频渠道，填写 Prompt / 方向 / 时长，可上传参考图

每个标签右侧实时预览生成结果（图片内联 / 视频播放），底部输出操作日志，生成完成后显示本地文件路径。

> 调试面板仅在 `GLIN_DEV_UI=1` 时可见（`run.sh` 自动设置）。

---

## 安装

```bash
# 安装前端依赖
cd frontend && npm install && cd ..

# 创建并激活 Python 虚拟环境
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## 运行

```bash
# 开发模式（含调试面板）
./run.sh

# 仅启动后端（前端需已构建）
python main.py
```

## 激活流程

1. 用户启动应用，看到 **设备ID**
2. 将设备ID 发送给管理员
3. 管理员运行 `python generate_code.py <设备ID>` 生成激活码
4. 用户输入激活码完成激活

---

## API Key 与 Base URL 配置

启动后进入「设置」页面，按渠道填入对应配置。所有渠道 Base URL 均持久化到数据库，有默认值的渠道首次启动自动写入，荷塘渠道需用户自行填写。

| 配置键 | 说明 | 默认值 |
|--------|------|--------|
| `yunwu_api_key` | 云雾 API Key（NanoBanana + Sora2 共用） | — |
| `yunwu_base_url` | 云雾 Base URL | `https://yunwu.ai` |
| `xiaobanshou_api_key` | 小搬手 API Key（NanoBanana + Sora2 共用） | — |
| `xiaobanshou_base_url` | 小搬手 Base URL | `https://api.xintianwengai.com` |
| `dayangyu_api_key` | 大洋鱼 API Key | — |
| `dayangyu_base_url` | 大洋鱼 Base URL | `https://api.dyuapi.com` |
| `bandianwa_api_key` | 斑点蛙 API Key | — |
| `bandianwa_base_url` | 斑点蛙 Base URL | `https://api.hellobabygo.com` |
| `haotian_api_key` | 好田 API Key | — |
| `haotian_base_url` | 好田 Base URL | `https://api.haoapi.top` |
| `hetang_veo_api_key` | 荷塘 API Key（VEO 视频 + NanoBanana 生图共用） | — |
| `hetang_veo_base_url` | 荷塘 Base URL（VEO 视频 + NanoBanana 生图共用，自定义） | — |
 