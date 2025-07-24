#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI对话实时分析更新功能测试脚本
测试AI在每次对话前是否能正确获取最新的绘画分析
"""

import requests
import json
import time
import datetime
from typing import Dict, Optional

class ChatAnalysisTest:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.chat_id = None
        
    def login(self, username: str, password: str) -> bool:
        """登录获取token"""
        try:
            response = requests.post(f"{self.base_url}/api/login", json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    self.token = data['data']['access_token']
                    print(f"✅ 登录成功，token: {self.token[:20]}...")
                    return True
            
            print(f"❌ 登录失败: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ 登录错误: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def create_test_analysis(self) -> bool:
        """创建测试分析数据（模拟绘画分析）"""
        try:
            # 这里可以调用绘画分析API来创建测试数据
            # 或者直接在数据库中插入测试数据
            print("📊 创建测试分析数据...")
            # 实际实现需要根据系统的绘画分析API来调整
            return True
        except Exception as e:
            print(f"❌ 创建测试分析失败: {str(e)}")
            return False
    
    def get_latest_analysis(self, time_limit: str = "recent") -> Optional[Dict]:
        """获取最新分析结果"""
        try:
            response = requests.get(
                f"{self.base_url}/api/user/latest-analysis?time_limit={time_limit}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data')
            
            return None
            
        except Exception as e:
            print(f"❌ 获取分析失败: {str(e)}")
            return None
    
    def send_chat_message(self, message: str) -> str:
        """发送聊天消息"""
        try:
            response = requests.post(
                f"{self.base_url}/api/stream-chat",
                headers=self.get_headers(),
                json={"message": message}
            )
            
            if response.status_code == 200:
                # 处理流式响应或普通响应
                return response.text
            else:
                return f"Error: {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def test_real_time_analysis_update(self):
        """测试实时分析更新功能"""
        print("\\n=== AI对话实时分析更新功能测试 ===\\n")
        
        # 1. 检查初始状态
        print("--- 步骤1：检查初始分析状态 ---")
        initial_analysis = self.get_latest_analysis()
        if initial_analysis:
            print(f"✅ 找到初始分析：{initial_analysis['analysis_date']}")
            print(f"   分析ID：{initial_analysis.get('_id', 'unknown')}")
        else:
            print("ℹ️  暂无分析记录")
        
        # 2. 发送第一条消息
        print("\\n--- 步骤2：发送第一条聊天消息 ---")
        response1 = self.send_chat_message("你好，我想了解一下我的心理状态")
        print(f"AI回复长度：{len(response1)} 字符")
        print(f"回复预览：{response1[:100]}...")
        
        # 3. 等待一段时间（模拟用户完成新的绘画分析）
        print("\\n--- 步骤3：等待期间（模拟用户完成新分析）---")
        print("⏰ 等待5秒...")
        time.sleep(5)
        
        # 4. 创建新的分析数据（模拟）
        print("\\n--- 步骤4：模拟创建新的分析数据 ---")
        self.create_test_analysis()
        
        # 5. 发送第二条消息，测试是否获取到新分析
        print("\\n--- 步骤5：发送第二条消息（测试实时更新）---")
        response2 = self.send_chat_message("请根据我最新的绘画分析给我一些建议")
        print(f"AI回复长度：{len(response2)} 字符")
        print(f"回复预览：{response2[:100]}...")
        
        # 6. 验证分析是否更新
        print("\\n--- 步骤6：验证分析获取情况 ---")
        latest_analysis = self.get_latest_analysis()
        if latest_analysis:
            print(f"✅ 当前最新分析：{latest_analysis['analysis_date']}")
            print(f"   分析ID：{latest_analysis.get('_id', 'unknown')}")
            
            if initial_analysis and latest_analysis.get('_id') != initial_analysis.get('_id'):
                print("🎯 检测到分析数据已更新！")
            else:
                print("ℹ️  分析数据未发生变化")
        else:
            print("ℹ️  当前无分析记录")
        
        # 7. 测试不同时间限制参数
        print("\\n--- 步骤7：测试不同时间限制参数 ---")
        time_limits = ['today', '4hours', 'recent', 'none']
        for limit in time_limits:
            analysis = self.get_latest_analysis(limit)
            status = "有" if analysis else "无"
            print(f"   {limit}: {status}分析记录")
    
    def test_context_isolation(self):
        """测试用户上下文隔离"""
        print("\\n=== 用户上下文隔离测试 ===\\n")
        
        # 发送多条消息测试上下文
        messages = [
            "我叫小明",
            "我今年25岁",
            "你还记得我的名字吗？",
            "我的年龄是多少？"
        ]
        
        for i, msg in enumerate(messages, 1):
            print(f"--- 消息{i}：{msg} ---")
            response = self.send_chat_message(msg)
            print(f"AI回复预览：{response[:50]}...")
            time.sleep(1)  # 避免请求过快
    
    def run_all_tests(self):
        """运行所有测试"""
        if not self.token:
            print("❌ 请先登录")
            return
        
        try:
            self.test_real_time_analysis_update()
            self.test_context_isolation()
            print("\\n=== 所有测试完成 ===")
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误：{str(e)}")

def main():
    """主函数"""
    print("AI对话实时分析更新功能测试")
    print("=" * 50)
    
    # 配置测试参数
    tester = ChatAnalysisTest("http://localhost:5000")  # 根据实际服务器地址调整
    
    # 获取登录信息
    username = input("请输入用户名: ").strip()
    password = input("请输入密码: ").strip()
    
    if not username or not password:
        print("❌ 用户名或密码不能为空")
        return
    
    # 登录
    if not tester.login(username, password):
        return
    
    # 运行测试
    tester.run_all_tests()

if __name__ == "__main__":
    main()
