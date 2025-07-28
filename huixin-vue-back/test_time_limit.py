#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
绘画分析时间限制功能测试脚本
测试当日和4小时内的分析结果获取功能
"""

import sys
import os
import datetime
import logging
from bson import ObjectId

# 添加项目根目录到路径
sys.path.append(os.path.dirname(__file__))

from mongodb_config import init_mongodb, drawing_analysis_manager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_time_limit_analysis():
    """测试时间限制分析功能"""
    print("=== 绘画分析时间限制功能测试 ===\n")
    
    try:
        # 初始化数据库
        init_mongodb()
        print("✅ MongoDB连接成功")
        
        # 创建测试用户ID（如果没有真实用户，使用模拟ID）
        test_user_id = "60f1b2b5e1234567890abcde"  # 模拟用户ID
        
        print(f"\n🔍 测试用户ID: {test_user_id}")
        
        # 测试1：获取当日分析
        print("\n--- 测试1：获取当日分析 ---")
        today_analysis = drawing_analysis_manager.get_recent_analysis(test_user_id, hours=0)
        if today_analysis:
            print(f"✅ 找到当日分析：{today_analysis['analysis_date']}")
            print(f"   创建时间：{today_analysis['created_at']}")
            print(f"   分析结果：{today_analysis['analysis_result'][:100]}...")
        else:
            print("ℹ️  当日暂无分析记录")
        
        # 测试2：获取4小时内分析
        print("\n--- 测试2：获取4小时内分析 ---")
        recent_analysis = drawing_analysis_manager.get_recent_analysis(test_user_id, hours=4)
        if recent_analysis:
            print(f"✅ 找到4小时内分析：{recent_analysis['analysis_date']}")
            print(f"   创建时间：{recent_analysis['created_at']}")
            print(f"   分析结果：{recent_analysis['analysis_result'][:100]}...")
        else:
            print("ℹ️  4小时内暂无分析记录")
        
        # 测试3：获取最新分析（不限时间）
        print("\n--- 测试3：获取最新分析（不限时间）---")
        latest_analysis = drawing_analysis_manager.get_latest_analysis(test_user_id)
        if latest_analysis:
            print(f"✅ 找到最新分析：{latest_analysis['analysis_date']}")
            print(f"   创建时间：{latest_analysis['created_at']}")
            print(f"   分析结果：{latest_analysis['analysis_result'][:100]}...")
        else:
            print("ℹ️  暂无任何分析记录")
        
        # 测试4：模拟AI对话时的逻辑
        print("\n--- 测试4：模拟AI对话逻辑 ---")
        # 优先获取当日分析
        ai_analysis = drawing_analysis_manager.get_recent_analysis(test_user_id, hours=0)
        
        if not ai_analysis:
            # 如果当日没有，获取4小时内的分析
            ai_analysis = drawing_analysis_manager.get_recent_analysis(test_user_id, hours=4)
        
        if ai_analysis:
            analysis_date = ai_analysis['analysis_date']
            print(f"✅ AI将参考分析结果：{analysis_date}")
            print(f"   分析内容：{ai_analysis['analysis_result'][:100]}...")
            
            # 构建系统消息（模拟）
            system_message = f"你现在是一名心理医师，你的名字叫绘心同学。用户在{analysis_date}完成了心理绘画测试，以下是最新的分析结果：{ai_analysis['analysis_result']}"
            print(f"   系统消息长度：{len(system_message)} 字符")
        else:
            print("ℹ️  AI将不参考任何分析结果（无符合时间条件的分析）")
        
        # 测试5：时间边界测试
        print("\n--- 测试5：时间边界测试 ---")
        test_hours = [1, 2, 6, 12, 24]
        for hours in test_hours:
            result = drawing_analysis_manager.get_recent_analysis(test_user_id, hours=hours)
            status = "有" if result else "无"
            print(f"   {hours}小时内：{status}分析记录")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")
        logging.error(f"测试错误：{str(e)}")

def create_test_analysis(user_id: str, hours_ago: int = 0):
    """创建测试分析数据"""
    try:
        current_time = datetime.datetime.utcnow()
        test_time = current_time - datetime.timedelta(hours=hours_ago)
        
        test_analysis = {
            "user_id": ObjectId(user_id),
            "image_url": "test_image.png",
            "analysis_result": f"这是{hours_ago}小时前的测试分析结果。用户心理状态良好，表现出积极的情绪特征。",
            "analysis_date": test_time.strftime("%Y年%m月%d日"),
            "emotion_scores": {
                "happiness": 0.8,
                "sadness": 0.1,
                "anxiety": 0.1
            },
            "psychological_indicators": {
                "stress_level": "低",
                "emotional_stability": "稳定",
                "social_connection": "良好"
            },
            "created_at": test_time,
            "updated_at": test_time,
            "is_active": True
        }
        
        result = drawing_analysis_manager.save_analysis(test_analysis)
        if result:
            print(f"✅ 创建测试分析成功：{hours_ago}小时前")
            return result
        else:
            print(f"❌ 创建测试分析失败：{hours_ago}小时前")
            return None
            
    except Exception as e:
        print(f"❌ 创建测试分析错误：{str(e)}")
        return None

def setup_test_data():
    """设置测试数据"""
    print("=== 设置测试数据 ===")
    test_user_id = "60f1b2b5e1234567890abcde"
    
    # 创建不同时间的测试分析
    test_scenarios = [
        (0, "当前时间"),
        (2, "2小时前"),
        (5, "5小时前"),
        (25, "25小时前（昨天）")
    ]
    
    for hours_ago, description in test_scenarios:
        create_test_analysis(test_user_id, hours_ago)
    
    print("测试数据创建完成\n")

if __name__ == "__main__":
    # 询问是否创建测试数据
    create_data = input("是否创建测试数据？(y/n): ").lower().strip()
    
    if create_data == 'y':
        setup_test_data()
    
    # 运行测试
    test_time_limit_analysis()
