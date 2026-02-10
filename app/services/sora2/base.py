"""Sora2 生成基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Sora2TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"          # 等待中
    PROCESSING = "processing"    # 处理中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败


@dataclass
class Sora2Task:
    """Sora2 任务信息"""
    task_id: str                          # 任务ID
    status: Sora2TaskStatus               # 任务状态
    prompt: str                           # 提示词
    video_url: Optional[str] = None       # 视频URL（完成后）
    error_message: Optional[str] = None   # 错误信息（失败时）
    progress: int = 0                     # 进度百分比 0-100
    created_at: Optional[str] = None      # 创建时间
    completed_at: Optional[str] = None    # 完成时间


class Sora2Base(ABC):
    """Sora2 生成基类"""

    def __init__(self, api_key: str):
        """
        初始化
        
        Args:
            api_key: API密钥
        """
        self.api_key = api_key

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """提供商名称"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """API基础地址"""
        pass

    @abstractmethod
    def create_task(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "1080p",
        **kwargs
    ) -> Sora2Task:
        """
        创建生成任务
        
        Args:
            prompt: 视频描述提示词
            duration: 视频时长（秒）
            resolution: 分辨率
            **kwargs: 其他参数
            
        Returns:
            Sora2Task: 任务信息
        """
        pass

    @abstractmethod
    def query_task(self, task_id: str) -> Sora2Task:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            Sora2Task: 任务信息
        """
        pass
