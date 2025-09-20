#!/usr/bin/env python3
"""
测试新的文献综述分析器
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
import json
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.literature_review_analyzer import LiteratureReviewAnalyzer

def test_literature_analyzer():
    """测试文献综述分析器"""
    
    print("🚀 开始测试文献综述分析器")
    
    # 创建测试分析器
    try:
        analyzer = LiteratureReviewAnalyzer()
        print(" 文献综述分析器初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 检查测试数据
    output_dir = Path("data/output")
    test_files = list(output_dir.glob("*_relevant_papers_Chinese.json"))
    
    if not test_files:
        print("❌ 未找到测试数据文件")
        return
    
    test_file = test_files[0]
    print(f"📁 使用测试文件: {test_file.name}")
    
    # 加载测试数据
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            chinese_papers = json.load(f)
        
        english_file = test_file.parent / test_file.name.replace('_Chinese.json', '_English.json')
        english_papers = []
        if english_file.exists():
            with open(english_file, 'r', encoding='utf-8') as f:
                english_papers = json.load(f)
        
        papers_by_lang = {
            'Chinese': chinese_papers[:10],  # 只取前10篇测试
            'English': english_papers[:10]
        }
        
        print(f"📊 加载文献数据: 中文{len(papers_by_lang['Chinese'])}篇, 英文{len(papers_by_lang['English'])}篇")
        
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return
    
    # 测试元数据分析
    try:
        print("\n🔍 测试元数据驱动分析...")
        metadata_analysis = analyzer._generate_metadata_driven_analysis(papers_by_lang)
        print(" 元数据分析生成成功")
        print("前300字符预览:")
        print("-" * 50)
        print(metadata_analysis[:300] + "...")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ 元数据分析失败: {e}")
    
    # 测试作者分析
    try:
        print("\n👥 测试作者分析...")
        all_papers = chinese_papers[:5] + english_papers[:5]  # 混合测试
        authors_analysis = analyzer._analyze_authors_metadata(all_papers)
        print(" 作者分析成功")
        print("作者分析结果:")
        print(authors_analysis)
        
    except Exception as e:
        print(f"❌ 作者分析失败: {e}")
    
    # 测试机构分析
    try:
        print("\n🏛️ 测试机构分析...")
        institutions_analysis = analyzer._analyze_institutions_metadata(all_papers)
        print(" 机构分析成功")
        print("机构分析结果:")
        print(institutions_analysis)
        
    except Exception as e:
        print(f"❌ 机构分析失败: {e}")
    
    # 测试基本功能
    try:
        print("\n📋 测试基本分析功能...")
        basic_analysis = analyzer._generate_basic_analysis_sections("这是一个测试文献综述内容" * 100, 50, 25)
        print(" 基本分析功能正常")
        print("基本分析预览:")
        print(basic_analysis[:200] + "...")
        
    except Exception as e:
        print(f"❌ 基本分析失败: {e}")
    
    print("\n🎉 测试完成!")

if __name__ == "__main__":
    test_literature_analyzer()
