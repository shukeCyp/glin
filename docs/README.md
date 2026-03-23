# Glin 渠道接口文档

本目录收录所有对接渠道的接口说明，包含认证方式、请求格式、响应结构与参数枚举，供开发与调试参考。

---

## 目录结构

```
docs/
├── README.md                      # 本文件：总览索引
├── nanobanana/                    # NanoBanana 图片生成渠道
│   ├── overview.md                # 协议总览与公共约定
│   ├── yunwu.md                   # 云雾渠道（fal-ai 队列接口）
│   ├── hetang.md                  # 荷塘渠道（SSE 流式，自定义 Base URL）
│   └── xiaobanshou.md             # 小搬手渠道
├── sora2/                         # Sora2 视频生成渠道
│   ├── overview.md                # 协议总览与公共约定
│   ├── dayangyu.md                # 大洋鱼渠道
│   ├── yunwu.md                   # 云雾渠道
│   ├── xiaobanshou.md             # 小搬手渠道
│   └── bandianwa.md               # 斑点蛙渠道
└── veo/
    └── hetang.md                  # 荷塘渠道 VEO3（SSE 流式）
```

---

## 渠道速查表

### NanoBanana 图片生成

| 渠道 | 代码标识 | Base URL | 协议 | 文档 |
|------|---------|----------|------|------|
| 云雾 (YW) | `nanobanana/yunwu` | `https://yunwu.ai` | fal-ai 队列 | [查看](./nanobanana/yunwu.md) |
| 荷塘 | `nanobanana/hetang` | 用户自定义 | OpenAI 兼容 SSE | [查看](./nanobanana/hetang.md) |
| 小搬手 (XBS) | `nanobanana/xiaobanshou` | `https://api.xintianwengai.com` | OpenAI 兼容 SSE | [查看](./nanobanana/xiaobanshou.md) |

### Sora2 视频生成

| 渠道 | 代码标识 | Base URL | 文档 |
|------|---------|----------|------|
| 大洋鱼 (DYY) | `sora2/dayangyu` | `https://api.dyuapi.com` | [查看](./sora2/dayangyu.md) |
| 云雾 (YW) | `sora2/yunwu` | `https://yunwu.ai` | [查看](./sora2/yunwu.md) |
| 小搬手 (XBS) | `sora2/xiaobanshou` | `https://api.xintianwengai.com` | [查看](./sora2/xiaobanshou.md) |
| 斑点蛙 (BDW) | `sora2/bandianwa` | `https://api.hellobabygo.com` | [查看](./sora2/bandianwa.md) |

### VEO3 视频生成

| 渠道 | 代码标识 | Base URL | 文档 |
|------|---------|----------|------|
| 荷塘 | `veo3/hetang` | 用户自定义 | [查看](./veo/hetang.md) |

> **注意**：荷塘渠道的 VEO3 视频与 NanoBanana 图片生成**共用同一套 Base URL 和 API Key**，在设置页面统一配置。

---

## 公共认证方式

所有渠道均使用 **Bearer Token** 认证：

```http
Authorization: Bearer <API_KEY>
```

---

## 配置键速查

| 配置键 | 说明 |
|--------|------|
| `yunwu_api_key` | 云雾 API Key（图片 + 视频共用） |
| `yunwu_base_url` | 云雾 Base URL |
| `xiaobanshou_api_key` | 小搬手 API Key（图片 + 视频共用） |
| `xiaobanshou_base_url` | 小搬手 Base URL |
| `dayangyu_api_key` | 大洋鱼 API Key |
| `dayangyu_base_url` | 大洋鱼 Base URL |
| `bandianwa_api_key` | 斑点蛙 API Key |
| `bandianwa_base_url` | 斑点蛙 Base URL |
| `hetang_veo_api_key` | 荷塘 API Key（VEO3 + NanoBanana 共用） |
| `hetang_veo_base_url` | 荷塘 Base URL（VEO3 + NanoBanana 共用，用户自定义） |
