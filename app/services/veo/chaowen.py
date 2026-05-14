"""超稳 AI (chaowenai.com) VEO 视频生成（异步任务型）"""

import base64
import os
import time
from typing import Optional

import requests

from ...logger import logger
from .base import VeoBase, VeoResult
from .utils import download_video

CW_BASE = "https://api.chaowenai.com"

# 任务状态
_PENDING_STATUSES = {"queued", "in_progress", "processing", "running"}
_FAILED_STATUSES = {"failed", "error", "cancelled"}

# 模型列表
_MODELS = {
    "fast": "veo3.1-fast",
    "lite": "veo3.1-lite",
}


class VeoChaowen(VeoBase):
    """超稳 AI VEO 视频生成"""

    @property
    def provider_name(self) -> str:
        return "超稳 AI"

    @property
    def base_url(self) -> str:
        return self._base_url or CW_BASE

    def __init__(self, api_key: str, base_url: str = ""):
        super().__init__(api_key)
        self._base_url = (base_url or "").strip().rstrip("/")

    def generate(
        self,
        prompt: str,
        orientation: str = "portrait",
        duration: int = 10,
        ref_image_path: Optional[str] = None,
        download_dir: Optional[str] = None,
        **kwargs,
    ) -> VeoResult:
        """
        生成视频（异步任务型）。

        Args:
            prompt:          视频描述提示词
            orientation:     方向，portrait（竖屏）/ landscape（横屏）
            duration:        视频时长（秒），CW 当前不通过此参数控制
            ref_image_path:  参考图片本地路径（图生视频时使用）
            download_dir:    视频下载目录
        """
        # 选择模型，默认使用 fast
        model = kwargs.get("model") or _MODELS["fast"]
        if model not in ("veo3.1-fast", "veo3.1-lite"):
            model = _MODELS.get(model, _MODELS["fast"])

        # 宽高比映射
        aspect_ratio = "9:16" if orientation == "portrait" else "16:9"

        payload = {
            "model": model,
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
        }

        # 如果有参考图，添加首帧
        if ref_image_path and os.path.isfile(ref_image_path):
            with open(ref_image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            # 根据文件扩展名确定 MIME 类型
            ext = os.path.splitext(ref_image_path)[1].lower()
            mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
            mime = mime_map.get(ext, "image/jpeg")
            payload["firstFrameBase64"] = f"data:{mime};base64,{img_b64}"

        # 提交任务
        task_id = self._submit_task(payload, model)
        if not task_id:
            return VeoResult(success=False, error_message="任务提交失败")

        # 轮询任务状态
        result = self._poll_task(task_id, model)
        if not result or not result.success:
            return result or VeoResult(success=False, error_message="任务轮询失败")

        # 如果配置了下载目录，下载视频
        if result.success and result.video_url and download_dir:
            result.file_path = download_video(
                result.video_url, download_dir, "veo_cw"
            )

        return result

    def _submit_task(self, payload: dict, model: str) -> Optional[str]:
        """提交异步任务"""
        url = f"{self.base_url}/v1/videos"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        mode = "图生视频" if payload.get("firstFrameBase64") else "文生视频"
        logger.info(
            f"[{self.provider_name}] VEO 请求 | "
            f"model={payload.get('model')} | 模式={mode} | "
            f"POST {url}"
        )

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            logger.info(f"[{self.provider_name}] 响应状态码: {resp.status_code}")
            logger.info(f"[{self.provider_name}] 响应体: {resp.text[:500]}")
            resp.raise_for_status()

            data = resp.json()
            task_id = data.get("id") or data.get("task_id")
            if not task_id:
                logger.error(f"[{self.provider_name}] 响应中未找到 task_id")
                return None

            logger.info(f"[{self.provider_name}] 任务已提交 | task_id={task_id}")
            return task_id

        except requests.exceptions.Timeout:
            logger.error(f"[{self.provider_name}] 任务提交超时")
            return None
        except requests.exceptions.HTTPError as exc:
            error_message = self._extract_error_message(exc.response)
            logger.error(f"[{self.provider_name}] 任务提交 HTTP 异常: {error_message}")
            return None
        except Exception as exc:
            logger.error(f"[{self.provider_name}] 任务提交异常: {exc}")
            return None

    def _poll_task(
        self,
        task_id: str,
        model: str,
        timeout_seconds: int = 600,
        interval_seconds: int = 15,
    ) -> Optional[VeoResult]:
        """轮询任务状态"""
        url = f"{self.base_url}/v1/videos/{task_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        deadline = time.time() + timeout_seconds

        while time.time() < deadline:
            try:
                resp = requests.get(
                    url,
                    headers=headers,
                    params={"model": model},
                    timeout=30,
                )
                logger.info(f"[{self.provider_name}] 轮询状态码: {resp.status_code}")
                logger.info(f"[{self.provider_name}] 轮询响应: {resp.text[:500]}")
                resp.raise_for_status()

                data = resp.json()
                status = str(data.get("status") or "").lower()

                # 检查是否完成
                if status == "completed":
                    logger.info(f"[{self.provider_name}] 任务完成 | task_id={task_id}")
                    return self._extract_result(data)

                # 检查是否失败
                if status in _FAILED_STATUSES:
                    error_msg = self._extract_error_from_response(data)
                    logger.error(f"[{self.provider_name}] 任务失败 | task_id={task_id} | error={error_msg}")
                    return VeoResult(success=False, error_message=str(error_msg))

                # 继续轮询
                if status not in _PENDING_STATUSES and status != "":
                    logger.warning(f"[{self.provider_name}] 未识别状态: {status}")

                time.sleep(interval_seconds)

            except requests.exceptions.Timeout:
                logger.warning(f"[{self.provider_name}] 轮询请求超时，继续重试")
                time.sleep(interval_seconds)
            except Exception as exc:
                logger.error(f"[{self.provider_name}] 轮询异常: {exc}")
                time.sleep(interval_seconds)

        return VeoResult(success=False, error_message="轮询视频结果超时")

    def _extract_result(self, data: dict) -> VeoResult:
        """从响应中提取视频结果"""
        try:
            video_url = data.get("video_url") or data.get("url")
            if video_url:
                logger.info(f"[{self.provider_name}] 成功获取视频 URL")
                return VeoResult(success=True, video_url=video_url)

            return VeoResult(success=False, error_message="未找到视频数据")

        except Exception as exc:
            logger.error(f"[{self.provider_name}] 响应解析异常: {exc}")
            return VeoResult(success=False, error_message=f"响应解析失败: {exc}")

    @staticmethod
    def _extract_error_message(response) -> str:
        """从 HTTP 响应中提取错误信息"""
        try:
            body = response.json()
            error = body.get("error")
            if isinstance(error, dict):
                return error.get("message") or error.get("detail") or str(error)
            return body.get("message") or str(error) or response.text[:500]
        except Exception:
            return response.text[:500] if response.text else str(response)

    @staticmethod
    def _extract_error_from_response(data: dict) -> str:
        """从轮询响应中提取错误信息"""
        error = data.get("error")
        if isinstance(error, dict):
            return error.get("message") or error.get("detail") or str(error)
        if isinstance(error, str):
            return error
        return data.get("message") or "任务执行失败"
