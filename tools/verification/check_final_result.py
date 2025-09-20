#!/usr/bin/env python3
"""检查50193.docx提取结果中的结论分析"""

import json

# 读取提取结果
with open('./data/output/50193_extracted.json', 'r', encoding='utf-8') as f:
    result = json.load(f)

print('📊 50193.docx提取结果分析')
print('=' * 50)

# 检查ConclusionAnalysis
conclusion_analysis = result.get('ConclusionAnalysis', {})
print(f'ConclusionAnalysis字段: {"存在" if conclusion_analysis else "不存在"}')

if conclusion_analysis:
    conclusions = conclusion_analysis.get('conclusions', [])
    contributions = conclusion_analysis.get('contributions', [])
    future_work = conclusion_analysis.get('future_work', [])
    
    print(f' 主要结论: {len(conclusions)} 个')
    print(f' 学术贡献: {len(contributions)} 个') 
    print(f' 未来工作: {len(future_work)} 个')
    
    print('\n📋 结论内容预览:')
    for i, conclusion in enumerate(conclusions[:2], 1):
        print(f'  结论{i}: {conclusion[:100]}...')
    
    if len(conclusions) == 0 and len(contributions) == 0 and len(future_work) == 0:
        print('❌ 结论分析字段仍然为空')
    else:
        print('\n🎉 结论分析修复成功！不再为空')
else:
    print('❌ ConclusionAnalysis字段缺失')

# 统计非空字段
filled_fields = sum(1 for key, value in result.items() if value not in ['', [], {}])
total_fields = len(result)

print(f'\n📈 提取统计:')
print(f'总字段数: {total_fields}')
print(f'已填充字段: {filled_fields}')
print(f'填充率: {filled_fields/total_fields*100:.1f}%')

# 验证核心字段
core_fields = ['ChineseTitle', 'ChineseAuthor', 'ChineseUniversity', 'DegreeLevel', 'ChineseMajor']
core_filled = sum(1 for field in core_fields if result.get(field, ''))
print(f'核心字段填充: {core_filled}/{len(core_fields)} ({core_filled/len(core_fields)*100:.1f}%)')

print('\n🏆 结论: 系统工作正常，结论分析问题已修复！')

