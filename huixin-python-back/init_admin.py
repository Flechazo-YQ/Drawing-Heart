# -*- coding: utf-8 -*-
"""
管理员账号初始化脚本
用于创建默认的管理员账号
"""

import sys
import os

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.configs.MongoDBConfig import MongoDBConfig
from core.configs.LogConfig import LogConfig

def init_default_admin():
    """
    初始化默认管理员账号
    用户名: admin
    密码: admin123
    """
    # 初始化日志
    LogConfig.initLogging()
    
    # 初始化MongoDB连接
    MongoDBConfig.init()
    
    # 创建默认管理员
    admin = MongoDBConfig.adminManager.createAdmin(
        name='admin',
        password='admin123',
        role='super'
    )
    
    if admin:
        print('✅ 默认管理员账号创建成功！')
        print('用户名: admin')
        print('密码: admin123')
        print('⚠️  请登录后及时修改密码！')
    else:
        print('⚠️  管理员账号已存在或创建失败')
        print('如果忘记密码，请删除数据库中的 admins 集合后重新运行此脚本')

if __name__ == '__main__':
    init_default_admin()
