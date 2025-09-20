#!/usr/bin/env python3
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
# -*- coding: utf-8 -*-

from src.thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
from docx import Document
import os
import json

def test_50193_extraction():
    """测试50193.docx文件的论文信息提取"""
    
    # 检查文件
    file_path = './data/input/50193.docx'
    print(f'📄 测试文件: {file_path}')
    print(f'📊 文件存在: {os.path.exists(file_path)}')
    
    if not os.path.exists(file_path):
        print(f'❌ 文件不存在: {file_path}')
        return
    
    # 提取文档内容
    print('📄 提取文档文本...')
    doc = Document(file_path)
    text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    print(f'📊 文档长度: {len(text):,} 字符')
    
    # 创建提取器并测试
    print('\n🚀 启动专业版论文信息提取器...')
    extractor = ThesisExtractorPro()
    result = extractor.extract_with_integrated_strategy(text)
    
    print(f'\n 提取完成')
    
    # 统计成功提取的字段
    successful_fields = []
    for k, v in result.items():
        if v and v != "未提取" and v != "(未提取)" and str(v).strip():
            successful_fields.append(k)
    
    print(f'📈 成功提取字段数: {len(successful_fields)}/33')
    
    # 显示关键信息
    print('\n📋 关键字段提取结果:')
    print('=' * 60)
    
    key_fields = [
        'ChineseTitle', 'EnglishTitle', 
        'ChineseAuthor', 'EnglishAuthor',
        'ChineseUniversity', 'EnglishUniversity',
        'ChineseSupervisor', 'EnglishSupervisor',
        'DegreeLevel', 'ChineseMajor'
    ]
    
    for field in key_fields:
        if field in result and result[field] and result[field] != '未提取':
            print(f'    {field:20}: {result[field]}')
        else:
            print(f'   ❌ {field:20}: 未提取')
    
    # 保存完整结果
    output_file = f'data/output/50193_extracted.json'
    os.makedirs('data/output', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f'\n💾 完整提取结果已保存: {output_file}')
    
    return result

if __name__ == "__main__":
    test_50193_extraction()
