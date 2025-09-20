#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试连接池修复效果
"""

import sys
import os
import time
sys.path.append(str(PROJECT_ROOT))

from src.thesis_inno_eval.ai_client import get_ai_client

def test_connection_pool():
    """测试连接池是否正确释放连接"""
    print("🔧 测试连接池修复效果...")
    
    try:
        # 获取AI客户端
        client = get_ai_client()
        
        print(f"📊 初始状态:")
        print(f"   API类型: {client.get_api_type()}")
        print(f"   活跃会话: {len(client.get_active_sessions())}")
        
        # 测试多次调用
        print(f"\n🔄 测试多次AI调用...")
        test_messages = [
            "Hello, this is test message 1",
            "Hello, this is test message 2", 
            "Hello, this is test message 3",
            "Hello, this is test message 4",
            "Hello, this is test message 5"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"   发送消息 {i}/5...")
            
            # 记录调用前的状态
            sessions_before = len(client.get_active_sessions())
            
            # 发送消息
            response = client.send_message(message)
            
            # 记录调用后的状态
            sessions_after = len(client.get_active_sessions())
            
            print(f"     响应长度: {len(response.content) if response else 0} 字符")
            print(f"     会话数变化: {sessions_before} → {sessions_after}")
            
            # 短暂等待
            time.sleep(1)
        
        print(f"\n📊 最终状态:")
        final_sessions = client.get_active_sessions()
        print(f"   活跃会话: {len(final_sessions)}")
        
        if len(final_sessions) <= 1:  # 应该只有很少的活跃会话
            print(" 连接池测试通过 - 会话正确释放")
            return True
        else:
            print("❌ 连接池测试失败 - 存在会话泄露")
            print(f"   泄露的会话: {final_sessions}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_processing():
    """测试批量处理的连接池效果"""
    print("\n🔄 测试批量处理...")
    
    try:
        client = get_ai_client()
        
        # 记录批量处理前的状态
        sessions_before = len(client.get_active_sessions())
        print(f"   批量处理前活跃会话: {sessions_before}")
        
        # 批量发送消息
        batch_messages = [
            "Batch message 1",
            "Batch message 2",
            "Batch message 3"
        ]
        
        responses = client.send_messages_batch(batch_messages)
        
        # 记录批量处理后的状态
        sessions_after = len(client.get_active_sessions())
        print(f"   批量处理后活跃会话: {sessions_after}")
        print(f"   成功响应数: {len([r for r in responses if r])}/{len(batch_messages)}")
        
        # 等待一下确保清理完成
        time.sleep(2)
        sessions_final = len(client.get_active_sessions())
        print(f"   等待清理后活跃会话: {sessions_final}")
        
        if sessions_final <= sessions_before + 1:  # 允许有少量增长
            print(" 批量处理测试通过")
            return True
        else:
            print("❌ 批量处理测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 批量处理测试错误: {e}")
        return False

if __name__ == "__main__":
    print("🧪 连接池修复验证测试")
    print("=" * 50)
    
    # 测试单次调用
    test1_result = test_connection_pool()
    
    # 测试批量调用
    test2_result = test_batch_processing()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"   单次调用测试: {'' if test1_result else '❌'}")
    print(f"   批量处理测试: {'' if test2_result else '❌'}")
    
    if test1_result and test2_result:
        print("\n🎉 连接池修复成功!")
        print("    会话正确释放，不会出现连接池耗尽问题")
    else:
        print("\n⚠️ 连接池修复不完全，仍需改进")
