#!/usr/bin/env python3
"""
单独生成文献综述深度分析报告的测试脚本
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import json
import os
from pathlib import Path
from src.thesis_inno_eval.literature_review_analyzer import LiteratureReviewAnalyzer

def main():
    # 数据路径
    base_name = "跨模态图像融合技术在医疗影像分析中的研究"
    data_dir = Path("data/output")
    
    # 加载论文提取信息
    extracted_info_file = data_dir / f"{base_name}_extracted_info.json"
    if extracted_info_file.exists():
        with open(extracted_info_file, 'r', encoding='utf-8') as f:
            extracted_data = json.load(f)
            thesis_extracted_info = extracted_data.get('extracted_info', {})
    else:
        print(f"❌ 找不到提取信息文件: {extracted_info_file}")
        return
    
    # 加载文献数据
    papers_by_lang = {}
    
    # 加载中文文献
    chinese_file = data_dir / f"{base_name}_relevant_papers_Chinese.json"
    if chinese_file.exists():
        with open(chinese_file, 'r', encoding='utf-8') as f:
            chinese_papers = json.load(f)
            papers_by_lang['Chinese'] = chinese_papers
            print(f" 加载中文文献: {len(chinese_papers)} 篇")
    
    # 加载英文文献
    english_file = data_dir / f"{base_name}_relevant_papers_English.json"
    if english_file.exists():
        with open(english_file, 'r', encoding='utf-8') as f:
            english_papers = json.load(f)
            papers_by_lang['English'] = english_papers
            print(f" 加载英文文献: {len(english_papers)} 篇")
    
    if not papers_by_lang:
        print("❌ 没有找到任何文献数据")
        return
    
    # 调试数据结构
    print(f"\n=== 数据结构调试 ===")
    all_papers = []
    for lang, papers in papers_by_lang.items():
        all_papers.extend(papers)
        print(f"{lang} 文献数量: {len(papers)}")
        if papers:
            first_paper = papers[0]
            authors = first_paper.get('Authors', [])
            print(f"  第一篇论文Authors类型: {type(authors)}")
            print(f"  第一篇论文Authors数量: {len(authors) if isinstance(authors, list) else 'N/A'}")
            if isinstance(authors, list) and authors:
                print(f"  第一个作者: {authors[0]}")
    
    print(f"总文献数量: {len(all_papers)}")
    
    # 创建分析器并生成报告
    analyzer = LiteratureReviewAnalyzer()
    
    try:
        print(f"\n=== 开始生成文献综述分析报告 ===")
        report_file = analyzer.analyze_literature_review(
            f"data/input/{base_name}.docx",
            thesis_extracted_info,
            papers_by_lang,
            "data/output"
        )
        print(f" 文献综述分析报告已生成: {report_file}")
        
        # 检查生成的报告内容
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 查找作者分析部分
        if "### 👥 作者网络分析" in content:
            start_idx = content.find("### 👥 作者网络分析")
            end_idx = content.find("### 🏛️ 机构分布分析", start_idx)
            if end_idx == -1:
                end_idx = start_idx + 500
            author_section = content[start_idx:end_idx]
            print(f"\n=== 作者网络分析部分 ===")
            print(author_section)
        
    except Exception as e:
        print(f"❌ 生成报告失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
