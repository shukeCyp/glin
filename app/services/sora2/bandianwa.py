"""斑点蛙 API Sora2 生成（请求方式与大洋芋一致）"""

from ...constants import ApiUrls
from .dayangyu import Sora2Dayangyu


class Sora2Bandianwa(Sora2Dayangyu):
    """斑点蛙 API Sora2 生成（继承大洋芋，仅覆盖 provider_name 和 base_url）"""

    @property
    def provider_name(self) -> str:
        return "斑点蛙 API"

    @property
    def base_url(self) -> str:
        return ApiUrls.BANDIANWA
