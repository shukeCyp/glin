import sys
from pathlib import Path

# 路径配置
# 打包后使用 exe 所在目录，开发时使用项目根目录
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后，sys.executable 指向 exe 文件
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # 开发环境
    BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "glin.db"
STATIC_DIR = BASE_DIR / "static"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 激活密钥
ACTIVATION_SECRET = "GLIN_ACTIVATION_KEY_2024"
