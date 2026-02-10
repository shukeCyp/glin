"""官方 API NanoBanana 图片生成（请求方式与云雾一致）"""

from ...constants import ApiUrls
from .yunwu import NanoBananaYunwu


class NanoBananaGuanfang(NanoBananaYunwu):
    """官方 API NanoBanana 图片生成（继承云雾，仅覆盖 provider_name 和 base_url）"""

    @property
    def provider_name(self) -> str:
        return "官方 API"

    @property
    def base_url(self) -> str:
        return ApiUrls.GUANFANG
