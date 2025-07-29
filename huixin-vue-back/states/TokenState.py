import hashlib

class TokenState:
    HAS_SECRET_KEY = 'jjj111@'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

    #创建sha256 Hash对象实现密码混淆加密
    @staticmethod
    def sha256Hash(password):
        shaSignature = hashlib.sha256(password.encode()).hexdigest()

        return shaSignature
    
    ADMIN_CREDENTIALS = {
        'admin': sha256Hash('admin123')
    }