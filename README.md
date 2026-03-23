# Glin

Glin 是一个基于 `pywebview + Vue 3` 的桌面应用，用来统一管理多渠道图片与视频生成能力。项目目前整合了 `NanoBanana` 图片生成、`Sora2` 视频生成、`VEO3` 视频生成，以及设备激活、任务队列、自动下载、失败重试和开发调试面板。

如果你第一次接手这个仓库，优先看这份 README；如果你要对接渠道协议，直接跳到 [docs/README.md](./docs/README.md)。

## 项目定位

这个项目本质上是一个“多渠道 AI 媒体生成工作台”：

- 对上游渠道屏蔽协议差异，把不同平台统一成一致的图片/视频生成接口。
- 对业务使用者提供桌面化交互界面，降低 API Key、Base URL、任务轮询和文件下载的使用门槛。
- 对开发者保留足够清晰的分层，让你可以单独替换渠道实现、扩展 provider，或只调整前端交互而不碰协议细节。

## 能做什么

- 统一接入多家图片/视频中转渠道，前端只关心平台与 provider，不关心底层协议差异。
- 支持同步返回型能力和异步任务型能力，异步任务会进入本地队列并由后台扫描器持续轮询。
- 所有配置持久化到 SQLite，包括 API Key、Base URL、主题、下载目录、重试策略等。
- 内置设备激活机制，客户端可展示设备 ID，管理员可通过 `generate_code.py` 生成激活码。
- 提供开发模式调试面板，便于单独验证渠道的创建任务、轮询查询和返回解析逻辑。

## 当前支持的渠道

| 能力 | 渠道 | 标识 |
|------|------|------|
| NanoBanana 图片生成 | 云雾 / 荷塘 / 小搬手 | `nanobanana/{provider}` |
| Sora2 视频生成 | 大洋鱼 / 云雾 / 小搬手 / 斑点蛙 | `sora2/{provider}` |
| VEO3 视频生成 | 荷塘 | `veo3/hetang` |

更细的请求格式、认证字段和响应结构见 [docs/README.md](./docs/README.md)。

## 技术栈

| 层级 | 技术 |
|------|------|
| 桌面壳 | `pywebview` |
| 前端 | `Vue 3` + `Vite` |
| 后端 | Python |
| 数据存储 | SQLite |
| 并发 | `ThreadPoolExecutor` |
| 网络请求 | `requests` |

这套组合的优点是依赖轻、调试直接、前后端边界清晰，适合这种“本地桌面壳 + 远程 API 聚合”的项目形态。

## 主要页面与工作流

前端不是单纯的设置面板，而是一组围绕图片/视频生成的业务工作流：

| 页面 | 作用 |
|------|------|
| `NanoBanana` | 多渠道图片生成，支持文生图和图生图 |
| `Sora2 视频` | 多渠道 Sora2 视频生成 |
| `VEO 视频` | 荷塘渠道的 VEO3 视频生成 |
| `Sora2 带货` | 面向带货场景的视频生成流程 |
| `VEO 带货` | 面向带货场景的 VEO 工作流 |
| `VEO 起号` | 起号素材生成流程 |
| `设置` | API Key、Base URL、主题、下载路径、重试策略等 |
| `调试` | 渠道联调页面，仅开发模式显示 |

如果你在查页面入口，优先看 [`frontend/src/App.vue`](/Users/chaiyapeng/Documents/Glin/frontend/src/App.vue)。

## 核心架构

项目结构很简单，真正需要先理解的是三层：

1. 前端层：`frontend/` 里的 Vue 应用负责页面、表单、任务展示和主题切换。
2. 桥接层：[`app/api.py`](/Users/chaiyapeng/Documents/Glin/app/api.py) 是前后端唯一入口，前端通过 `window.pywebview.api.*` 调用它暴露的方法。
3. 服务层：`app/services/` 下按能力拆分为 `nanobanana`、`sora2`、`veo`，由 `MediaGenerationRegistry` 统一注册和路由。

运行时流程：

1. `main.py` 初始化数据库、线程池和后台视频扫描器。
2. `pywebview` 加载 `static/index.html`，前端开始工作。
3. 前端通过 `window.pywebview.api.*` 调后端。
4. 后端把请求路由到具体渠道实现，并把结果写回 SQLite 或保存到本地文件。

