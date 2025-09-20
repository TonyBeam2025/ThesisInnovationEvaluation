#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试专业版分批次抽取论文信息
使用 extract_sections_with_pro_strategy 进行高级抽取
"""

import os
import json
import time
from pathlib import Path
from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy

def test_pro_strategy_batch_extraction():
    """测试专业版策略分批次抽取功能"""
    
    # 测试文件列表 - 只测试指定的两个文件
    test_files = [
        r".\data\input\跨模态图像融合技术在医疗影像分析中的研究.docx",
        r".\data\input\50193.docx"
    ]
    
    results = {}
    
    print("🚀 开始专业版分批次抽取测试...")
    print("=" * 60)
    
    for i, file_path in enumerate(test_files, 1):
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            continue
            
        print(f"\n📄 测试文件 {i}: {Path(file_path).name}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            # 使用专业版策略抽取
            result = extract_sections_with_pro_strategy(
                file_path=file_path,
                use_cache=True
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            if result:
                # 分析提取结果
                field_count = len([k for k, v in result.items() if v and str(v).strip()])
                total_fields = 25  # 标准字段数
                completion_rate = (field_count / total_fields) * 100
                
                print(f" 抽取成功!")
                print(f"⏱️  处理时间: {processing_time:.2f} 秒")
                print(f"📊 提取字段: {field_count}/{total_fields} ({completion_rate:.1f}%)")
                
                # 显示关键字段
                key_fields = ['title_cn', 'author_cn', 'university_cn', 'major_cn', 'supervisor_cn']
                print("\n🔍 关键字段预览:")
                for field in key_fields:
                    value = result.get(field, '')
                    if value:
                        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"  {field}: {display_value}")
                
                # 检查是否有多学科特征
                if hasattr(result, 'multidisciplinary_features'):
                    features = result.get('multidisciplinary_features', [])
                    if features:
                        print(f"🔬 多学科特征: {', '.join(features)}")
                
                results[file_path] = {
                    'success': True,
                    'field_count': field_count,
                    'completion_rate': completion_rate,
                    'processing_time': processing_time,
                    'result': result
                }
                
                # 保存详细结果到文件
                output_file = f"pro_strategy_result_{i}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'file_path': file_path,
                        'processing_time': processing_time,
                        'completion_rate': completion_rate,
                        'extracted_data': result
                    }, f, ensure_ascii=False, indent=2)
                print(f"💾 详细结果已保存: {output_file}")
                
            else:
                print(f"❌ 抽取失败: 返回结果为空")
                results[file_path] = {
                    'success': False,
                    'error': 'Empty result',
                    'processing_time': processing_time
                }
                
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"❌ 抽取异常: {str(e)}")
            results[file_path] = {
                'success': False,
                'error': str(e),
                'processing_time': processing_time
            }
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("📊 专业版分批次抽取测试总结")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results.values() if r.get('success', False))
    total_tests = len(results)
    
    print(f" 成功测试: {successful_tests}/{total_tests}")
    
    if successful_tests > 0:
        avg_completion = sum(r.get('completion_rate', 0) for r in results.values() if r.get('success')) / successful_tests
        avg_time = sum(r.get('processing_time', 0) for r in results.values() if r.get('success')) / successful_tests
        print(f"📈 平均完成率: {avg_completion:.1f}%")
        print(f"⏱️  平均处理时间: {avg_time:.2f} 秒")
    
    # 显示失败的测试
    failed_tests = [file_path for file_path, result in results.items() if not result.get('success', False)]
    if failed_tests:
        print(f"\n❌ 失败的测试:")
        for file_path in failed_tests:
            error = results[file_path].get('error', 'Unknown error')
            print(f"  - {Path(file_path).name}: {error}")
    
    return results

def analyze_pro_strategy_features():
    """分析专业版策略的特性"""
    print("\n🔬 专业版策略特性分析")
    print("-" * 40)
    
    try:
        from src.thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
        
        # 创建提取器实例
        extractor = ThesisExtractorPro()
        
        print(f"📋 支持的标准字段数: {len(extractor.standard_fields)}")
        print(f"🎓 支持的学科领域: {len(extractor.supported_disciplines)}")
        
        print("\n📋 标准字段列表:")
        for i, field in enumerate(extractor.standard_fields, 1):
            print(f"  {i:2d}. {field}")
        
        print("\n🎓 支持的学科领域:")
        for key, name in extractor.supported_disciplines.items():
            print(f"  - {key}: {name}")
            
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")

if __name__ == "__main__":
    print("🔥 专业版分批次抽取测试程序")
    print("=" * 60)
    
    # 分析专业版特性
    analyze_pro_strategy_features()
    
    # 运行分批次测试
    results = test_pro_strategy_batch_extraction()
    
    print(f"\n🎉 测试完成! 共处理 {len(results)} 个文件")
