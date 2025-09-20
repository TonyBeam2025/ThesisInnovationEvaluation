#!/usr/bin/env python3
"""
测试字段提取修复
验证论文51177是否能正确提取所有高级分析字段
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
import json
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

def test_field_extraction_fix():
    """测试字段提取修复"""
    
    print("🧪 测试字段提取修复效果")
    print("=" * 60)
    
    try:
        from thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy
        
        # 测试论文51177
        test_file = "data/input/51177.docx"
        
        if not os.path.exists(test_file):
            print(f"❌ 测试文件不存在: {test_file}")
            return False
        
        print(f"📄 测试文件: {test_file}")
        
        # 执行提取
        print("🚀 开始提取...")
        result = extract_sections_with_pro_strategy(test_file, use_cache=False)
        
        if not result:
            print("❌ 提取失败，返回None")
            return False
        
        print(" 提取成功!")
        
        # 检查关键字段
        expected_fields = [
            'table_of_contents',
            'chapter_summaries', 
            'literature_analysis',
            'methodology_analysis',
            'experimental_analysis',
            'results_analysis',
            'conclusion_analysis',
            'theoretical_framework',
            'author_contributions'
        ]
        
        print(f"\n🔍 检查高级分析字段:")
        missing_fields = []
        present_fields = []
        
        for field in expected_fields:
            if field in result:
                present_fields.append(field)
                # 检查字段是否为空
                value = result[field]
                if isinstance(value, dict) and value:
                    print(f"    {field}: 有内容 ({len(value)} 个子项)")
                elif isinstance(value, list) and value:
                    print(f"    {field}: 有内容 ({len(value)} 个条目)")
                elif isinstance(value, str) and value.strip():
                    print(f"    {field}: 有内容 ({len(value)} 字符)")
                else:
                    print(f"   ⚠️ {field}: 存在但为空")
            else:
                missing_fields.append(field)
                print(f"   ❌ {field}: 缺失")
        
        print(f"\n📊 字段统计:")
        print(f"   总字段数: {len(result)}")
        print(f"   高级字段: {len(present_fields)}/{len(expected_fields)}")
        print(f"   缺失字段: {len(missing_fields)}")
        
        if missing_fields:
            print(f"   缺失列表: {', '.join(missing_fields)}")
        
        # 保存测试结果
        output_file = "field_extraction_test_result.json"
        test_result = {
            'test_file': test_file,
            'extraction_success': True,
            'total_fields': len(result),
            'expected_advanced_fields': expected_fields,
            'present_fields': present_fields,
            'missing_fields': missing_fields,
            'field_completeness': len(present_fields) / len(expected_fields),
            'extracted_data': result
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 测试结果已保存: {output_file}")
        
        # 判断修复成功
        if len(missing_fields) == 0:
            print("\n🎉 修复成功! 所有高级字段都已正确提取")
            return True
        elif len(present_fields) > 5:
            print("\n 修复基本成功! 大部分高级字段已提取")
            return True
        else:
            print("\n❌ 修复失败! 仍有大量字段缺失")
            return False
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return False

def compare_with_reference():
    """与参考文件50193进行比较"""
    
    print("\n🔍 与参考文件50193比较")
    print("=" * 60)
    
    # 读取参考文件
    ref_file = "data/output/50193_pro_extracted_info.json"
    test_file = "field_extraction_test_result.json"
    
    try:
        if not os.path.exists(ref_file):
            print(f"❌ 参考文件不存在: {ref_file}")
            return
            
        if not os.path.exists(test_file):
            print(f"❌ 测试结果文件不存在: {test_file}")
            return
        
        with open(ref_file, 'r', encoding='utf-8') as f:
            ref_data = json.load(f)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        ref_fields = set(ref_data['extracted_info'].keys())
        test_fields = set(test_data['extracted_data'].keys())
        
        print(f"参考文件字段数: {len(ref_fields)}")
        print(f"测试结果字段数: {len(test_fields)}")
        
        missing_in_test = ref_fields - test_fields
        extra_in_test = test_fields - ref_fields
        
        if missing_in_test:
            print(f"\n❌ 测试结果中缺失的字段:")
            for field in sorted(missing_in_test):
                print(f"   - {field}")
        
        if extra_in_test:
            print(f"\n➕ 测试结果中额外的字段:")
            for field in sorted(extra_in_test):
                print(f"   + {field}")
        
        if not missing_in_test:
            print("\n🎉 完美! 测试结果包含所有参考字段")
        
    except Exception as e:
        print(f"❌ 比较失败: {e}")

if __name__ == "__main__":
    success = test_field_extraction_fix()
    compare_with_reference()
    
    if success:
        print("\n 字段提取修复测试通过!")
    else:
        print("\n❌ 字段提取修复测试失败!")
