#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试更新后的AI TOC提取器
"""

import sys
import os
sys.path.append('src')

from thesis_inno_eval.ai_toc_extractor import AITocExtractor

def test_updated_extractor():
    """测试更新后的提取器"""
    print("🚀 测试更新后的AI TOC提取器")
    print("=" * 80)
    
    # 测试计算机应用技术论文
    extractor = AITocExtractor()
    doc_path = "data/input/1_计算机应用技术_17211204005-苏慧婧-基于MLP和SepCNN模型的藏文文本分类研究与实现-计算机应用技术-群诺.docx"
    
    print(f"📁 测试文件: {os.path.basename(doc_path)}")
    
    try:
        # 提取TOC
        result = extractor.extract_toc(doc_path)
        
        print(f"\n📊 提取结果:")
        print(f"  - 论文标题: {result.title}")
        print(f"  - 作者: {result.author}")
        print(f"  - 总条目数: {result.total_entries}")
        print(f"  - 最大层级: {result.max_level}")
        print(f"  - 提取方法: {result.extraction_method}")
        print(f"  - 置信度: {result.confidence_score:.2f}")
        
        print(f"\n📋 目录条目 ({len(result.entries)} 个):")
        print("-" * 60)
        
        for i, entry in enumerate(result.entries[:20], 1):  # 显示前20个
            level_indent = "  " * (entry.level - 1)
            print(f"{i:2d}. {level_indent}[L{entry.level}] {entry.number} {entry.title}")
            if entry.page:
                print(f"    {level_indent}    页码: {entry.page}")
        
        if len(result.entries) > 20:
            print(f"    ... 还有 {len(result.entries) - 20} 个条目")
        
        print(f"\n📄 原始目录内容预览:")
        print("-" * 60)
        preview_lines = result.toc_content.split('\n')[:15]
        for line in preview_lines:
            if line.strip():
                print(f"  {line}")
        if len(result.toc_content.split('\n')) > 15:
            print("  ...")
        
        # 检查语言检测
        print(f"\n🌍 语言检测结果:")
        print("-" * 60)
        try:
            with open(doc_path.replace('.docx', '_analysis.txt'), 'w', encoding='utf-8') as f:
                f.write("AI TOC提取结果\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"论文标题: {result.title}\n")
                f.write(f"作者: {result.author}\n")
                f.write(f"总条目数: {result.total_entries}\n")
                f.write(f"提取方法: {result.extraction_method}\n")
                f.write(f"置信度: {result.confidence_score:.2f}\n\n")
                f.write("目录结构:\n")
                f.write("-" * 30 + "\n")
                for entry in result.entries:
                    level_indent = "  " * (entry.level - 1)
                    f.write(f"{level_indent}[L{entry.level}] {entry.number} {entry.title}\n")
                f.write("\n原始内容:\n")
                f.write("-" * 30 + "\n")
                f.write(result.toc_content)
            
            print(f" 结果已保存到分析文件")
            
        except Exception as e:
            print(f"⚠️ 保存分析文件失败: {e}")
        
        return result
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_updated_extractor()
