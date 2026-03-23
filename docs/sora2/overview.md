# Sora2 视频生成 — 协议总览

Sora2 是基于 OpenAI Sora 2 模型的视频生成能力，支持**文生视频**和**图生视频**两种模式。  
所有渠道均采用**异步任务模式**：先创建任务获得 task_id，再轮询状态，等待完成后获取视频链接。

---

## 接口流程

```
1. 创建任务  →  POST /v1/videos
              返回 task_id
2. 轮询状态  →  GET /v1/videos/{task_id}
              等待 status = completed
3. 获取视频  →  video_url（直接下载）
```

> 云雾渠道的创建/查询接口路径不同，见[云雾文档](./yunwu.md)。

---

## 任务状态枚举

| API 返回值 | 含义 | 内部枚举 |
|-----------|------|----------|
| `pending` / `queued` | 排队等待 | `PENDING` |
| `processing` / `running` | 生成中 | `PROCESSING` |
| `success` / `succeeded` / `completed` / `done` | 已完成 | `COMPLETED` |
| `failed` / `error` / `cancelled` | 失败 | `FAILED` |

---

## 模型命名规则

| 渠道 | 文生视频模型格式 | 图生视频模型格式 |
|------|----------------|----------------|
| 大洋鱼 | `sora2-{orientation}` / `sora2-{orientation}-15s` | 同左 |
| 云雾 | `sora-2` | `sora-2-all` |
| 小搬手 | `sora-2-{orientation}-{duration}s` | 同左 |
| 斑点蛙 | `sora-2-{orientation}-{duration}s-guanzhuan` | 同左 |

| 参数 | 可选值 |
|------|--------|
| `orientation` | `portrait`（竖屏 9:16）/ `landscape`（横屏 16:9） |
| `duration` | `10` / `15`（秒，大洋鱼默认 10s） |

---

## 图生视频说明

| 渠道 | 上传方式 | 字段名 |
|------|---------|--------|
| 大洋鱼 | `multipart/form-data` 直传 | `input_reference` |
| 云雾 | 先上传图床获取 URL | `images[]` |
| 小搬手 | `multipart/form-data` 直传 | `input_reference` |
| 斑点蛙 | `multipart/form-data` 直传 | `input_reference` |

---

## 轮询策略

| 配置 | 值 |
|------|----|
| 轮询间隔 | 5 秒 |
| 最大等待时长 | 900 秒（15 分钟） |
| 超时行为 | 返回最后一次查询结果，标记失败 |

---

## 视频下载

任务完成后，`video_url` 为公网可访问链接，直接 HTTP GET 流式下载即可。

> 大洋鱼渠道额外提供 `GET /v1/videos/{task_id}/content` 接口，可直接获取视频二进制内容（适用于 URL 短时效场景）。

---

## 子渠道文档

- [大洋鱼渠道](./dayangyu.md) — `POST /v1/videos`，支持 `get_video_content`
- [云雾渠道](./yunwu.md) — 独立创建/查询接口，需图床上传
- [小搬手渠道](./xiaobanshou.md) — 与大洋鱼接口兼容
- [斑点蛙渠道](./bandianwa.md) — 继承大洋鱼协议，独立 Base URL
