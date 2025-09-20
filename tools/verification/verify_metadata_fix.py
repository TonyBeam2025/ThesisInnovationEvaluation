#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append(r'f:\MyProjects\thesis_Inno_Eval\src')

from thesis_inno_eval.literature_review_analyzer import LiteratureReviewAnalyzer
import json

def test_metadata_analysis():
    """测试元数据分析功能"""
    
    # 创建分析器实例
    analyzer = LiteratureReviewAnalyzer()
    
    # 读取数据
    chinese_path = r"f:\MyProjects\thesis_Inno_Eval\data\output\15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究_relevant_papers_dedup_Chinese.json"
    english_path = r"f:\MyProjects\thesis_Inno_Eval\data\output\15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究_relevant_papers_dedup_English.json"
    
    with open(chinese_path, 'r', encoding='utf-8') as f:
        chinese_papers = json.load(f)
    
    with open(english_path, 'r', encoding='utf-8') as f:
        english_papers = json.load(f)
    
    # 构造 papers_by_lang 格式
    papers_by_lang = {
        'Chinese': chinese_papers,
        'English': english_papers
    }
    
    print("📊 测试元数据分析功能")
    print("=" * 50)
    
    # 测试元数据分析
    metadata_result = analyzer._generate_metadata_driven_analysis(papers_by_lang)
    
    # 检查是否包含"暂无有效的作者信息进行分析"
    if "暂无有效的作者信息进行分析" in metadata_result:
        print("❌ 发现问题：返回了'暂无有效的作者信息进行分析'")
        return False
    else:
        print(" 元数据分析正常，包含详细的作者信息分析")
        
        # 显示作者网络分析部分
        lines = metadata_result.split('\n')
        author_section_start = False
        author_lines = []
        
        for line in lines:
            if "### 👥 作者网络分析" in line:
                author_section_start = True
            elif line.startswith("### ") and author_section_start:
                break
            
            if author_section_start:
                author_lines.append(line)
        
        print("\n📋 作者网络分析部分预览：")
        print("-" * 30)
        for line in author_lines[:15]:  # 显示前15行
            print(line)
        
        return True

if __name__ == "__main__":
    success = test_metadata_analysis()
    if success:
        print("\n🎉 元数据分析功能验证通过！")
        print("📝 建议：重新生成报告以获取最新的分析结果")
    else:
        print("\n❌ 元数据分析功能存在问题")

