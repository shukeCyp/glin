"""常量定义"""


class ApiUrls:
    """API 地址"""
    DAYANGYU = "https://api.dyuapi.com"
    YUNWU = "https://yunwu.zeabur.app"
    XIAOBANSHOU = "https://api.xintianwengai.com"
    HAOTIAN = "https://api.haoapi.top"
    BANDIANWA = "https://api.hellobabygo.com"
    GLIN = "https://glinflow.lyvideo.top"


class ModelProviders:
    """模型提供商"""
    DAYANGYU = "dayangyu"
    YUNWU = "yunwu"
    XIAOBANSHOU = "xiaobanshou"
    HAOTIAN = "haotian"
    BANDIANWA = "bandianwa"


class SettingKeys:
    """设置键名"""
    DEVICE_ID = "device_id"
    ACTIVATION_CODE = "activation_code"
    # 自定义 API
    DAYANGYU_API_KEY = "dayangyu_api_key"
    YUNWU_API_KEY = "yunwu_api_key"
    XIAOBANSHOU_API_KEY = "xiaobanshou_api_key"
    HAOTIAN_API_KEY = "haotian_api_key"
    GLIN_API_KEY = "glin_api_key"
    SORA2_MODEL = "sora2_model"
    SORA2_ORIENTATION = "sora2_orientation"
    SORA2_DURATION = "sora2_duration"
    NANOBANANA_MODEL = "nanobanana_model"
    NANOBANANA_RATIO = "nanobanana_ratio"
    NANOBANANA_QUALITY = "nanobanana_quality"
    GLIN_NANOBANANA_RATIO = "glin_nanobanana_ratio"
    GLIN_NANOBANANA_QUALITY = "glin_nanobanana_quality"
    GLIN_VEO_ORIENTATION = "glin_veo_orientation"
    # 斑点蛙
    BANDIANWA_API_KEY = "bandianwa_api_key"
    # 下载配置
    AUTO_DOWNLOAD = "auto_download"
    DOWNLOAD_PATH = "download_path"
    # 重试配置
    AUTO_RETRY = "auto_retry"
    IMAGE_MAX_RETRY = "image_max_retry"
    VIDEO_MAX_RETRY = "video_max_retry"
    # 图片处理
    IMAGE_PROCESS_PROMPT = "image_process_prompt"
    # 视频处理提示词
    VIDEO_PROCESS_PROMPT = "video_process_prompt"
    # 起号图片提示词
    QIHAO_IMAGE_PROMPT = "qihao_image_prompt"
    # 起号视频提示词
    QIHAO_VIDEO_PROMPT = "qihao_video_prompt"
    # 线程池大小
    THREAD_POOL_SIZE = "thread_pool_size"
    # 主题
    THEME = "theme"
