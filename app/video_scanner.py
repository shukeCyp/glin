"""视频任务扫描器 - 后台线程持续扫描待处理任务并提交到线程池"""

import os
import threading
import time
import requests

from .constants import SettingKeys, ModelProviders
from .database import (
    get_pending_video_tasks,
    update_video_task,
    get_all_settings,
    get_setting,
)
from .logger import logger
from .thread_pool import get_pool
from .services.sora2 import Sora2Guanfang, Sora2Dayangyu, Sora2Yunwu, Sora2Xiaobanshou
from .services.sora2.base import Sora2TaskStatus


def _get_sora2_service(settings: dict):
    """根据设置获取 Sora2 服务实例"""
    api_mode = settings.get(SettingKeys.API_MODE, "custom")

    if api_mode == "official":
        api_key = settings.get(SettingKeys.GUANFANG_API_KEY, "")
        if not api_key:
            return None, "未配置官方 API Key"
        model = settings.get(SettingKeys.GUANFANG_SORA2_MODEL, "") or "sora2-portrait-15s"
        return (Sora2Guanfang(api_key), model), None
    else:
        # 自定义模式 - 按 sora2_model 选择
        provider = settings.get(SettingKeys.SORA2_MODEL, ModelProviders.DAYANGYU)

        if provider == ModelProviders.DAYANGYU:
            api_key = settings.get(SettingKeys.DAYANGYU_API_KEY, "")
            if not api_key:
                return None, "未配置 DYY API Key"
            model = settings.get(SettingKeys.DAYANGYU_SORA2_MODEL, "") or "sora2-portrait-15s"
            return (Sora2Dayangyu(api_key), model), None

        elif provider == ModelProviders.YUNWU:
            api_key = settings.get(SettingKeys.YUNWU_API_KEY, "")
            if not api_key:
                return None, "未配置 YW API Key"
            # 云雾不用 model 参数，用 orientation/duration
            return (Sora2Yunwu(api_key), None), None

        elif provider == ModelProviders.XIAOBANSHOU:
            api_key = settings.get(SettingKeys.XIAOBANSHOU_API_KEY, "")
            if not api_key:
                return None, "未配置 XBS API Key"
            model = settings.get(SettingKeys.XIAOBANSHOU_SORA2_MODEL, "") or "sora-2-portrait-10s"
            return (Sora2Xiaobanshou(api_key), model), None

        return None, f"未知的 Sora2 提供商: {provider}"


def _create_sora2_task(service, settings, prompt, image_path, model):
    """创建 Sora2 任务，封装云雾特殊参数"""
    kwargs = {}
    if model:
        kwargs["model"] = model
    if image_path and os.path.isfile(image_path):
        kwargs["image_path"] = image_path

    api_mode = settings.get(SettingKeys.API_MODE, "custom")
    provider = settings.get(SettingKeys.SORA2_MODEL, "dayangyu")
    if api_mode == "custom" and provider == ModelProviders.YUNWU:
        orientation = settings.get(SettingKeys.YUNWU_SORA2_ORIENTATION, "portrait")
        duration = int(settings.get(SettingKeys.YUNWU_SORA2_DURATION, "10"))
        kwargs["orientation"] = orientation
        return service.create_task(prompt, duration=duration, **kwargs)
    else:
        return service.create_task(prompt, **kwargs)


