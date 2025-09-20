#!/usr/bin/env python3
"""
测试文献综述深度分析的思维链功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

from src.thesis_inno_eval.literature_review_analyzer import LiteratureReviewAnalyzer

def test_cot_analysis():
    """测试思维链深度分析功能"""
    
    # 创建分析器实例
    analyzer = LiteratureReviewAnalyzer()
    
    # 模拟测试数据
    test_thesis_info = {
        'ChineseTitle': '基于深度学习的图像识别技术研究',
        'ChineseKeywords': '深度学习,图像识别,卷积神经网络,计算机视觉',
        'ChineseAbstract': '本文研究了基于深度学习的图像识别技术，通过构建卷积神经网络模型，实现了对复杂图像的高精度识别。研究结果表明该方法具有良好的性能表现。',
        'ReferenceList': '[1] LeCun Y, Bengio Y, Hinton G. Deep learning[J]. Nature, 2015, 521(7553): 436-444.\n[2] Krizhevsky A, Sutskever I, Hinton G E. Imagenet classification with deep convolutional neural networks[C]//Advances in neural information processing systems. 2012: 1097-1105.',
        'LiteratureReview': '深度学习技术在图像识别领域取得了显著进展。LeCun等人提出的深度学习理论为该领域奠定了基础。Krizhevsky等人开发的AlexNet在ImageNet竞赛中取得突破性成果。然而，现有研究在复杂场景下的识别精度仍有待提升。'
    }
    
    test_papers_by_lang = {
        'Chinese': [
            {
                'title': '深度卷积神经网络在图像分类中的应用',
                '年份': '2020',
                '被引次数': 150,
                '下载次数': 3000
            },
            {
                'title': '计算机视觉中的深度学习方法研究',
                '年份': '2021',
                '被引次数': 120,
                '下载次数': 2500
            }
        ],
        'English': [
            {
                'title': 'Deep Learning for Computer Vision: A Brief Review',
                'Year': '2022',
                '被引次数': 200,
                '下载次数': 4000
            }
        ]
    }
    
    print("🧠 测试思维链深度分析功能...")
    print("=" * 60)
    
    # 测试备用分析功能（不需要调用API）
    print("📋 测试备用深度分析功能:")
    fallback_result = analyzer._generate_fallback_depth_analysis(
        test_thesis_info, test_papers_by_lang, test_thesis_info['ReferenceList']
    )
    print(fallback_result[:500] + "..." if len(fallback_result) > 500 else fallback_result)
    
    print("\n" + "=" * 60)
    
    # 测试总结生成功能
    print("📊 测试主报告总结生成功能:")
    summary = analyzer.generate_summary_for_main_report(test_thesis_info, test_papers_by_lang)
    
    print(f"综合评分: {summary.get('overall_score', 0):.1f}/10.0")
    print(f"覆盖度评分: {summary.get('coverage_score', 0):.1f}/10.0")
    print(f"深度评分: {summary.get('depth_score', 0):.1f}/10.0")
    print(f"相关性评分: {summary.get('relevance_score', 0):.1f}/10.0")
    print(f"时效性评分: {summary.get('timeliness_score', 0):.1f}/10.0")
    
    print("\n" + "=" * 60)
    print(" 思维链分析功能测试完成!")
    
    # 测试提示词模板
    print("\n🎯 提示词模板预览:")
    prompt_preview = analyzer.depth_analysis_prompt[:300] + "..."
    print(prompt_preview)
    
    return True

if __name__ == "__main__":
    test_cot_analysis()
