#!/usr/bin/env python3
"""
测试supervisor_en模式在实际提取中的应用
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro

def test_supervisor_en_extraction():
    """测试supervisor_en在实际提取中的效果"""
    print("🧪 测试supervisor_en在实际提取系统中的应用")
    print("=" * 60)
    
    # 创建提取器实例
    extractor = ThesisExtractorPro()
    
    # 模拟包含supervisor_en信息的文本片段
    test_texts = [
        """
        BEIJING UNIVERSITY OF POSTS AND TELECOMMUNICATIONS
        
        Research on Nonlinear Impairment Equalization Technology 
        for Coherent Optical Communication Systems Based on Neural Network
        
        By: Xiaoqian Feng
        Supervisor: Prof. Wenbo Zhang
        College: School of Science
        
        A thesis submitted in partial fulfillment
        """,
        """
        University Research Report
        
        Advanced Machine Learning Applications
        
        Author: John Smith
        Advisor: Dr. Michael Johnson
        DIRECTED BY: Professor Sarah Chen
        Under the guidance of: Dr. Robert Liu
        """,
        """
        Doctoral Dissertation
        
        Title: Innovation in AI Systems
        
        Student: Emily Davis
        SUPERVISOR: Professor David Wilson
        ADVISOR: Dr. Lisa Wang
        """,
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📄 测试文本 {i}:")
        print("-" * 40)
        
        # 使用模式匹配提取supervisor_en
        if hasattr(extractor, 'patterns') and 'supervisor_en' in extractor.patterns:
            for j, pattern in enumerate(extractor.patterns['supervisor_en'], 1):
                import re
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    print(f"   模式{j} 匹配: {matches}")
                else:
                    print(f"  ❌ 模式{j} 无匹配")
        else:
            print("  ⚠️ 未找到supervisor_en模式定义")
    
    print("\n" + "=" * 60)
    print(" 实际提取测试完成")

if __name__ == "__main__":
    test_supervisor_en_extraction()
