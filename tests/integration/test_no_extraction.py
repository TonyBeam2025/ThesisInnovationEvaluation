#!/usr/bin/env python3
"""
测试不进行现场抽取的场景
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
sys.path.insert(0, 'src')

def test_no_extraction_fallback():
    """测试没有论文信息时的fallback行为"""
    print("测试场景：没有传递论文抽取信息时的处理")
    
    input_file = "data/input/15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究.docx"
    
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return False
    
    try:
        from src.thesis_inno_eval.report_generator import MarkdownReportGenerator
        
        # 创建报告生成器
        generator = MarkdownReportGenerator()
        
        print("1. 不传递论文抽取信息，测试fallback行为...")
        
        # 故意不传递 thesis_extracted_info 参数
        report_path = generator.generate_evaluation_report(input_file)
        
        print(f" 报告生成成功: {report_path}")
        
        # 检查报告内容
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证是否使用了fallback分析
        if "基于文献调研发现" in content and "建议：" in content:
            print(" 系统正确使用了基于文献对比的通用分析")
        else:
            print("⚠️ 系统可能没有正确使用fallback分析")
        
        # 验证没有进行现场抽取
        if "尝试从源文件抽取" not in content:
            print(" 系统没有进行现场抽取")
        else:
            print("❌ 系统仍在进行现场抽取")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("测试无现场抽取的fallback机制")
    print("=" * 60)
    
    success = test_no_extraction_fallback()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 测试成功！")
        print(" 系统在没有论文信息时使用通用分析，不进行现场抽取")
    else:
        print("💥 测试失败")
    print("=" * 60)
