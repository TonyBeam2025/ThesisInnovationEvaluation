#!/usr/bin/env python3
"""
测试新的论文评估流程
测试cnki_auto_search返回结构化信息并传递给report_generator
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import os
import sys
sys.path.insert(0, 'src')

from src.thesis_inno_eval.report_generator import MarkdownReportGenerator

def test_report_generation():
    """测试报告生成功能"""
    
    # 输入文件路径
    input_file = "data/input/15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究.docx"
    
    # 模拟从cnki_auto_search返回的论文抽取信息
    mock_thesis_info = {
        'ChineseTitle': '基于风险管理视角的互联网医院政策文本量化分析与优化路径研究',
        'ChineseKeywords': '互联网医院;政策文本;风险管理;量化分析;PMC指数',
        'ChineseAbstract': '本研究运用PMC指数评价模型对互联网医院政策进行量化分析...',
        'ResearchMethods': 'PMC指数评价模型、ROST CM 6.0文本挖掘、五维度评价框架',
        'TheoreticalFramework': '风险管理理论、内部控制理论、协同治理理论',
        'PracticalProblems': '互联网医院政策碎片化、风险预警机制不完善、协同治理缺失',
        'MainInnovations': 'PMC指数模型在互联网医院政策分析中的首次应用、风险管理视角的政策量化分析框架',
        'ProposedSolutions': '构建风险预警动态库、建立协同治理机制、完善政策评价体系',
        'ResearchConclusions': '提出了系统性的互联网医院政策优化路径',
        'ApplicationValue': '为政策制定部门和医院管理层提供科学决策依据'
    }
    
    print("开始测试报告生成...")
    
    try:
        # 创建报告生成器
        generator = MarkdownReportGenerator()
        
        # 生成评估报告，传递模拟的论文信息
        report_path = generator.generate_evaluation_report(
            input_file, 
            thesis_extracted_info=mock_thesis_info
        )
        
        print(f" 报告生成成功: {report_path}")
        
        # 读取并显示报告的前几行
        print("\n📄 报告预览:")
        print("-" * 50)
        with open(report_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:20]):  # 显示前20行
                print(f"{i+1:2d}: {line.rstrip()}")
            
            if len(lines) > 20:
                print(f"... (还有 {len(lines) - 20} 行)")
        
        return True
        
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_report_generation()
    if success:
        print("\n🎉 测试成功！新的流程工作正常。")
    else:
        print("\n💥 测试失败，需要进一步调试。")
