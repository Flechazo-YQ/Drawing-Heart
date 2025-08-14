import random, smtplib, traceback, logging

from email.mime.text import MIMEText
from email.utils import formataddr

from typing import Final

class EmailCodeHandler:
    SEND_BY: Final[str] = "1241010058@zust.edu.cn"  # 官方邮箱地址
    PASSWORD: Final[str] = "BbSBhhaLuxaCjQ8e"  # 官方邮箱授权码
    MAIL_HOST: Final[str] = "smtp.exmail.qq.com"  # 官方邮箱SMTP服务器地址
    MAIL_PORT: Final[int] = 465  # 官方邮箱SMTP_SSL服务器端口

    # 四位数字验证码生成
    @staticmethod
    def generateCode(length: int = 4):
        code = ""

        for _ in range(length):
            code += str(random.randint(0, 9))

        return code

    # 发送邮件，辅助函数
    @classmethod
    def sendEmail(cls, sendTo: str, content: str, subject: str = "验证码"):
        try:
            logging.info(f"准备邮件: 发送到 { sendTo }, 主题 { subject }")

            message = MIMEText(content, "plain", "utf-8")
            message["From"] = formataddr(("绘心同学", cls.SEND_BY))
            message["To"] = sendTo
            message["Subject"] = subject

            logging.info(f"连接SMTP服务器: { cls.MAIL_HOST }:{ cls.MAIL_PORT }")

            smtp = smtplib.SMTP_SSL(cls.MAIL_HOST, cls.MAIL_PORT)

            logging.info(f"登录邮箱: { cls.SEND_BY }")
            smtp.login(cls.SEND_BY, cls.PASSWORD)
            logging.info(f"发送邮件: 从 { cls.SEND_BY } 到 { sendTo }")
            smtp.sendmail(cls.SEND_BY, sendTo, message.as_string())
            logging.info(f"关闭SMTP连接")
            smtp.quit()
            logging.info("邮件发送成功")
        except Exception as e:
            logging.error(f"❌ 邮件发送过程中出错: { str(e) }")
            raise  # 重新抛出异常以便上层捕获

    # 发送验证码
    @classmethod
    def sendEmailCode(cls, sendTo: str):
        verificateCode = cls.generateCode()
        content = f"【绘心同学】您的验证码是：{ verificateCode }。60秒内有效，请勿向任何人泄露。如非本人操作，请忽略此邮件。"

        try:
            logging.info(f"开始向 { sendTo } 发送验证码")
            cls.sendEmail(sendTo, content)
            logging.info(f"向 { sendTo } 发送验证码成功")
            return verificateCode
        except Exception as e:
            logging.error(f"❌ 向 { sendTo } 发送验证码失败：{ str(e) }")
            traceback.print_exc()  # 打印完整的错误堆栈
            return False