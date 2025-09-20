#!/usr/bin/env python3
"""
测试改进后的英文导师字段清理
"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
import os
sys.path.insert(0, os.path.join(str(PROJECT_ROOT), 'src'))

from thesis_inno_eval.extract_sections_with_ai import extract_text_from_word, ThesisExtractorPro

def test_supervisor_field_cleaning():
    """测试英文导师字段清理"""
    
    print("🧪 测试英文导师字段清理改进")
    print("=" * 50)
    
    file_path = "data/input/50286.docx"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    try:
        # 提取文档文本
        text = extract_text_from_word(file_path)
        extractor = ThesisExtractorPro()
        
        # 只测试封面信息提取
        cover_metadata = extractor._extract_front_metadata(text)
        
        print("🎯 重点测试字段:")
        test_fields = {
            'EnglishAuthor': '英文作者',
            'EnglishSupervisor': '英文导师', 
            'EnglishUniversity': '英文大学',
            'EnglishMajor': '英文专业'
        }
        
        for field, description in test_fields.items():
            value = cover_metadata.get(field, '')
            if value:
                print(f"    {description:8}: {value}")
            else:
                print(f"   ❌ {description:8}: (未提取)")
        
        # 检查清理质量
        print(f"\n🔍 清理质量检查:")
        issues = []
        
        supervisor = cover_metadata.get('EnglishSupervisor', '')
        if supervisor:
            if 'School' in supervisor or 'University' in supervisor or 'Beihang' in supervisor:
                issues.append(f"英文导师包含机构信息: {supervisor}")
            else:
                print(f"    英文导师清理完成: {supervisor}")
        
        university = cover_metadata.get('EnglishUniversity', '')
        if university:
            if university == 'Beihang University':
                print(f"    英文大学标准化: {university}")
            else:
                print(f"   ⚠️ 英文大学需要检查: {university}")
        
        major = cover_metadata.get('EnglishMajor', '')
        if major:
            if 'University' not in major:
                print(f"    英文专业清理完成: {major}")
            else:
                issues.append(f"英文专业包含大学信息: {major}")
        
        if issues:
            print(f"\n⚠️ 发现的问题:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"\n🎉 所有字段清理质量良好！")
        
        return cover_metadata
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_supervisor_field_cleaning()
