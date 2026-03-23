# NanoBanana 图片生成 — 协议总览

NanoBanana 是基于 Google Gemini 图像模型的图片生成能力，支持文生图与图生图两种模式。  
各渠道均通过不同的中转平台代理同一套底层模型，接口风格分为两类：

| 接口风格 | 使用渠道 | 说明 |
|---------|---------|------|
| **fal-ai 队列接口** | 云雾 | 先提交任务，再轮询状态，最后拉取结果 |
| **OpenAI 兼容 SSE 流式** | 荷塘、小搬手 | 单次 POST，流式返回 Markdown 图片 |

---

## 公共模型命名规则（OpenAI 兼容接口）

```
gemini-3.0-pro-image-{orientation}{size_suffix}
```

| 参数 | 可选值 | 说明 |
|------|--------|------|
| `orientation` | `portrait` / `landscape` / `square` / `four-three` / `three-four` | 由 `aspect_ratio` 映射得出 |
| `size_suffix` | `""` / `-2k` / `-4k` | 由 `image_size` 映射得出 |

**宽高比 → orientation 映射：**

| `aspect_ratio` | `orientation` |
|----------------|---------------|
| `9:16` | `portrait` |
| `16:9` | `landscape` |
| `1:1` | `square` |
| `4:3` | `four-three` |
| `3:4` | `three-four` |

**清晰度 → size_suffix 映射：**

| `image_size` | `size_suffix` | 示例模型 |
|-------------|--------------|----------|
| `1K` | `""` | `gemini-3.0-pro-image-portrait` |
| `2K` | `-2k` | `gemini-3.0-pro-image-portrait-2k` |
| `4K` | `-4k` | `gemini-3.0-pro-image-portrait-4k` |

---

## 公共认证

所有渠道均使用 Bearer Token：

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

---

## 通用返回约定

- 图片以 **Markdown 格式** 内嵌在 SSE content 中：`![](data:image/png;base64,...)`
- 或以 **URL** 形式返回，需再次下载
- 失败时 `success: false`，`error_message` 包含具体原因

---

## 子渠道文档

- [云雾渠道](./yunwu.md) — fal-ai 队列接口
- [荷塘渠道](./hetang.md) — OpenAI 兼容 SSE，自定义 Base URL
- [小搬手渠道](./xiaobanshou.md) — OpenAI 兼容 SSE
