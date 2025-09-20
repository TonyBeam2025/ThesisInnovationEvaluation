#!/usr/bin/env python3
"""
调试提示词来源
"""

import sys
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from thesis_inno_eval.extract_sections_with_gemini import extract_sections_with_gemini

def debug_prompt():
    """调试提示词的来源"""
    
    # 模拟一段简短的论文文本
    test_text = """
    学位论文测试
    
    标题：人工智能在教育中的应用研究
    
    摘要：本研究探讨了人工智能技术在现代教育中的应用前景...
    """
    
    # 打补丁以捕获实际发送的消息
    original_send_message = None
    captured_messages = []
    
    class MockAIClient:
        def send_message(self, message, session_id=None):
            captured_messages.append(message)
            print("=== 捕获的提示词 ===")
            print(message[:500] + "..." if len(message) > 500 else message)
            print("=== 提示词结束 ===")
            
            # 返回模拟响应
            class MockResponse:
                content = '''{"ChineseTitle": "测试标题", "ChineseKeywords": "测试关键词"}'''
            
            return MockResponse()
    
    # 使用模拟客户端调用函数
    try:
        result = extract_sections_with_gemini(test_text, gemini_client=MockAIClient())
        print("函数调用成功")
        print("捕获的消息数量:", len(captured_messages))
        
        # 显示捕获的提示词的关键部分
        if captured_messages:
            prompt = captured_messages[0]
            if "请从论文中抽取以下关键信息，以简洁的JSON格式输出" in prompt:
                print(" 找到神秘提示词！")
            elif "请从下方论文文本中准确抽取以下内容" in prompt:
                print(" 找到代码中的提示词！")
            else:
                print("❓ 发现了未知的提示词格式")
                
    except Exception as e:
        print(f"函数调用失败: {e}")

if __name__ == "__main__":
    debug_prompt()

