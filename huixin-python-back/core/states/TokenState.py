import hashlib

from typing import Final

class TokenState:
    HAS_SECRET_KEY: Final[str] = 'jjj111@'
    ALGORITHM: Final[str] = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 60
    IP: Final[str] = 'http://n42294i452.wicp.vip'

    #创建sha256 Hash对象实现密码混淆加密
    @staticmethod
    def sha256Hash(password: str):
        shaSignature = hashlib.sha256(password.encode()).hexdigest()

        return shaSignature

    ADMIN_CREDENTIALS: Final[dict] = {
        'admin': sha256Hash('admin123')
    }