## 数据与运行模型

理解这两个存储对象，基本就理解了应用运行方式：

| 存储对象 | 用途 |
|----------|------|
| `Settings` | 保存 API Key、Base URL、主题、下载目录、模型偏好、重试配置、激活状态等 |
| `VideoTask` | 保存异步视频任务的状态、远端任务 ID、结果 URL、本地文件路径等 |

运行时还有两条关键后台机制：

- 全局线程池：处理图片生成、视频生成和异步任务提交。
- 视频扫描器：每 5 秒扫描一次待处理视频任务，把 `pending` 任务提交到线程池执行。

这也是为什么 Sora2 一类能力即使应用重启，也可以靠数据库状态恢复任务处理。

## 快速开始

### 1. 安装 Python 依赖

项目没有复杂的 Python 打包配置，直接使用虚拟环境即可：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

如果你本地已经使用 `uv` 管理 Python，也可以继续沿用；仓库内的开发脚本默认就是这么跑的。

最小 Python 依赖在 [`requirements.txt`](/Users/chaiyapeng/Documents/Glin/requirements.txt) 中，目前比较轻量，主要包括：

- `pywebview`
- `peewee`
- `requests`

### 2. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 3. 构建前端

```bash
cd frontend
npm run build
cd ..
```

构建产物会输出到根目录的 `static/`，这是 `pywebview` 启动时加载的前端资源目录。

### 4. 启动应用

开发模式推荐直接使用仓库自带脚本：

```bash
./run.sh
```

这个脚本会做三件事：

1. 在 `frontend/` 下执行 `npm run build`
2. 激活 `.venv`
3. 注入 `GLIN_DEV_UI=1` 后运行 `uv run main.py`

如果你想手动启动：

```bash
source .venv/bin/activate
uv run main.py
```

首次启动如果没有激活，会先进入设备激活页。

## 激活流程

项目带有设备激活机制，适用于内部分发或受控交付场景。标准流程如下：

1. 用户首次启动应用，页面会展示设备 ID。
2. 用户把设备 ID 发给管理员。
3. 管理员运行 [`generate_code.py`](/Users/chaiyapeng/Documents/Glin/generate_code.py) 生成对应激活码。
4. 用户输入激活码后，激活状态写入本地 SQLite。

这个设计的关键点是：

- 设备 ID 在客户端生成并持久化。
- 激活状态也是本地持久化，不需要单独的远端授权服务。
- 管理员只需要使用激活码生成工具，不需要直接操作数据库。

## 配置说明

应用启动后，绝大多数使用问题都集中在设置页。你通常需要先配置这些内容：

| 类别 | 说明 |
|------|------|
| API Key | 每个渠道或一组共用渠道的访问令牌 |
| Base URL | 上游渠道基础地址，部分渠道有默认值，部分需要手动填写 |
| 模型偏好 | 如 Sora2 provider、方向、时长，NanoBanana 比例和清晰度 |
| 下载配置 | 下载目录、是否自动下载 |
| 重试配置 | 是否自动重试、图片/视频最大重试次数 |
| 界面配置 | 主题等前端表现项 |

几个容易混淆的约定：

- 云雾的图片和视频通常共用同一套 `API Key + Base URL`。
- 小搬手的图片和视频通常也共用一套配置。
- 荷塘的 `NanoBanana` 与 `VEO3` 共用 `hetang_veo_api_key` 和 `hetang_veo_base_url`。
- 荷塘默认没有 Base URL，需要用户手动填写。

## 常用开发入口

| 入口 | 作用 |
|------|------|
| [`main.py`](/Users/chaiyapeng/Documents/Glin/main.py) | 桌面应用启动入口 |
| [`app/api.py`](/Users/chaiyapeng/Documents/Glin/app/api.py) | pywebview JS API 桥接层 |
| [`app/services/media_generation.py`](/Users/chaiyapeng/Documents/Glin/app/services/media_generation.py) | 统一注册图片/视频生成器 |
| [`app/video_scanner.py`](/Users/chaiyapeng/Documents/Glin/app/video_scanner.py) | Sora2 异步任务轮询与自动重试 |
| [`frontend/src/App.vue`](/Users/chaiyapeng/Documents/Glin/frontend/src/App.vue) | 前端壳层与页面切换入口 |
| [`generate_code.py`](/Users/chaiyapeng/Documents/Glin/generate_code.py) | 管理员生成激活码的小工具 |

