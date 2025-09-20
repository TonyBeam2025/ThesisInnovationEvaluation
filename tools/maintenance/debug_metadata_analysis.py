#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append(r'f:\MyProjects\thesis_Inno_Eval\src')

from thesis_inno_eval.literature_review_analyzer import LiteratureReviewAnalyzer
import json

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

print(f"papers_by_lang 结构:")
for lang, papers in papers_by_lang.items():
    print(f"  {lang}: {len(papers)} 篇论文")

# 调用 _generate_metadata_driven_analysis 方法
print("\n=== 调用 _generate_metadata_driven_analysis 方法 ===")
result = analyzer._generate_metadata_driven_analysis(papers_by_lang)
print("返回结果:")
print(result[:1000])  # 只打印前1000字符以便查看
print("...")
print(result[-500:])  # 打印最后500字符
