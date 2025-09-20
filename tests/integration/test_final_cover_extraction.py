#!/usr/bin/env python3
"""
最终测试：展示封面信息提取的完整改进效果
对比之前的问题和现在的解决方案
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

import json
from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word, ThesisExtractorPro

def final_test():
    """最终测试：完整展示改进效果"""
    
    print("🎯 论文封面信息提取改进效果展示")
    print("=" * 60)
    
    file_path = "data/input/50286.docx"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    try:
        # 提取文档文本
        print("📄 提取文档文本...")
        text = extract_text_from_word(file_path)
        print(f"📊 文档长度: {len(text):,} 字符")
        
        # 使用改进后的提取器
        print("\n🚀 使用改进后的提取器...")
        extractor = ThesisExtractorPro()
        
        # 测试封面信息提取
        cover_metadata = extractor._extract_front_metadata(text)
        
        print(f"\n📊 核心改进技术:")
        print(f"    精准定位：在'学位论文使用授权书'之前")
        print(f"    智能清理：移除所有标签文字")
        print(f"    字段特化：针对不同字段的专门处理")
        
        print(f"\n🎉 改进后的提取结果:")
        print("-" * 50)
        
        # 重点展示之前有问题的字段
        problem_fields = {
            'ThesisNumber': '学号',
            'ChineseTitle': '中文标题', 
            'ChineseAuthor': '作者姓名',
            'ChineseUniversity': '学校名称',
            'DegreeLevel': '学位级别',
            'ChineseMajor': '专业名称',
            'College': '学院名称',
            'ChineseSupervisor': '导师姓名'
        }
        
        for field, description in problem_fields.items():
            value = cover_metadata.get(field, '')
            status = "" if value else "❌"
            print(f"   {status} {description:12}: {value}")
        
        print(f"\n📈 质量评估:")
        extracted_count = len([v for v in cover_metadata.values() if v])
        total_fields = len(problem_fields)
        completeness = extracted_count / total_fields
        print(f"   提取成功率: {extracted_count}/{total_fields} ({completeness:.1%})")
        
        # 检查是否还有标签文字残留
        has_labels = any('：' in str(v) or '姓名' in str(v) or '学位授予单位' in str(v) 
                        for v in cover_metadata.values() if v)
        print(f"   标签清理: {'完成' if not has_labels else '仍有残留'}")
        
        print(f"\n🆚 与之前结果对比:")
        print("-" * 50)
        
        # 读取之前的问题结果
        prev_file = "data/output/50286_pro_extracted_info.json"
        if os.path.exists(prev_file):
            with open(prev_file, 'r', encoding='utf-8') as f:
                prev_data = json.load(f)
            prev_info = prev_data.get('extracted_info', {})
            
            print("   🔴 之前的问题:")
            print(f"      ChineseTitle: {prev_info.get('ChineseTitle', '')}")
            print(f"      ChineseAuthor: {prev_info.get('ChineseAuthor', '')}")
            print(f"      ChineseUniversity: {prev_info.get('ChineseUniversity', '')}")
            
            print("   🟢 现在的结果:")
            print(f"      ChineseTitle: {cover_metadata.get('ChineseTitle', '(暂未提取)')}")
            print(f"      ChineseAuthor: {cover_metadata.get('ChineseAuthor', '')}")
            print(f"      ChineseUniversity: {cover_metadata.get('ChineseUniversity', '')}")
        
        print(f"\n💡 技术突破点:")
        print(f"   1. 精准定位封面区域 - 避免混入后续内容")
        print(f"   2. 智能标签清理 - 移除'姓名：'等格式文字") 
        print(f"   3. 字段特化处理 - 针对不同类型字段专门优化")
        print(f"   4. 多层验证机制 - 确保结果质量")
        
        print(f"\n🎯 下一步优化建议:")
        print(f"   - 集成AI智能识别（目前因导入问题暂未启用）")
        print(f"   - 增强中文标题提取逻辑")
        print(f"   - 添加更多大学名称和格式支持")
        
        # 保存最终结果
        output_file = "data/output/50286_final_cover_extracted_info.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        result_data = {
            'final_cover_metadata': cover_metadata,
            'extraction_method': 'precise_location_plus_smart_cleaning',
            'improvements': [
                'precise_cover_location',
                'intelligent_label_cleaning', 
                'field_specific_processing',
                'multi_layer_validation'
            ],
            'extraction_time': '2025-08-20T17:25:00',
            'file_path': file_path,
            'quality_metrics': {
                'extracted_fields': extracted_count,
                'total_fields': total_fields,
                'completeness': completeness,
                'labels_cleaned': not has_labels
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 最终结果已保存: {output_file}")
        
        return cover_metadata
        
    except Exception as e:
        print(f"❌ 最终测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    final_test()
