#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试改进后的章节分析功能
"""

import sys
import os
sys.path.append('src')

from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro

def test_improved_chapter_analysis():
    """测试改进后的章节分析功能"""
    print("🔧 测试改进后的章节分析功能")
    print("=" * 80)
    
    # 测试计算机应用技术论文
    extractor = ThesisExtractorPro()
    doc_path = "data/input/1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    
    print(f"📁 测试文件: {os.path.basename(doc_path)}")
    
    try:
        # 先读取文档文本
        print(f"\n📖 读取文档内容...")
        from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word
        text = extract_text_from_word(doc_path)
        print(f"   文档长度: {len(text)} 字符")
        
        # 单独测试目录提取和章节分析
        print(f"\n🔍 测试目录提取和章节分析...")
        toc_analysis = extractor._extract_and_analyze_toc(text, doc_path)
        
        print(f"\n📊 目录分析结果:")
        print(f"  - 提取方法: {toc_analysis.get('extraction_method', 'unknown')}")
        print(f"  - 置信度: {toc_analysis.get('confidence_score', 0):.3f}")
        print(f"  - 总条目数: {toc_analysis.get('total_entries', 0)}")
        print(f"  - 最大层级: {toc_analysis.get('max_level', 0)}")
        
        # 显示目录结构
        chapters = toc_analysis.get('table_of_contents', [])
        if chapters:
            print(f"\n📚 提取的章节结构 ({len(chapters)} 个):")
            print("-" * 70)
            for i, chapter in enumerate(chapters, 1):
                level_indent = "  " * (chapter.get('level', 1) - 1)
                title = chapter.get('title', 'Unknown')
                number = chapter.get('number', '')
                section_type = chapter.get('section_type', '')
                confidence = chapter.get('confidence', 0)
                
                print(f"{i:2d}. {level_indent}[L{chapter.get('level', 1)}] {number} {title}")
                print(f"    {level_indent}    类型: {section_type}, 置信度: {confidence:.2f}")
                
                # 测试章节类型分类
                classified_type = extractor._classify_chapter_type(chapter)
                print(f"    {level_indent}    分类: {classified_type}")
        
        # 显示章节分析结果
        chapter_summaries = toc_analysis.get('chapter_summaries', {})
        if chapter_summaries:
            print(f"\n🧠 章节AI分析结果 ({len(chapter_summaries)} 个):")
            print("-" * 70)
            for i, (chapter_title, summary) in enumerate(chapter_summaries.items(), 1):
                print(f"\n{i}. 📖 {chapter_title}")
                print("-" * 50)
                
                if isinstance(summary, dict):
                    print(f"摘要: {summary.get('summary', 'N/A')[:200]}...")
                    print(f"关键点数: {len(summary.get('key_points', []))}")
                    if summary.get('key_points'):
                        for j, point in enumerate(summary.get('key_points', [])[:3], 1):
                            print(f"  {j}. {point}")
                    
                    # 显示其他分析结果
                    for key in ['methods', 'results', 'parameters', 'research_trends', 'chapter_type']:
                        if key in summary and summary[key]:
                            print(f"{key}: {summary[key]}")
                else:
                    print(f"内容: {str(summary)[:200]}...")
        
        # 显示文献综述分析
        lit_analysis = toc_analysis.get('literature_analysis', {})
        if lit_analysis:
            print(f"\n📚 文献综述分析:")
            print("-" * 50)
            for key, value in lit_analysis.items():
                if value and isinstance(value, list):
                    print(f"{key}: {value[:3]}")  # 只显示前3个
                elif value:
                    print(f"{key}: {str(value)[:100]}...")
        
        # 显示方法论分析
        method_analysis = toc_analysis.get('methodology_analysis', {})
        if method_analysis:
            print(f"\n🔬 方法论分析:")
            print("-" * 50)
            for key, value in method_analysis.items():
                if value and isinstance(value, list):
                    print(f"{key}: {value[:3]}")
                elif value:
                    print(f"{key}: {str(value)[:100]}...")
        
        # 保存详细结果
        output_file = "improved_chapter_analysis.json"
        try:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                # 简化结果以便JSON序列化
                simplified_result = {}
                for key, value in toc_analysis.items():
                    if isinstance(value, (str, int, float, bool, list, dict)):
                        simplified_result[key] = value
                    else:
                        simplified_result[key] = str(value)
                
                json.dump(simplified_result, f, ensure_ascii=False, indent=2)
            
            print(f"\n 详细结果已保存到 {output_file}")
            
        except Exception as e:
            print(f"⚠️ 保存结果文件失败: {e}")
        
        return toc_analysis
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_improved_chapter_analysis()
