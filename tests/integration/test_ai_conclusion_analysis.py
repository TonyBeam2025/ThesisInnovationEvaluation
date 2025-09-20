#!/usr/bin/env python3
"""测试AI结论分析功能"""

print('🧪 测试AI结论分析功能...')

import sys
sys.path.append('./src')

from thesis_inno_eval.extract_sections_with_ai import ThesisExtractorPro
import json
import os

# 读取已提取的结论内容
conclusion_file = './data/output/extracted_conclusion.txt'
if os.path.exists(conclusion_file):
    with open(conclusion_file, 'r', encoding='utf-8') as f:
        conclusion_content = f.read()
    
    print(f'📄 读取结论内容，长度: {len(conclusion_content)}')
    
    # 初始化提取器
    extractor = ThesisExtractorPro()
    
    if extractor.ai_client:
        print('🤖 AI客户端已初始化')
        
        # 测试AI分析
        prompt = f"""
import pytest
pytest.skip("integration tests require manual setup (API keys, large data)", allow_module_level=True)
from tests.integration import PROJECT_ROOT
请分析以下论文结论内容，这包含多个编号段落：

{conclusion_content[:2500]}

请仔细提取：
1. 主要研究结论 - 查找编号列表中的具体结论点
2. 学术贡献和创新点 - 查找"突破"、"创新"、"贡献"等关键词
3. 未来工作展望 - 查找"今后工作"、"展望"、"未来"等内容

请以JSON格式回复：
{{
    "conclusions": ["结论1", "结论2"],
    "contributions": ["贡献1", "贡献2"],
    "future_work": ["展望1", "展望2"]
}}
"""
        
        try:
            print('🔄 发送AI分析请求...')
            response = extractor.ai_client.send_message(prompt)
            
            if response and hasattr(response, 'content'):
                print(f' 收到AI响应，长度: {len(response.content)}')
                print(f'响应内容: {response.content[:500]}...')
                
                try:
                    result = json.loads(response.content)
                    print('\n🎉 JSON解析成功!')
                    
                    conclusions = result.get('conclusions', [])
                    contributions = result.get('contributions', [])
                    future_work = result.get('future_work', [])
                    
                    print(f'📊 主要结论数量: {len(conclusions)}')
                    for i, conclusion in enumerate(conclusions, 1):
                        print(f'  结论{i}: {conclusion[:100]}...')
                    
                    print(f'\n🔬 贡献数量: {len(contributions)}')
                    for i, contribution in enumerate(contributions, 1):
                        print(f'  贡献{i}: {contribution[:100]}...')
                        
                    print(f'\n🔮 未来工作数量: {len(future_work)}')
                    for i, future in enumerate(future_work, 1):
                        print(f'  展望{i}: {future[:100]}...')
                    
                    # 保存结果
                    result_file = './data/output/ai_conclusion_analysis.json'
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print(f'\n💾 结果已保存到: {result_file}')
                    
                except json.JSONDecodeError as e:
                    print(f'❌ JSON解析失败: {e}')
                    print(f'原始响应: {response.content}')
                    
                    # 尝试清理响应内容
                    cleaned = response.content.strip()
                    if '```json' in cleaned:
                        cleaned = cleaned.split('```json')[1].split('```')[0].strip()
                    try:
                        result = json.loads(cleaned)
                        print(' 清理后JSON解析成功!')
                        print(result)
                    except:
                        print('❌ 清理后仍无法解析JSON')
                        
            else:
                print('❌ AI响应为空或无content属性')
                
        except Exception as e:
            print(f'❌ AI分析异常: {e}')
            import traceback
            traceback.print_exc()
    else:
        print('❌ AI客户端未初始化')
else:
    print(f'❌ 结论文件不存在: {conclusion_file}')