def _process_task(task) -> None:
    """处理单个视频任务（带重试）"""
    task_db_id = task.id
    logger.info(f"[Scanner] 开始处理视频任务 id={task_db_id}")

    try:
        settings = get_all_settings()

        # 读取重试配置
        auto_retry = settings.get(SettingKeys.AUTO_RETRY, "false") == "true"
        max_retry = int(settings.get(SettingKeys.VIDEO_MAX_RETRY, "3")) if auto_retry else 0

        result, err = _get_sora2_service(settings)
        if err or not result:
            logger.error(f"[Scanner] 获取 Sora2 服务失败: {err}")
            update_video_task(task_db_id, status='failed')
            return

        service, model = result
        prompt = task.prompt or ""
        image_path = task.image_path or ""

        attempt = 0
        while attempt <= max_retry:
            if attempt > 0:
                logger.info(f"[Scanner] 视频任务重试 id={task_db_id} | 第 {attempt}/{max_retry} 次重试")

            # 创建任务
            sora2_task = _create_sora2_task(service, settings, prompt, image_path, model)

            if sora2_task.status == Sora2TaskStatus.FAILED:
                logger.error(f"[Scanner] 创建任务失败 id={task_db_id}: {sora2_task.error_message}")
                attempt += 1
                if attempt <= max_retry:
                    time.sleep(5)  # 重试前等待 5 秒
                continue

            remote_task_id = sora2_task.task_id
            logger.info(f"[Scanner] 任务已提交 id={task_db_id}, remote_id={remote_task_id}")

            # 轮询等待完成 - 每 30 秒查询一次，最多 30 分钟
            max_polls = 60
            poll_interval = 30

            poll_success = False
            for poll_idx in range(max_polls):
                time.sleep(poll_interval)
                logger.info(f"[Scanner] 轮询任务 id={task_db_id} | 第 {poll_idx + 1}/{max_polls} 次查询")
                query_result = service.query_task(remote_task_id)

                if query_result.status == Sora2TaskStatus.COMPLETED:
                    video_url = query_result.video_url or ""
                    update_video_task(
                        task_db_id,
                        status='completed',
                        video_url=video_url,
                    )
                    logger.info(f"[Scanner] 任务完成 id={task_db_id}, video_url={video_url[:80] if video_url else 'N/A'}")

                    # 自动下载
                    auto_download = settings.get(SettingKeys.AUTO_DOWNLOAD, "false") == "true"
                    download_path = settings.get(SettingKeys.DOWNLOAD_PATH, "")
                    if auto_download and download_path and video_url:
                        _download_video(task_db_id, video_url, download_path)

                    return  # 成功，退出

                elif query_result.status == Sora2TaskStatus.FAILED:
                    logger.error(f"[Scanner] 远程任务失败 id={task_db_id}: {query_result.error_message}")
                    break  # 跳出轮询，进入重试

                # 继续轮询（pending / processing）

            else:
                # 轮询超时
                logger.warning(f"[Scanner] 轮询超时 id={task_db_id}")

            # 任务失败或超时，尝试重试
            attempt += 1
            if attempt <= max_retry:
                logger.info(f"[Scanner] 准备重试 id={task_db_id}")
                time.sleep(5)

        # 所有重试都失败
        logger.error(f"[Scanner] 视频任务最终失败 id={task_db_id} (已重试 {max_retry} 次)")
        update_video_task(task_db_id, status='failed')

    except Exception as e:
        logger.error(f"[Scanner] 处理任务异常 id={task_db_id}: {type(e).__name__}: {e}")
        update_video_task(task_db_id, status='failed')


def _download_video(task_db_id: int, video_url: str, download_dir: str) -> None:
    """下载视频到本地"""
    try:
        os.makedirs(download_dir, exist_ok=True)
        filename = f"video_{task_db_id}.mp4"
        filepath = os.path.join(download_dir, filename)

        logger.info(f"[Scanner] 开始下载视频 id={task_db_id} | {video_url[:80]}")
        resp = requests.get(video_url, timeout=120, stream=True)
        resp.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        update_video_task(task_db_id, video_path=filepath)
        logger.info(f"[Scanner] 视频已下载 id={task_db_id}: {filepath}")
    except Exception as e:
        logger.error(f"[Scanner] 下载视频失败 id={task_db_id}: {e}")


def start_scanner() -> None:
    """启动后台扫描线程"""
    def _scan_loop():
        logger.info("[Scanner] 视频任务扫描器已启动, 扫描间隔: 5秒")
        scan_count = 0
        while True:
            try:
                scan_count += 1
                tasks = get_pending_video_tasks()
                pool = get_pool()
                if tasks and pool:
                    logger.info(f"[Scanner] 第{scan_count}轮扫描, 发现 {len(tasks)} 个待处理任务")
                    for task in tasks:
                        update_video_task(task.id, status='processing')
                        pool.submit(_process_task, task)
                        logger.info(f"[Scanner] 已提交任务 id={task.id} 到线程池")
                elif scan_count % 60 == 0:
                    # 每 5 分钟打印一次心跳日志
                    logger.debug(f"[Scanner] 第{scan_count}轮扫描, 无待处理任务")
            except Exception as e:
                logger.error(f"[Scanner] 扫描异常: {type(e).__name__}: {e}")

            time.sleep(5)  # 每 5 秒扫描一次新任务

    t = threading.Thread(target=_scan_loop, daemon=True, name="VideoScanner")
    t.start()
    logger.info("[Scanner] 扫描线程已启动")
