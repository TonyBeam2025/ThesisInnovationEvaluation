#!/usr/bin/env python3
"""
测试改进后的封面信息提取
重点验证：精准定位 + AI智能识别
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

import json
from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word, ThesisExtractorPro

def test_cover_extraction():
    """测试封面信息提取"""
    
    print("🎯 测试改进后的封面信息提取")
    print("=" * 60)
    
    file_path = "data/input/50286.docx"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    try:
        # 提取文档文本
        print("📄 提取文档文本...")
        text = extract_text_from_word(file_path)
        
        if not text:
            print("❌ 文档文本提取失败")
            return
        
        print(f"📊 文档长度: {len(text):,} 字符")
        
        # 使用改进后的提取器
        extractor = ThesisExtractorPro()
        
        # 只测试封面信息提取
        print("\n🎯 测试封面信息提取...")
        cover_metadata = extractor._extract_front_metadata(text)
        
        print("\n📊 封面信息提取结果:")
        print("-" * 40)
        
        key_fields = [
            'ThesisNumber', 'ChineseTitle', 'ChineseAuthor', 
            'ChineseUniversity', 'DegreeLevel', 'ChineseMajor',
            'College', 'ChineseSupervisor', 'DefenseDate'
        ]
        
        for field in key_fields:
            value = cover_metadata.get(field, '')
            status = "" if value else "❌"
            print(f"   {status} {field}: {value}")
        
        # 检查是否有明显的错误标记
        print("\n🔍 错误检查:")
        for field, value in cover_metadata.items():
            if value:
                if '转换时间' in str(value):
                    print(f"   ⚠️ {field} 包含转换时间标记: {value}")
                elif field == 'ChineseAuthor' and ('姓名' in str(value) or len(str(value)) > 10):
                    print(f"   ⚠️ {field} 可能包含标签或异常: {value}")
                elif field == 'ChineseUniversity' and ('学位授予单位' in str(value)):
                    print(f"   ⚠️ {field} 包含格式标签: {value}")
        
        # 显示改进效果
        print(f"\n📈 改进效果对比:")
        print(f"   提取字段数: {len([v for v in cover_metadata.values() if v])}/{len(key_fields)}")
        print(f"   是否包含AI智能识别: {'是' if extractor.ai_client else '否（使用模式匹配）'}")
        
        # 保存结果
        output_file = "data/output/50286_cover_extracted_info.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        result_data = {
            'cover_metadata': cover_metadata,
            'extraction_method': 'ai_enhanced' if extractor.ai_client else 'pattern_matching',
            'extraction_time': '2025-08-20T17:15:00',
            'file_path': file_path
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 封面提取结果已保存: {output_file}")
        
        return cover_metadata
        
    except Exception as e:
        print(f"❌ 封面信息提取失败: {e}")
        import traceback
        traceback.print_exc()


def compare_with_previous():
    """与之前的结果对比"""
    
    print("\n📊 与之前结果对比:")
    print("=" * 40)
    
    # 读取之前的结果
    prev_file = "data/output/50286_pro_extracted_info.json"
    if os.path.exists(prev_file):
        with open(prev_file, 'r', encoding='utf-8') as f:
            prev_data = json.load(f)
        
        prev_info = prev_data.get('extracted_info', {})
        
        print("之前的问题字段:")
        problem_fields = {
            'ChineseTitle': prev_info.get('ChineseTitle', ''),
            'ChineseAuthor': prev_info.get('ChineseAuthor', ''),
            'EnglishAuthor': prev_info.get('EnglishAuthor', ''),
            'ChineseUniversity': prev_info.get('ChineseUniversity', '')
        }
        
        for field, value in problem_fields.items():
            print(f"   {field}: {value}")
    
    # 读取新的结果
    new_file = "data/output/50286_cover_extracted_info.json"
    if os.path.exists(new_file):
        with open(new_file, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
        
        new_info = new_data.get('cover_metadata', {})
        
        print("\n改进后的结果:")
        for field in ['ChineseTitle', 'ChineseAuthor', 'EnglishAuthor', 'ChineseUniversity']:
            value = new_info.get(field, '')
            print(f"   {field}: {value}")


if __name__ == "__main__":
    test_cover_extraction()
    compare_with_previous()
