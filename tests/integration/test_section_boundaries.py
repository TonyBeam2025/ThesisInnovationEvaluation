#!/usr/bin/env python3
"""
测试章节边界识别功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os

# 添加源代码路径
current_dir = str(PROJECT_ROOT)
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

try:
    # 直接导入模块
    import thesis_inno_eval.extract_sections_with_ai as extract_module
    ThesisExtractorPro = extract_module.ThesisExtractorPro
    print(" 成功导入 ThesisExtractorPro 类")
except ImportError as e:
    print(f"❌ 无法导入 ThesisExtractorPro 类: {e}")
    print("请确保文件路径正确")
    sys.exit(1)

def test_section_boundary_detection():
    """测试章节边界识别功能"""
    
    # 创建测试文本
    test_text = """
某大学硕士学位论文

基于深度学习的图像识别技术研究

作者：张三
导师：李四教授

摘要

本文研究了基于深度学习的图像识别技术。通过分析现有的深度学习模型，提出了一种新的卷积神经网络架构。实验结果表明，该方法在图像分类任务上取得了显著的性能提升。

关键词：深度学习；图像识别；卷积神经网络；特征提取

ABSTRACT

This paper studies image recognition technology based on deep learning. By analyzing existing deep learning models, a new convolutional neural network architecture is proposed. Experimental results show that this method achieves significant performance improvement in image classification tasks.

Keywords: Deep Learning; Image Recognition; Convolutional Neural Network; Feature Extraction

第一章 引言

1.1 研究背景

随着人工智能技术的快速发展，图像识别技术已经成为计算机视觉领域的重要研究方向...

1.2 研究意义

图像识别技术的发展对于智能监控、自动驾驶等领域具有重要意义...

第二章 文献综述

2.1 深度学习理论基础

深度学习是机器学习的一个重要分支，通过构建多层神经网络来学习数据的表示...

2.2 图像识别相关技术

传统的图像识别方法主要包括特征提取、特征选择和分类器设计...

第三章 研究方法

3.1 网络架构设计

本文提出的卷积神经网络架构包含多个卷积层、池化层和全连接层...

3.2 训练策略

为了提高模型的泛化能力，本文采用了数据增强、dropout等技术...

第四章 实验结果与分析

4.1 实验设置

实验采用CIFAR-10数据集进行验证，包含10个类别的60000张32x32彩色图像...

4.2 实验结果

实验结果显示，提出的方法在准确率、召回率等指标上都优于基准方法...

结论

本文提出了一种基于深度学习的图像识别方法，通过实验验证了其有效性。主要贡献包括：
1. 设计了新的网络架构
2. 提高了识别准确率
3. 减少了计算复杂度

参考文献

[1] LeCun Y, Bengio Y, Hinton G. Deep learning[J]. Nature, 2015, 521(7553): 436-444.
[2] Krizhevsky A, Sutskever I, Hinton G E. Imagenet classification with deep convolutional neural networks[C]//Advances in neural information processing systems. 2012: 1097-1105.
[3] Simonyan K, Zisserman A. Very deep convolutional networks for large-scale image recognition[J]. arXiv preprint arXiv:1409.1556, 2014.

致谢

感谢导师李四教授的悉心指导，感谢实验室同学的帮助和支持...
"""
    
    print("🔍 开始测试章节边界识别功能...")
    print("=" * 60)
    
    # 创建提取器实例
    extractor = ThesisExtractorPro()
    
    # 测试1: 分析文档结构
    print("\n📊 测试1: 分析文档结构")
    print("-" * 40)
    sections = extractor._analyze_document_structure(test_text)
    
    print(f"\n识别到的章节数量: {len([k for k in sections.keys() if not k.endswith('_info')])}")
    
    # 显示识别到的章节信息
    for key, value in sections.items():
        if key.endswith('_info') and isinstance(value, dict):
            section_name = key.replace('_info', '')
            print(f"\n📝 章节: {section_name}")
            print(f"   标题: {value.get('title', 'N/A')}")
            print(f"   位置: 行 {value.get('boundaries', {}).get('start_line', 'N/A')}-{value.get('boundaries', {}).get('end_line', 'N/A')}")
            print(f"   长度: {value.get('content_length', 0)} 字符")
            print(f"   置信度: {value.get('boundary_confidence', 0):.2f}")
    
    # 测试2: 精确边界检测
    print("\n\n🎯 测试2: 精确边界检测")
    print("-" * 40)
    
    test_sections = ['摘要', '第一章', '第二章', '结论', '参考文献']
    
    for section_title in test_sections:
        print(f"\n🔍 测试章节: {section_title}")
        boundary_info = extractor.find_precise_section_boundaries(test_text, section_title)
        
        if boundary_info['found']:
            print(f"    找到章节")
            print(f"   📋 标题: {boundary_info['title']}")
            print(f"   📍 字符位置: {boundary_info['start_pos']}-{boundary_info['end_pos']}")
            print(f"   📏 行位置: {boundary_info['start_line']}-{boundary_info['end_line']}")
            print(f"   📖 内容长度: {len(boundary_info['content'])} 字符")
            print(f"   🎯 置信度: {boundary_info['confidence']:.2f}")
            if boundary_info['next_section']:
                print(f"   ⏭️ 下一章节: {boundary_info['next_section']}")
            
            # 显示内容预览（前100字符）
            content_preview = boundary_info['content'][:100]
            if len(boundary_info['content']) > 100:
                content_preview += "..."
            print(f"   📄 内容预览: {content_preview}")
        else:
            print(f"   ❌ 未找到章节")
    
    # 测试3: 内容提取
    print("\n\n📄 测试3: 基于章节的内容提取")
    print("-" * 40)
    content_info = extractor._extract_content_by_sections(test_text, sections)
    
    print(f"\n提取结果概览:")
    for key, value in content_info.items():
        if key != 'section_boundaries':
            if isinstance(value, str):
                print(f"   {key}: {len(value)} 字符")
            elif isinstance(value, list):
                print(f"   {key}: {len(value)} 项")
            else:
                print(f"   {key}: {type(value).__name__}")
    
    print("\n 测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_section_boundary_detection()
