#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试修改后的AI TOC提取器对目录域的处理
"""

import sys
import os
sys.path.append(str(PROJECT_ROOT))

from src.thesis_inno_eval.ai_toc_extractor import AITocExtractor

def test_toc_field_extraction():
    """测试目录域处理功能"""
    print("🧠 测试AI TOC提取器对目录域的处理")
    print("=" * 80)
    
    # 测试计算机应用技术论文
    doc_path = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    
    print(f"📄 测试文档: {os.path.basename(doc_path)}")
    print("-" * 60)
    
    try:
        extractor = AITocExtractor()
        result = extractor.extract_toc(doc_path)
        
        if result and result.entries:
            print(f" 成功提取目录")
            print(f"📊 提取条目数: {len(result.entries)}")
            print(f"🎯 置信度: {result.confidence_score:.2f}")
            print(f"🔧 提取方法: {result.extraction_method}")
            
            # 显示所有条目
            print(f"\n📋 完整目录条目列表:")
            print("-" * 80)
            
            for i, entry in enumerate(result.entries, 1):
                type_label = f"【{entry.section_type}】" if entry.section_type else "【unknown】"
                page_info = f"页码: {entry.page}" if entry.page else "页码: None"
                
                print(f"{i:2d}. {type_label} {entry.title}")
                print(f"     {page_info} | 级别: {entry.level}")
            
            # 检查是否包含典型的学术章节
            academic_sections = ["绪论", "总结", "参考文献", "致谢", "攻读", "学术成果"]
            
            print(f"\n🎯 学术章节检查:")
            print("-" * 50)
            
            found_academic = []
            for entry in result.entries:
                for academic in academic_sections:
                    if academic in entry.title:
                        found_academic.append(entry)
                        print(f" 找到: {entry.title} (页码: {entry.page}, 类型: {entry.section_type})")
                        break
            
            if not found_academic:
                print("❌ 没有找到典型的学术章节")
            else:
                print(f" 找到 {len(found_academic)} 个学术章节")
                
        else:
            print("❌ 提取失败或结果为空")
            
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_toc_field_extraction()
