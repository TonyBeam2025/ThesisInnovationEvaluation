#!/usr/bin/env python3
"""
测试质量检测和降级策略功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro

def test_quality_degradation():
    """测试质量检测和降级策略"""
    print("🧪 开始测试质量检测和降级策略功能")
    print("=" * 60)
    
    # 创建提取器实例（不使用AI客户端，强制使用模式匹配）
    extractor = ThesisExtractorPro()
    
    # 测试用例1: 高质量封面文本
    print("\n📋 测试用例1: 高质量封面文本")
    print("-" * 40)
    
    high_quality_text = """
    北京航空航天大学
    硕士学位论文
    
    高温合金成分优化与性能预测研究
    
    作者姓名：张三
    指导教师：李四教授
    学科专业：材料科学与工程
    学院：材料科学与工程学院
    
    二〇二四年六月
    """
    
    result1 = extractor._pattern_extract_cover_metadata_with_quality_check(high_quality_text)
    print(f"\n 高质量测试结果:")
    for key, value in result1.items():
        print(f"   {key}: {value}")
    
    # 测试用例2: 低质量封面文本
    print("\n📋 测试用例2: 低质量封面文本")
    print("-" * 40)
    
    low_quality_text = """
    一些随机文本
    123456
    英文 text mixed
    没有明确的标题、作者等信息
    """
    
    result2 = extractor._pattern_extract_cover_metadata_with_quality_check(low_quality_text)
    print(f"\n❌ 低质量测试结果:")
    for key, value in result2.items():
        print(f"   {key}: {value}")
    
    # 测试用例3: 中等质量封面文本
    print("\n📋 测试用例3: 中等质量封面文本")
    print("-" * 40)
    
    medium_quality_text = """
    某大学
    论文题目不够清晰的研究
    作者：X
    """
    
    result3 = extractor._pattern_extract_cover_metadata_with_quality_check(medium_quality_text)
    print(f"\n⚖️ 中等质量测试结果:")
    for key, value in result3.items():
        print(f"   {key}: {value}")
    
    # 测试用例4: 空文本
    print("\n📋 测试用例4: 空文本")
    print("-" * 40)
    
    empty_text = ""
    
    result4 = extractor._pattern_extract_cover_metadata_with_quality_check(empty_text)
    print(f"\n🔳 空文本测试结果:")
    for key, value in result4.items():
        print(f"   {key}: {value}")

def test_individual_field_quality():
    """测试单个字段质量评估"""
    print("\n\n🔍 测试单个字段质量评估")
    print("=" * 60)
    
    extractor = ThesisExtractorPro()
    
    # 测试不同质量的字段值
    test_cases = [
        # 标题测试
        ('title_cn', '高温合金成分优化与性能预测研究', '高质量中文标题'),
        ('title_cn', '研究', '太短的标题'),
        ('title_cn', '作者姓名：张三的论文标题', '包含非标题内容'),
        
        # 作者测试
        ('author_cn', '张三', '标准中文姓名'),
        ('author_cn', '张三教授博士', '包含职称'),
        ('author_cn', 'Zhang123', '包含数字和英文'),
        
        # 大学测试
        ('university_cn', '北京航空航天大学', '标准大学名称'),
        ('university_cn', '材料科学与工程学院', '学院名称'),
        ('university_cn', '某机构', '非标准名称'),
        
        # 专业测试
        ('major_cn', '材料科学与工程', '标准专业'),
        ('major_cn', '工程技术研究', '包含关键词'),
        ('major_cn', '专业', '太短'),
    ]
    
    for field, value, description in test_cases:
        quality = extractor._assess_field_quality(field, value)
        print(f"   {field:15} | {value:20} | 质量: {quality:.2f} | {description}")

def test_complete_extraction_flow():
    """测试完整的提取流程"""
    print("\n\n🔄 测试完整提取流程")
    print("=" * 60)
    
    # 创建一个没有AI客户端的提取器
    extractor = ThesisExtractorPro()
    # 确保没有AI客户端，强制使用降级策略
    extractor.ai_client = None
    
    # 使用真实的论文文本片段
    real_thesis_text = """
    分类号：TG146.1+5                    UDC：669.715
    
    北京航空航天大学
    硕士学位论文
    
    Alloy Design and Performance Optimization 
    for High-Temperature Applications
    
    高温合金成分设计与性能优化研究
    
    作者姓名：王小明
    指导教师：李教授 副教授
    申请学位：工学硕士
    学科专业：材料科学与工程
    所在学院：材料科学与工程学院
    答辩日期：2024年6月15日
    
    Beijing University of Aeronautics and Astronautics
    June 2024
    """
    
    print("📄 使用真实论文文本进行完整提取测试...")
    result = extractor._pattern_extract_cover_metadata_with_quality_check(real_thesis_text)
    
    print(f"\n 完整提取结果:")
    for key, value in result.items():
        print(f"   {key}: {value}")
    
    # 检查是否触发了质量检测
    if 'quality_score' in result:
        print(f"\n📊 质量评估信息:")
        print(f"   质量分数: {result['quality_score']:.2f}")
        print(f"   提取方法: {result['extraction_method']}")
    elif 'quality_warning' in result:
        print(f"\n⚠️ 质量警告: {result['quality_warning']}")

if __name__ == "__main__":
    test_quality_degradation()
    test_individual_field_quality()
    test_complete_extraction_flow()
    
    print("\n" + "=" * 60)
    print("🎉 质量检测和降级策略测试完成！")
