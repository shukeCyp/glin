"""常量定义"""


class ApiUrls:
    """API 地址"""
    DAYANGYU = "https://api.dyuapi.com"
    YUNWU = "https://yunwu.zeabur.app"
    XIAOBANSHOU = "https://api.xintianwengai.com"
    GUANFANG = "https://api.haoapi.top"
    BANDIANWA = "https://api.hellobabygo.com"


class ModelProviders:
    """模型提供商"""
    DAYANGYU = "dayangyu"
    YUNWU = "yunwu"
    XIAOBANSHOU = "xiaobanshou"
    GUANFANG = "guanfang"
    HAOTIAN = "haotian"
    BANDIANWA = "bandianwa"


class SettingKeys:
    """设置键名"""
    DEVICE_ID = "device_id"
    ACTIVATION_CODE = "activation_code"
    # API 模式: official / custom
    API_MODE = "api_mode"
    # 官方 API
    GUANFANG_API_KEY = "guanfang_api_key"
    GUANFANG_SORA2_PROVIDER = "guanfang_sora2_provider"
    GUANFANG_SORA2_MODEL = "guanfang_sora2_model"
    # 自定义 API
    DAYANGYU_API_KEY = "dayangyu_api_key"
    YUNWU_API_KEY = "yunwu_api_key"
    XIAOBANSHOU_API_KEY = "xiaobanshou_api_key"
    SORA2_MODEL = "sora2_model"
    NANOBANANA_MODEL = "nanobanana_model"
    NANOBANANA_RATIO = "nanobanana_ratio"
    NANOBANANA_QUALITY = "nanobanana_quality"
    # 大洋芋 Sora2 配置
    DAYANGYU_SORA2_MODEL = "dayangyu_sora2_model"
    # 云雾 Sora2 配置
    YUNWU_SORA2_ORIENTATION = "yunwu_sora2_orientation"
    YUNWU_SORA2_DURATION = "yunwu_sora2_duration"
    # 小扳手 Sora2 配置
    XIAOBANSHOU_SORA2_MODEL = "xiaobanshou_sora2_model"
    # 斑点蛙 Sora2 配置
    BANDIANWA_API_KEY = "bandianwa_api_key"
    BANDIANWA_SORA2_MODEL = "bandianwa_sora2_model"
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
    # 线程池大小
    THREAD_POOL_SIZE = "thread_pool_size"
