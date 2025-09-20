#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试包含参考文献后章节的目录抽取功能
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.ai_toc_extractor import AITocExtractor
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_extended_toc():
    """测试包含参考文献后章节的目录内容"""
    
    # 模拟包含完整目录的内容
    mock_toc_content = """
第一章 绪论.....................................1
1.1 研究背景....................................2
1.1.1 基本概念..................................3
1.1.2 研究现状..................................5
1.2 研究意义....................................8
第二章 相关理论................................10
2.1 基础理论...................................11
2.2 关键技术...................................15
第三章 系统设计................................20
3.1 总体设计...................................21
3.2 详细设计...................................25
第四章 实验与分析..............................30
4.1 实验设置...................................31
4.2 结果分析...................................35
第五章 结论....................................40
5.1 研究总结...................................41
5.2 展望.......................................43
参考文献.......................................45
攻读博士学位期间取得的研究成果..................48
致  谢.........................................50
作者简介.......................................52
"""
    
    print("🔍 测试包含参考文献后章节的目录抽取")
    print("=" * 60)
    
    # 创建抽取器
    extractor = AITocExtractor()
    
    # 初始化AI客户端
    extractor.init_ai_client()
    
    # 直接调用AI分析方法
    entries = extractor._ai_extract_entries_with_llm(mock_toc_content)
    
    print(f"📊 抽取结果: {len(entries)} 个条目")
    print("\n📖 详细目录结构:")
    print("-" * 60)
    
    references_found = False
    post_ref_count = 0
    
    for i, entry in enumerate(entries):
        indent = "  " * (entry.level - 1) if entry.level > 0 else ""
        page_info = f" (第{entry.page}页)" if entry.page else ""
        conf_info = f" [{entry.confidence:.2f}]"
        number_part = f"{entry.number} " if entry.number else ""
        
        # 检查是否到了参考文献
        if entry.section_type == 'references':
            references_found = True
            print(f"{i+1:3d}. 🔖 {indent}{number_part}{entry.title}{page_info}{conf_info}")
        elif references_found:
            post_ref_count += 1
            print(f"{i+1:3d}. ✨ {indent}{number_part}{entry.title}{page_info}{conf_info} (参考文献后)")
        else:
            print(f"{i+1:3d}. 📄 {indent}{number_part}{entry.title}{page_info}{conf_info}")
    
    print(f"\n📈 统计信息:")
    print(f"   总条目数: {len(entries)}")
    print(f"   参考文献后条目数: {post_ref_count}")
    
    # 分析章节类型
    type_stats = {}
    for entry in entries:
        section_type = entry.section_type
        if section_type not in type_stats:
            type_stats[section_type] = 0
        type_stats[section_type] += 1
    
    print(f"\n📋 章节类型统计:")
    for section_type, count in type_stats.items():
        print(f"   {section_type}: {count} 个")
    
    # 验证是否包含目标章节
    target_sections = ['achievements', 'acknowledgment', 'author_profile']
    found_sections = [entry.section_type for entry in entries]
    
    print(f"\n 目标章节检查:")
    for target in target_sections:
        if target in found_sections:
            print(f"   ✓ {target}: 已识别")
        else:
            print(f"   ✗ {target}: 未识别")
    
    return entries

if __name__ == "__main__":
    test_extended_toc()
