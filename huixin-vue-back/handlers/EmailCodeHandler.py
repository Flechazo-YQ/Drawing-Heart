import random
import smtplib

from email.mime.text import MIMEText

class EmailCodeHandler:
    sendBy = 'your_email@example.com' #替换为官方邮箱地址
    password = 'your_password' #替换为官方邮箱密码
    mailHost = 'smtp.example.com' #替换为官方邮箱SMTP服务器地址
    mailPort = 465 #替换为官方邮箱SMTP服务器端口

    #四位数字验证码生成
    @staticmethod
    def generateCode(length = 4):
        code = ''

        for i in range(length):
            code += str(random.randint(0, 9))

        return code
    
    #发送邮件, 辅助函数
    @classmethod
    def sendEmail(cls, sendTo, content, subject = '验证码'):
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = cls.sendBy
        message['To'] = sendTo
        message['Subject'] = subject
        smtp = smtplib.SMTP_SSL(cls.mailHost, cls.mailPort, 'utf-8')

        smtp.login(cls.sendBy, cls.password)
        smtp.sendmail(cls.sendBy, sendTo, message.as_string())

    #发送验证码
    @classmethod
    def sendEmailCode(cls, sendTo):
        verificateCode = cls.generateCode()
        content = f'您的验证码是：{ verificateCode }'
        
        try:
            cls.sendEmail(sendTo, content)
            return verificateCode
        except Exception as error:
            print(f'发送验证码失败: { error }')
            return False