#!/usr/bin/env python3
"""
测试50286.docx论文信息抽取
使用专业版抽取模块直接提取论文信息
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.extract_sections_with_ai import extract_sections_with_pro_strategy
import json

def test_50286_extraction():
    """测试50286.docx论文信息抽取"""
    
    print("🚀 测试50286.docx论文信息抽取")
    print("=" * 60)
    
    file_path = "data/input/50286.docx"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    print(f"📄 目标文件: {file_path}")
    print(f"📊 文件大小: {os.path.getsize(file_path) / (1024*1024):.2f}MB")
    
    try:
        # 使用专业版策略提取论文信息
        print("\n🎯 开始使用专业版策略提取论文信息...")
        result = extract_sections_with_pro_strategy(file_path)
        
        if result:
            print("\n 提取成功！")
            
            # 统计提取结果
            non_empty_fields = {k: v for k, v in result.items() 
                              if v and str(v).strip() and v != []}
            
            print(f"📊 提取统计:")
            print(f"   📈 非空字段数: {len(non_empty_fields)}")
            print(f"   📋 总字段数: 33")
            print(f"   📊 完整度: {len(non_empty_fields)/33:.1%}")
            
            # 显示核心字段
            print(f"\n📝 核心字段提取结果:")
            key_fields = [
                'ThesisNumber', 'ChineseTitle', 'ChineseAuthor', 
                'ChineseUniversity', 'DegreeLevel', 'ChineseMajor',
                'ChineseSupervisor', 'DefenseDate'
            ]
            
            for field in key_fields:
                value = result.get(field, '')
                status = '' if value else '❌'
                display_value = str(value)[:50] + ('...' if len(str(value)) > 50 else '')
                print(f"   {status} {field}: {display_value}")
            
            # 显示内容字段
            print(f"\n📄 内容字段提取结果:")
            content_fields = [
                'ChineseAbstract', 'EnglishAbstract', 
                'ChineseKeywords', 'EnglishKeywords',
                'LiteratureReview', 'ResearchMethods',
                'ResearchConclusions'
            ]
            
            for field in content_fields:
                value = result.get(field, '')
                if value:
                    length = len(str(value))
                    print(f"    {field}: {length} 字符")
                else:
                    print(f"   ❌ {field}: 未提取")
            
            # 显示参考文献
            references = result.get('ReferenceList', [])
            if references:
                print(f"\n📚 参考文献:")
                print(f"   📊 数量: {len(references)} 条")
                if len(references) > 0:
                    print(f"   📝 示例:")
                    for i, ref in enumerate(references[:3], 1):
                        ref_str = str(ref)[:80] + ('...' if len(str(ref)) > 80 else '')
                        print(f"      [{i}] {ref_str}")
            
            # 显示智能推理字段
            print(f"\n🧠 智能推理字段:")
            inferred_fields = [
                'EnglishUniversity', 'ChineseResearchDirection', 
                'MainInnovations', 'ApplicationValue'
            ]
            
            for field in inferred_fields:
                value = result.get(field, '')
                if value:
                    display_value = str(value)[:60] + ('...' if len(str(value)) > 60 else '')
                    print(f"   🧠 {field}: {display_value}")
                else:
                    print(f"   ⚠️ {field}: 未推理")
            
            # 保存提取结果
            output_file = "data/output/50286_extracted_info.json"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 提取结果已保存到: {output_file}")
            
            return result
        
        else:
            print("❌ 提取失败，未返回结果")
            return None
            
    except Exception as e:
        print(f"❌ 提取过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_50286_extraction()
