"""HT 渠道 NanoBanana 图片生成（OpenAI chat/completions + SSE 流式）"""

import base64
import json
import re

import requests

from ...constants import ApiUrls
from ...logger import logger
from .base import NanoBananaBase, NanoBananaResult


def _build_model_name(aspect_ratio: str, image_size: str) -> str:
    """根据宽高比和清晰度拼接模型名称"""
    # 方向映射
    if aspect_ratio in ("9:16", "1:1"):
        orientation = "portrait"
    else:
        orientation = "landscape"

    # 清晰度后缀
    size_suffix = ""
    if image_size == "2K":
        size_suffix = "-2k"
    elif image_size == "4K":
        size_suffix = "-4k"

    return f"gemini-3.0-pro-image-{orientation}{size_suffix}"


class NanoBananaHaotian(NanoBananaBase):
    """HT 渠道 NanoBanana 图片生成（OpenAI chat/completions SSE 流式）"""

    @property
    def provider_name(self) -> str:
        return "HT API"

    @property
    def base_url(self) -> str:
        return ApiUrls.GUANFANG

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = "9:16",
        image_size: str = "1K",
        **kwargs
    ) -> NanoBananaResult:
        """
        生成图片（通过 OpenAI 兼容的 chat/completions 接口 + SSE 流式）

        Args:
            prompt: 图片描述提示词
            aspect_ratio: 宽高比，可选 9:16 / 16:9 / 1:1
            image_size: 图片清晰度，可选 1K / 2K / 4K
            **kwargs: ref_image (base64), ref_mime_type

        Returns:
            NanoBananaResult: 生成结果
        """
        model = _build_model_name(aspect_ratio, image_size)
        url = f"{self.base_url.rstrip('/')}/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 构建 messages
        ref_image = kwargs.get("ref_image")
        ref_mime_type = kwargs.get("ref_mime_type", "image/jpeg")

        if ref_image:
            # 图生图：content 是数组
            content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{ref_mime_type};base64,{ref_image}"
                    }
                }
            ]
        else:
            # 文生图：content 是字符串
            content = prompt

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "stream": True,
        }

        try:
            logger.info(
                f"[{self.provider_name}] NanoBanana 生成请求 | "
                f"URL: {url} | model={model} | 比例: {aspect_ratio}, 清晰度: {image_size}"
            )
            logger.info(f"[{self.provider_name}] 模式: {'图生图' if ref_image else '文生图'}")

            resp = requests.post(url, headers=headers, json=payload, timeout=180, stream=True)
            logger.info(f"[{self.provider_name}] 响应状态码: {resp.status_code}")
            resp.raise_for_status()

            # 解析 SSE 流，收集所有 content 片段
            full_content = ""
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]  # 去掉 "data: " 前缀
                if data_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    choices = chunk.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        c = delta.get("content")
                        if c:
                            full_content += c
                except json.JSONDecodeError:
                    continue

            if not full_content:
                return NanoBananaResult(
                    success=False,
                    error_message="SSE 流中未收到 content 数据",
                )

            logger.info(f"[{self.provider_name}] SSE 完成, content 长度: {len(full_content)}")

            # 从 content 中提取图片：![Generated Image](...)
            return self._extract_image_from_content(full_content)

        except requests.exceptions.Timeout:
            logger.error(f"[{self.provider_name}] NanoBanana 请求超时")
            return NanoBananaResult(success=False, error_message="请求超时，请稍后重试")
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP 错误: {e.response.status_code}"
            resp_text = ""
            try:
                resp_text = e.response.text[:1000] if e.response.text else ""
                error_detail = e.response.json()
                error_msg = error_detail.get("error", {}).get("message", error_msg)
            except Exception:
                if resp_text:
                    error_msg = f"{error_msg} | {resp_text}"
            logger.error(f"[{self.provider_name}] NanoBanana {error_msg}")
            logger.error(f"[{self.provider_name}] 响应体: {resp_text}")
            return NanoBananaResult(success=False, error_message=error_msg)
        except Exception as e:
            logger.error(f"[{self.provider_name}] NanoBanana 生成异常: {e}")
            return NanoBananaResult(success=False, error_message=f"生成失败: {str(e)}")

    def _extract_image_from_content(self, content: str) -> NanoBananaResult:
        """从 markdown 格式的 content 中提取图片数据"""
        # 匹配 ![...](data:image/xxx;base64,...) 或 ![...](https://...)
        match = re.search(r'!\[.*?\]\((.*?)\)', content, re.DOTALL)
        if not match:
            return NanoBananaResult(
                success=False,
                error_message="未能从响应中提取图片",
            )

        image_src = match.group(1).strip()

        if image_src.startswith("data:"):
            # base64 data URL
            data_match = re.match(r'data:(image/[^;]+);base64,(.*)', image_src, re.DOTALL)
            if not data_match:
                return NanoBananaResult(success=False, error_message="无法解析 base64 data URL")
            mime_type = data_match.group(1)
            image_data = data_match.group(2).replace("\n", "").replace(" ", "").replace("\r", "")
            logger.info(f"[{self.provider_name}] 提取到 base64 图片 | mime={mime_type}")
            return NanoBananaResult(
                success=True,
                image_data=image_data,
                mime_type=mime_type,
            )
        elif image_src.startswith("http"):
            # URL - 需要下载
            logger.info(f"[{self.provider_name}] 提取到图片 URL，开始下载: {image_src[:80]}")
            try:
                img_resp = requests.get(image_src, timeout=60)
                img_resp.raise_for_status()
                content_type = (img_resp.headers.get("Content-Type") or "image/jpeg").split(";")[0].strip()
                image_data = base64.b64encode(img_resp.content).decode("ascii")
                logger.info(f"[{self.provider_name}] 图片下载成功 | mime={content_type}, size={len(img_resp.content)} bytes")
                return NanoBananaResult(
                    success=True,
                    image_data=image_data,
                    mime_type=content_type,
                )
            except Exception as e:
                logger.error(f"[{self.provider_name}] 图片下载失败: {e}")
                return NanoBananaResult(success=False, error_message=f"图片下载失败: {str(e)}")
        else:
            return NanoBananaResult(success=False, error_message=f"未知的图片格式: {image_src[:100]}")
