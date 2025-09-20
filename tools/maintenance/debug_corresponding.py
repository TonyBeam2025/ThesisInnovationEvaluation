#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# 读取中文文献数据
chinese_path = r"f:\MyProjects\thesis_Inno_Eval\data\output\15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究_relevant_papers_dedup_Chinese.json"

with open(chinese_path, 'r', encoding='utf-8') as f:
    chinese_papers = json.load(f)

print("检查 corresponding 字段值:")
for i, paper in enumerate(chinese_papers[:5]):
    authors = paper.get('Authors', [])
    print(f"\n论文{i+1}: {paper.get('Title', '')[:30]}...")
    for j, author_info in enumerate(authors):
        if isinstance(author_info, dict):
            author_name = author_info.get('name', '')
            corresponding = author_info.get('corresponding', None)
            print(f"  作者{j+1}: {author_name}")
            print(f"    corresponding: {corresponding} (类型: {type(corresponding)})")
            print(f"    bool(corresponding): {bool(corresponding)}")
            print(f"    corresponding == True: {corresponding == True}")
            print(f"    corresponding is True: {corresponding is True}")

print("\n=== 统计 corresponding 字段的所有可能值 ===")
corresponding_values = set()
for paper in chinese_papers:
    authors = paper.get('Authors', [])
    for author_info in authors:
        if isinstance(author_info, dict):
            corresponding = author_info.get('corresponding', None)
            corresponding_values.add((str(corresponding), type(corresponding).__name__))

for value, type_name in sorted(corresponding_values):
    print(f"值: {value} (类型: {type_name})")
