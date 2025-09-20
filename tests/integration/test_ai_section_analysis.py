#!/usr/bin/env python3
"""
测试基于步骤3结构分析结果的AI智能分析功能
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
import json
import glob
from typing import Dict, Any

# 添加源代码路径
current_dir = str(PROJECT_ROOT)
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def test_ai_section_analysis():
    """测试AI章节分析功能"""
    
    print("🧠 AI章节分析功能测试")
    print("=" * 80)
    
    # 导入提取器
    try:
        import thesis_inno_eval.extract_sections_with_ai as extract_module
        extractor = extract_module.ThesisExtractorPro()
        print("    提取器初始化成功")
    except Exception as e:
        print(f"   ❌ 提取器初始化失败: {e}")
        return
    
    # 测试用的简化论文文本
    test_text = """
# 基于深度学习的图像识别技术研究

## 摘要

本研究提出了一种基于深度学习的图像识别方法，通过改进卷积神经网络结构，实现了更高的识别精度。实验结果表明，该方法在标准数据集上达到了95%的准确率，相比传统方法提升了10%。

关键词：深度学习，图像识别，卷积神经网络，机器学习

## Abstract

This research proposes a deep learning-based image recognition method that achieves higher recognition accuracy by improving the convolutional neural network structure. Experimental results show that this method achieves 95% accuracy on standard datasets, which is 10% higher than traditional methods.

Keywords: deep learning, image recognition, convolutional neural network, machine learning

## 第一章 绪论

### 1.1 研究背景

随着人工智能技术的快速发展，图像识别技术在各个领域得到了广泛应用。传统的图像识别方法依赖手工设计的特征，存在泛化能力有限的问题。深度学习技术的兴起为图像识别带来了新的机遇。

### 1.2 研究意义

本研究的意义在于：
1. 提高图像识别的准确率
2. 降低人工特征设计的复杂度
3. 为相关应用提供技术支撑

## 第二章 相关工作

### 2.1 传统图像识别方法

传统的图像识别方法主要包括：
- 基于模板匹配的方法
- 基于统计学习的方法
- 基于特征工程的方法

### 2.2 深度学习方法

深度学习在图像识别领域的应用包括：
- CNN卷积神经网络
- ResNet残差网络
- Transformer架构

## 第三章 研究方法

### 3.1 网络架构设计

本研究提出的网络架构包含以下组件：
1. 特征提取层
2. 注意力机制
3. 分类器层

### 3.2 训练策略

采用以下训练策略：
- 数据增强
- 学习率调度
- 正则化技术

## 第四章 实验结果

### 4.1 数据集

使用的数据集包括：
- CIFAR-10
- ImageNet
- 自建数据集

### 4.2 实验设置

实验环境：
- GPU: NVIDIA RTX 3080
- Framework: PyTorch
- Batch Size: 32

### 4.3 结果分析

实验结果显示，本方法在各个数据集上都取得了良好的性能：
- CIFAR-10: 95.2%
- ImageNet: 78.9%
- 自建数据集: 92.1%

## 第五章 结论

### 5.1 研究总结

本研究成功提出了一种改进的深度学习图像识别方法，在多个数据集上验证了其有效性。主要贡献包括：
1. 设计了新的网络架构
2. 提出了有效的训练策略
3. 实现了性能提升

### 5.2 未来工作

未来的研究方向包括：
- 网络架构的进一步优化
- 在更多领域的应用
- 计算效率的提升

## 参考文献

[1] LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. nature, 521(7553), 436-444.
[2] He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition.
[3] Krizhevsky, A., Sutskever, I., & Hinton, G. E. (2012). Imagenet classification with deep convolutional neural networks.

## 致谢

