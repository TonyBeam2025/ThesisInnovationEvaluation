#!/usr/bin/env python3
"""调试元数据分析问题"""

import json
import sys
import os

def debug_metadata():
    try:
        # 读取中文文献数据
        chinese_file = "data/output/15-基于风险管理视角的互联网医院政策文本量化分析与优化路径研究_relevant_papers_dedup_Chinese.json"
        with open(chinese_file, 'r', encoding='utf-8') as f:
            chinese_papers = json.load(f)
        
        print(f"中文文献数量: {len(chinese_papers)}")
        
        # 检查第一篇论文的结构
        if chinese_papers:
            paper = chinese_papers[0]
            print(f"\n第一篇论文字段: {list(paper.keys())}")
            print(f"Authors字段: {paper.get('Authors', 'Not found')}")
            print(f"Authors类型: {type(paper.get('Authors'))}")
            print(f"Affiliations字段: {paper.get('Affiliations', 'Not found')}")
            print(f"Metrics字段: {paper.get('Metrics', 'Not found')}")
        
        # 统计有作者信息的论文数量
        papers_with_authors = 0
        papers_with_affiliations = 0
        papers_with_metrics = 0
        
        for paper in chinese_papers:
            authors = paper.get('Authors', [])
            if authors and isinstance(authors, list) and len(authors) > 0:
                papers_with_authors += 1
                
            affiliations = paper.get('Affiliations', [])
            if affiliations and isinstance(affiliations, list) and len(affiliations) > 0:
                papers_with_affiliations += 1
                
            metrics = paper.get('Metrics', {})
            if metrics and isinstance(metrics, dict) and any(metrics.values()):
                papers_with_metrics += 1
        
        print(f"\n统计结果:")
        print(f"有作者信息的论文: {papers_with_authors}")
        print(f"有机构信息的论文: {papers_with_affiliations}")
        print(f"有指标信息的论文: {papers_with_metrics}")
        
        # 检查具体的作者数据
        print(f"\n前3篇论文的作者信息:")
        for i, paper in enumerate(chinese_papers[:3]):
            authors = paper.get('Authors', [])
            print(f"论文{i+1}: {authors}")
            if authors and isinstance(authors, list):
                for j, author in enumerate(authors):
                    if isinstance(author, dict):
                        name = author.get('name', '')
                        print(f"  作者{j+1}: {name} (长度: {len(name)})")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    debug_metadata()
