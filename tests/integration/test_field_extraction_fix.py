#!/usr/bin/env python3
"""
测试修复后的pro_strategy是否能正确提取所有字段
验证是否解决了51177论文缺少字段的问题
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
import json
sys.path.append(os.path.join(str(PROJECT_ROOT), 'src'))

def test_field_extraction_fix():
    """测试字段提取修复"""
    print("🧪 测试修复后的专业策略字段提取...")
    print("="*60)
    
    try:
        from thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy
        
        # 使用51177论文进行测试
        test_file = "data/input/51177.docx"
        
        if not os.path.exists(test_file):
            print(f"❌ 测试文件不存在: {test_file}")
            return
        
        print(f"📁 测试文件: {test_file}")
        print("🚀 开始提取...")
        
        # 执行提取
        result = extract_sections_with_pro_strategy(test_file, use_cache=False)
        
        if not result:
            print("❌ 提取失败")
            return
        
        # 检查必要字段
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
        
        print(f"\n📊 字段提取结果检查:")
        print(f"总字段数: {len(result)}")
        
        missing_fields = []
        present_fields = []
        
        for field in expected_fields:
            if field in result:
                value = result[field]
                if isinstance(value, dict) and value:
                    present_fields.append(field)
                    print(f" {field}: {len(value)} 项")
                elif isinstance(value, list) and value:
                    present_fields.append(field) 
                    print(f" {field}: {len(value)} 项")
                elif isinstance(value, str) and value.strip():
                    present_fields.append(field)
                    print(f" {field}: {len(value)} 字符")
                else:
                    missing_fields.append(field)
                    print(f"⚠️ {field}: 空值")
            else:
                missing_fields.append(field)
                print(f"❌ {field}: 缺失")
        
        print(f"\n📈 提取成功率:")
        success_rate = len(present_fields) / len(expected_fields)
        print(f"成功字段: {len(present_fields)}/{len(expected_fields)} ({success_rate:.1%})")
        
        if missing_fields:
            print(f"\n⚠️ 缺失字段:")
            for field in missing_fields:
                print(f"   - {field}")
        
        # 检查多学科分析
        if 'multidisciplinary_analysis' in result:
            print(f"\n🎓 多学科分析:")
            ma = result['multidisciplinary_analysis']
            print(f"   主要学科: {ma.get('primary_discipline', 'unknown')}")
            print(f"   学科名称: {ma.get('discipline_name', 'unknown')}")
            features = ma.get('interdisciplinary_features', [])
            print(f"   交叉特征: {len(features)} 个")
        
        # 保存测试结果
        output_file = "51177_fixed_extraction_test.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 测试结果已保存: {output_file}")
        
        # 对比原始结果
        original_file = "data/output/51177_pro_extracted_info.json"
        if os.path.exists(original_file):
            with open(original_file, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
                original_result = original_data.get('extracted_info', {})
            
            print(f"\n🔄 与原始结果对比:")
            print(f"原始字段数: {len(original_result)}")
            print(f"修复后字段数: {len(result)}")
            print(f"新增字段数: {len(result) - len(original_result)}")
            
            new_fields = set(result.keys()) - set(original_result.keys())
            if new_fields:
                print(f"新增字段: {', '.join(sorted(new_fields))}")
        
        if success_rate >= 0.7:
            print(f"\n 修复测试成功！成功率: {success_rate:.1%}")
        else:
            print(f"\n❌ 修复测试失败！成功率: {success_rate:.1%}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_field_extraction_fix()
