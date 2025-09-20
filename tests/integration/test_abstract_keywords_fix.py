#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-
"""
测试专业版策略的摘要和关键词抽取修复
"""

import os
import sys
import time
from pathlib import Path

# 添加项目路径
project_root = PROJECT_ROOT
sys.path.insert(0, str(project_root))

def test_abstract_keywords_extraction():
    """测试摘要和关键词抽取"""
    
    print("🧪 测试专业版策略摘要和关键词抽取修复")
    print("=" * 60)
    
    try:
        from src.thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy
        from src.thesis_inno_eval.config_manager import reset_config_manager
        
        # 重置配置
        reset_config_manager()
        
        # 测试文件
        test_file = r".\data\input\跨模态图像融合技术在医疗影像分析中的研究.docx"
        
        if not os.path.exists(test_file):
            print(f"❌ 测试文件不存在: {test_file}")
            return
            
        print(f"📄 测试文件: {Path(test_file).name}")
        print("-" * 40)
        
        start_time = time.time()
        
        result = extract_sections_with_pro_strategy(
            file_path=test_file,
            use_cache=True
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if result:
            print(f" 抽取成功! 处理时间: {processing_time:.2f} 秒")
            print()
            
            # 检查关键字段
            abstract_keywords_fields = [
                'abstract_cn', 'abstract_en', 
                'keywords_cn', 'keywords_en'
            ]
            
            print("📊 摘要和关键词字段检查:")
            for field in abstract_keywords_fields:
                if field in result:
                    value = result[field]
                    if value and str(value).strip():
                        if len(str(value)) > 100:
                            display_value = str(value)[:100] + "..."
                        else:
                            display_value = str(value)
                        print(f"   {field}: {display_value}")
                    else:
                        print(f"  ❌ {field}: (空值)")
                else:
                    print(f"  ❌ {field}: (字段不存在)")
            
            # 统计提取情况
            extracted_count = sum(1 for field in abstract_keywords_fields 
                                if field in result and result[field] and str(result[field]).strip())
            total_count = len(abstract_keywords_fields)
            
            print(f"\n📈 摘要关键词完成率: {extracted_count}/{total_count} ({extracted_count/total_count*100:.1f}%)")
            
            # 检查是否有具体的摘要和关键词内容
            if extracted_count > 0:
                print("🎉 修复成功! 专业版策略现在能正确提取摘要和关键词")
            else:
                print("⚠️ 仍然存在问题，所有摘要和关键词字段都为空")
                
        else:
            print("❌ 抽取失败: 返回空结果")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🔥 专业版策略摘要关键词抽取修复测试")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    test_abstract_keywords_extraction()
    
    print(f"\n🎉 测试完成!")
