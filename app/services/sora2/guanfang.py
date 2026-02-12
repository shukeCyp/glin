"""官方 API Sora2 生成（请求方式与大洋芋一致 / 小扳手一致）"""

from ...constants import ApiUrls
from .dayangyu import Sora2Dayangyu
from .xiaobanshou import Sora2Xiaobanshou


class Sora2Guanfang(Sora2Dayangyu):
    """官方 API Sora2 生成 - DYY 调用方式（继承大洋芋，仅覆盖 provider_name 和 base_url）"""

    @property
    def provider_name(self) -> str:
        return "官方 API (DYY)"

    @property
    def base_url(self) -> str:
        return ApiUrls.GUANFANG


class Sora2GuanfangXbs(Sora2Xiaobanshou):
    """官方 API Sora2 生成 - XBS 调用方式（继承小扳手，仅覆盖 provider_name 和 base_url）"""

    @property
    def provider_name(self) -> str:
        return "官方 API (XBS)"

    @property
    def base_url(self) -> str:
        return ApiUrls.GUANFANG
