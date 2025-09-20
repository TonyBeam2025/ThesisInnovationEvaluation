#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-

"""
测试章节边界确定逻辑修复
"""

import sys
import os
sys.path.insert(0, 'src')

def test_boundary_detection():
    print("============================================================")
    print("测试章节边界确定逻辑修复")
    print("============================================================")
    
    # 模拟文档结构
    sample_text = """绪论
这是绪论内容
这是绪论的第二行

第一章 曲牌体道情戏的历史与现状
这是第一章内容
这是第一章的更多内容

第二章 曲牌体道情戏的音乐结构
这是第二章内容
这是第二章的更多内容

第三章 "非遗"政策保护下的曲牌体道情戏
这是第三章内容
这是第三章的更多内容

结语
这是结语内容

参考文献
[1] 参考文献1
[2] 参考文献2

致谢与声明
感谢内容

致谢
详细致谢

个人简历
个人简历内容"""

    # 模拟章节结构
    chapters = [
        {'title': '第一章 曲牌体道情戏的历史与现状', 'number': '第一章'},
        {'title': '第二章 曲牌体道情戏的音乐结构', 'number': '第二章'}, 
        {'title': '第三章 "非遗"政策保护下的曲牌体道情戏', 'number': '第三章'},
        {'title': '参考文献', 'number': ''},
        {'title': '致谢', 'number': ''},
        {'title': '个人简历', 'number': ''}
    ]
    
    print("📝 测试文档结构:")
    lines = sample_text.split('\n')
    for i, line in enumerate(lines):
        if line.strip():
            print(f"  [{i:2d}] {line}")
    
    print(f"\n📊 文档统计: {len(lines)} 行")
    
    # 导入并测试边界检测逻辑
    try:
        from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
        extractor = ThesisExtractorPro()
        
        print("\n🔍 测试边界检测:")
        boundaries = extractor._determine_chapter_content_boundaries(sample_text, chapters)
        
        print("\n📋 边界检测结果:")
        for title, boundary in boundaries.items():
            start = boundary['start_line']
            end = boundary['end_line']
            count = boundary['total_lines']
            print(f"  📖 {title}")
            print(f"     边界: 行 {start}-{end} ({count} 行)")
            if count > 0:
                content_lines = lines[start:end+1]
                content_preview = ' '.join(content_lines)[:60]
                print(f"     内容: {content_preview}...")
            print()
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_boundary_detection()
