"""视频任务扫描器 - 后台线程持续扫描待处理任务并提交到线程池"""

import os
import threading
import time
import requests

from .api import get_default_download_dir
from .constants import SettingKeys, ModelProviders
from .database import (
    get_pending_video_tasks,
    get_processing_video_tasks,
    update_video_task,
    get_all_settings,
    get_setting,
)
from .logger import logger
from .thread_pool import get_pool
from .services.sora2 import Sora2Dayangyu, Sora2Xiaobanshou, Sora2Bandianwa
from .services.sora2.base import Sora2TaskStatus


def _build_model_name(provider: str, orientation: str, duration: str) -> str:
    """根据渠道、比例、时长构建模型名称"""
    d = duration
    o = orientation
    if provider == ModelProviders.DAYANGYU:
        return f"sora2-pro-{o}-hd-{d}s"
    elif provider == ModelProviders.XIAOBANSHOU:
        return f"sora-2-{o}-{d}s"
    elif provider == ModelProviders.BANDIANWA:
        return f"sora-2-{o}-{d}s-guanzhuan"
    return None


def _get_sora2_service(settings: dict):
    """根据设置获取 Sora2 服务实例"""
    provider = settings.get(SettingKeys.SORA2_MODEL, ModelProviders.DAYANGYU)
    orientation = settings.get(SettingKeys.SORA2_ORIENTATION, "portrait")
    duration = settings.get(SettingKeys.SORA2_DURATION, "10")

    if provider == ModelProviders.DAYANGYU:
        api_key = settings.get(SettingKeys.DAYANGYU_API_KEY, "")
        if not api_key:
            return None, "未配置大洋芋 API Key"
        model = _build_model_name(provider, orientation, duration)
        return (Sora2Dayangyu(api_key), model), None

    elif provider == ModelProviders.XIAOBANSHOU:
        api_key = settings.get(SettingKeys.XIAOBANSHOU_API_KEY, "")
        if not api_key:
            return None, "未配置小扳手 API Key"
        model = _build_model_name(provider, orientation, duration)
        return (Sora2Xiaobanshou(api_key), model), None

    elif provider == ModelProviders.BANDIANWA:
        api_key = settings.get(SettingKeys.BANDIANWA_API_KEY, "")
        if not api_key:
            return None, "未配置斑点蛙 API Key"
        model = _build_model_name(provider, orientation, duration)
        return (Sora2Bandianwa(api_key), model), None

    return None, f"未知的 Sora2 提供商: {provider}"


def _create_sora2_task(service, settings, prompt, image_path, model):
    """创建 Sora2 任务，根据渠道选择封装参数"""
    kwargs = {}
    if model:
        kwargs["model"] = model
    if image_path and os.path.isfile(image_path):
        kwargs["image_path"] = image_path

    provider = settings.get(SettingKeys.SORA2_MODEL, ModelProviders.DAYANGYU)
    if provider == ModelProviders.YUNWU:
        orientation = settings.get(SettingKeys.SORA2_ORIENTATION, "portrait")
        duration = int(settings.get(SettingKeys.SORA2_DURATION, "10"))
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

            sora2_task = _create_sora2_task(service, settings, prompt, image_path, model)

            if sora2_task.status == Sora2TaskStatus.FAILED:
                logger.error(f"[Scanner] 创建任务失败 id={task_db_id}: {sora2_task.error_message}")
                attempt += 1
                if attempt <= max_retry:
                    time.sleep(5)
                continue

            remote_task_id = sora2_task.task_id
            logger.info(f"[Scanner] 任务已提交 id={task_db_id}, remote_id={remote_task_id}")
            update_video_task(task_db_id, remote_task_id=remote_task_id)

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

                    dl_dir = str(get_default_download_dir())
                    _download_video(task_db_id, video_url, dl_dir, service=service, remote_task_id=remote_task_id)

                    return

                elif query_result.status == Sora2TaskStatus.FAILED:
                    logger.error(f"[Scanner] 远程任务失败 id={task_db_id}: {query_result.error_message}")
                    break

            else:
                logger.warning(f"[Scanner] 轮询超时 id={task_db_id}")

            attempt += 1
            if attempt <= max_retry:
                logger.info(f"[Scanner] 准备重试 id={task_db_id}")
                time.sleep(5)

        logger.error(f"[Scanner] 视频任务最终失败 id={task_db_id} (已重试 {max_retry} 次)")
        update_video_task(task_db_id, status='failed')

    except Exception as e:
        logger.error(f"[Scanner] 处理任务异常 id={task_db_id}: {type(e).__name__}: {e}")
        update_video_task(task_db_id, status='failed')


