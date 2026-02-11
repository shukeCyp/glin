import sys
from pathlib import Path

# 路径配置
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后
    # 用户数据目录：exe 所在目录（数据库、日志等持久化文件）
    BASE_DIR = Path(sys.executable).resolve().parent
    # 打包资源目录：PyInstaller 解压的临时目录（static 等只读资源）
    _BUNDLE_DIR = Path(sys._MEIPASS)
else:
    # 开发环境
    BASE_DIR = Path(__file__).resolve().parent.parent
    _BUNDLE_DIR = BASE_DIR

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "glin.db"
STATIC_DIR = _BUNDLE_DIR / "static"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 激活密钥
ACTIVATION_SECRET = "GLIN_ACTIVATION_KEY_2024"
