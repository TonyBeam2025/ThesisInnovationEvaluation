#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
简化版专业版分批次抽取测试
延迟加载AI客户端，专注测试核心功能
"""

import os
import json
import time
from pathlib import Path

def test_pro_strategy_direct():
    """直接测试专业版策略功能"""
    
    # 测试文件
    test_file = r".\data\input\基于神经网络的相干光通信系统非线性损伤均衡技术研究_冯晓倩.pdf"
    
    print("🚀 专业版策略直接测试")
    print("=" * 50)
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return
    
    print(f"📄 测试文件: {Path(test_file).name}")
    print("-" * 50)
    
    try:
        # 动态导入，避免模块级别的初始化问题
        print("📥 导入专业版抽取函数...")
        
        start_time = time.time()
        
        # 使用专业版策略抽取
        from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy
        
        print(" 模块导入成功，开始抽取...")
        
        result = extract_sections_with_pro_strategy(
            file_path=test_file,
            use_cache=True
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if result:
            # 分析提取结果
            field_count = len([k for k, v in result.items() if v and str(v).strip()])
            total_fields = 25  # 标准字段数
            completion_rate = (field_count / total_fields) * 100
            
            print(f" 专业版抽取成功!")
            print(f"⏱️  处理时间: {processing_time:.2f} 秒")
            print(f"📊 提取字段: {field_count}/{total_fields} ({completion_rate:.1f}%)")
            
            # 显示所有提取到的字段
            print("\n📋 提取结果详情:")
            for field, value in result.items():
                if value and str(value).strip():
                    display_value = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                    print(f"  ✓ {field}: {display_value}")
            
            # 保存详细结果
            output_file = "pro_strategy_test_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'file_path': test_file,
                    'processing_time': processing_time,
                    'completion_rate': completion_rate,
                    'field_count': field_count,
                    'extracted_data': result
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 详细结果已保存: {output_file}")
            
            return result
            
        else:
            print("❌ 抽取失败: 返回结果为空")
            return None
            
    except Exception as e:
        print(f"❌ 抽取异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def analyze_extraction_capabilities():
    """分析专业版抽取能力"""
    print("\n🔬 专业版抽取能力分析")
    print("-" * 40)
    
    try:
        # 分析ThesisExtractorPro的特性（不实例化）
        from src.thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
        
        # 检查类的定义
        print("📋 ThesisExtractorPro 特性:")
        print(f"  - 类文档: {ThesisExtractorPro.__doc__.split('.')[0] if ThesisExtractorPro.__doc__ else 'N/A'}")
        
        # 查看方法列表
        methods = [method for method in dir(ThesisExtractorPro) if not method.startswith('_')]
        print(f"  - 公共方法数: {len(methods)}")
        print(f"  - 主要方法: {', '.join(methods[:5])}...")
        
        print("\n 专业版提取器类分析完成")
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")

def check_pro_strategy_availability():
    """检查专业版策略可用性"""
    print("\n🔍 检查专业版策略可用性")
    print("-" * 40)
    
    try:
        # 检查函数是否可导入
        from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy
        print(" extract_sections_with_pro_strategy 可用")
        
        # 检查函数签名
        import inspect
        sig = inspect.signature(extract_sections_with_pro_strategy)
        print(f"📝 函数签名: {sig}")
        
        # 检查文档
        doc = extract_sections_with_pro_strategy.__doc__
        if doc:
            print(f"📖 函数说明: {doc.split('.')[0]}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 检查异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔥 简化版专业版分批次抽取测试")
    print("=" * 60)
    
    # 1. 检查可用性
    if not check_pro_strategy_availability():
        print("❌ 专业版策略不可用，退出测试")
        exit(1)
    
    # 2. 分析能力
    analyze_extraction_capabilities()
    
    # 3. 直接测试
    result = test_pro_strategy_direct()
    
    if result:
        print(f"\n🎉 专业版测试成功完成!")
        print(f"📊 提取到 {len(result)} 个字段")
    else:
        print(f"\n❌ 专业版测试失败")
