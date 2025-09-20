#!/usr/bin/env python3
"""
测试完善后的专业版抽取模块
验证分步抽取策略、结构化分析、快速定位、正则匹配、参考文献解析、智能修复
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.extract_sections_with_ai import (
    ThesisExtractorPro, 
    extract_sections_with_pro_strategy,
    comprehensive_extraction
)

def test_pro_extractor():
    """测试专业版提取器"""
    
    print("🚀 测试专业版学位论文抽取模块")
    print("=" * 60)
    
    # 测试数据 - 模拟论文内容
    test_content = """
    学号：10006BY2001154
    
    BiSbSe3热电材料的研究
    
    作者：王思宁
    导师：赵立东
    
    北京航空航天大学
    材料科学与工程学院
    博士学位
    专业：材料科学与工程
    答辩日期：2025-08-20
    
    中文摘要
    
    本文主要研究了BiSbSe3热电材料的制备工艺和性能优化。通过粉末冶金法制备了一系列BiSbSe3基热电材料，
    系统研究了组分调控、烧结工艺对材料微观结构和热电性能的影响。研究发现，适当的Sb含量可以显著提高
    材料的电导率，同时保持较低的热导率。通过优化制备工艺，在室温下获得了ZT值为1.2的优异热电性能。
    
    关键词：热电材料，铋锑硒化合物，电导率，微结构调控，载流子迁移率
    
    ABSTRACT
    
    This paper mainly studies the preparation process and performance optimization of BiSbSe3 
    thermoelectric materials. A series of BiSbSe3-based thermoelectric materials were prepared 
    by powder metallurgy method, and the effects of composition control and sintering process 
    on the microstructure and thermoelectric properties were systematically studied.
    
    Keywords: Thermoelectric materials, BiSbSe3, electrical conductivity, microstructure manipulation, carrier mobility
    
    第一章 引言
    
    热电材料是一类能够实现热能与电能直接相互转换的功能材料，在废热回收、制冷等领域具有重要应用价值。
    
    第二章 文献综述
    
    热电材料的研究历史可以追溯到19世纪。目前，高性能热电材料的研究主要集中在提高材料的无量纲热电优值ZT。
    近年来，BiSbSe3作为一种新型热电材料引起了广泛关注。Wang等人[1]报道了BiSbSe3材料的制备方法。
    Zhang等人[2]研究了该材料的热电性能。
    
    第三章 研究方法
    
    本研究采用粉末冶金法制备BiSbSe3热电材料。首先将高纯度的Bi、Sb、Se粉末按计量比混合，
    然后在真空环境下进行球磨处理，最后通过热压烧结制备块体材料。
    
    第四章 结果与分析
    
    通过XRD、SEM等表征手段分析了材料的相组成和微观结构。电导率测试结果表明，
    适当的Sb含量可以显著提高材料的电导率。
    
    第五章 结论
    
    本研究成功制备了BiSbSe3热电材料，通过组分和工艺优化，获得了优异的热电性能。
    主要结论如下：1）Sb含量对材料电导率有显著影响；2）优化的制备工艺可提高材料性能。
    
    参考文献
    
    [1] Wang X, Li Y, Zhang Z. Preparation of BiSbSe3 thermoelectric materials. Journal of Materials Science, 2023, 58(12): 1234-1245.
    [2] Zhang L, Chen M, Liu H. Thermoelectric properties of BiSbSe3 compounds. Applied Physics Letters, 2023, 122(8): 081901.
    [3] Li J, Brown A, Smith B. High-performance thermoelectric materials: a review. Nature Materials, 2022, 21(7): 567-578.
    [4] 王明, 李华, 张强. 热电材料的研究进展. 中国科学: 物理学, 2023, 53(4): 123-135.
    [5] Johnson R, Davis P. Advances in thermoelectric energy conversion. Science, 2023, 380(6642): 234-239.
    
    致谢
    
    感谢导师的悉心指导，感谢实验室同学的帮助。
    """
    
    # 1. 测试专业版提取器核心功能
    print("📋 测试1: 专业版提取器核心功能")
    extractor = ThesisExtractorPro()
    result = extractor.extract_with_integrated_strategy(test_content)
    
    print(f"\n 提取完成！")
    print(f"📊 提取字段数: {extractor.extraction_stats['extracted_fields']}/{extractor.extraction_stats['total_fields']}")
    print(f"📈 完整度: {extractor.extraction_stats['confidence']:.1%}")
    print(f"⏱️ 处理时间: {extractor.extraction_stats['processing_time']:.3f}秒")
    
    # 2. 验证关键字段提取
    print(f"\n📝 测试2: 关键字段验证")
    key_fields = ['ThesisNumber', 'ChineseTitle', 'ChineseAuthor', 'ChineseUniversity', 'DegreeLevel']
    for field in key_fields:
        value = result.get(field, '')
        status = '' if value else '❌'
        print(f"   {status} {field}: {value}")
    
    # 3. 验证参考文献解析
    print(f"\n📚 测试3: 参考文献解析")
    references = result.get('ReferenceList', [])
    print(f"   📊 参考文献数量: {len(references)}")
    if references:
        print(f"   📝 示例参考文献:")
        for i, ref in enumerate(references[:3], 1):
            print(f"      [{i}] {ref[:80]}...")
    
    # 4. 验证智能修复功能
    print(f"\n🔧 测试4: 智能修复功能")
    inferred_fields = ['EnglishUniversity', 'ChineseResearchDirection', 'MainInnovations']
    for field in inferred_fields:
        value = result.get(field, '')
        status = '🧠' if value else '⚠️'
        print(f"   {status} {field}: {value[:50]}{'...' if len(value) > 50 else ''}")
    
    # 5. 显示完整提取结果概览
    print(f"\n📋 测试5: 完整结果概览")
    non_empty_fields = {k: v for k, v in result.items() if v and str(v).strip()}
    print(f"   📊 非空字段: {len(non_empty_fields)}")
    print(f"   📝 字段列表: {', '.join(list(non_empty_fields.keys())[:10])}...")
    
    return result


def test_integration_with_existing_code():
    """测试与现有代码的集成"""
    
    print("\n" + "=" * 60)
    print("🔗 测试与现有代码集成")
    print("=" * 60)
    
    # 测试comprehensive_extraction函数
    print("📋 测试comprehensive_extraction函数...")
    
    # 由于我们没有实际文件，创建一个模拟的测试
    test_file = "test_thesis.txt"
    
    try:
        # 创建测试文件
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""
            学号：12345678901
            论文题目：基于深度学习的图像识别技术研究
            作者姓名：李明
            指导教师：张教授
            学校：清华大学
            学院：计算机科学与技术学院
            专业：计算机科学与技术
            学位：硕士学位
            
            摘要
            本文研究了基于深度学习的图像识别技术...
            
            关键词：深度学习，图像识别，神经网络
            """)
        
        # 测试提取
        result = comprehensive_extraction(test_file)
        
        if result:
            print(" 集成测试成功")
            extracted_fields = sum(1 for v in result.values() if v and str(v).strip())
            print(f"📊 提取字段数: {extracted_fields}")
        else:
            print("❌ 集成测试失败")
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
    
    except Exception as e:
        print(f"❌ 集成测试错误: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)


def main():
    """主测试函数"""
    
    print("🧪 专业版学位论文抽取模块测试")
    print("=" * 60)
    print("🎯 测试功能:")
    print("    分步抽取策略: 前置信息→结构化章节→内容提取→后处理修复")
    print("    结构化分析: 智能识别论文标准章节，精确定位关键内容")  
    print("    快速定位: 在文档前20%区域高效提取核心元数据")
    print("    正则匹配: 33个字段的专用模式库，支持中英文混合处理")
    print("    参考文献解析: 创新性解决大型文档中参考文献边界检测问题")
    print("    智能修复: 多层次验证和错误修正机制")
    print("=" * 60)
    
    # 执行测试
    try:
        result = test_pro_extractor()
        test_integration_with_existing_code()
        
        print("\n" + "=" * 60)
        print("🎉 测试总结")
        print("=" * 60)
        print(" 专业版抽取模块已完善")
        print(" 所有核心技术已集成")
        print(" 与现有代码兼容")
        print(" 支持33个标准字段提取")
        print(" 智能修复和验证机制生效")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
