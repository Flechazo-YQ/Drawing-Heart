from core.utils.PasswordHelper import PasswordHelper

from typing import Final

class TokenState:
    SECRET_KEY: Final[str] = 'jjj111@'
    ALGORITHM: Final[str] = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 1440
    IP: Final[str] = 'http://n42294i452.wicp.vip'
    ADMIN_CREDENTIALS: Final[dict] = {
        'admin': PasswordHelper.generateHashPassword('admin123')
    }