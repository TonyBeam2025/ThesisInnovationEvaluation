#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(r'f:\MyProjects\thesis_Inno_Eval\src')

from thesis_inno_eval.literature_review_analyzer import LiteratureReviewAnalyzer

# 创建分析器实例
analyzer = LiteratureReviewAnalyzer()

input_file = r"f:\MyProjects\thesis_Inno_Eval\data\input\15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究.docx"

print("正在生成新的文献分析报告...")

try:
    # 生成报告
    report_path = analyzer.analyze_literature_review(input_file)
    print(f" 报告生成成功: {report_path}")
    
    # 读取报告中的元数据部分
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找元数据驱动分析部分
        metadata_start = content.find("## 📊 元数据驱动分析")
        if metadata_start != -1:
            ai_insights_start = content.find("## 🤖 AI驱动文献洞察", metadata_start)
            if ai_insights_start != -1:
                metadata_section = content[metadata_start:ai_insights_start]
            else:
                metadata_section = content[metadata_start:]
            
            print("\n=== 新生成报告中的元数据驱动分析部分 ===")
            print(metadata_section[:2000])  # 显示前2000字符
        else:
            print("\n❌ 未找到元数据驱动分析部分")
            
except Exception as e:
    print(f"❌ 生成报告时出错: {e}")
    import traceback
    traceback.print_exc()
