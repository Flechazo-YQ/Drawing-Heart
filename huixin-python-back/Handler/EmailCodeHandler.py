import random
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

class EmailCodeHandler:
    sendBy = '1241010058@zust.edu.cn'  # 官方邮箱地址
    password = 'BbSBhhaLuxaCjQ8e'  # 官方邮箱授权码
    mailHost = 'smtp.exmail.qq.com'  # 官方邮箱SMTP服务器地址
    mailPort = 465  # 官方邮箱SMTP_SSL服务器端口

    # 四位数字验证码生成
    @staticmethod
    def generateCode(length=4):
        code = ''
        for i in range(length):
            code += str(random.randint(0, 9))
        return code

    # 发送邮件，辅助函数
    @classmethod
    def sendEmail(cls, sendTo, content, subject='验证码'):
        try:
            print(f'准备邮件: 发送到 {sendTo}, 主题 {subject}')
            message = MIMEText(content, 'plain', 'utf-8')
            message['From'] = formataddr(('绘心同学', cls.sendBy))
            message['To'] = sendTo
            message['Subject'] = subject
            
            print(f'连接SMTP服务器: {cls.mailHost}:{cls.mailPort}')
            smtp = smtplib.SMTP_SSL(cls.mailHost, cls.mailPort)
            
            print(f'登录邮箱: {cls.sendBy}')
            smtp.login(cls.sendBy, cls.password)
            
            print(f'发送邮件: 从 {cls.sendBy} 到 {sendTo}')
            smtp.sendmail(cls.sendBy, sendTo, message.as_string())
            
            print('关闭SMTP连接')
            smtp.quit()
            print('邮件发送成功')
        except Exception as e:
            print(f'邮件发送过程中出错: {str(e)}')
            raise  # 重新抛出异常以便上层捕获

    # 发送验证码
    @classmethod
    def sendEmailCode(cls, sendTo):
        verificateCode = cls.generateCode()
        content = f'【绘心同学】您的验证码是：{verificateCode}。60秒内有效，请勿向任何人泄露。如非本人操作，请忽略此邮件。'
        try:
            print(f'开始向 {sendTo} 发送验证码')
            cls.sendEmail(sendTo, content)
            print(f'向 {sendTo} 发送验证码成功')
            return verificateCode
        except Exception as error:
            print(f'向 {sendTo} 发送验证码失败：{error}')
            import traceback
            traceback.print_exc()  # 打印完整的错误堆栈
            return False