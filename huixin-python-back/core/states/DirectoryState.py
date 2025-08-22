import os

from typing import Final

class DirectoryState:
    BASE_DIR: Final[str] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # 基础目录

    SAVED_DRAWINGS_DIR: Final[str] = "uploads/saved_drawings" # 保存图片的目录
    AVATAR_DIR: Final[str] = "uploads/avatars" # 保存头像的目录

