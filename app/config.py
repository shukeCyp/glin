import sys
from pathlib import Path

# 路径配置
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "glin.db"

# 静态资源目录：打包后从 _MEIPASS 读取，开发时从项目根目录读取
if getattr(sys, 'frozen', False):
    STATIC_DIR = Path(sys._MEIPASS) / "static"
else:
    STATIC_DIR = BASE_DIR / "static"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 激活密钥
ACTIVATION_SECRET = "GLIN_ACTIVATION_KEY_2024"
