import os

from typing import Final

class DirectoryState:
    SAVE_DIR: Final[str] = "uploads/saved_drawings" # 保存图片的目录
    BASE_DIR: Final[str] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) # 基础目录