## 目录说明

```text
Glin/
├── app/                Python 后端、数据库、激活逻辑、渠道实现
├── docs/               各渠道接口文档与协议说明
├── frontend/           Vue 3 前端源码
├── static/             Vite 构建产物，供 pywebview 加载
├── data/               本地数据库与运行数据
├── logs/               运行日志
├── main.py             应用入口
├── run.sh              开发启动脚本
└── generate_code.py    激活码生成工具
```

`data/` 和 `logs/` 在开发模式下位于项目根目录；如果以后做成打包应用，路径会切换到系统应用数据目录，逻辑定义在 [`app/config.py`](/Users/chaiyapeng/Documents/Glin/app/config.py)。

## 渠道与配置约定

- 所有用户配置都保存在 SQLite `Settings` 表。
- Sora2 任务会写入 `VideoTask` 表，由后台扫描器恢复和轮询。
- 云雾和小搬手的图片/视频通常共用同一套 API Key 与 Base URL。
- 荷塘的 `NanoBanana` 和 `VEO3` 共用 `hetang_veo_api_key` 与 `hetang_veo_base_url`。

默认 Base URL 常量定义在 [`app/constants.py`](/Users/chaiyapeng/Documents/Glin/app/constants.py)。

## 常见开发场景

### 新增一个渠道

通常需要同时改这几层：

1. 在 `app/services/{platform}/` 下新增渠道实现。
2. 在 `app/services/media_generation.py` 注册 `platform/provider`。
3. 在设置页补充 API Key、Base URL 或模型配置项。
4. 在 [docs/README.md](./docs/README.md) 和对应子文档补协议说明。

### 只改前端页面

开发时可以先在 `frontend/` 里调整组件，但最终要记得重新构建：

```bash
cd frontend
npm run build
cd ..
```

因为桌面应用读取的是根目录 `static/`，不是 Vite 内存产物。

### 排查视频任务卡住

优先检查三处：

1. `Settings` 里当前选择的 provider 和 API Key 是否正确。
2. `logs/` 下最新日志里有没有扫描器或上游接口错误。
3. `VideoTask` 表里任务是否停留在 `pending`、`processing` 或已被标记为 `failed`。

## 测试与调试

仓库里有一组以渠道为单位拆分的测试文件，位于 `tests/`。当前更偏向集成验证，适合在你调整协议解析、字段映射或错误处理时做针对性回归。

如果要调试渠道请求，开发模式下会显示调试页面：

```bash
GLIN_DEV_UI=1 uv run main.py
```

## 文档导航

- [docs/README.md](./docs/README.md): 渠道文档总入口
- [docs/nanobanana/overview.md](./docs/nanobanana/overview.md): NanoBanana 协议总览
- [docs/sora2/overview.md](./docs/sora2/overview.md): Sora2 协议总览
- [docs/veo/hetang.md](./docs/veo/hetang.md): 荷塘 VEO3 详细说明

## 常见问题

### 为什么改了前端但桌面应用没变化？

因为 `pywebview` 读取的是构建后的 `static/` 目录。改完前端后需要重新执行 `cd frontend && npm run build`。

### 为什么本地有数据目录和日志目录？

开发模式下，数据库和日志默认直接写在项目根目录，方便调试；打包后则会切到系统应用数据目录。

### 为什么 Sora2 任务不是立刻返回结果？

因为这类能力本身就是异步任务模型。应用会先创建远端任务，再由后台扫描器轮询，完成后再下载文件并更新状态。

### 哪些地方最容易因为字段不一致出问题？

- 前端传给 `window.pywebview.api` 的参数结构
- `app/api.py` 的入参处理
- `app/services/*` 渠道实现里的字段映射
- 文档中记录的协议字段和真实代码没有同步更新

## 维护建议

- 新增渠道时，代码和文档要一起补：`app/services/*` 的实现、注册表配置、`docs/` 协议说明、设置页字段说明缺一不可。
- 任何会影响调用方的字段改动，都应该同步更新 `docs/README.md` 里的速查表。
- 如果你只改前端交互，不要忘记重新执行 `cd frontend && npm run build`，否则桌面壳加载的仍然是旧的 `static/` 资源。
