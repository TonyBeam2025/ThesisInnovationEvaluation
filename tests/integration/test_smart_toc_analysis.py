#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试使用智能目录提取类的章节分析功能
"""

import sys
import os
sys.path.append('src')

from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro

def test_smart_toc_extraction():
    """测试智能目录提取和章节分析"""
    print("🚀 测试智能目录提取的章节分析功能")
    print("=" * 80)
    
    # 测试计算机应用技术论文
    extractor = ThesisExtractorPro()
    doc_path = "data/input/1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    
    print(f"📁 测试文件: {os.path.basename(doc_path)}")
    
    try:
        # 先读取文档文本
        print(f"\n📖 读取文档内容...")
        if doc_path.endswith('.docx'):
            from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word
            text = extract_text_from_word(doc_path)
        else:
            print("⚠️ 当前仅支持Word文档格式")
            return None
        
        print(f"   文档长度: {len(text)} 字符")
        
        # 提取内容
        print(f"\n🔄 开始智能提取...")
        result = extractor.extract_with_integrated_strategy(text, doc_path)
        
        print(f"\n📊 提取统计:")
        print(f"  - 总字段数: {extractor.extraction_stats['total_fields']}")
        print(f"  - 已提取字段: {extractor.extraction_stats['extracted_fields']}")
        print(f"  - 提取率: {extractor.extraction_stats['extracted_fields']/extractor.extraction_stats['total_fields']*100:.1f}%")
        print(f"  - 整体置信度: {extractor.extraction_stats['confidence']:.2f}")
        print(f"  - 处理时间: {extractor.extraction_stats['processing_time']:.2f}s")
        
        # 检查目录分析结果
        if 'toc_analysis' in result:
            toc_info = result['toc_analysis']
            print(f"\n📋 目录提取结果:")
            print(f"  - 提取方法: {toc_info.get('extraction_method', 'unknown')}")
            print(f"  - 置信度: {toc_info.get('confidence_score', 0):.2f}")
            print(f"  - 总条目数: {toc_info.get('total_entries', 0)}")
            print(f"  - 最大层级: {toc_info.get('max_level', 0)}")
            
            # 显示目录结构
            chapters = toc_info.get('table_of_contents', [])
            if chapters:
                print(f"\n📚 章节结构 ({len(chapters)} 个):")
                print("-" * 60)
                for i, chapter in enumerate(chapters[:15], 1):  # 显示前15个
                    level_indent = "  " * (chapter.get('level', 1) - 1)
                    title = chapter.get('title', 'Unknown')
                    number = chapter.get('number', '')
                    confidence = chapter.get('confidence', 0)
                    print(f"{i:2d}. {level_indent}[L{chapter.get('level', 1)}] {number} {title} (置信度: {confidence:.2f})")
                
                if len(chapters) > 15:
                    print(f"    ... 还有 {len(chapters) - 15} 个章节")
            
            # 显示章节分析结果
            chapter_summaries = toc_info.get('chapter_summaries', {})
            if chapter_summaries:
                print(f"\n🧠 章节AI分析结果 ({len(chapter_summaries)} 个):")
                print("-" * 60)
                for chapter_title, summary in list(chapter_summaries.items())[:5]:
                    print(f"📖 {chapter_title[:40]}...")
                    if isinstance(summary, dict):
                        print(f"   摘要: {summary.get('summary', 'N/A')[:100]}...")
                        print(f"   关键点: {summary.get('key_points', [])[:3]}")
                    else:
                        print(f"   内容: {str(summary)[:100]}...")
                    print()
            
            # 显示文献综述分析
            lit_analysis = toc_info.get('literature_analysis', {})
            if lit_analysis:
                print(f"📚 文献综述分析:")
                print(f"   研究主题: {lit_analysis.get('research_themes', [])[:3]}")
                print(f"   方法论: {lit_analysis.get('methodologies', [])[:3]}")
                print(f"   研究差距: {lit_analysis.get('research_gaps', [])[:2]}")
        
        # 保存详细结果
        output_file = "smart_toc_analysis_result.json"
        try:
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                # 简化结果以便JSON序列化
                simplified_result = {}
                for key, value in result.items():
                    if isinstance(value, (str, int, float, bool, list, dict)):
                        simplified_result[key] = value
                    else:
                        simplified_result[key] = str(value)
                
                json.dump(simplified_result, f, ensure_ascii=False, indent=2)
            
            print(f"\n 详细结果已保存到 {output_file}")
            
        except Exception as e:
            print(f"⚠️ 保存结果文件失败: {e}")
        
        return result
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_smart_toc_extraction()
