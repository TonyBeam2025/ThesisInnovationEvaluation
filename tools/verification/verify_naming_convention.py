#!/usr/bin/env python3
"""
验证项目中所有字段都使用了正确的snake_case和语言后缀命名法
"""

import re
import os
from pathlib import Path

def check_naming_convention():
    """检查命名规范的符合性"""
    
    print("🔍 验证字段命名规范")
    print("=" * 60)
    
    # 定义正确的命名模式
    valid_patterns = {
        'chinese_fields': r'[a-z_]+_cn',      # 中文字段: *_cn
        'english_fields': r'[a-z_]+_en',      # 英文字段: *_en  
        'snake_case': r'^[a-z]+(_[a-z]+)*$',  # 标准snake_case
    }
    
    # 需要检查的旧命名模式（应该被替换）
    old_patterns = [
        r'ChineseTitle|EnglishTitle',
        r'ChineseAbstract|EnglishAbstract', 
        r'ChineseKeywords|EnglishKeywords',
        r'ChineseAuthor|EnglishAuthor',
        r'ChineseUniversity|EnglishUniversity',
        r'ChineseSupervisor|EnglishSupervisor',
        r'ChineseMajor|EnglishMajor',
        r'ThesisNumber|DegreeLevel|DefenseDate|ReferenceList'
    ]
    
    # 检查主要文件
    files_to_check = [
        'src/thesis_inno_eval/extract_sections_with_ai.py',
        'src/thesis_inno_eval/report_generator.py'
    ]
    
    issues_found = []
    
    for file_path in files_to_check:
        full_path = Path(file_path)
        if not full_path.exists():
            continue
            
        print(f"\n📄 检查文件: {file_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查是否还有旧的命名模式
        for pattern in old_patterns:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                matches = re.findall(pattern, line)
                if matches:
                    # 跳过兼容性代码 - 包含 .get('旧名', '') or .get('新名', '') 的行
                    if '.get(' in line and 'or' in line and line.count('.get(') >= 2:
                        continue
                    
                    unique_matches = list(set(matches))
                    for match in unique_matches:
                        issues_found.append(f"{file_path}: 发现旧命名 '{match}'")
                        print(f"   ⚠️  发现旧命名: {match}")
    
    # 验证标准字段列表
    try:
        from src.thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
        extractor = ThesisExtractorPro()
        
        print(f"\n📋 标准字段验证:")
        print(f"   字段总数: {len(extractor.standard_fields)}")
        
        # 统计命名规范符合性
        cn_fields = [f for f in extractor.standard_fields if f.endswith('_cn')]
        en_fields = [f for f in extractor.standard_fields if f.endswith('_en')]
        snake_fields = [f for f in extractor.standard_fields 
                       if not (f.endswith('_cn') or f.endswith('_en'))]
        
        print(f"   中文字段 (_cn): {len(cn_fields)}")
        print(f"   英文字段 (_en): {len(en_fields)}")
        print(f"   其他字段 (snake_case): {len(snake_fields)}")
        
        # 验证所有字段都符合命名规范
        all_valid = True
        for field in extractor.standard_fields:
            if field.endswith('_cn') or field.endswith('_en'):
                continue
            elif re.match(valid_patterns['snake_case'], field):
                continue
            else:
                all_valid = False
                issues_found.append(f"标准字段 '{field}' 不符合命名规范")
                print(f"   ❌ 字段 '{field}' 不符合命名规范")
        
        if all_valid:
            print(f"    所有标准字段都符合命名规范")
            
    except Exception as e:
        issues_found.append(f"无法导入ThesisExtractorPro: {e}")
        print(f"   ❌ 导入失败: {e}")
    
    # 总结报告
    print(f"\n" + "=" * 60)
    print(f"📊 验证总结:")
    
    if not issues_found:
        print(f" 完美！所有字段都使用了正确的命名规范:")
        print(f"   • 中文字段: *_cn")
        print(f"   • 英文字段: *_en") 
        print(f"   • 其他字段: snake_case")
        print(f"\n🎉 命名规范验证通过！")
        return True
    else:
        print(f"❌ 发现 {len(issues_found)} 个命名规范问题:")
        for issue in issues_found:
            print(f"   • {issue}")
        print(f"\n⚠️  请修复上述问题")
        return False

if __name__ == "__main__":
    success = check_naming_convention()
    exit(0 if success else 1)

