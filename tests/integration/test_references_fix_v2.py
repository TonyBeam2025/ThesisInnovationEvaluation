#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试专业版策略中参考文献提取修复效果
"""

import sys
import os
sys.path.append(str(PROJECT_ROOT))

from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy

def test_references_extraction():
    """测试参考文献提取功能"""
    print("🔬 测试专业版策略参考文献提取修复...")
    
    # 测试文件路径
    test_file = r".\data\input\跨模态图像融合技术在医疗影像分析中的研究.docx"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    try:
        # 使用专业版策略提取
        result = extract_sections_with_pro_strategy(test_file)
        
        if not result:
            print("❌ 提取失败，结果为空")
            return False
        
        # 检查参考文献提取结果
        references = result.get('references', [])
        literature_review = result.get('literature_review', '')
        
        print("\n📊 提取结果分析:")
        print(f"   📚 参考文献数量: {len(references)} 条")
        print(f"   📖 文献综述长度: {len(literature_review)} 字符")
        
        # 详细分析参考文献格式
        if references:
            print("\n📋 参考文献样例 (国标格式检查):")
            for i, ref in enumerate(references[:5]):  # 显示前5条
                # 检查是否包含数字编号格式
                has_bracket_number = ref.strip().startswith('[') and ']' in ref[:10]
                has_dot_number = ref.strip().split('.')[0].isdigit() if '.' in ref[:5] else False
                
                print(f"   [{i+1}] {ref[:120]}...")
                if has_bracket_number:
                    print(f"        包含[数字]编号格式")
                elif has_dot_number:
                    print(f"        包含数字.编号格式")
                else:
                    print(f"       ⚠️ 未检测到标准编号格式")
        else:
            print("   ⚠️ 没有提取到参考文献")
        
        # 分析文献综述
        if literature_review:
            print(f"\n📖 文献综述预览:")
            print(f"   {literature_review[:200]}...")
        else:
            print("   ⚠️ 没有提取到文献综述")
        
        # 成功标准
        success = len(references) > 0
        
        if success:
            print(f"\n🎉 修复成功! 专业版策略现在能正确提取参考文献")
            print(f"📈 参考文献提取完成率: {len(references)} 条")
        else:
            print(f"\n❌ 修复失败，参考文献仍为空")
        
        return success
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_references_extraction()
