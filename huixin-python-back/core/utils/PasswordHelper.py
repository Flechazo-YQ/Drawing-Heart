import hashlib

class PasswordHelper:

    # 创建Hash对象实现密码混淆加密
    @staticmethod
    def generateHashPassword(password: str):
        shaSignature = hashlib.sha256(password.encode()).hexdigest()

        return shaSignature

    # 验证密码是否匹配
    @classmethod
    def verifyHashPassword(cls, password: str, storedHashPassword: str):
        return cls.generateHashPassword(password) == storedHashPassword