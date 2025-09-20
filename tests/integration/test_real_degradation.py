#!/usr/bin/env python3
"""
测试真实论文的质量检测和降级策略
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro

def test_real_degradation_scenario():
    """测试真实的降级场景"""
    print("🔧 测试真实论文的质量检测和降级策略")
    print("=" * 60)
    
    # 创建提取器实例，模拟AI不可用的场景
    extractor = ThesisExtractorPro()
    extractor.ai_client = None  # 强制使用降级策略
    
    # 测试案例1: 标准论文封面（高质量）
    print("\n📄 案例1: 标准学位论文封面")
    print("-" * 40)
    
    standard_cover = """
    分类号：TG146.2                      密级：公开
    UDC：669.142
    
    北京航空航天大学
    博士学位论文
    
    基于机器学习的钛合金微观组织预测与优化研究
    
    Research on Microstructure Prediction and Optimization 
    of Titanium Alloys Based on Machine Learning
    
    作者姓名：李小华
    指导教师：张教授  教授
    申请学位：工学博士
    学科专业：材料科学与工程
    研究方向：金属材料
    所在学院：材料科学与工程学院
    
    答辩日期：二○二四年十二月
    
    Beijing University of Aeronautics and Astronautics
    December 2024
    """
    
    result1 = test_extraction_with_degradation(extractor, standard_cover)
    analyze_result(result1, "标准论文封面")
    
    # 测试案例2: 破损或不完整的封面（中等质量）
    print("\n📄 案例2: 不完整论文封面")
    print("-" * 40)
    
    incomplete_cover = """
    某大学学位论文
    
    关于某项技术的研究
    
    学生：小明
    导师：某教授
    """
    
    result2 = test_extraction_with_degradation(extractor, incomplete_cover)
    analyze_result(result2, "不完整封面")
    
    # 测试案例3: 严重损坏的文本（低质量）
    print("\n📄 案例3: 严重损坏的文本")
    print("-" * 40)
    
    corrupted_text = """
    %%PDF-1.4
    1 0 obj
    <<
    /Type /Catalog
    /Pages 2 0 R
    >>
    endobj
    
    一些无法识别的文本
    &#39;%&*(
    """
    
    result3 = test_extraction_with_degradation(extractor, corrupted_text)
    analyze_result(result3, "损坏文本")

def test_extraction_with_degradation(extractor, text):
    """测试带降级的提取"""
    try:
        # 使用新的质量检测方法
        result = extractor._pattern_extract_cover_metadata_with_quality_check(text)
        return result
    except Exception as e:
        print(f"   ❌ 提取失败: {e}")
        return {
            'error': str(e),
            'extraction_method': 'failed'
        }

def analyze_result(result, scenario_name):
    """分析提取结果"""
    print(f"\n📊 {scenario_name} - 结果分析:")
    
    if 'error' in result:
        print(f"   ❌ 提取错误: {result['error']}")
        return
    
    # 检查质量分数
    if 'quality_score' in result:
        quality = result['quality_score']
        if quality >= 0.7:
            quality_level = "高质量 "
        elif quality >= 0.3:
            quality_level = "中等质量 ⚖️"
        else:
            quality_level = "低质量 ❌"
        
        print(f"   📈 质量分数: {quality:.2f} ({quality_level})")
        print(f"   🔧 提取方法: {result.get('extraction_method', '未知')}")
        
        # 显示提取的关键字段
        key_fields = ['title_cn', 'author_cn', 'university_cn', 'major_cn']
        extracted_count = 0
        for field in key_fields:
            if field in result and result[field]:
                extracted_count += 1
                print(f"    {field}: {result[field]}")
        
        print(f"   📋 关键字段提取率: {extracted_count}/{len(key_fields)} ({extracted_count/len(key_fields)*100:.0f}%)")
        
    elif 'quality_warning' in result:
        print(f"   ⚠️ 质量警告: {result['quality_warning']}")
        print(f"   🔧 降级到基础方法: {result.get('extraction_method', '未知')}")
        print(f"   🔄 返回了默认值以确保系统稳定性")
    
    print(f"   📝 总共提取字段数: {len([k for k, v in result.items() if v and not k.startswith('quality') and not k.startswith('extraction')])}")

def test_quality_threshold_adjustment():
    """测试质量阈值调整"""
    print("\n\n🎛️ 测试不同质量阈值的影响")
    print("=" * 60)
    
    extractor = ThesisExtractorPro()
    
    # 测试用例：中等质量的文本
    medium_text = """
    大学论文
    标题：某项研究
    作者：小李
    """
    
    # 先获取质量分数
    metadata = extractor._pattern_extract_cover_metadata(medium_text)
    quality = extractor._assess_extraction_quality(metadata)
    
    print(f"📊 测试文本的实际质量分数: {quality:.2f}")
    
    # 测试不同阈值的影响
    thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    for threshold in thresholds:
        if quality >= threshold:
            status = " 通过"
        else:
            status = "❌ 降级"
        print(f"   阈值 {threshold:.1f}: {status}")
    
    print(f"\n💡 当前系统使用阈值 0.3，对于该文本：{' 会正常提取' if quality >= 0.3 else '❌ 会触发降级'}")

if __name__ == "__main__":
    test_real_degradation_scenario()
    test_quality_threshold_adjustment()
    
    print("\n" + "=" * 60)
    print("🎯 质量检测和降级策略的实际应用测试完成！")
    print("\n📋 总结:")
    print("    高质量文本：正常提取，提供详细元数据")
    print("   ⚖️ 中等质量文本：继续提取，但会记录质量分数")
    print("   ❌ 低质量文本：触发降级，返回安全的默认值")
    print("   🔄 系统始终保持稳定，不会因质量问题而崩溃")
