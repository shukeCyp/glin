"""云雾 API NanoBanana 图片生成"""

import base64
import re

import requests

from ...constants import ApiUrls
from ...logger import logger
from .base import NanoBananaBase, NanoBananaResult


class NanoBananaYunwu(NanoBananaBase):
    """云雾 API NanoBanana 图片生成（Gemini 原生格式）"""

    MODEL = "gemini-3-pro-image-preview"

    @property
    def provider_name(self) -> str:
        return "云雾 API"

    @property
    def base_url(self) -> str:
        return ApiUrls.YUNWU

    def generate(
        self,
        prompt: str,
        aspect_ratio: str = "9:16",
        image_size: str = "1K",
        **kwargs
    ) -> NanoBananaResult:
        """
        生成图片

        Args:
            prompt: 图片描述提示词
            aspect_ratio: 宽高比，可选 9:16 / 16:9 / 1:1
            image_size: 图片清晰度，可选 1K / 2K / 4K
            **kwargs: 其他参数

        Returns:
            NanoBananaResult: 生成结果
        """
        url = f"{self.base_url}/v1beta/models/{self.MODEL}:generateContent"

        headers = {
            "Content-Type": "application/json",
        }

        params = {
            "key": self.api_key,
        }

        # 构建请求体 - parts
        parts = [{"text": prompt}]

        # 如果传入了参考图片（base64），添加 inline_data
        ref_image = kwargs.get("ref_image")
        ref_mime_type = kwargs.get("ref_mime_type", "image/jpeg")
        if ref_image:
            parts.append({
                "inline_data": {
                    "mime_type": ref_mime_type,
                    "data": ref_image,
                }
            })

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": parts,
                }
            ],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {
                    "aspectRatio": aspect_ratio,
                    "imageSize": image_size,
                },
            },
        }

        try:
            logger.info(
                f"[{self.provider_name}] NanoBanana 生成请求 | "
                f"URL: {url} | 比例: {aspect_ratio}, 清晰度: {image_size}"
            )
            logger.debug(f"[{self.provider_name}] 请求头: {headers}")
            logger.debug(f"[{self.provider_name}] 请求参数: key=***{self.api_key[-6:] if len(self.api_key) > 6 else '***'}")
            # payload 中可能包含大量 base64 图片数据，只打印结构
            log_payload = {
                "contents": [{"role": "user", "parts": [
                    {"text": prompt[:100]} if p.get("text") else {"inline_data": f"<{ref_mime_type}, {len(ref_image) if ref_image else 0} chars>"}
                    for p in parts
                ]}],
                "generationConfig": payload.get("generationConfig"),
            }
            logger.info(f"[{self.provider_name}] 请求体: {log_payload}")

            resp = requests.post(
                url,
                headers=headers,
                params=params,
                json=payload,
                timeout=120,
            )

            logger.info(f"[{self.provider_name}] 响应状态码: {resp.status_code}")
            # 响应体可能包含大量 base64 图片数据，只打印前 500 字符
            resp_text = resp.text
            logger.info(f"[{self.provider_name}] 响应体 (前500字符): {resp_text[:500]}")

            resp.raise_for_status()
            data = resp.json()

            # 解析响应，提取图片数据
            candidates = data.get("candidates", [])
            if not candidates:
                return NanoBananaResult(
                    success=False,
                    error_message="API 返回结果为空，未生成图片",
                )

            content = candidates[0].get("content", {})
            parts_resp = content.get("parts", [])

            image_data = None
            mime_type = None
            text_content = None

            for part in parts_resp:
                if "inlineData" in part:
                    image_data = part["inlineData"].get("data")
                    mime_type = part["inlineData"].get("mimeType", "image/png")
                elif "text" in part:
                    text_val = part["text"]
                    # 兼容 ![image](data:image/xxx;base64,...) 格式
                    md_match = re.search(
                        r'!\[.*?\]\(data:(image/[^;]+);base64,([A-Za-z0-9+/=\s]+)\)',
                        text_val,
                    )
                    if md_match and not image_data:
                        mime_type = md_match.group(1)
                        image_data = md_match.group(2).replace("\n", "").replace(" ", "")
                        logger.info(f"[{self.provider_name}] 从 markdown text 中提取到图片数据 | mime={mime_type}")
                    else:
                        text_content = text_val

            if not image_data:
                return NanoBananaResult(
                    success=False,
                    error_message=text_content or "API 未返回图片数据",
                )

            logger.info(f"[{self.provider_name}] NanoBanana 生成成功")

            return NanoBananaResult(
                success=True,
                image_data=image_data,
                mime_type=mime_type,
                text_content=text_content,
            )

        except requests.exceptions.Timeout:
            logger.error(f"[{self.provider_name}] NanoBanana 请求超时")
            return NanoBananaResult(
                success=False,
                error_message="请求超时，请稍后重试",
            )
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP 错误: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg = error_detail.get("error", {}).get("message", error_msg)
            except Exception:
                pass
            logger.error(f"[{self.provider_name}] NanoBanana {error_msg}")
            return NanoBananaResult(
                success=False,
                error_message=error_msg,
            )
        except Exception as e:
            logger.error(f"[{self.provider_name}] NanoBanana 生成异常: {e}")
            return NanoBananaResult(
                success=False,
                error_message=f"生成失败: {str(e)}",
            )
