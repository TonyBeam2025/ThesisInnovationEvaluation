#!/usr/bin/env python3
"""
测试文献综述分析功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

def test_literature_review_analysis():
    """测试文献综述分析功能"""
    from thesis_inno_eval.report_generator import MarkdownReportGenerator
    
    # 模拟论文抽取信息
    thesis_extracted_info = {
        'Abstract': '本研究探讨了跨模态图像融合技术在医疗影像分析中的应用，提出了基于深度学习的融合算法。',
        'Introduction': '医疗影像分析是计算机视觉领域的重要应用方向，随着多模态成像技术的发展，如何有效融合不同模态的影像信息成为研究热点。',
        'Keywords': '跨模态图像融合;医疗影像;深度学习;计算机视觉',
        'ReferenceList': '''[1] Wang L, Chen H. Deep learning for medical image fusion[J]. IEEE Transactions on Medical Imaging, 2023, 42(3): 567-580.
[2] Zhang Y, Liu X. Multi-modal medical image analysis: A survey[J]. Medical Image Analysis, 2022, 78: 102401.
[3] 李明, 王强. 基于深度学习的医疗影像融合技术研究[J]. 计算机学报, 2023, 46(2): 234-248.
[4] Smith J, Brown A. Cross-modal image fusion in healthcare[C]. MICCAI 2023, 2023: 123-135.
[5] 陈伟, 张华. 医疗影像多模态融合算法综述[J]. 中国图像图形学报, 2022, 27(8): 2156-2170.'''
    }
    
    # 模拟CNKI检索结果
    papers_by_lang = {
        'Chinese': [
            {'title': '基于注意力机制的多模态医疗影像融合', 'author': '刘天明', 'year': '2023'},
            {'title': '深度学习在医疗影像分析中的应用综述', 'author': '王雅琳', 'year': '2022'},
            {'title': '跨模态医疗影像融合技术研究进展', 'author': '张志强', 'year': '2023'},
            {'title': '医疗影像AI诊断系统关键技术', 'author': '李晓红', 'year': '2023'},
            {'title': '多模态融合在肿瘤诊断中的应用', 'author': '陈建国', 'year': '2022'}
        ],
        'English': [
            {'title': 'Attention-based multi-modal medical image fusion', 'author': 'Johnson M', 'year': '2023'},
            {'title': 'Deep learning approaches for medical image analysis', 'author': 'Williams R', 'year': '2023'},
            {'title': 'Cross-modal fusion in medical imaging: A comprehensive review', 'author': 'Davis L', 'year': '2022'},
            {'title': 'AI-driven medical image interpretation systems', 'author': 'Miller K', 'year': '2023'},
            {'title': 'Multi-modal imaging for cancer diagnosis', 'author': 'Thompson S', 'year': '2022'}
        ]
    }
    
    # 创建报告生成器
    generator = MarkdownReportGenerator()
    
    print("🧪 测试文献综述分析功能...")
    
    # 测试各个分析方法
    print("\n📊 测试覆盖度分析...")
    coverage = generator._analyze_literature_coverage(
        thesis_extracted_info['ReferenceList'], 
        papers_by_lang
    )
    print(coverage[:200] + "...")
    
    print("\n🤔 测试深度分析（CoT）...")
    depth = generator._analyze_literature_depth_cot(
        thesis_extracted_info['ReferenceList'],
        papers_by_lang,
        thesis_extracted_info
    )
    print(depth[:200] + "...")
    
    print("\n🎯 测试相关性分析...")
    relevance = generator._analyze_literature_relevance(
        thesis_extracted_info['ReferenceList'],
        papers_by_lang,
        thesis_extracted_info
    )
    print(relevance[:200] + "...")
    
    print("\n⏰ 测试时效性分析...")
    timeliness = generator._analyze_literature_timeliness(
        thesis_extracted_info['ReferenceList'],
        papers_by_lang
    )
    print(timeliness[:200] + "...")
    
    print("\n🔍 测试缺失文献分析...")
    missing = generator._find_missing_references(
        thesis_extracted_info['ReferenceList'],
        papers_by_lang
    )
    print(missing[:200] + "...")
    
    print("\n 测试完整的文献综述分析...")
    full_analysis = generator._generate_literature_review_analysis(
        thesis_extracted_info,
        papers_by_lang,
        {}
    )
    print(f"生成的文献综述分析长度: {len(full_analysis)} 字符")
    print(full_analysis[:500] + "...")
    
    print("\n🎉 文献综述分析功能测试完成！")

if __name__ == "__main__":
    test_literature_review_analysis()
