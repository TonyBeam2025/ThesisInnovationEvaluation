#!/usr/bin/env python3
"""
测试全学科通用化对比分析功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from thesis_inno_eval.report_generator import MarkdownReportGenerator

def test_universal_analysis():
    """测试通用化的对比分析功能"""
    
    print("=== 测试全学科通用化对比分析功能 ===\n")
    
    # 创建报告生成器
    generator = MarkdownReportGenerator()
    
    # 模拟不同学科的主题分析数据
    test_cases = [
        {
            "name": "计算机科学",
            "theme_analysis": {
                'chinese_themes': {
                    '机器学习': 15, '深度学习': 12, '神经网络': 10, '人工智能': 8,
                    '算法优化': 6, '数据挖掘': 5, '计算机视觉': 4
                },
                'english_themes': {
                    'machine learning': 18, 'deep learning': 14, 'neural network': 9,
                    'algorithm': 7, 'artificial intelligence': 6, 'data mining': 5
                }
            }
        },
        {
            "name": "生物医学",
            "theme_analysis": {
                'chinese_themes': {
                    '基因表达': 12, '蛋白质结构': 10, '细胞培养': 8, '药物设计': 7,
                    '生物标志物': 6, '临床试验': 5, '分子机制': 4
                },
                'english_themes': {
                    'gene expression': 15, 'protein structure': 11, 'cell culture': 9,
                    'drug design': 8, 'biomarker': 6, 'clinical trial': 5
                }
            }
        },
        {
            "name": "经济管理",
            "theme_analysis": {
                'chinese_themes': {
                    '企业管理': 14, '市场分析': 11, '财务管理': 9, '供应链': 7,
                    '战略管理': 6, '组织行为': 5, '投资决策': 4
                },
                'english_themes': {
                    'business management': 16, 'market analysis': 12, 'financial management': 10,
                    'supply chain': 8, 'strategic management': 6, 'organizational behavior': 5
                }
            }
        },
        {
            "name": "材料科学",
            "theme_analysis": {
                'chinese_themes': {
                    '纳米材料': 13, '复合材料': 10, '材料表征': 8, '材料制备': 7,
                    '性能测试': 6, '结构分析': 5, '功能材料': 4
                },
                'english_themes': {
                    'nanomaterials': 15, 'composite materials': 11, 'material characterization': 9,
                    'material synthesis': 8, 'performance testing': 6, 'functional materials': 5
                }
            }
        }
    ]
    
    # 测试每个学科案例
    for case in test_cases:
        print(f"--- 测试学科：{case['name']} ---")
        
        # 测试研究热点分布分析
        hotspots_analysis = generator._generate_research_hotspots_analysis(case['theme_analysis'])
        print(f"研究热点分布分析:\n{hotspots_analysis}")
        
        # 测试研究趋势对比
        trend_comparison = generator._generate_trend_comparison(case['theme_analysis'])
        print(f"研究趋势对比:\n{trend_comparison}")
        
        # 测试论文相关度分析（模拟不同类型的论文）
        test_papers = [
            {"KeyWords": "算法;优化;模型", "Title": "基于深度学习的优化算法研究"},
            {"KeyWords": "理论;框架;概念", "Title": "新型理论框架构建与验证"},
            {"KeyWords": "实验;数据;分析", "Title": "实验数据分析与处理方法"},
            {"KeyWords": "应用;系统;实践", "Title": "智能系统的应用与实践"}
        ]
        
        print("论文相关度分析示例:")
        for i, paper in enumerate(test_papers, 1):
            relevance = generator._analyze_paper_relevance(paper)
            print(f"  {i}. {paper['Title']} -> {relevance}")
        
        print("-" * 60)
    
    print(" 全学科通用化对比分析功能测试完成！")
    print("\n特点总结：")
    print("1. 研究热点分布分析不再局限于特定领域")
    print("2. 使用通用的学术研究分类标准")
    print("3. 论文相关度分析适用于各个学科")
    print("4. 研究趋势对比提供通用的差异化分析")
    print("5. 支持跨学科的文献对比分析")

if __name__ == "__main__":
    test_universal_analysis()
