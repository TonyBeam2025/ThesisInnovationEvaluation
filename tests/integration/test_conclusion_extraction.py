#!/usr/bin/env python3
"""测试50193.docx结论部分提取"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

print('🔍 测试文档中是否包含结论标志...')

import docx
import re

file_path = './data/input/50193.docx'
doc = docx.Document(file_path)
text = '\n'.join([para.text for para in doc.paragraphs])

print(f'文档总长度: {len(text)}')

# 查找各种结论标志
patterns_to_test = [
    '本论文主要研究了',
    '研究所得到的主要结论', 
    '参考文献',
    '致谢'
]

for pattern in patterns_to_test:
    matches = [i for i, para in enumerate(text.split('\n')) if pattern in para]
    if matches:
        print(f' 找到"{pattern}"在第{matches[0]+1}行')
        # 显示匹配行的内容
        lines = text.split('\n')
        if matches[0] < len(lines):
            print(f'   内容: {lines[matches[0]][:100]}...')
    else:
        print(f'❌ 未找到"{pattern}"')

# 查找结论部分的具体位置
conclusion_start = text.find('本论文主要研究了')
ref_start = text.find('参考文献')

if conclusion_start >= 0:
    print(f'\n 结论开始位置: {conclusion_start}')
    if ref_start >= 0:
        print(f' 参考文献位置: {ref_start}')
        conclusion_length = ref_start - conclusion_start
        print(f' 结论部分长度: {conclusion_length}')
        
        if conclusion_length > 0:
            conclusion_content = text[conclusion_start:ref_start]
            print(f' 提取的结论部分长度: {len(conclusion_content)}')
            print(f'开头: {conclusion_content[:150]}...')
            
            # 保存到文件
            with open('./data/output/extracted_conclusion.txt', 'w', encoding='utf-8') as f:
                f.write(conclusion_content)
            print('📄 结论内容已保存到 ./data/output/extracted_conclusion.txt')
            
            # 测试修复后的正则表达式
            print('\n🔧 测试正则表达式:')
            pattern = r'(本论文主要研究了[\s\S]{500,12000}?)(?=参考文献|致谢|附录|$)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                print(f' 正则表达式匹配成功，长度: {len(match.group(1))}')
            else:
                print('❌ 正则表达式未匹配')
        else:
            print('❌ 结论长度为负数')
    else:
        print('❌ 未找到参考文献')
else:
    print('❌ 未找到结论开始位置')
