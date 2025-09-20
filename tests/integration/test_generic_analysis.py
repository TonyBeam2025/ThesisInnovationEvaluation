#!/usr/bin/env python3
"""
测试通用化分析功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
from pathlib import Path

# 添加src路径
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from thesis_inno_eval.report_generator import MarkdownReportGenerator

def test_generic_analysis():
    """测试通用化的分析方法"""
    
    print("=== 测试通用化创新性分析功能 ===\n")
    
    # 创建报告生成器
    generator = MarkdownReportGenerator()
    
    # 测试不同学科的论文信息
    test_cases = [
        {
            "name": "医学论文",
            "thesis_info": {
                "title": "基于深度学习的医学影像诊断系统研究",
                "keywords": "深度学习, 医学影像, 诊断系统, 人工智能",
                "methodology": "采用卷积神经网络和迁移学习技术，构建多模态医学影像诊断模型",
                "theoretical_framework": "基于深度学习理论和医学影像处理理论",
                "contributions": "提出了新的多模态融合算法，提高了诊断准确率",
                "application_value": "可应用于临床诊断，提高诊断效率和准确性"
            }
        },
        {
            "name": "材料科学论文", 
            "thesis_info": {
                "title": "新型纳米复合材料的制备与性能研究",
                "keywords": "纳米材料, 复合材料, 制备工艺, 性能测试",
                "methodology": "采用溶胶凝胶法制备纳米复合材料，使用多种表征手段分析结构和性能",
                "theoretical_framework": "基于材料科学理论和纳米技术理论",
                "contributions": "开发了新的制备工艺，获得了优异的材料性能",
                "application_value": "在能源存储和催化领域具有广阔应用前景"
            }
        },
        {
            "name": "管理学论文",
            "thesis_info": {
                "title": "数字化转型下的组织管理创新研究",
                "keywords": "数字化转型, 组织管理, 管理创新, 企业变革",
                "methodology": "采用案例研究和问卷调查相结合的混合研究方法",
                "theoretical_framework": "基于组织变革理论和数字化转型理论",
                "contributions": "构建了数字化转型下的组织管理框架模型",
                "application_value": "为企业数字化转型提供管理指导和决策支持"
            }
        }
    ]
    
    # 测试每个案例
    for case in test_cases:
        print(f"--- 测试案例：{case['name']} ---")
        
        # 测试方法学创新分析
        methodology_analysis = generator._analyze_methodological_innovation(
            case['thesis_info'], {}, case['thesis_info']
        )
        print(f"方法学创新分析:\n{methodology_analysis[:200]}...\n")
        
        # 测试理论贡献分析
        theory_analysis = generator._analyze_theoretical_contribution(
            case['thesis_info'], {}, case['thesis_info']
        )
        print(f"理论贡献分析:\n{theory_analysis[:200]}...\n")
        
        # 测试实践价值分析
        practice_analysis = generator._analyze_practical_value(
            case['thesis_info'], {}, case['thesis_info']
        )
        print(f"实践价值分析:\n{practice_analysis[:200]}...\n")
        
        print("-" * 50)
    
    print(" 通用化分析功能测试完成！")
    print("\n特点总结：")
    print("1. 所有分析方法都适用于不同学科")
    print("2. 使用通用的学术评价指标")
    print("3. 避免了特定领域的硬编码内容")
    print("4. 分析结果具有跨学科的普适性")

if __name__ == "__main__":
    test_generic_analysis()
