import sys

from .activation import get_device_id, verify_activation
from .constants import SettingKeys
from .database import get_setting, set_setting, get_all_settings
from .logger import logger
from .services.nanobanana import NanoBananaYunwu, NanoBananaGuanfang
from .services.sora2 import Sora2Yunwu, Sora2Dayangyu, Sora2Xiaobanshou, Sora2Guanfang


class Api:
    """pywebview JS API"""

    def get_app_info(self) -> dict:
        """获取应用信息（是否开发模式等）"""
        is_dev = not getattr(sys, 'frozen', False)
        logger.debug(f"[API] get_app_info -> is_dev={is_dev}")
        return {"is_dev": is_dev}

    def get_status(self) -> dict:
        """检查激活状态"""
        logger.debug("[API] get_status 调用")
        device_id = get_device_id()
        stored_code = get_setting(SettingKeys.ACTIVATION_CODE)

        if stored_code and verify_activation(device_id, stored_code):
            logger.info(f"[API] get_status -> 设备已激活: {device_id}")
            return {"state": "activated"}

        logger.info(f"[API] get_status -> 设备未激活: {device_id}")
        return {
            "state": "pending",
            "device_id": device_id,
        }

    def activate(self, code: str) -> dict:
        """激活设备"""
        logger.info(f"[API] activate 调用, code={code[:6]}...")
        device_id = get_device_id()

        if verify_activation(device_id, code):
            set_setting(SettingKeys.ACTIVATION_CODE, code.strip().upper())
            logger.info(f"[API] activate -> 激活成功: {device_id}")
            return {"ok": True}

        logger.warning(f"[API] activate -> 激活失败: {device_id}, 输入的激活码: {code}")
        return {"ok": False, "msg": "激活码无效"}

    def save_settings(self, settings: dict) -> dict:
        """保存设置"""
        logger.info(f"[API] save_settings 调用, keys={list(settings.keys())}")
        for key, value in settings.items():
            set_setting(key, str(value))
        logger.info(f"[API] save_settings -> 保存成功, 共 {len(settings)} 项")
        return {"ok": True}

    def get_all_settings(self) -> dict:
        """获取所有设置"""
        logger.debug("[API] get_all_settings 调用")
        return get_all_settings()

    # ==================== 文件夹选择 ====================

    def select_folder(self) -> dict:
        """打开文件夹选择对话框"""
        logger.debug("[API] select_folder 调用")
        import webview
        window = webview.windows[0] if webview.windows else None
        if not window:
            logger.warning("[API] select_folder -> 无法获取窗口实例")
            return {"ok": False, "msg": "无法获取窗口实例"}
        result = window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            folder = result[0]
            logger.info(f"[API] select_folder -> 已选择: {folder}")
            return {"ok": True, "path": folder}
        logger.debug("[API] select_folder -> 用户取消选择")
        return {"ok": False, "msg": "未选择文件夹"}

    # ==================== 图片处理 ====================

    # 图片处理默认提示词
    _DEFAULT_IMAGE_PROMPT = "请根据图片中的产品，为其绘制一个真实、自然的展示场景。场景需要与产品类型相匹配，突出产品本身，背景环境要逼真有质感。注意：画面中不要出现任何文字、标签或水印。"

    def get_image_process_prompt(self) -> dict:
        """获取图片处理提示词"""
        logger.debug("[API] get_image_process_prompt 调用")
        prompt = get_setting(SettingKeys.IMAGE_PROCESS_PROMPT) or self._DEFAULT_IMAGE_PROMPT
        return {"ok": True, "prompt": prompt}

    def set_image_process_prompt(self, prompt: str) -> dict:
        """保存图片处理提示词"""
        logger.info(f"[API] set_image_process_prompt 调用, prompt={prompt[:50]}...")
        set_setting(SettingKeys.IMAGE_PROCESS_PROMPT, prompt.strip())
        logger.info("[API] set_image_process_prompt -> 保存成功")
        return {"ok": True}

    # ==================== 调试接口 ====================

    def debug_dayangyu_sora2_create(self, prompt: str, image_base64: str = "", mime_type: str = "") -> dict:
        """调试 大洋芋 Sora2 - 创建任务（文生视频 / 图生视频）"""
        import base64
        import os
        import tempfile

        settings = get_all_settings()
        api_key = settings.get(SettingKeys.DAYANGYU_API_KEY, "")
        if not api_key:
            return {"ok": False, "msg": "未配置大洋芋 API Key，请前往设置页面配置"}
        model_name = settings.get(SettingKeys.DAYANGYU_SORA2_MODEL, "") or "sora2-portrait-15s"
        image_path = None
        try:
            service = Sora2Dayangyu(api_key)
            if image_base64:
                ext_map = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}
                ext = ext_map.get(mime_type or "", ".png")
                image_data = base64.b64decode(image_base64)
                tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
                tmp.write(image_data)
                tmp.close()
                image_path = tmp.name
                task = service.create_task(prompt, model=model_name, image_path=image_path)
            else:
                task = service.create_task(prompt, model=model_name)
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            return {
                "ok": True,
                "task_id": task.task_id,
                "status": task.status.value,
                "prompt": task.prompt,
                "mode": "图生视频" if image_base64 else "文生视频",
            }
        except Exception as e:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception:
                    pass
            logger.error(f"调试 大洋芋 Sora2 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def debug_dayangyu_sora2_query(self, task_id: str) -> dict:
        """调试 大洋芋 Sora2 - 查询任务状态"""
        settings = get_all_settings()
        api_key = settings.get(SettingKeys.DAYANGYU_API_KEY, "")
        if not api_key:
            return {"ok": False, "msg": "未配置大洋芋 API Key"}
        try:
            service = Sora2Dayangyu(api_key)
            task = service.query_task(task_id)
            result = {
                "ok": True,
                "task_id": task.task_id,
                "status": task.status.value,
                "progress": task.progress,
            }
            if task.video_url:
                result["video_url"] = task.video_url
            if task.error_message:
                result["error_message"] = task.error_message
            return result
        except Exception as e:
            logger.error(f"调试 大洋芋 Sora2 查询异常: {e}")
            return {"ok": False, "msg": str(e)}

    def debug_dayangyu_sora2_content(self, task_id: str) -> dict:
        """调试 大洋芋 Sora2 - 查看视频内容（接口较慢，建议优先用查询结果中的 video_url）"""
        import base64

        settings = get_all_settings()
        api_key = settings.get(SettingKeys.DAYANGYU_API_KEY, "")
        if not api_key:
            return {"ok": False, "msg": "未配置大洋芋 API Key"}
        try:
            service = Sora2Dayangyu(api_key)
            data, content_type, err = service.get_video_content(task_id)
            if err:
                return {"ok": False, "msg": err}
            if not data:
                return {"ok": False, "msg": "未获取到视频数据"}
            return {
                "ok": True,
                "content_type": content_type or "video/mp4",
                "data": base64.b64encode(data).decode("ascii"),
            }
        except Exception as e:
            logger.error(f"调试 大洋芋 Sora2 查看视频异常: {e}")
            return {"ok": False, "msg": str(e)}

    def debug_xiaobanshou_sora2_create(self, prompt: str, image_base64: str = "", mime_type: str = "") -> dict:
        """调试 小扳手 Sora2 - 创建任务（文生视频 / 图生视频）"""
        import base64
        import os
        import tempfile

        settings = get_all_settings()
        api_key = settings.get(SettingKeys.XIAOBANSHOU_API_KEY, "")
        if not api_key:
            return {"ok": False, "msg": "未配置小扳手 API Key，请前往设置页面配置"}
        model_name = settings.get(SettingKeys.XIAOBANSHOU_SORA2_MODEL, "") or "sora-2-portrait-10s"
        image_path = None
        try:
            service = Sora2Xiaobanshou(api_key)
            if image_base64:
                ext_map = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}
                ext = ext_map.get(mime_type or "", ".png")
                image_data = base64.b64decode(image_base64)
                tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
                tmp.write(image_data)
                tmp.close()
                image_path = tmp.name
                task = service.create_task(prompt, model=model_name, image_path=image_path)
            else:
                task = service.create_task(prompt, model=model_name)
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            return {
                "ok": True,
                "task_id": task.task_id,
                "status": task.status.value,
                "prompt": task.prompt,
                "mode": "图生视频" if image_base64 else "文生视频",
            }
        except Exception as e:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception:
                    pass
            logger.error(f"调试 小扳手 Sora2 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def debug_xiaobanshou_sora2_query(self, task_id: str) -> dict:
        """调试 小扳手 Sora2 - 查询任务状态"""
        settings = get_all_settings()
        api_key = settings.get(SettingKeys.XIAOBANSHOU_API_KEY, "")
        if not api_key:
            return {"ok": False, "msg": "未配置小扳手 API Key"}
        try:
            service = Sora2Xiaobanshou(api_key)
            task = service.query_task(task_id)
            result = {
                "ok": True,
                "task_id": task.task_id,
                "status": task.status.value,
                "progress": task.progress,
            }
            if task.video_url:
                result["video_url"] = task.video_url
            if task.error_message:
                result["error_message"] = task.error_message
            return result
        except Exception as e:
            logger.error(f"调试 小扳手 Sora2 查询异常: {e}")
            return {"ok": False, "msg": str(e)}

    def debug_yunwu_sora2_create(self, prompt: str, image_base64: str = "", mime_type: str = "") -> dict:
        """调试 云雾 Sora2 - 创建任务（传入图片base64后内部自动上传图床+创建任务）"""
        import base64
        import tempfile
        import os

        settings = get_all_settings()
        api_key = settings.get(SettingKeys.YUNWU_API_KEY, "")
        if not api_key:
            return {"ok": False, "msg": "未配置云雾 API Key，请前往设置页面配置"}

        orientation = settings.get(SettingKeys.YUNWU_SORA2_ORIENTATION, "portrait")
        duration = int(settings.get(SettingKeys.YUNWU_SORA2_DURATION, "10"))

        try:
            service = Sora2Yunwu(api_key)
            image_path = None

            # 如果有图片，先写入临时文件
            if image_base64:
                ext_map = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}
                ext = ext_map.get(mime_type, ".png")
                image_data = base64.b64decode(image_base64)

                tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
                tmp.write(image_data)
                tmp.close()
                image_path = tmp.name

            task = service.create_task(
                prompt,
                duration=duration,
                orientation=orientation,
                image_path=image_path,
            )

            # 清理临时文件
            if image_path and os.path.exists(image_path):
                os.remove(image_path)

            return {
                "ok": True,
                "task_id": task.task_id,
                "status": task.status.value,
                "prompt": task.prompt,
                "mode": "图生视频" if image_base64 else "文生视频",
                "duration": duration,
                "orientation": orientation,
            }
        except Exception as e:
            # 清理临时文件
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            logger.error(f"调试 云雾 Sora2 创建任务异常: {e}")
            return {"ok": False, "msg": str(e)}

    def debug_yunwu_sora2_query(self, task_id: str) -> dict:
        """调试 云雾 Sora2 - 查询任务"""
        settings = get_all_settings()
        api_key = settings.get(SettingKeys.YUNWU_API_KEY, "")
        if not api_key:
            return {"ok": False, "msg": "未配置云雾 API Key"}

        try:
            service = Sora2Yunwu(api_key)
            task = service.query_task(task_id)
            result = {
                "ok": True,
                "task_id": task.task_id,
                "status": task.status.value,
            }
            if task.video_url:
                result["video_url"] = task.video_url
            if task.prompt:
                result["enhanced_prompt"] = task.prompt
            if task.error_message:
                result["error_message"] = task.error_message
            return result
        except Exception as e:
            logger.error(f"调试 云雾 Sora2 查询任务异常: {e}")
            return {"ok": False, "msg": str(e)}

    def debug_nanobanana(self, prompt: str, ref_image: str = "", ref_mime_type: str = "") -> dict:
        """调试 NanoBanana - 生成图片（支持文生图和图生图），根据 API 模式自动选择官方/云雾"""
        settings = get_all_settings()
        api_mode = settings.get(SettingKeys.API_MODE, "custom")

        if api_mode == "official":
            api_key = settings.get(SettingKeys.GUANFANG_API_KEY, "")
            if not api_key:
                return {"ok": False, "msg": "未配置官方 API Key，请前往设置页面配置"}
            service = NanoBananaGuanfang(api_key)
            provider_label = "官方"
        else:
            api_key = settings.get(SettingKeys.YUNWU_API_KEY, "")
            if not api_key:
                return {"ok": False, "msg": "未配置云雾 API Key，请前往设置页面配置"}
            service = NanoBananaYunwu(api_key)
            provider_label = "云雾"

        aspect_ratio = settings.get(SettingKeys.NANOBANANA_RATIO, "9:16")
        image_size = settings.get(SettingKeys.NANOBANANA_QUALITY, "1K")

        try:
            kwargs = {}
            if ref_image:
                kwargs["ref_image"] = ref_image
                kwargs["ref_mime_type"] = ref_mime_type or "image/jpeg"
                logger.info(f"NanoBanana 调试 ({provider_label}): 图生图模式")
            else:
                logger.info(f"NanoBanana 调试 ({provider_label}): 文生图模式")

            result = service.generate(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                image_size=image_size,
                **kwargs,
            )

            if result.success:
                return {
                    "ok": True,
                    "image_data": result.image_data,
                    "mime_type": result.mime_type,
                    "text_content": result.text_content,
                }
            else:
                return {"ok": False, "msg": result.error_message}
        except Exception as e:
            logger.error(f"调试 NanoBanana ({provider_label}) 异常: {e}")
            return {"ok": False, "msg": str(e)}

    # ==================== 官方 API 调试接口 ====================

    def debug_guanfang_sora2_create(self, prompt: str, image_base64: str = "", mime_type: str = "") -> dict:
        """调试 官方 Sora2 - 创建任务（文生视频 / 图生视频）"""
        import base64
        import os
        import tempfile

        settings = get_all_settings()
        api_key = settings.get(SettingKeys.GUANFANG_API_KEY, "")
        if not api_key:
            return {"ok": False, "msg": "未配置官方 API Key，请前往设置页面配置"}
        model_name = settings.get(SettingKeys.GUANFANG_SORA2_MODEL, "") or "sora2-portrait-15s"
        image_path = None
        try:
            service = Sora2Guanfang(api_key)
            if image_base64:
                ext_map = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}
                ext = ext_map.get(mime_type or "", ".png")
                image_data = base64.b64decode(image_base64)
                tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
                tmp.write(image_data)
                tmp.close()
                image_path = tmp.name
                task = service.create_task(prompt, model=model_name, image_path=image_path)
            else:
                task = service.create_task(prompt, model=model_name)
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            return {
                "ok": True,
                "task_id": task.task_id,
                "status": task.status.value,
                "prompt": task.prompt,
                "mode": "图生视频" if image_base64 else "文生视频",
            }
        except Exception as e:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception:
                    pass
            logger.error(f"调试 官方 Sora2 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def debug_guanfang_sora2_query(self, task_id: str) -> dict:
        """调试 官方 Sora2 - 查询任务状态"""
        settings = get_all_settings()
        api_key = settings.get(SettingKeys.GUANFANG_API_KEY, "")
        if not api_key:
            return {"ok": False, "msg": "未配置官方 API Key"}
        try:
            service = Sora2Guanfang(api_key)
            task = service.query_task(task_id)
            result = {
                "ok": True,
                "task_id": task.task_id,
                "status": task.status.value,
                "progress": task.progress,
            }
            if task.video_url:
                result["video_url"] = task.video_url
            if task.error_message:
                result["error_message"] = task.error_message
            return result
        except Exception as e:
            logger.error(f"调试 官方 Sora2 查询异常: {e}")
            return {"ok": False, "msg": str(e)}

    def debug_guanfang_sora2_content(self, task_id: str) -> dict:
        """调试 官方 Sora2 - 查看视频内容"""
        import base64

        settings = get_all_settings()
        api_key = settings.get(SettingKeys.GUANFANG_API_KEY, "")
        if not api_key:
            return {"ok": False, "msg": "未配置官方 API Key"}
        try:
            service = Sora2Guanfang(api_key)
            data, content_type, err = service.get_video_content(task_id)
            if err:
                return {"ok": False, "msg": err}
            if not data:
                return {"ok": False, "msg": "未获取到视频数据"}
            return {
                "ok": True,
                "content_type": content_type or "video/mp4",
                "data": base64.b64encode(data).decode("ascii"),
            }
        except Exception as e:
            logger.error(f"调试 官方 Sora2 查看视频异常: {e}")
            return {"ok": False, "msg": str(e)}

    # ==================== 视频任务 ====================

    _DEFAULT_VIDEO_PROMPT = "根据图片内容生成一段自然流畅的展示视频"

    def get_video_process_prompt(self) -> dict:
        """获取视频处理提示词"""
        logger.debug("[API] get_video_process_prompt 调用")
        prompt = get_setting(SettingKeys.VIDEO_PROCESS_PROMPT) or self._DEFAULT_VIDEO_PROMPT
        return {"ok": True, "prompt": prompt}

    def set_video_process_prompt(self, prompt: str) -> dict:
        """保存视频处理提示词"""
        logger.info(f"[API] set_video_process_prompt 调用, prompt={prompt[:50]}...")
        set_setting(SettingKeys.VIDEO_PROCESS_PROMPT, prompt.strip())
        logger.info("[API] set_video_process_prompt -> 保存成功")
        return {"ok": True}

    def get_video_tasks(self) -> dict:
        """获取所有视频任务"""
        logger.debug("[API] get_video_tasks 调用")
        from .database import get_video_tasks
        try:
            tasks = get_video_tasks()
            logger.debug(f"[API] get_video_tasks -> 返回 {len(tasks)} 条任务")
            return {
                "ok": True,
                "tasks": [
                    {
                        "id": t.id,
                        "image_path": t.image_path,
                        "prompt": t.prompt,
                        "status": t.status,
                        "remote_task_id": t.remote_task_id,
                        "video_url": t.video_url,
                        "video_path": t.video_path,
                        "created_at": str(t.created_at),
                    }
                    for t in tasks
                ],
            }
        except Exception as e:
            logger.error(f"[API] get_video_tasks -> 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def create_video_task(self, image_base64: str, mime_type: str, prompt: str) -> dict:
        """手动创建视频任务"""
        logger.info(f"[API] create_video_task 调用, mime={mime_type}, prompt={prompt[:50]}...")
        import base64
        import os
        import uuid
        from .config import DATA_DIR

        try:
            images_dir = DATA_DIR / "images"
            images_dir.mkdir(exist_ok=True)
            ext_map = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}
            ext = ext_map.get(mime_type or "", ".png")
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = images_dir / filename
            image_data = base64.b64decode(image_base64)
            filepath.write_bytes(image_data)
            logger.debug(f"[API] create_video_task -> 图片已保存: {filepath}")

            from .database import create_video_task as db_create
            task = db_create(image_path=str(filepath), prompt=prompt)
            logger.info(f"[API] create_video_task -> 成功, id={task.id}, image={filename}")
            return {"ok": True, "task_id": task.id}
        except Exception as e:
            logger.error(f"[API] create_video_task -> 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def auto_create_video_task(self, image_base64: str, mime_type: str) -> dict:
        """图片生成完毕后自动创建视频任务"""
        logger.info(f"[API] auto_create_video_task 调用, mime={mime_type}")
        import base64
        import os
        import uuid
        from .config import DATA_DIR

        try:
            prompt = get_setting(SettingKeys.VIDEO_PROCESS_PROMPT) or self._DEFAULT_VIDEO_PROMPT
            images_dir = DATA_DIR / "images"
            images_dir.mkdir(exist_ok=True)
            ext_map = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/gif": ".gif"}
            ext = ext_map.get(mime_type or "", ".png")
            filename = f"{uuid.uuid4().hex}{ext}"
            filepath = images_dir / filename
            image_data = base64.b64decode(image_base64)
            filepath.write_bytes(image_data)
            logger.debug(f"[API] auto_create_video_task -> 图片已保存: {filepath}")

            from .database import create_video_task as db_create
            task = db_create(image_path=str(filepath), prompt=prompt)
            logger.info(f"[API] auto_create_video_task -> 成功, id={task.id}, image={filename}")
            return {"ok": True, "task_id": task.id}
        except Exception as e:
            logger.error(f"[API] auto_create_video_task -> 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def delete_video_task(self, task_id: int) -> dict:
        """删除视频任务"""
        logger.info(f"[API] delete_video_task 调用, task_id={task_id}")
        from .database import delete_video_task as db_delete
        try:
            db_delete(task_id)
            logger.info(f"[API] delete_video_task -> 成功, id={task_id}")
            return {"ok": True}
        except Exception as e:
            logger.error(f"[API] delete_video_task -> 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def download_video_task(self, task_id: int) -> dict:
        """下载视频到设置的下载目录（DYY 类型走 get_video_content API，其他走 URL 直接下载）"""
        import requests
        from datetime import datetime
        from pathlib import Path

        logger.info(f"[API] download_video_task 调用, task_id={task_id}")

        # 检查下载路径
        download_path = get_setting(SettingKeys.DOWNLOAD_PATH)
        if not download_path or not download_path.strip():
            logger.warning("[API] download_video_task -> 未设置下载路径")
            return {"ok": False, "msg": "未设置下载路径，请先在设置中选择下载文件夹"}

        download_dir = Path(download_path)
        if not download_dir.exists():
            try:
                download_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"[API] download_video_task -> 创建下载目录失败: {e}")
                return {"ok": False, "msg": f"下载目录不存在且无法创建: {download_path}"}

        # 获取任务信息
        from .database import get_video_tasks, update_video_task
        try:
            tasks = get_video_tasks()
            task = None
            for t in tasks:
                if t.id == task_id:
                    task = t
                    break
            if not task:
                return {"ok": False, "msg": "任务不存在"}
            if not task.video_url:
                return {"ok": False, "msg": "该任务暂无视频链接"}

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            remote_id = task.remote_task_id or ""

            # 判断是否可以走 DYY 类型的 get_video_content API 下载
            settings = get_all_settings()
            api_mode = settings.get(SettingKeys.API_MODE, "custom")
            use_api_download = False

            if remote_id:
                if api_mode == "official":
                    provider = settings.get("guanfang_sora2_provider", "dayangyu")
                    if provider == "dayangyu":
                        use_api_download = True
                else:
                    provider = settings.get(SettingKeys.SORA2_MODEL, "dayangyu")
                    if provider == "dayangyu":
                        use_api_download = True

            if use_api_download:
                # DYY 类型：通过 get_video_content API 下载
                logger.info(f"[API] download_video_task -> 使用 API 下载, remote_id={remote_id}")
                if api_mode == "official":
                    api_key = settings.get(SettingKeys.GUANFANG_API_KEY, "")
                    service = Sora2Guanfang(api_key)
                else:
                    api_key = settings.get(SettingKeys.DAYANGYU_API_KEY, "")
                    service = Sora2Dayangyu(api_key)

                data, content_type, err = service.get_video_content(remote_id)
                if err or not data:
                    logger.warning(f"[API] download_video_task -> API 下载失败: {err}，回退到 URL 下载")
                    use_api_download = False
                else:
                    ext = ".mp4"
                    if content_type and "webm" in content_type:
                        ext = ".webm"
                    elif content_type and "mov" in content_type:
                        ext = ".mov"
                    filename = f"video_{task_id}_{timestamp}{ext}"
                    filepath = download_dir / filename
                    filepath.write_bytes(data)
                    logger.info(f"[API] download_video_task -> API 下载完成: {filepath}")
                    update_video_task(task_id, video_path=str(filepath))
                    return {"ok": True, "path": str(filepath)}

            # 其他类型 / API 下载失败回退：通过 URL 直接下载
            video_url = task.video_url
            ext = ".mp4"
            if ".webm" in video_url:
                ext = ".webm"
            elif ".mov" in video_url:
                ext = ".mov"
            filename = f"video_{task_id}_{timestamp}{ext}"
            filepath = download_dir / filename

            logger.info(f"[API] download_video_task -> 使用 URL 下载: {video_url}")
            resp = requests.get(video_url, timeout=120, stream=True)
            resp.raise_for_status()
            with open(str(filepath), "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"[API] download_video_task -> URL 下载完成: {filepath}")

            update_video_task(task_id, video_path=str(filepath))
            return {"ok": True, "path": str(filepath)}
        except Exception as e:
            logger.error(f"[API] download_video_task -> 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def delete_all_video_tasks(self) -> dict:
        """删除所有视频任务"""
        logger.info("[API] delete_all_video_tasks 调用")
        from .database import delete_all_video_tasks as db_delete_all
        try:
            count = db_delete_all()
            logger.info(f"[API] delete_all_video_tasks -> 成功, 共删除 {count} 条")
            return {"ok": True, "count": count}
        except Exception as e:
            logger.error(f"[API] delete_all_video_tasks -> 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def retry_video_task(self, task_id: int) -> dict:
        """重试失败的视频任务（重置状态为 pending）"""
        logger.info(f"[API] retry_video_task 调用, task_id={task_id}")
        from .database import update_video_task
        try:
            update_video_task(task_id, status='pending', video_url='', video_path='')
            logger.info(f"[API] retry_video_task -> 成功, id={task_id}")
            return {"ok": True}
        except Exception as e:
            logger.error(f"[API] retry_video_task -> 异常: {e}")
            return {"ok": False, "msg": str(e)}

    # ==================== 数据文件状态 ====================

    def get_data_status(self) -> dict:
        """获取数据库和日志文件的状态信息"""
        import os
        from .config import BASE_DIR, DB_PATH, LOGS_DIR

        logger.debug("[API] get_data_status 调用")
        try:
            # 数据库文件信息
            db_size = 0
            db_exists = DB_PATH.exists()
            if db_exists:
                db_size = DB_PATH.stat().st_size

            # 日志目录信息
            log_files = 0
            log_total_size = 0
            if LOGS_DIR.exists():
                for f in LOGS_DIR.iterdir():
                    if f.is_file():
                        log_files += 1
                        log_total_size += f.stat().st_size

            return {
                "ok": True,
                "base_dir": str(BASE_DIR),
                "db_path": str(DB_PATH),
                "db_exists": db_exists,
                "db_size": db_size,
                "logs_dir": str(LOGS_DIR),
                "log_files": log_files,
                "log_total_size": log_total_size,
            }
        except Exception as e:
            logger.error(f"[API] get_data_status -> 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def clean_logs(self) -> dict:
        """清理历史日志文件（保留当前运行的日志）"""
        import os
        from .config import LOGS_DIR
        from .logger import log_filename as current_log_filename

        logger.info("[API] clean_logs 调用")
        try:
            if not LOGS_DIR.exists():
                return {"ok": True, "count": 0}

            deleted = 0
            for f in LOGS_DIR.iterdir():
                if f.is_file() and f.name != current_log_filename:
                    try:
                        f.unlink()
                        deleted += 1
                    except Exception as e:
                        logger.warning(f"[API] clean_logs -> 删除文件失败 {f.name}: {e}")

            logger.info(f"[API] clean_logs -> 已删除 {deleted} 个日志文件")
            return {"ok": True, "count": deleted}
        except Exception as e:
            logger.error(f"[API] clean_logs -> 异常: {e}")
            return {"ok": False, "msg": str(e)}

    def open_root_directory(self) -> dict:
        """在文件管理器中打开应用根目录"""
        import os
        import platform
        import subprocess
        from .config import BASE_DIR

        logger.info(f"[API] open_root_directory 调用, path={BASE_DIR}")
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(str(BASE_DIR))
            elif system == "Darwin":
                subprocess.Popen(["open", str(BASE_DIR)])
            else:
                subprocess.Popen(["xdg-open", str(BASE_DIR)])
            return {"ok": True}
        except Exception as e:
            logger.error(f"[API] open_root_directory -> 异常: {e}")
            return {"ok": False, "msg": str(e)}
