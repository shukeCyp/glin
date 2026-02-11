import os
import sys
from pathlib import Path

# 路径配置
if getattr(sys, 'frozen', False):
    # 打包后：数据存放到 APPDATA/Roaming/Glin（Windows）或 ~/Library/Application Support/Glin（macOS）
    _appdata = os.environ.get("APPDATA") or os.path.expanduser("~/Library/Application Support")
    BASE_DIR = Path(_appdata) / "Glin"
    STATIC_DIR = Path(sys._MEIPASS) / "static"
else:
    # 开发环境：项目根目录
    BASE_DIR = Path(__file__).resolve().parent.parent
    STATIC_DIR = BASE_DIR / "static"

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "glin.db"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 激活密钥
ACTIVATION_SECRET = "GLIN_ACTIVATION_KEY_2024"
