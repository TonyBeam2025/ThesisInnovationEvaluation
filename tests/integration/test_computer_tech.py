#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试计算机应用技术论文的目录提取
"""

import sys
import os
sys.path.append(str(PROJECT_ROOT))

from src.thesis_inno_eval.ai_toc_extractor import AITocExtractor

def test_computer_tech_thesis():
    """测试计算机应用技术论文目录提取"""
    print("🖥️ 测试计算机应用技术论文目录提取")
    print("=" * 80)
    
    doc_path = r"c:\MyProjects\thesis_Inno_Eval\data\input\1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    print(f"📁 文件: {os.path.basename(doc_path)}")
    
    try:
        print("🔄 开始提取目录...")
        extractor = AITocExtractor()
        result = extractor.extract_toc(doc_path)
        
        if result and result.entries:
            print(f"\n📊 提取结果:")
            print(f"  总条目数: {len(result.entries)}")
            print(f"  置信度: {result.confidence_score:.2f}")
            print(f"  提取方法: {result.extraction_method}")
            
            print(f"\n📋 完整目录条目列表:")
            print("-" * 80)
            
            for i, entry in enumerate(result.entries, 1):
                type_label = f"【{entry.section_type}】" if entry.section_type else "【unknown】"
                page_info = f"页码: {entry.page}" if entry.page else "页码: None"
                
                print(f"{i:2d}. {type_label} {entry.title}")
                print(f"     {page_info} | 级别: {entry.level}")
            
            # 检查预期的章节是否都存在
            expected_chapters = [
                "第一章 绪论",
                "第二章 相关理论及技术", 
                "第三章 基于MLP模型的藏文文本分类方法研究",
                "第四章 基于SepCNN模型的藏文文本分类方法研究",
                "第五章 藏文文本分类探究与对比实验",
                "第六章 藏文文本分类系统的设计与实现",
                "第七章 总结与展望"
            ]
            
            print(f"\n🎯 预期章节检查:")
            print("-" * 50)
            
            found_chapters = []
            for expected in expected_chapters:
                found = False
                for entry in result.entries:
                    if expected.replace(" ", "") in entry.title.replace(" ", "") or \
                       any(word in entry.title for word in expected.split() if len(word) > 2):
                        found_chapters.append(entry.title)
                        print(f" 找到: {entry.title}")
                        found = True
                        break
                if not found:
                    print(f"❌ 缺失: {expected}")
            
            # 检查学术后章节
            academic_sections = ["参考文献", "攻读硕士学位期间获得的成果", "致谢"]
            print(f"\n📖 学术后章节检查:")
            print("-" * 50)
            
            for academic in academic_sections:
                found = False
                for entry in result.entries:
                    if academic in entry.title:
                        print(f" 找到: {entry.title}")
                        found = True
                        break
                if not found:
                    print(f"❌ 缺失: {academic}")
                    
            print(f"\n🔍 原始目录内容预览（前500字符）:")
            print("-" * 50)
            print(result.toc_content[:500] + "..." if len(result.toc_content) > 500 else result.toc_content)
                    
        else:
            print("❌ 提取失败或结果为空")
            
    except Exception as e:
        print(f"❌ 提取过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_computer_tech_thesis()
