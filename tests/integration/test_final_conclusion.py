#!/usr/bin/env python3
"""测试完整的结论分析流程"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT

import sys
sys.path.append('./src')
from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
import docx
import json

print('🧪 测试完整的结论分析流程...')

# 读取文档
file_path = './data/input/50193.docx'
doc = docx.Document(file_path)
text = '\n'.join([para.text for para in doc.paragraphs])

# 初始化提取器
extractor = ThesisExtractorPro()

# 测试结论分析
conclusion_analysis = extractor._analyze_conclusion_with_ai(text)

print('\n📊 结论分析结果:')
conclusions = conclusion_analysis.get('conclusions', [])
contributions = conclusion_analysis.get('contributions', [])
future_work = conclusion_analysis.get('future_work', [])

print(f'主要结论: {len(conclusions)} 个')
for i, conclusion in enumerate(conclusions, 1):
    print(f'  {i}. {conclusion[:80]}...')

print(f'\n学术贡献: {len(contributions)} 个')
for i, contribution in enumerate(contributions, 1):
    print(f'  {i}. {contribution[:80]}...')

print(f'\n未来工作: {len(future_work)} 个')
for i, future in enumerate(future_work, 1):
    print(f'  {i}. {future[:80]}...')

# 保存详细结果
with open('./data/output/final_conclusion_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(conclusion_analysis, f, ensure_ascii=False, indent=2)

print('\n💾 详细结果已保存到 ./data/output/final_conclusion_analysis.json')

# 验证结论部分不再为空
if conclusions or contributions or future_work:
    print('\n🎉 结论分析修复成功！结论部分不再为空')
else:
    print('\n❌ 结论分析仍然为空，需要进一步调试')
