#!/usr/bin/env python3
"""测试SmartReferenceExtractor边界检测集成"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
sys.path.append('src')

from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro, extract_text_from_word

def test_boundary_integration():
    print("============================================================")
    print("测试SmartReferenceExtractor边界检测集成")
    print("============================================================")
    
    # 读取文档
    print("📄 读取音乐论文文档...")
    text = extract_text_from_word('data/input/1_音乐_20172001013韩柠灿（硕士毕业论文）.docx')
    print(f"   📏 文档长度: {len(text):,} 字符")
    
    # 初始化提取器
    print("🔧 初始化论文提取器...")
    extractor = ThesisExtractorPro()
    
    # 步骤1：提取章节列表
    print("🔍 步骤1: 识别第一层级章节...")
    # 首先需要获取目录
    toc_analysis = extractor._extract_and_analyze_toc_with_content_boundaries(text)
    sections = extractor._extract_first_level_chapters(toc_analysis.get('toc_entries', []))
    print(f"   ✅ 识别到 {len(sections)} 个章节:")
    for i, section in enumerate(sections):
        print(f"     {i+1}. {section['title']}")
    
    # 步骤2：检测章节边界
    print("\n📏 步骤2: 确定章节边界...")
    boundaries = extractor._determine_chapter_content_boundaries(text, sections)
    
    # 步骤3：显示结果
    print("\n📊 边界检测结果:")
    print("="*60)
    for title, boundary in boundaries.items():
        start = boundary['start_line']
        end = boundary['end_line']
        lines = boundary['total_lines']
        chars = boundary['estimated_chars']
        
        print(f"📖 {title}")
        print(f"   边界: 行 {start}-{end} ({lines} 行)")
        print(f"   字符: {chars:,} 字符")
        
        # 显示章节开头内容
        text_lines = text.split('\n')
        if start < len(text_lines) and lines > 0:
            content_preview = ' '.join(text_lines[start:min(start+2, end+1)]).strip()[:100]
            print(f"   内容: {content_preview}...")
        print()

if __name__ == "__main__":
    test_boundary_integration()
