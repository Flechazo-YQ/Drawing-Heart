import random, logging, traceback

from datetime import datetime, timedelta, timezone
from email import utils
from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from typing import Final, TYPE_CHECKING

if (TYPE_CHECKING):
    from core.configs.MongoDBConfig import MongoDBConfig

class CodeManager:
    SEND_BY: Final[str] = '1241010058@zust.edu.cn'  # 官方邮箱地址
    PASSWORD: Final[str] = 'BbSBhhaLuxaCjQ8e'  # 官方邮箱授权码
    MAIL_HOST: Final[str] = 'smtp.exmail.qq.com'  # 官方邮箱SMTP服务器地址
    MAIL_PORT: Final[int] = 465  # 官方邮箱SMTP_SSL服务器端口

    def __init__(self, db: 'MongoDBConfig.MongoDB'):
        self.db = db

    # 创建验证码
    def createCode(self, email: str, purpose: str, ttlMinutes: int = 10):
        try:
            code = self.generateCode()
            expiredAt = datetime.now(timezone.utc) + timedelta(minutes=ttlMinutes)
            emailFilter = {
                'email': email,
                'purpose': purpose
            }
            updateQuery = {
                '$set': {
                    'code': code,
                    'expiredAt': expiredAt,
                    'createAt': datetime.now(timezone.utc)
                }
            }

            self.db.codes.update_one(emailFilter, updateQuery, upsert=True)
            return code
        except Exception as e:
            logging.error(f'❌ 创建验证码失败: { str(e) }')
            return None

    # 验证验证码
    def verifyCode(self, email: str, code: str, purpose: str) -> bool:
        try:
            updateQuery = {
                'email': email,
                'code': code,
                'purpose': purpose,
                'expiredAt': {
                    '$gt': datetime.now(timezone.utc)
                }
            }
            result = self.db.codes.find_one_and_delete(updateQuery)

            if (not result):
                logging.warning(f'⚠️ 验证码 { code } for { email } ({ purpose }) 验证失败或已过期。')

            logging.info(f'✅ 验证码 { code } for { email } ({ purpose }) 验证成功。')
            return True
        except Exception as e:
            logging.error(f'❌ 验证码 { code } for { email } ({ purpose }) 验证失败: { str(e) }')
            return False

    # 四位数字验证码生成
    @staticmethod
    def generateCode(length: int = 4):
        code = ''

        for _ in range(length):
            code += str(random.randint(0, 9))

        return code
    
    # 发送邮件，辅助函数
    @classmethod
    def sendEmail(cls, sendTo: str, content: str, subject: str = '验证码'):
        try:
            logging.info(f'准备邮件: 发送到 { sendTo }, 主题 { subject }')

            message = MIMEText(content, 'plain', 'utf-8')
            message['From'] = utils.formataddr(('绘心同学', cls.SEND_BY))
            message['To'] = sendTo
            message['Subject'] = subject

            logging.info(f'连接SMTP服务器: { cls.MAIL_HOST }:{ cls.MAIL_PORT }')

            smtp = SMTP_SSL(cls.MAIL_HOST, cls.MAIL_PORT)

            logging.info(f'登录邮箱: { cls.SEND_BY }')
            smtp.login(cls.SEND_BY, cls.PASSWORD)
            logging.info(f'发送邮件: 从 { cls.SEND_BY } 到 { sendTo }')
            smtp.sendmail(cls.SEND_BY, sendTo, message.as_string())
            logging.info(f'关闭SMTP连接')
            smtp.quit()
            logging.info('邮件发送成功')
        except Exception as e:
            logging.error(f'❌ 邮件发送过程中出错: { str(e) }')
            raise

    # 发送验证码
    @classmethod
    def sendEmailCode(cls, sendTo: str):
        verificateCode = cls.generateCode()
        content = f'【绘心同学】您的验证码是：{ verificateCode }。60秒内有效，请勿向任何人泄露。如非本人操作，请忽略此邮件。'

        try:
            logging.info(f'开始向 { sendTo } 发送验证码')
            cls.sendEmail(sendTo, content)
            logging.info(f'向 { sendTo } 发送验证码成功')
            return verificateCode
        except Exception as e:
            logging.error(f'❌ 向 { sendTo } 发送验证码失败：{ str(e) }')
            traceback.print_exc()
            return False