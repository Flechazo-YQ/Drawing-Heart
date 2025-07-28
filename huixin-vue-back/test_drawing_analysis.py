#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绘画分析数据库功能测试脚本
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mongodb_config import init_mongodb, drawing_analysis_manager

# 配置日志
logging.basicConfig(level=logging.INFO)

def test_drawing_analysis_db():
    """测试绘画分析数据库功能"""
    try:
        # 初始化数据库
        print("正在初始化数据库...")
        init_mongodb()
        print("数据库初始化成功！")
        
        # 测试用户ID（请替换为实际的用户ID）
        test_user_id = "60f1b2b5e4b0a123456789ab"  # 示例用户ID
        
        # 测试保存分析结果
        print("\n测试保存分析结果...")
        analysis_id = drawing_analysis_manager.save_analysis(
            user_id=test_user_id,
            image_path="/test/path/drawing.png",
            analysis_result="这是一个测试分析结果。用户的绘画显示了积极的情绪状态，画面布局合理，色彩搭配和谐。",
            image_size="1024 bytes",
            analysis_type="house_tree_person",
            ai_model="doubao-1-5-vision-pro",
            tags=["积极", "稳定", "创造力"],
            anxiety_level=2,
            depression_level=1,
            stress_level=3,
            confidence_level=8,
            creativity_level=7
        )
        print(f"分析结果保存成功，ID: {analysis_id}")
        
        # 测试获取当日分析结果
        print("\n测试获取当日分析结果...")
        today_analysis = drawing_analysis_manager.get_today_analysis(test_user_id)
        if today_analysis:
            print(f"找到当日分析结果: {today_analysis['analysis_result'][:50]}...")
        else:
            print("未找到当日分析结果")
        
        # 测试获取最新分析结果
        print("\n测试获取最新分析结果...")
        latest_analysis = drawing_analysis_manager.get_latest_analysis(test_user_id)
        if latest_analysis:
            print(f"找到最新分析结果: 日期={latest_analysis['analysis_date']}, 内容={latest_analysis['analysis_result'][:50]}...")
        else:
            print("未找到最新分析结果")
        
        # 测试获取用户历史分析
        print("\n测试获取用户分析历史...")
        analyses = drawing_analysis_manager.get_user_analyses(test_user_id, limit=5)
        print(f"找到 {len(analyses)} 条历史分析记录")
        for i, analysis in enumerate(analyses):
            print(f"  {i+1}. 日期: {analysis['analysis_date']}, 内容: {analysis['analysis_result'][:30]}...")
        
        print("\n所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_drawing_analysis_db()