感谢导师的悉心指导和实验室同学的帮助。
"""
    
    print("\n🔍 步骤1: 文档结构分析")
    print("-" * 50)
    
    # 执行步骤3的结构分析
    sections = extractor._analyze_document_structure(test_text)
    
    print(f"识别的章节数量: {len([k for k in sections.keys() if not k.endswith('_info')])}")
    
    # 显示识别的章节
    for key, value in sections.items():
        if not key.endswith('_info') and isinstance(value, str):
            info_key = f"{key}_info"
            info = sections.get(info_key, {})
            title = info.get('title', 'N/A') if isinstance(info, dict) else 'N/A'
            confidence = info.get('boundary_confidence', 0) if isinstance(info, dict) else 0
            print(f"   📖 {key}: {title} (置信度: {confidence:.2f}, 长度: {len(value)})")
    
    print("\n🧠 步骤2: AI智能分析")
    print("-" * 50)
    
    # 执行AI智能分析
    if extractor.ai_client:
        ai_analysis = extractor._conduct_ai_analysis_on_sections(test_text, sections)
        
        print(f"\n📊 AI分析结果概览:")
        print(f"   章节分析数量: {len(ai_analysis.get('section_analysis', {}))}")
        
        # 显示各章节分析结果
        for section_name, analysis in ai_analysis.get('section_analysis', {}).items():
            if isinstance(analysis, dict):
                overall_score = analysis.get('overall_score', 0)
                summary = analysis.get('summary', '')[:50]
                print(f"   📖 {section_name}: 评分 {overall_score:.1f}/10")
                if summary:
                    print(f"      💭 摘要: {summary}...")
                
                # 显示评分详情
                scores = []
                for score_key in ['content_quality_score', 'structure_score', 'academic_value_score', 'language_score']:
                    score = analysis.get(score_key, 0)
                    if score > 0:
                        scores.append(f"{score_key.replace('_score', '')}: {score}")
                
                if scores:
                    print(f"      📊 详细评分: {', '.join(scores)}")
                
                # 显示优点和建议
                strengths = analysis.get('strengths', [])
                if strengths:
                    print(f"       优点: {', '.join(strengths[:2])}")
                
                suggestions = analysis.get('improvement_suggestions', [])
                if suggestions:
                    print(f"      💡 建议: {', '.join(suggestions[:2])}")
        
        # 显示整体结构评估
        structure_eval = ai_analysis.get('structure_evaluation', {})
        if structure_eval:
            print(f"\n🏗️ 整体结构评估:")
            for key, value in structure_eval.items():
                if key.endswith('_score') or key == 'overall_structure_score':
                    print(f"   📊 {key.replace('_', ' ').title()}: {value}")
        
        # 显示学术质量评估
        quality_assessment = ai_analysis.get('content_quality', {})
        if quality_assessment:
            print(f"\n🎓 学术质量评估:")
            for key, value in quality_assessment.items():
                if key.endswith('_score'):
                    print(f"   📊 {key.replace('_', ' ').title()}: {value}")
    
    else:
        print("   ⚠️ AI客户端不可用，跳过AI分析")
    
    print("\n🧪 步骤3: 完整提取测试")
    print("-" * 50)
    
    # 测试完整的提取流程
    try:
        full_result = extractor.extract_with_integrated_strategy(test_text)
        
        print(f" 完整提取成功")
        print(f"   📊 字段数量: {len(full_result)}")
        
        # 显示AI分析相关字段
        if 'ai_analysis' in full_result:
            ai_data = full_result['ai_analysis']
            print(f"   🧠 AI分析: {len(ai_data.get('section_analysis', {}))} 个章节")
        
        if 'ai_insights' in full_result:
            insights = full_result['ai_insights']
            print(f"   💡 AI洞察: {len(insights)} 条")
            for insight in insights[:3]:
                print(f"      - {insight}")
        
        # 保存结果到文件
        output_file = os.path.join(current_dir, 'ai_analysis_test_result.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(full_result, f, ensure_ascii=False, indent=2)
        
        print(f"   💾 结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"   ❌ 完整提取失败: {e}")
        import traceback
        traceback.print_exc()

def test_cached_documents():
    """测试缓存文档的AI分析"""
    
    print("\n" + "=" * 80)
    print("📚 缓存文档AI分析测试")
    print("=" * 80)
    
    # 导入提取器
    try:
        import thesis_inno_eval.extract_sections_with_ai as extract_module
        extractor = extract_module.ThesisExtractorPro()
    except Exception as e:
        print(f"   ❌ 提取器初始化失败: {e}")
        return
    
    # 获取缓存文档
    cache_dir = os.path.join(current_dir, 'cache', 'documents')
    if not os.path.exists(cache_dir):
        print("   ⚠️ 缓存目录不存在")
        return
    
    md_files = glob.glob(os.path.join(cache_dir, "*.md"))
    if not md_files:
        print("   ⚠️ 没有找到缓存的markdown文件")
        return
    
    # 选择最新的文档进行测试
    md_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    test_file = md_files[0]
    
    print(f"📖 测试文档: {os.path.basename(test_file)}")
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"   📄 文档长度: {len(content)} 字符")
        
        # 执行AI分析
        print(f"   🧠 执行AI分析...")
        
        # 首先进行结构分析
        sections = extractor._analyze_document_structure(content)
        section_count = len([k for k in sections.keys() if not k.endswith('_info')])
        print(f"   📖 识别章节: {section_count} 个")
        
        # 执行AI智能分析
        if extractor.ai_client:
            ai_analysis = extractor._conduct_ai_analysis_on_sections(content, sections)
            
            analyzed_sections = len(ai_analysis.get('section_analysis', {}))
            print(f"   🤖 AI分析完成: {analyzed_sections} 个章节")
            
            # 计算平均评分
            total_scores = []
            for analysis in ai_analysis.get('section_analysis', {}).values():
                if isinstance(analysis, dict):
                    score = analysis.get('overall_score', 0)
                    if score > 0:
                        total_scores.append(score)
            
            if total_scores:
                avg_score = sum(total_scores) / len(total_scores)
                print(f"   📊 平均质量评分: {avg_score:.2f}/10")
            
            # 保存分析结果
            result_file = os.path.join(current_dir, f'cached_doc_ai_analysis_{os.path.basename(test_file)}.json')
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(ai_analysis, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 AI分析结果已保存到: {os.path.basename(result_file)}")
        
        else:
            print(f"   ⚠️ AI客户端不可用")
            
    except Exception as e:
        print(f"   ❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_section_analysis()
    test_cached_documents()
    print(f"\n AI章节分析测试完成!")
