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

# 合并数据
all_papers = chinese_papers + english_papers

print(f"总论文数: {len(all_papers)}")
print(f"中文论文数: {len(chinese_papers)}")
print(f"英文论文数: {len(english_papers)}")

# 直接调用作者分析方法
print("\n=== 调用 _analyze_authors_metadata 方法 ===")
result = analyzer._analyze_authors_metadata(all_papers)
print("返回结果:")
print(result)

# 也测试机构分析
print("\n=== 调用 _analyze_institutions_metadata 方法 ===")
inst_result = analyzer._analyze_institutions_metadata(all_papers)
print("机构分析结果:")
print(inst_result)