def _download_video(task_db_id: int, video_url: str, download_dir: str, service=None, remote_task_id: str = "") -> None:
    """下载视频到本地（DYY 类型优先用 get_video_content API，其他走 URL）"""
    from datetime import datetime
    try:
        os.makedirs(download_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if service and remote_task_id and hasattr(service, 'get_video_content'):
            logger.info(f"[Scanner] 使用 API 下载视频 id={task_db_id}, remote_id={remote_task_id}")
            data, content_type, err = service.get_video_content(remote_task_id)
            if not err and data:
                ext = ".mp4"
                if content_type and "webm" in content_type:
                    ext = ".webm"
                elif content_type and "mov" in content_type:
                    ext = ".mov"
                filename = f"video_{task_db_id}_{timestamp}{ext}"
                filepath = os.path.join(download_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(data)
                update_video_task(task_db_id, video_path=filepath)
                logger.info(f"[Scanner] API 下载完成 id={task_db_id}: {filepath}")
                return
            else:
                logger.warning(f"[Scanner] API 下载失败 id={task_db_id}: {err}，回退到 URL 下载")

        if not video_url:
            logger.warning(f"[Scanner] 无视频 URL，跳过下载 id={task_db_id}")
            return

        filename = f"video_{task_db_id}_{timestamp}.mp4"
        filepath = os.path.join(download_dir, filename)

        logger.info(f"[Scanner] 使用 URL 下载视频 id={task_db_id} | {video_url[:80]}")
        resp = requests.get(video_url, timeout=120, stream=True)
        resp.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        update_video_task(task_db_id, video_path=filepath)
        logger.info(f"[Scanner] URL 下载完成 id={task_db_id}: {filepath}")
    except Exception as e:
        logger.error(f"[Scanner] 下载视频失败 id={task_db_id}: {e}")


def _resume_poll_task(task, service) -> None:
    """恢复轮询一个已有 remote_task_id 的处理中任务（跳过创建阶段）"""
    task_db_id = task.id
    remote_task_id = task.remote_task_id
    logger.info(f"[Scanner] 恢复轮询任务 id={task_db_id}, remote_id={remote_task_id}")

    try:
        settings = get_all_settings()
        max_polls = 60
        poll_interval = 30

        for poll_idx in range(max_polls):
            time.sleep(poll_interval)
            logger.info(f"[Scanner] 恢复轮询 id={task_db_id} | 第 {poll_idx + 1}/{max_polls} 次查询")
            query_result = service.query_task(remote_task_id)

            if query_result.status == Sora2TaskStatus.COMPLETED:
                video_url = query_result.video_url or ""
                update_video_task(task_db_id, status='completed', video_url=video_url)
                logger.info(f"[Scanner] 恢复任务完成 id={task_db_id}, video_url={video_url[:80] if video_url else 'N/A'}")

                dl_dir = str(get_default_download_dir())
                _download_video(task_db_id, video_url, dl_dir, service=service, remote_task_id=remote_task_id)
                return

            elif query_result.status == Sora2TaskStatus.FAILED:
                logger.error(f"[Scanner] 恢复任务失败 id={task_db_id}: {query_result.error_message}")
                update_video_task(task_db_id, status='failed')
                return

        logger.warning(f"[Scanner] 恢复轮询超时 id={task_db_id}")
        update_video_task(task_db_id, status='failed')

    except Exception as e:
        logger.error(f"[Scanner] 恢复轮询异常 id={task_db_id}: {type(e).__name__}: {e}")
        update_video_task(task_db_id, status='failed')


def _resume_processing_tasks() -> None:
    """启动时恢复处理中的任务"""
    try:
        tasks = get_processing_video_tasks()
        if not tasks:
            logger.info("[Scanner] 无需恢复的处理中任务")
            return

        settings = get_all_settings()
        result, err = _get_sora2_service(settings)
        if err or not result:
            logger.error(f"[Scanner] 恢复任务失败，获取 Sora2 服务失败: {err}")
            for task in tasks:
                update_video_task(task.id, status='pending')
            return

        service, model = result
        pool = get_pool()
        if not pool:
            logger.error("[Scanner] 恢复任务失败，线程池未初始化")
            return

        for task in tasks:
            remote_id = task.remote_task_id or ""
            if remote_id:
                logger.info(f"[Scanner] 恢复轮询任务 id={task.id}, remote_id={remote_id}")
                pool.submit(_resume_poll_task, task, service)
            else:
                logger.info(f"[Scanner] 任务 id={task.id} 无 remote_task_id，重置为 pending")
                update_video_task(task.id, status='pending')

        logger.info(f"[Scanner] 已恢复 {len(tasks)} 个处理中的任务")
    except Exception as e:
        logger.error(f"[Scanner] 恢复处理中任务异常: {type(e).__name__}: {e}")


def start_scanner() -> None:
    """启动后台扫描线程"""
    _resume_processing_tasks()

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
                    logger.debug(f"[Scanner] 第{scan_count}轮扫描, 无待处理任务")
            except Exception as e:
                logger.error(f"[Scanner] 扫描异常: {type(e).__name__}: {e}")

            time.sleep(5)

    t = threading.Thread(target=_scan_loop, daemon=True, name="VideoScanner")
    t.start()
    logger.info("[Scanner] 扫描线程已启动")
