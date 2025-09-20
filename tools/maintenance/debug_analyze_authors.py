#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def is_valid_author_name(name: str) -> bool:
    """判断是否为有效的作者姓名（过滤掉机构名称）"""
    if not name or len(name) > 50:  # 过滤掉过长的名称
        return False
    # 过滤掉明显的机构关键词
    institution_keywords = ['University', 'Department', 'College', 'Institute', 'Hospital', 
                          'Center', 'School', 'Laboratory', 'Research', 'Medical', 
                          'Electronic address', 'USA', 'China', 'Dept.']
    name_lower = name.lower()
    if any(keyword.lower() in name_lower for keyword in institution_keywords):
        return False
    return True

# 读取中文文献数据
chinese_path = r"f:\MyProjects\thesis_Inno_Eval\data\output\15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究_relevant_papers_dedup_Chinese.json"

with open(chinese_path, 'r', encoding='utf-8') as f:
    papers = json.load(f)

author_counts = {}
corresponding_authors = {}
first_authors = {}
total_papers_with_authors = 0
total_corresponding_authors = 0

print("=== 模拟 _analyze_authors_metadata 方法 ===")

for i, paper in enumerate(papers):
    authors = paper.get('Authors', [])
    first_author = paper.get('FirstAuthor', '')
    
    print(f"\n论文 {i+1}: {paper.get('Title', '')[:50]}...")
    print(f"Authors 字段: {authors}")
    print(f"FirstAuthor 字段: {first_author}")
    
    if authors and isinstance(authors, list):
        valid_authors_found = False
        
        # 统计所有作者
        for author_info in authors:
            if isinstance(author_info, dict):
                author_name = author_info.get('name', '')
                is_corresponding = author_info.get('corresponding', False)
                
                print(f"  处理作者: {author_name}")
                print(f"    corresponding 原值: {is_corresponding}")
                print(f"    is_valid_author_name: {is_valid_author_name(author_name)}")
                
                if author_name and is_valid_author_name(author_name):
                    valid_authors_found = True
                    author_counts[author_name] = author_counts.get(author_name, 0) + 1
                    print(f"    ✓ 添加到作者统计: {author_name}")
                    
                    if is_corresponding:
                        corresponding_authors[author_name] = corresponding_authors.get(author_name, 0) + 1
                        total_corresponding_authors += 1
                        print(f"    ✓ 添加到通讯作者统计: {author_name}")
                else:
                    print(f"    ✗ 无效作者名称，跳过")
        
        if valid_authors_found:
            total_papers_with_authors += 1
            print(f"  ✓ 论文有有效作者")
        else:
            print(f"  ✗ 论文无有效作者")
        
        # 统计第一作者
        if first_author and is_valid_author_name(first_author):
            first_authors[first_author] = first_authors.get(first_author, 0) + 1
            print(f"  ✓ 第一作者: {first_author}")
    
    # 只处理前5篇进行调试
    if i >= 4:
        break

print(f"\n=== 最终统计结果 ===")
print(f"author_counts: {dict(list(author_counts.items())[:5])}")
print(f"corresponding_authors: {corresponding_authors}")
print(f"first_authors: {dict(list(first_authors.items())[:5])}")
print(f"total_papers_with_authors: {total_papers_with_authors}")
print(f"total_corresponding_authors: {total_corresponding_authors}")

print(f"\n判断条件:")
print(f"not author_counts: {not author_counts}")
print(f"len(author_counts): {len(author_counts)}")
