#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试完整的结构化JSON输出，验证参考文献后章节的分类
"""

import sys
import os
from pathlib import Path
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.ai_toc_extractor import AITocExtractor, ThesisToc, TocEntry
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_json_structure():
    """测试完整的JSON结构输出"""
    
    print("🔍 测试完整的结构化JSON输出")
    print("=" * 60)
    
    # 创建模拟的完整目录结构
    entries = [
        TocEntry(level=1, number="第一章", title="绪论", page=1, line_number=1, confidence=0.90, section_type="chapter"),
        TocEntry(level=2, number="1.1", title="研究背景", page=2, line_number=2, confidence=0.85, section_type="level2_section"),
        TocEntry(level=3, number="1.1.1", title="基本概念", page=3, line_number=3, confidence=0.85, section_type="level3_section"),
        TocEntry(level=2, number="1.2", title="研究意义", page=5, line_number=4, confidence=0.85, section_type="level2_section"),
        TocEntry(level=1, number="第二章", title="相关理论", page=10, line_number=5, confidence=0.90, section_type="chapter"),
        TocEntry(level=2, number="2.1", title="基础理论", page=11, line_number=6, confidence=0.85, section_type="level2_section"),
        TocEntry(level=1, number="", title="结论", page=40, line_number=7, confidence=0.90, section_type="conclusion"),
        TocEntry(level=1, number="", title="参考文献", page=45, line_number=8, confidence=0.95, section_type="references"),
        TocEntry(level=1, number="", title="攻读博士学位期间取得的研究成果", page=48, line_number=9, confidence=0.95, section_type="achievements"),
        TocEntry(level=1, number="", title="致谢", page=50, line_number=10, confidence=0.95, section_type="acknowledgment"),
        TocEntry(level=1, number="", title="作者简介", page=52, line_number=11, confidence=0.95, section_type="author_profile"),
    ]
    
    # 创建模拟的ThesisToc对象
    toc = ThesisToc(
        title="测试论文标题",
        author="测试作者",
        entries=entries,
        total_entries=len(entries),
        max_level=3,
        extraction_method="Test_Method",
        confidence_score=0.90,
        toc_content="模拟目录内容"
    )
    
    # 创建抽取器并保存JSON
    extractor = AITocExtractor()
    output_file = "test_complete_structure.json"
    toc_json = extractor.save_toc_json(toc, output_file)
    
    print(f"📊 基本信息:")
    print(f"   总条目数: {toc.total_entries}")
    print(f"   最大层级: {toc.max_level}")
    print(f"   整体置信度: {toc.confidence_score:.2f}")
    
    # 分析JSON结构
    print(f"\n📋 JSON结构分析:")
    print(f"   正文章节数: {len(toc_json['toc_structure']['chapters'])}")
    print(f"   特殊章节数: {len(toc_json['toc_structure']['special_sections'])}")
    print(f"   参考文献后章节数: {len(toc_json['toc_structure']['post_references'])}")
    
    # 显示参考文献后的章节
    print(f"\n✨ 参考文献后章节:")
    for i, section in enumerate(toc_json['toc_structure']['post_references']):
        print(f"   {i+1}. {section['type']}: {section['title']} (第{section['page']}页)")
    
    # 验证所有条目都被正确分类
    print(f"\n🔍 条目分类验证:")
    total_in_structure = (len(toc_json['toc_structure']['chapters']) + 
                         len(toc_json['toc_structure']['special_sections']) + 
                         len(toc_json['toc_structure']['post_references']))
    
    # 计算章节中的所有子条目
    subsection_count = 0
    for chapter in toc_json['toc_structure']['chapters']:
        subsection_count += len(chapter['sections'])
    
    # 正文章节数量（主章节 + 子章节）
    chapter_entries = len([e for e in entries if e.section_type in ['chapter', 'level2_section', 'level3_section']])
    special_entries = len([e for e in entries if e.section_type in ['conclusion', 'references']])
    post_ref_entries = len([e for e in entries if e.section_type in ['achievements', 'acknowledgment', 'author_profile']])
    
    print(f"   正文条目: {chapter_entries} (主章节 + 子章节)")
    print(f"   特殊章节: {special_entries}")
    print(f"   参考文献后: {post_ref_entries}")
    print(f"   总计: {chapter_entries + special_entries + post_ref_entries}")
    
    # 保存和显示完整JSON
    print(f"\n💾 完整JSON已保存到: {output_file}")
    
    # 显示JSON的关键部分
    print(f"\n📄 JSON结构预览:")
    print(f"```json")
    print(f"{{")
    print(f'  "metadata": {{')
    print(f'    "total_entries": {toc_json["metadata"]["total_entries"]},')
    print(f'    "confidence_score": {toc_json["metadata"]["confidence_score"]}')
    print(f'  }},')
    print(f'  "toc_structure": {{')
    print(f'    "chapters": {len(toc_json["toc_structure"]["chapters"])} 个正文章节,')
    print(f'    "special_sections": {len(toc_json["toc_structure"]["special_sections"])} 个特殊章节,')
    print(f'    "post_references": [')
    for section in toc_json['toc_structure']['post_references']:
        print(f'      {{ "type": "{section["type"]}", "title": "{section["title"]}", "page": {section["page"]} }},')
    print(f'    ]')
    print(f'  }}')
    print(f'}}')
    print(f"```")
    
    return toc_json

if __name__ == "__main__":
    test_complete_json_structure()
