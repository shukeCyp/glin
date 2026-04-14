# Glin 渠道文档

这份文档索引服务两个场景：

- 你要新增或修复某个渠道实现，需要快速定位它的认证方式、请求体和结果解析规则。
- 你要核对设置项、Base URL 或 provider 标识，确认前端参数和后端实现有没有对齐。

如果你只是第一次了解项目，先看仓库根目录的 [README.md](../README.md)；如果你已经在改渠道逻辑，这里就是入口。

## 建议阅读顺序

1. 先看对应能力的 `overview.md`，理解这一类渠道的公共约定。
2. 再看具体 provider 文档，确认它相对公共协议的差异。
3. 最后对照代码实现，通常在 `app/services/{platform}/` 下找到对应类。

## 文档结构

```text
docs/
├── README.md
├── nanobanana/
│   ├── overview.md
│   ├── yunwu.md
│   ├── hetang.md
│   ├── xiaobanshou.md
│   └── bandianwa.md
├── sora2/
│   ├── overview.md
│   ├── dayangyu.md
│   ├── yunwu.md
│   ├── xiaobanshou.md
│   └── bandianwa.md
└── veo/
    ├── hetang.md
    ├── xiaobanshou.md
    ├── bandianwa.md
    └── zyg.md
```

## 按能力查看

### NanoBanana 图片生成

先读总览：[nanobanana/overview.md](./nanobanana/overview.md)

| 渠道 | provider | 默认 Base URL | 接口风格 | 文档 |
|------|----------|---------------|----------|------|
| 云雾 | `yunwu` | `https://yunwu.ai` | Gemini generateContent 接口 | [yunwu.md](./nanobanana/yunwu.md) |
| 荷塘 | `hetang` | 用户自定义 | OpenAI 兼容 SSE | [hetang.md](./nanobanana/hetang.md) |
| 小搬手 | `xiaobanshou` | `https://api.xintianwengai.com` | 异步任务轮询 | [xiaobanshou.md](./nanobanana/xiaobanshou.md) |
| 斑点蛙 | `bandianwa` | `https://api.hellobabygo.com` | 异步任务轮询 | [bandianwa.md](./nanobanana/bandianwa.md) |

### Sora2 视频生成

先读总览：[sora2/overview.md](./sora2/overview.md)

| 渠道 | provider | 默认 Base URL | 模式 | 文档 |
|------|----------|---------------|------|------|
| 大洋鱼 | `dayangyu` | `https://api.dyuapi.com` | 创建任务 + 轮询状态 | [dayangyu.md](./sora2/dayangyu.md) |
| 云雾 | `yunwu` | `https://yunwu.ai` | 创建任务 + 轮询状态 | [yunwu.md](./sora2/yunwu.md) |
| 小搬手 | `xiaobanshou` | `https://api.xintianwengai.com` | 创建任务 + 轮询状态 | [xiaobanshou.md](./sora2/xiaobanshou.md) |
| 斑点蛙 | `bandianwa` | `https://api.hellobabygo.com` | 创建任务 + 轮询状态 | [bandianwa.md](./sora2/bandianwa.md) |

### VEO3 视频生成

| 渠道 | provider | 默认 Base URL | 接口风格 | 文档 |
|------|----------|---------------|----------|------|
| 荷塘 | `hetang` | 用户自定义 | OpenAI 兼容 SSE | [hetang.md](./veo/hetang.md) |
| 小扳手 | `xiaobanshou` | `https://xibapi.com` | `multipart/form-data` 创建 + 异步任务轮询 | [xiaobanshou.md](./veo/xiaobanshou.md) |
| 斑点蛙 | `bandianwa` | `https://api.hellobabygo.com` | 异步任务轮询 | [bandianwa.md](./veo/bandianwa.md) |
| ZYG | `zyg` | `https://otuapi.com` | `multipart/form-data` 创建 + 异步任务轮询 | [zyg.md](./veo/zyg.md) |

## 公共约定

### 认证

所有渠道都使用 Bearer Token：

```http
Authorization: Bearer <API_KEY>
```

### 配置来源

所有 API Key、Base URL、模型偏好和下载配置都保存在 SQLite `Settings` 表中。文档里出现的“配置键”就是这张表里的 key。

### 前后端职责

- 前端负责选择 `platform`、`provider`、提示词、附件与用户偏好。
- `app/api.py` 负责参数接收与路由。
- `app/services/*` 负责把统一入参转换成各渠道所需的请求格式。
- 异步任务的轮询、失败恢复和自动下载由 `app/video_scanner.py` 负责。

## 配置键速查

| 配置键 | 用途 |
|--------|------|
| `yunwu_api_key` | 云雾 API Key，NanoBanana 与 Sora2 共用 |
| `yunwu_base_url` | 云雾 Base URL |
| `xiaobanshou_api_key` | 小搬手 API Key，NanoBanana、Sora2 与 VEO3 共用 |
| `xiaobanshou_base_url` | 小搬手 Base URL（当前主要用于既有 NanoBanana/Sora2 接入） |
| `dayangyu_api_key` | 大洋鱼 API Key |
| `dayangyu_base_url` | 大洋鱼 Base URL |
| `bandianwa_api_key` | 斑点蛙 API Key |
| `bandianwa_base_url` | 斑点蛙 Base URL |
| `zyg_api_key` | ZYG API Key |
| `hetang_veo_api_key` | 荷塘 API Key，VEO3 与 NanoBanana 共用 |
| `hetang_veo_base_url` | 荷塘 Base URL，VEO3 与 NanoBanana 共用 |

## 与代码的映射关系

改文档前后最好一起核对这几处：

| 文档维度 | 代码位置 |
|----------|----------|
| 默认 Base URL | `app/constants.py` |
| 注册平台与 provider | `app/services/media_generation.py` |
| 设置项读写 | `app/api.py`、`app/database.py` |
| 渠道实现 | `app/services/nanobanana/`、`app/services/sora2/`、`app/services/veo/` |

## 维护规则

- 新增 provider 时，必须同时补充文档索引和具体协议说明。
- 如果一个渠道沿用别家的协议，也要明确写出“继承自谁”和“差异点是什么”，不要只写“兼容”。
- 如果配置键、模型名或默认 Base URL 发生变化，文档与常量定义必须同一提交更新。
