# -*- coding: utf-8 -*-
"""
管理员密码修改脚本
用于修改管理员账号密码
"""

import sys
import os
import getpass

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.configs.MongoDBConfig import MongoDBConfig
from core.configs.LogConfig import LogConfig
from core.utils.PasswordHelper import PasswordHelper
from datetime import datetime, timezone

def change_admin_password():
    """
    修改管理员密码
    """
    # 初始化日志
    LogConfig.initLogging()
    
    # 初始化MongoDB连接
    MongoDBConfig.init()
    
    print('=' * 50)
    print('管理员密码修改工具')
    print('=' * 50)
    
    # 获取管理员用户名
    username = input('请输入管理员用户名 (默认: admin): ').strip()
    if not username:
        username = 'admin'
    
    # 验证管理员是否存在
    admin = MongoDBConfig.adminManager.getAdminByName(username)
    if not admin:
        print(f'❌ 管理员 "{username}" 不存在！')
        return
    
    # 获取旧密码
    old_password = getpass.getpass('请输入当前密码: ')
    
    # 验证旧密码
    if not PasswordHelper.verifyHashPassword(old_password, admin['password']):
        print('❌ 当前密码错误！')
        return
    
    # 获取新密码
    new_password = getpass.getpass('请输入新密码: ')
    confirm_password = getpass.getpass('请再次输入新密码: ')
    
    # 验证两次输入是否一致
    if new_password != confirm_password:
        print('❌ 两次输入的密码不一致！')
        return
    
    # 验证密码长度
    if len(new_password) < 6:
        print('❌ 密码长度至少为6位！')
        return
    
    # 更新密码
    try:
        idFilter = {
            'name': username
        }
        updateQuery = {
            '$set': {
                'password': PasswordHelper.generateHashPassword(new_password),
                'timeNode.updatedAt': datetime.now(timezone.utc)
            }
        }
        
        result = MongoDBConfig.db.admins.update_one(idFilter, updateQuery)
        
        if result.modified_count > 0:
            print('✅ 密码修改成功！')
            print('请使用新密码重新登录。')
        else:
            print('❌ 密码修改失败！')
    except Exception as e:
        print(f'❌ 密码修改失败: {str(e)}')

if __name__ == '__main__':
    change_admin_password()
